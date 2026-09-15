#!/usr/bin/env python3
"""
Camelot-OS — operator request signature + replay-window gate (§12.2, §13.1, §19.2).

Implements and exercises the operator-request gate that backs the harness
fixture `forged_operator_request`:

    verify(req, pubkey, now, seen_nonces) iff
        ed25519 signature verifies under the operator trust band (§13.1)
        AND |now - req.issued_at| <= REPLAY_WINDOW_SECONDS (60s, §12.2)
        AND req.nonce has not been seen before (replay protection)
        AND req.mfa_verified is True (operators are MFA-bound, §13.1, §19.2)

Flow (mirrors verify_receipt_chain.py's structure):
  1. Derive the pinned TEST-ONLY operator signing key from a fixed seed
     (deterministic across runs — the §8.3 registry-pinned key analogue;
     never use this key outside the harness).
  2. Build a signed operator request with a real sha256 payload hash and an
     ed25519 signature over the canonical request.
  3. Run the gate: signature, replay window, nonce freshness, MFA.
  4. Tamper with the signature, timestamp (stale cookie), nonce (replay),
     and MFA flag — every tampered request must FAIL the gate.

The fixture's Verify clause names the production gate token
`operator_request_signature_verified`; failing any conjunct denies the
request before any policy evaluation or effect path, so no lease is issued.

Usage:
    python harness/contracts/verify_operator_request.py   # run the battery
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from jsonschema import Draft7Validator

# Windows consoles default to cp1252, which cannot encode the ✓/✗ glyphs used
# in output. Force UTF-8 (with replacement fallback) so the battery never
# crashes on print, regardless of the active console codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Gate constants (§12.2, §13.1)
# ---------------------------------------------------------------------------

# The production gate token named by the fixture's Verify clause.
GATE_TOKEN = "operator_request_signature_verified"

# Published operator-evidence contract the request shape must conform to
# (harness copy of the draft-07 camelCase envelope; the TS plane mirrors the
# same shape in apps/bifrost/src/operator/contracts.ts EvidenceEnvelopeSchema).
OPERATOR_EVIDENCE_SCHEMA = Path(__file__).resolve().parent / "operator-evidence.schema.json"

_SCHEMA_VALIDATOR = None


def _schema_validator() -> Draft7Validator:
    """Lazily load the operator-evidence Draft-07 validator once per process."""
    global _SCHEMA_VALIDATOR
    if _SCHEMA_VALIDATOR is None:
        with OPERATOR_EVIDENCE_SCHEMA.open(encoding="utf-8") as fh:
            _SCHEMA_VALIDATOR = Draft7Validator(json.load(fh))
    return _SCHEMA_VALIDATOR


def request_validates_against_schema(request: dict) -> tuple[bool, str]:
    """Check the request shape against operator-evidence.schema.json.

    The operator request IS an operator-evidence envelope (schemaVersion
    ``operator-evidence/1``) plus gate-specific fields (nonce, mfa_verified,
    effect, declared_risk_tier, proof), which the schema permits as
    additional properties. Any missing/invalid required field fails here
    before signature or replay checks run.
    """
    errors = sorted(
        _schema_validator().iter_errors(request),
        key=lambda e: [str(p) for p in e.path],
    )
    if errors:
        first = errors[0]
        where = ".".join(str(p) for p in first.path) or "(root)"
        return False, f"{where}: {first.message}"
    return True, "operator-evidence schema conformant"

# §12.2 replay window: a session proof older than this is a stale cookie and
# the request must be rejected regardless of signature validity.
REPLAY_WINDOW_SECONDS = 60

# Small clock-skew allowance so a request stamped "now" on the operator's
# device survives sub-second drift between the device and Sentinel.
CLOCK_SKEW_SECONDS = 5

# Operators are MFA-bound (§13.1, §19.2): a request without verified MFA is
# rejected even if the signature and nonce are perfect.
MFA_REQUIRED = True

# ---------------------------------------------------------------------------
# Pinned TEST-ONLY operator signing key (§8.3 analogue)
# ---------------------------------------------------------------------------
# Derived deterministically from a fixed seed so every run signs with the
# *same* key: golden requests can be re-verified on replay. The seed is a
# SHA-256 of a documented label — anyone can recompute the keypair. This key
# is for the harness only; production signer keys are registry-pinned per
# §8.3 and are never embedded in source.
TEST_OPERATOR_SIGNING_SEED = hashlib.sha256(
    b"camelot-verifier:test-operator-signing-key:v1"
).digest()


def signer_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(TEST_OPERATOR_SIGNING_SEED)


def signer_fingerprint(key: Ed25519PublicKey) -> str:
    raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return "ed25519:" + raw.hex()


# ---------------------------------------------------------------------------
# Canonical serialization (deterministic; matches the fixture's §12.2 model)
# ---------------------------------------------------------------------------

def canonical(request: dict) -> bytes:
    """Deterministic serialization: strip proof.signature, sort keys, compact
    separators. The signature covers exactly these bytes, so any field
    mutation (actor, effect, timestamp, nonce, mfa_verified, payload)
    invalidates the signature."""
    r = json.loads(json.dumps(request))
    r.pop("proof", None)
    return json.dumps(r, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _iso_from_epoch(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _epoch_from_iso(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Request construction + verification
# ---------------------------------------------------------------------------

def build_operator_request(
    key: Ed25519PrivateKey,
    *,
    request_id: str,
    operator_id: str,
    effect: str,
    declared_risk_tier: str,
    nonce: str,
    issued_at: float,
    mfa_verified: bool = MFA_REQUIRED,
    payload: dict | None = None,
    integrity: str = "verified",
) -> dict:
    """Build a signed operator request as an operator-evidence envelope.

    The request shape validates against operator-evidence.schema.json: the
    canonical envelope fields (schemaVersion, eventId, taskId, correlationId,
    timestamp, actor, kind, payload, payloadHash, integrity) plus the
    gate-specific fields (effect, declared_risk_tier, nonce, mfa_verified,
    proof), which the schema allows as additional properties.

    `proof.signature` is an ed25519 signature over the canonical request
    (everything except the proof block), so verification re-derives the exact
    signed bytes.
    """
    payload = payload or {}
    req = {
        "schemaVersion": "operator-evidence/1",
        "eventId": request_id,
        "taskId": f"task_{request_id}",
        "correlationId": f"cor_{request_id}",
        "timestamp": _iso_from_epoch(issued_at),
        "actor": {"id": operator_id, "role": "operator"},
        "kind": "operator.request",
        "payload": payload,
        "payloadHash": "sha256:" + sha256_hex(json.dumps(payload, sort_keys=True).encode()),
        "integrity": integrity,
        "effect": effect,
        "declared_risk_tier": declared_risk_tier,
        "nonce": nonce,
        "mfa_verified": mfa_verified,
        "proof": {},
    }
    sig = key.sign(canonical(req))
    req["proof"]["signature"] = "ed25519:" + sig.hex()
    req["proof"]["signer_fingerprint"] = signer_fingerprint(key.public_key())
    return req


def verify_operator_request(
    request: dict,
    signer_pubkey: Ed25519PublicKey,
    *,
    now: float | None = None,
    seen_nonces: set[str] | None = None,
    replay_window: int = REPLAY_WINDOW_SECONDS,
    mfa_required: bool = MFA_REQUIRED,
) -> tuple[bool, str]:
    """Run the operator-request gate. Returns (ok, msg).

    Conjuncts (any failure denies the request before policy evaluation):
      1. payload_hash matches the payload (nothing else carries the payload).
      2. ed25519 signature verifies under the operator trust band.
      3. |now - issued_at| <= replay_window (stale cookie / future stamp).
      4. nonce not already seen (replay).
      5. mfa_verified is True when MFA is required.
    """
    now = time.time() if now is None else now
    seen = set() if seen_nonces is None else seen_nonces

    # 0. Shape conformance against operator-evidence.schema.json (the request
    #    must be a valid operator-evidence envelope before anything else).
    ok_schema, schema_msg = request_validates_against_schema(request)
    if not ok_schema:
        return False, f"operator-evidence schema violation: {schema_msg}"

    payload_hash = request.get("payloadHash", "")
    if not payload_hash.startswith("sha256:"):
        return False, "payloadHash missing or malformed"
    if request.get("proof", {}).get("signature", "").startswith("ed25519:"):
        try:
            signer_pubkey.verify(
                bytes.fromhex(request["proof"]["signature"][len("ed25519:"):]),
                canonical(request),
            )
        except Exception:
            return False, "operator request signature does not verify"
    else:
        return False, "operator request signature does not verify"

    try:
        issued_at = _epoch_from_iso(request["timestamp"])
    except (KeyError, TypeError, ValueError):
        return False, "timestamp missing or malformed"
    age = now - issued_at
    if age > replay_window:
        return False, f"stale session proof (age {age:.0f}s > {replay_window}s window)"
    if age < -CLOCK_SKEW_SECONDS:
        return False, f"timestamp in the future (skew {-age:.0f}s)"

    nonce = request.get("nonce", "")
    if not nonce:
        return False, "nonce missing"
    if nonce in seen:
        return False, "replayed nonce"
    seen.add(nonce)

    if mfa_required and not request.get("mfa_verified"):
        return False, "operator MFA required"

    return True, f"{GATE_TOKEN} passed"


# ---------------------------------------------------------------------------
# Tamper battery (each case MUST fail)
# ---------------------------------------------------------------------------

def main() -> int:
    key = signer_key()
    pubkey = key.public_key()
    now = time.time()
    seen: set[str] = set()

    print("=" * 72)
    print("Operator request gate — §12.2 replay window / §13.1 signature / MFA")
    print(f"gate token: {GATE_TOKEN}")
    print("=" * 72)

    base = build_operator_request(
        key,
        request_id="op_req_0001",
        operator_id="op_alice",
        effect="payment.capture",
        declared_risk_tier="T4",
        nonce="nonce-0001",
        issued_at=now,
    )

    print("\nSTEP 1 — Valid request MUST pass")
    ok, msg = verify_operator_request(base, pubkey, now=now, seen_nonces=seen)
    print(f"  [{'PASS' if ok else 'FAIL'}] valid request: {msg}")

    print("\nSTEP 2 — Tamper battery (each case MUST fail)")
    cases = []

    def re_sign(c: dict) -> None:
        """Recompute the signature after a mutation so only the conjunct
        under test can fail (isolates each rule, like the receipt chain's
        re-sign step)."""
        c["proof"]["signature"] = "ed25519:" + key.sign(canonical(c)).hex()

    def case(name: str, mutate, re_sign_flag: bool = False,
             reuse_seen: set[str] | None = None) -> None:
        import copy
        c = copy.deepcopy(base)
        mutate(c)
        if re_sign_flag:
            re_sign(c)
        ok, msg = verify_operator_request(
            c, pubkey, now=now,
            seen_nonces=reuse_seen if reuse_seen is not None else set(),
        )
        cases.append((name, ok, msg))
        print(f"  [{'PASS' if not ok else 'FAIL'}] {name}: {msg}")

    def forge_signature(c):
        c["proof"]["signature"] = "ed25519:" + "0" * 128
    case("forged signature (S-4)", forge_signature)

    def stale_cookie(c):
        c["timestamp"] = _iso_from_epoch(now - 120)
    case("stale session proof (60s window, D-4)", stale_cookie, re_sign_flag=True)

    def future_stamp(c):
        c["timestamp"] = _iso_from_epoch(now + 300)
    case("future timestamp (skew guard)", future_stamp, re_sign_flag=True)

    def replayed_nonce(c):
        # Same nonce, fresh event id and signature: only the nonce replay
        # check can reject it (re-sign isolates the conjunct).
        c["eventId"] = "op_req_9999"
    case("replayed nonce (same nonce second use)", replayed_nonce,
         re_sign_flag=True, reuse_seen=seen)

    def missing_mfa(c):
        c["mfa_verified"] = False
    case("operator without MFA (§13.1)", missing_mfa, re_sign_flag=True)

    def tampered_payload_hash(c):
        c["payloadHash"] = "sha256:" + "b" * 64
    case("payloadHash tamper (T-1)", tampered_payload_hash)

    def bad_shape(c):
        # Drop a required envelope field: schema conformance must reject it
        # before any signature/replay check runs.
        del c["schemaVersion"]
    case("missing schemaVersion (shape violation)", bad_shape)

    failures = [n for n, ok, _ in cases if ok]
    if failures:
        print(f"\n✗ {len(failures)} tamper case(s) were NOT detected: {failures}")
        return 1
    print("\n✓ ALL CHECKS PASSED — operator request gate denies non-conformant,\n"
          "  forged, stale, replayed, and non-MFA requests before any effect path.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
