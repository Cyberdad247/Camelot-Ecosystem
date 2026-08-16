#!/usr/bin/env python3
"""
Camelot-OS — receipt chain end-to-end verification harness.

Implements and exercises the §11.3 chain verification rule against the
published contract schema `packages/contracts/receipt.schema.json`:

    verify(chain) iff ∀ receipt r:
        sha256(canonical(r, r.parent_hash)) == r.self_hash
        AND r.signature verifies under signer_trust_band
        AND r.chain_height == r.parent.chain_height + 1
        AND r.authority_epoch >= trusted_epoch_at_verify_time

Flow:
  1. Derive the pinned TEST-ONLY Sentinel signing key from a fixed seed
     (deterministic across runs — the registry-pinned signer-trust-band key
     analogue of §8.3; never use this key outside the harness).
  2. Build a 4-receipt chain (genesis + 3) with real sha256 self-hashes and
     ed25519 signatures.
  3. Validate every receipt against `receipt.schema.json` (Draft 2020-12).
  4. Run the §11.3 verification rule over the chain.
  5. Tamper with parent_hash, payload, chain_height, signature, and epoch —
     every tampered chain must FAIL verification (tamper detection).
  6. Ledger anchoring (§11.3): build a 2,000-receipt long-run chain, write a
     ledger-anchor record at every Nth entry (N=1000) capturing the chain
     head, ed25519-sign each record with the pinned key so tampering is
     detectable from the record alone (no chain re-derivation), validate the
     records against `receipt-chain.schema.json`, and run anchor tamper
     detection (T-10, S-4).
  7. Emit the committed golden set: receipts, ledger-anchor records (the
     tenant_ledger anchors at every Nth entry AND golden-anchor-0000.json
     covering the demo chain's genesis head), and the pinned public key, so
     any later run can re-verify the exact same artifacts from disk
     (`--replay`).

Usage:
    python harness/contracts/verify_receipt_chain.py            # build + verify + emit golden receipts
    python harness/contracts/verify_receipt_chain.py --replay   # verify the emitted golden receipts from disk
    python harness/contracts/verify_receipt_chain.py --anchor-every 100 --chain-size 5000
                                                                # stress-test: anchor every 100th entry over 5,000 receipts
    python harness/run_all.py --anchor-every 100 --chain-size 5000
                                                                # same config through the full gate

Flags:
    --anchor-every N   write the head to the ledger anchor every N entries
                       (default 1000, SADD §11.3). Affects build/emit only.
    --chain-size N     number of receipts in the anchored stress-test chain
                       (default 2000). Affects build/emit only.
    --replay           verify committed artifacts from disk. The anchored-chain
                       config is read from chain.verified (written at emit
                       time), so --anchor-every and --chain-size are ignored
                       on replay — replay always re-derives with the persisted
                       config so the committed anchors must match exactly.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from jsonschema import Draft202012Validator

# Windows consoles default to cp1252, which cannot encode the ✓/✗ glyphs
# used in output. Force UTF-8 (with replacement fallback) so the harness never
# crashes on print, regardless of the active console codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "packages" / "contracts" / "receipt.schema.json"
GOLDEN_DIR = ROOT / "harness" / "golden-receipts"
PUBKEY_FILE = GOLDEN_DIR / "sentinel_test_public.pem"
MARKER_FILE = GOLDEN_DIR / "chain.verified"
GOLDEN_ANCHOR_FILE = GOLDEN_DIR / "golden-anchor-0000.json"
CHAIN_SIZE = 4  # rcp_0000..rcp_0003

SIGNER = "sentinel"
TRUSTED_EPOCH = 43

# Ledger anchoring (§11.3): the chain head is written to the ledger anchor at
# every Nth entry (default N=1000). ANCHORED_CHAIN_SIZE receipts give two
# anchor points (heights 0 and 1000) for a per-tenant long-run chain.
ANCHOR_INTERVAL = 1000
ANCHORED_CHAIN_SIZE = 2000
ANCHOR_TENANT = "tenant_ledger"
ANCHOR_CHAIN_SCHEMA = ROOT / "packages" / "contracts" / "receipt-chain.schema.json"

# Realistic effect-class cycle for the long-run anchored chain (§5.5 classes).
EFFECT_CYCLE = [
    ("ro.fetch", "T0", "fetch.context", {"kind": "retrieval"}),
    ("ro.audit", "T0", "audit.static", {"kind": "audit"}),
    ("workspace.test", "T1", "tests.passed", {"passed": 1}),
    ("internal.synth", "T1", "summary.issued", {"kind": "summary"}),
    ("workspace.patch", "T2", "patch.applied", {"changed_paths_count": 1}),
]

# ---------------------------------------------------------------------------
# Pinned TEST-ONLY Sentinel signing key (§8.3 analogue)
# ---------------------------------------------------------------------------
# Derived deterministically from a fixed seed so that every run signs with the
# *same* key: golden receipts written to disk can be re-verified on replay
# (full signature verification, not just self_hash). The seed is a SHA-256 of
# a documented label — anyone can recompute the keypair. This key is for the
# harness only; production signer keys are registry-pinned per §8.3 and are
# never embedded in source.
TEST_SIGNING_SEED = hashlib.sha256(
    b"camelot-verifier:test-sentinel-signing-key:v1"
).digest()


def signer_key() -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(TEST_SIGNING_SEED)


def signer_fingerprint(key: Ed25519PublicKey) -> str:
    raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return "ed25519:" + raw.hex()


# ---------------------------------------------------------------------------
# Canonical serialization (§11.3)
# ---------------------------------------------------------------------------

def canonical(receipt: dict) -> bytes:
    """Deterministic serialization: strip self_hash and proof.signature,
    sort keys, compact separators. Matches the schema's stated self_hash
    definition ('self_hash and signature fields stripped')."""
    r = copy.deepcopy(receipt)
    r.pop("self_hash", None)
    r.get("proof", {}).pop("signature", None)
    return json.dumps(r, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Chain builder
# ---------------------------------------------------------------------------

def build_receipt(
    key: Ed25519PrivateKey,
    *,
    receipt_id: str,
    parent_hash: str,
    chain_height: int,
    tenant_id: str,
    correlation_id: str,
    task_id: str,
    authority_epoch: int,
    effect_class: str,
    declared_risk_tier: str,
    event: str,
    payload: dict,
    ledger_anchor_eligible: bool = False,
    timestamp: str | None = None,
) -> dict:
    receipt = {
        "schema_version": "camelot-receipt/1",
        "receipt_id": receipt_id,
        "parent_hash": parent_hash,
        "chain_height": chain_height,
        "tenant_id": tenant_id,
        "correlation_id": correlation_id,
        "task_id": task_id,
        "authority_epoch": authority_epoch,
        "effect_class": effect_class,
        "declared_risk_tier": declared_risk_tier,
        "timestamp": (
            timestamp
            if timestamp is not None
            else f"2026-08-14T{16 + chain_height:02d}:00:00Z"
        ),
        "actor": {
            "id": "sir-forge",
            "role": "engineering_builder",
            "node_id": "engineering-01",
            "trust_band": "attested",
        },
        "event": event,
        "refs": {"manifest_hash": "sha256:" + "1" * 64, "lease_id": "lease_0001"},
        "payload_redacted": payload,
        "proof": {
            "hash_algorithm": "sha256",
            "signature_algorithm": "ed25519",
            "signer": SIGNER,
            "signature": "",
        },
        "ledger_anchor_eligible": ledger_anchor_eligible,
    }
    receipt["self_hash"] = sha256_hex(canonical(receipt))
    receipt["proof"]["signature"] = "ed25519:" + key.sign(canonical(receipt)).hex()
    return receipt


def build_chain() -> tuple[list[dict], Ed25519PrivateKey]:
    """Genesis + three linked receipts. Genesis parent_hash = sha256:0{64}.
    Always signed with the pinned TEST-ONLY key — deterministic across runs.
    Returns (chain, signer_private_key)."""
    key = signer_key()
    genesis = build_receipt(
        key,
        receipt_id="rcp_0000",
        parent_hash="sha256:" + "0" * 64,
        chain_height=0,
        tenant_id="tenant_alpha",
        correlation_id="cor_c001",
        task_id="task_t001",
        authority_epoch=TRUSTED_EPOCH,
        effect_class="ro.fetch",
        declared_risk_tier="T0",
        event="chain.genesis",
        payload={"kind": "genesis"},
        ledger_anchor_eligible=True,
    )
    r1 = build_receipt(
        key,
        receipt_id="rcp_0001",
        parent_hash=genesis["self_hash"],
        chain_height=1,
        tenant_id="tenant_alpha",
        correlation_id="cor_c001",
        task_id="task_t001",
        authority_epoch=TRUSTED_EPOCH,
        effect_class="workspace.patch",
        declared_risk_tier="T2",
        event="patch.applied",
        payload={"changed_paths_count": 1, "diff_sha256": "sha256:" + "a" * 64},
    )
    r2 = build_receipt(
        key,
        receipt_id="rcp_0002",
        parent_hash=r1["self_hash"],
        chain_height=2,
        tenant_id="tenant_alpha",
        correlation_id="cor_c001",
        task_id="task_t001",
        authority_epoch=TRUSTED_EPOCH,
        effect_class="workspace.test",
        declared_risk_tier="T1",
        event="tests.passed",
        payload={"passed": 42, "failed": 0},
    )
    r3 = build_receipt(
        key,
        receipt_id="rcp_0003",
        parent_hash=r2["self_hash"],
        chain_height=3,
        tenant_id="tenant_alpha",
        correlation_id="cor_c001",
        task_id="task_t001",
        authority_epoch=TRUSTED_EPOCH,
        effect_class="promote.worktree.merge",
        declared_risk_tier="T3",
        event="merge.promoted",
        payload={"base_revision": "git-sha-base", "candidate_revision": "git-sha-candidate"},
        ledger_anchor_eligible=False,
    )
    return [genesis, r1, r2, r3], key


# ---------------------------------------------------------------------------
# Ledger anchoring (§11.3) — batch N receipts, write head to ledger anchor
# ---------------------------------------------------------------------------

def build_anchored_chain(chain_size: int, anchor_interval: int) -> list[dict]:
    """Deterministic long-run per-tenant chain (tenant_ledger) built with the
    pinned key: `chain_size` receipts, heights 0..chain_size-1. Anchor-eligible
    heights are chain_height % anchor_interval == 0 (the receipt schema's
    ledger_anchor_eligible rule), so every Nth entry can anchor the head."""
    key = signer_key()
    chain = []
    for h in range(chain_size):
        if h == 0:
            effect_class, tier, event, payload = (
                "ro.fetch", "T0", "chain.genesis", {"kind": "genesis"},
            )
        else:
            effect_class, tier, event, payload = EFFECT_CYCLE[h % len(EFFECT_CYCLE)]
        chain.append(build_receipt(
            key,
            receipt_id=f"rcp_{h:04d}",
            parent_hash=(
                "sha256:" + "0" * 64
                if h == 0 else chain[h - 1]["self_hash"]
            ),
            chain_height=h,
            tenant_id=ANCHOR_TENANT,
            correlation_id=f"cor_l{h // 100:04d}",
            task_id=f"task_l{h // 50:04d}",
            authority_epoch=TRUSTED_EPOCH,
            effect_class=effect_class,
            declared_risk_tier=tier,
            event=event,
            payload={**payload, "seq": h},
            ledger_anchor_eligible=(h % anchor_interval == 0),
            timestamp=f"2026-08-14T16:{h % 60:02d}:00Z",
        ))
    return chain


def build_anchor(
    receipt: dict,
    prev_anchor_height: int,
    prev_anchor_hash: str,
    anchor_interval: int,
) -> dict:
    """Ledger-anchor record for an eligible receipt: captures the chain head
    (self_hash), links the previous anchor (zero-hash convention for the first
    anchor, mirroring genesis parent_hash), and carries an ed25519 proof signed
    with the pinned TEST-ONLY key so tampering is detectable from the record
    alone — no chain re-derivation required. Conforms to
    receipt-chain.schema.json."""
    anchor = {
        "schema_version": "camelot-receipt-chain/1",
        "tenant_id": receipt["tenant_id"],
        "chain_height": receipt["chain_height"],
        "head_hash": receipt["self_hash"],
        "anchor_interval": anchor_interval,
        "last_anchor_height": prev_anchor_height,
        "last_anchor_hash": prev_anchor_hash,
        "verified": True,
        "last_verified_at": "2026-08-14T17:00:00Z",
        "replay_protected": True,
        "proof": {
            "hash_algorithm": "sha256",
            "signature_algorithm": "ed25519",
            "signer": SIGNER,
            "signature": "",
        },
    }
    anchor["proof"]["signature"] = (
        "ed25519:" + signer_key().sign(canonical(anchor)).hex()
    )
    return anchor


def compute_anchors(chain: list[dict], anchor_interval: int) -> list[dict]:
    """Anchor records for every eligible height (chain_height % N == 0)."""
    anchors = []
    prev_height, prev_hash = 0, "sha256:" + "0" * 64
    for r in chain:
        if r["chain_height"] % anchor_interval != 0:
            continue
        anchors.append(build_anchor(r, prev_height, prev_hash, anchor_interval))
        prev_height, prev_hash = r["chain_height"], r["self_hash"]
    return anchors


def verify_golden_anchor(
    anchor: dict,
    genesis: dict,
    signer_pubkey: Ed25519PublicKey,
) -> tuple[bool, str]:
    """Verify the golden-set ledger-anchor record that covers the demo chain's
    genesis head (height 0 — ledger_anchor_eligible per the receipt schema).
    Schema validation happens separately; here we check signature and the
    linkage to the committed genesis receipt."""
    if anchor["tenant_id"] != genesis["tenant_id"]:
        return False, f"golden anchor: tenant mismatch " \
                       f"({anchor['tenant_id']} vs {genesis['tenant_id']})"
    if anchor["chain_height"] != 0 or anchor["head_hash"] != genesis["self_hash"]:
        return False, "golden anchor: head_hash does not cover the golden genesis"
    if anchor["last_anchor_height"] != 0 or anchor["last_anchor_hash"] != "sha256:" + "0" * 64:
        return False, "golden anchor: bad first-anchor linkage (expected zero-hash predecessor)"
    if anchor.get("anchor_interval") != ANCHOR_INTERVAL:
        return False, f"golden anchor: unexpected interval {anchor.get('anchor_interval')}"
    ok, msg = verify_anchor_proofs([anchor], signer_pubkey)
    if not ok:
        return False, f"golden anchor: {msg}"
    return True, f"golden anchor verified (covers {genesis['receipt_id']} head)"


def verify_anchor_proofs(
    anchors: list[dict],
    signer_pubkey: Ed25519PublicKey,
) -> tuple[bool, str]:
    """Verify every anchor's ed25519 proof over its canonical serialization.
    This detects tampering of the anchor record itself (head_hash, heights,
    interval, tenant, …) WITHOUT re-deriving the chain — STRIDE S-4 forged
    signature and T-10 ledger anchor tampering."""
    if not anchors:
        return False, "no anchors to verify"
    for a in anchors:
        proof = a.get("proof")
        if not proof or proof.get("signature_algorithm") != "ed25519":
            return False, f"anchor@{a['chain_height']}: missing ed25519 proof"
        try:
            signer_pubkey.verify(
                bytes.fromhex(proof["signature"][len("ed25519:"):]),
                canonical(a),
            )
        except Exception:
            return False, f"anchor@{a['chain_height']}: signature does not verify (tampered anchor record)"
        if proof.get("signer") != SIGNER:
            return False, f"anchor@{a['chain_height']}: unexpected signer {proof.get('signer')!r}"
    return True, f"{len(anchors)} anchor signature(s) verified"


def verify_anchors(
    anchors: list[dict],
    chain: list[dict],
    anchor_interval: int,
) -> tuple[bool, str]:
    """Re-derive anchor eligibility from the chain and assert every committed
    anchor matches: height, head_hash, previous-anchor linkage, and the record's
    own anchor_interval. Any of these mismatching catches ledger-anchor
    tampering (STRIDE T-10)."""
    eligible = [r for r in chain if r["chain_height"] % anchor_interval == 0]
    if not eligible:
        return False, "no anchor-eligible receipts in chain"
    if len(anchors) != len(eligible):
        return False, f"anchor count mismatch: {len(anchors)} vs {len(eligible)}"
    prev_height, prev_hash = 0, "sha256:" + "0" * 64
    for anchor, r in zip(anchors, eligible):
        if anchor["chain_height"] != r["chain_height"]:
            return False, f"anchor@{anchor['chain_height']}: height mismatch"
        if anchor["head_hash"] != r["self_hash"]:
            return False, f"anchor@{anchor['chain_height']}: head_hash mismatch (ledger anchor tampering)"
        if anchor.get("anchor_interval") != anchor_interval:
            return False, f"anchor@{anchor['chain_height']}: interval mismatch " \
                           f"({anchor.get('anchor_interval')} vs {anchor_interval})"
        if anchor["last_anchor_height"] != prev_height:
            return False, f"anchor@{anchor['chain_height']}: last_anchor_height mismatch"
        if anchor["last_anchor_hash"] != prev_hash:
            return False, f"anchor@{anchor['chain_height']}: last_anchor_hash mismatch"
        prev_height, prev_hash = r["chain_height"], r["self_hash"]
    return True, f"{len(anchors)} anchor(s) verified @ heights " \
                 f"{','.join(str(a['chain_height']) for a in anchors)}"


def emit_anchors(anchors: list[dict], chain_size: int, anchor_interval: int) -> None:
    """Persist ledger-anchor records next to the golden receipts and record the
    anchored-chain config + anchors in the chain.verified marker. The config
    line is what replay reads to re-derive the same chain deterministically.

    Emission is authoritative for the CURRENT config: any stale anchor_*.json
    left over from an earlier --chain-size/--anchor-every run is removed first,
    so the committed anchor set always matches the persisted config exactly."""
    removed = 0
    for stale in GOLDEN_DIR.glob("anchor_*.json"):
        stale.unlink()
        removed += 1
    if removed:
        print(f"  removed {removed} stale anchor file(s) from a previous config")
    for a in anchors:
        path = GOLDEN_DIR / f"anchor_{a['chain_height']:04d}.json"
        path.write_text(json.dumps(a, indent=2) + "\n", encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT)}")
    heights = ",".join(str(a["chain_height"]) for a in anchors)
    with MARKER_FILE.open("a", encoding="utf-8") as f:
        f.write(f"anchored_chain: size={chain_size} interval={anchor_interval} "
                f"tenant={ANCHOR_TENANT}\n")
        f.write(f"anchors: {len(anchors)} @ heights {heights} "
                f"(interval {anchor_interval}, {ANCHOR_TENANT})\n")
    print(f"  appended config + anchors lines to {MARKER_FILE.relative_to(ROOT)}")


def load_config_from_marker() -> tuple[int, int]:
    """Read the anchored-chain config persisted by the last emit
    (chain.verified): (chain_size, anchor_interval). Falls back to defaults if
    the line is absent. The LAST occurrence wins (marker is append-only)."""
    size, interval = ANCHORED_CHAIN_SIZE, ANCHOR_INTERVAL
    if MARKER_FILE.is_file():
        for line in MARKER_FILE.read_text(encoding="utf-8").splitlines():
            if not line.startswith("anchored_chain:"):
                continue
            kv = dict(
                part.split("=", 1)
                for part in line[len("anchored_chain:"):].strip().split()
                if "=" in part
            )
            size = int(kv.get("size", size))
            interval = int(kv.get("interval", interval))
    return size, interval


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--anchor-every", type=int, default=ANCHOR_INTERVAL,
        help=f"write head to ledger anchor every N entries (default {ANCHOR_INTERVAL})",
    )
    parser.add_argument(
        "--chain-size", type=int, default=ANCHORED_CHAIN_SIZE,
        help=f"receipts in the anchored stress-test chain (default {ANCHORED_CHAIN_SIZE})",
    )
    parser.add_argument(
        "--replay", action="store_true",
        help="verify committed artifacts from disk (config read from chain.verified)",
    )
    args = parser.parse_args(argv)
    if args.anchor_every < 1 or args.chain_size < 1:
        parser.error("--anchor-every and --chain-size must be >= 1")
    return args


def load_anchors() -> list[dict]:
    """Load committed ledger-anchor records (anchor_*.json), height-ordered."""
    anchors = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in GOLDEN_DIR.glob("anchor_*.json")
    ]
    anchors.sort(key=lambda a: a["chain_height"])
    return anchors


# ---------------------------------------------------------------------------
# §11.3 verification rule
# ---------------------------------------------------------------------------

def verify_chain(
    chain: list[dict],
    signer_pubkey: Ed25519PublicKey,
    trusted_epoch: int = TRUSTED_EPOCH,
) -> tuple[bool, str]:
    """Deterministic re-runnable §11.3 verification. Genesis is a receipt with
    chain_height 0 whose parent_hash is the zero hash. The signer public key is
    the registry-pinned key for the 'sentinel' signer trust band (§8.3)."""
    if not chain:
        return False, "empty chain"
    prev = None
    for i, r in enumerate(chain):
        # 1. self_hash must equal sha256(canonical(r, r.parent_hash))
        if sha256_hex(canonical(r)) != r.get("self_hash"):
            return False, f"receipt {r['receipt_id']}: self_hash mismatch (tampered content)"
        # 2. signature verifies under the signer's pinned public key
        try:
            signer_pubkey.verify(
                bytes.fromhex(r["proof"]["signature"][len("ed25519:"):]),
                canonical(r),
            )
        except Exception:
            return False, f"receipt {r['receipt_id']}: signature does not verify"
        # 3. height continuity
        if i == 0:
            if r["chain_height"] != 0 or r["parent_hash"] != "sha256:" + "0" * 64:
                return False, f"genesis {r['receipt_id']}: bad genesis (height/parent)"
        else:
            if r["chain_height"] != prev["chain_height"] + 1:
                return False, f"receipt {r['receipt_id']}: height gap"
            if r["parent_hash"] != prev["self_hash"]:
                return False, f"receipt {r['receipt_id']}: parent_hash mismatch (chain break)"
        # 4. epoch freshness
        if r["authority_epoch"] < trusted_epoch:
            return False, f"receipt {r['receipt_id']}: stale epoch"
        prev = r
    return True, "chain verified"


# ---------------------------------------------------------------------------
# Golden-receipt emission / disk replay
# ---------------------------------------------------------------------------

def emit_golden(chain: list[dict], key: Ed25519PrivateKey) -> None:
    """Write the committed golden set: the 4 receipts, the pinned public key,
    the verified marker, and golden-anchor-0000.json — the signed ledger-anchor
    record covering the demo chain's genesis head (height 0 is
    ledger_anchor_eligible per the receipt schema), so the golden set is
    self-contained. A later `--replay` re-verifies all of it from disk."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    for r in chain:
        path = GOLDEN_DIR / f"{r['receipt_id']}.json"
        path.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT)}")
    pub = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    PUBKEY_FILE.write_bytes(pub)
    print(f"  wrote {PUBKEY_FILE.relative_to(ROOT)}")
    fp = signer_fingerprint(key.public_key())
    MARKER_FILE.write_text(
        f"verify(chain) -> PASS (4 receipts, ed25519, epoch 43)\n"
        f"signer_public_key: {fp}\n",
        encoding="utf-8",
    )
    print(f"  wrote {MARKER_FILE.relative_to(ROOT)} (signer_public_key {fp[:24]}…)")
    golden_anchor = build_anchor(chain[0], 0, "sha256:" + "0" * 64, ANCHOR_INTERVAL)
    GOLDEN_ANCHOR_FILE.write_text(
        json.dumps(golden_anchor, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  wrote {GOLDEN_ANCHOR_FILE.relative_to(ROOT)}")
    with MARKER_FILE.open("a", encoding="utf-8") as f:
        f.write(f"golden_anchor: height={golden_anchor['chain_height']} "
                f"tenant={golden_anchor['tenant_id']} "
                f"interval={golden_anchor['anchor_interval']}\n")


def load_golden() -> tuple[list[dict], Ed25519PublicKey]:
    """Load the golden receipts + pinned public key emitted by a prior run."""
    if not PUBKEY_FILE.is_file():
        raise FileNotFoundError(
            f"missing pinned signer key {PUBKEY_FILE.relative_to(ROOT)} — "
            "run the harness once (no args) to emit golden receipts + key"
        )
    pubkey = serialization.load_pem_public_key(PUBKEY_FILE.read_bytes())
    if not isinstance(pubkey, Ed25519PublicKey):
        raise ValueError("pinned signer key is not ed25519")
    chain = []
    for i in range(CHAIN_SIZE):
        p = GOLDEN_DIR / f"rcp_{i:04d}.json"
        if not p.is_file():
            raise FileNotFoundError(f"missing golden receipt {p.name}")
        chain.append(json.loads(p.read_text(encoding="utf-8")))
    return chain, pubkey


def replay(args: argparse.Namespace) -> int:
    """Replay verification of the golden receipts from disk, using only the
    pinned public key (no key generation, no re-signing). The anchored-chain
    config is read from chain.verified (written at emit time), so CLI flags
    are ignored — replay must re-derive with the exact persisted config for
    the committed anchors to match."""
    print("=" * 72)
    print("REPLAY — verify golden receipts from disk (pinned §8.3 signer key)")
    print("=" * 72)
    if args.anchor_every != ANCHOR_INTERVAL or args.chain_size != ANCHORED_CHAIN_SIZE:
        print("  (note: --anchor-every/--chain-size are ignored on replay — "
              "the persisted config from chain.verified is authoritative)")
    try:
        chain, pubkey = load_golden()
    except (FileNotFoundError, ValueError) as e:
        print(f"  ✗ {e}")
        return 1

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    print(f"  loaded {len(chain)} receipts from {GOLDEN_DIR.relative_to(ROOT)}")
    for r in chain:
        errors = sorted(validator.iter_errors(r), key=lambda e: list(e.path))
        status = "PASS" if not errors else "FAIL"
        print(f"  schema [{status}] {r['receipt_id']}  height={r['chain_height']}")
        for e in errors[:5]:
            print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
    if any(e for r in chain for e in validator.iter_errors(r)):
        print("\n✗ Schema conformance FAILED on disk replay.")
        return 1

    ok, msg = verify_chain(chain, pubkey)
    print(f"  verify(chain from disk) -> {'PASS' if ok else 'FAIL'}: {msg}")

    if MARKER_FILE.is_file():
        marker_txt = MARKER_FILE.read_text(encoding="utf-8")
        expected = f"signer_public_key: {signer_fingerprint(pubkey)}"
        if expected in marker_txt:
            print(f"  marker chain.verified matches pinned key ({expected[:24]}…)")
        else:
            print(f"  ✗ chain.verified does not match the pinned key")
            return 1
    else:
        print("  ⚠ chain.verified marker missing (regenerate with a plain run)")

    if not ok:
        print("\n✗ REPLAY FAILED — golden receipts do not verify from disk.")
        return 1

    print("\n" + "=" * 72)
    print("REPLAY — ledger anchors from disk (SADD §11.3, N=1000)")
    print("=" * 72)
    anchors = load_anchors()
    if not anchors:
        print("  ✗ no anchor_*.json committed — run the harness once to emit them")
        return 1
    print(f"  loaded {len(anchors)} anchor(s) from {GOLDEN_DIR.relative_to(ROOT)}: "
          + ", ".join(f"height {a['chain_height']}" for a in anchors))

    an_schema = json.loads(ANCHOR_CHAIN_SCHEMA.read_text(encoding="utf-8"))
    an_validator = Draft202012Validator(an_schema)
    an_errors = [e for a in anchors for e in an_validator.iter_errors(a)]
    for e in an_errors[:5]:
        print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
    if an_errors:
        print("\n✗ REPLAY FAILED — anchor records fail schema validation.")
        return 1
    print(f"  schema [PASS] {len(anchors)} anchor record(s) (receipt-chain.schema.json)")

    sok, smsg = verify_anchor_proofs(anchors, pubkey)
    print(f"  verify(anchor signatures) -> {'PASS' if sok else 'FAIL'}: {smsg}")
    if not sok:
        print("\n✗ REPLAY FAILED — an anchor signature does not verify "
              "(tampered anchor record; no chain re-derivation needed).")
        return 1

    size, interval = load_config_from_marker()
    print(f"  config from chain.verified: size={size} interval={interval} "
          f"tenant={ANCHOR_TENANT}")
    anchored = build_anchored_chain(size, interval)  # deterministic, pinned key
    aok, amsg = verify_anchors(anchors, anchored, interval)
    print(f"  verify(anchors vs re-derived chain) -> {'PASS' if aok else 'FAIL'}: {amsg}")
    if not aok:
        print("\n✗ REPLAY FAILED — committed anchors do not match the re-derived chain "
              "(tampered, stale, or config-mismatched anchor records).")
        return 1

    print("\n" + "=" * 72)
    print("REPLAY — golden-set ledger anchor (covers demo chain head)")
    print("=" * 72)
    if not GOLDEN_ANCHOR_FILE.is_file():
        print(f"  ✗ missing {GOLDEN_ANCHOR_FILE.relative_to(ROOT)} — "
              "run the harness once to emit it")
        return 1
    golden_anchor = json.loads(GOLDEN_ANCHOR_FILE.read_text(encoding="utf-8"))
    g_errors = [e for e in an_validator.iter_errors(golden_anchor)]
    for e in g_errors[:5]:
        print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
    if g_errors:
        print("\n✗ REPLAY FAILED — golden anchor fails schema validation.")
        return 1
    gok, gmsg = verify_golden_anchor(golden_anchor, chain[0], pubkey)
    print(f"  verify(golden anchor from disk) -> {'PASS' if gok else 'FAIL'}: {gmsg}")
    if not gok:
        print("\n✗ REPLAY FAILED — committed golden anchor does not verify "
              "(tampered, stale, or missing coverage of the golden chain head).")
        return 1

    print("\n✓ REPLAY PASSED — golden receipts, anchor signatures, and the "
          "golden-set ledger anchor all verify from disk under the pinned "
          "TEST-ONLY signer key; committed ledger anchors match the "
          "re-derived chain.")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(args: argparse.Namespace) -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    chain, signer_key_priv = build_chain()
    fp = signer_fingerprint(signer_key_priv.public_key())

    print("=" * 72)
    print("STEP 1 — Schema conformance (receipt.schema.json, Draft 2020-12)")
    print("=" * 72)
    for r in chain:
        errors = sorted(validator.iter_errors(r), key=lambda e: list(e.path))
        status = "PASS" if not errors else "FAIL"
        print(f"  [{status}] {r['receipt_id']}  height={r['chain_height']}  "
              f"self_hash={r['self_hash'][:24]}…  sig={r['proof']['signature'][:24]}…")
        for e in errors[:5]:
            print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
    if any(e for r in chain for e in validator.iter_errors(r)):
        print("\n✗ Schema conformance FAILED — chain not valid.")
        return 1
    print(f"  signer (pinned TEST-ONLY sentinel key): {fp[:24]}…")

    print("\n" + "=" * 72)
    print("STEP 2 — §11.3 chain verification rule")
    print("=" * 72)
    ok, msg = verify_chain(chain, signer_key_priv.public_key())
    print(f"  verify(chain) -> {'PASS' if ok else 'FAIL'}: {msg}")

    print("\n" + "=" * 72)
    print("STEP 3 — Tamper detection (each case MUST fail)")
    print("=" * 72)
    cases = []

    def re_sign(r: dict):
        """Recompute self_hash + signature after a mutation, so only the rule
        under test can fail (isolates each conjunct of the §11.3 rule)."""
        r["self_hash"] = sha256_hex(canonical(r))
        r["proof"]["signature"] = "ed25519:" + signer_key_priv.sign(canonical(r)).hex()

    def case(name: str, mutate, re_sign_idx: int | None = None):
        c = copy.deepcopy(chain)
        mutate(c)
        if re_sign_idx is not None:
            re_sign(c[re_sign_idx])
        ok, msg = verify_chain(c, signer_key_priv.public_key())
        cases.append((name, ok, msg))
        print(f"  [{'PASS' if not ok else 'FAIL'}] {name}: {msg}")

    def tamper_parent_hash(c):
        c[2]["parent_hash"] = "sha256:" + "f" * 64
    case("parent_hash rewrite (T-1)", tamper_parent_hash, re_sign_idx=2)

    def tamper_payload(c):
        c[1]["payload_redacted"]["diff_sha256"] = "sha256:" + "b" * 64
    case("payload tamper (T-5)", tamper_payload)

    def tamper_height(c):
        c[3]["chain_height"] = 99
    case("chain_height gap (T-1)", tamper_height, re_sign_idx=3)

    def tamper_signature(c):
        c[2]["proof"]["signature"] = "ed25519:" + "0" * 128
    case("forged signature (S-4)", tamper_signature)

    def tamper_epoch(c):
        c[2]["authority_epoch"] = TRUSTED_EPOCH - 1
    case("stale authority epoch (D-4)", tamper_epoch, re_sign_idx=2)

    def tamper_self_hash(c):
        c[0]["self_hash"] = "sha256:" + "e" * 64
    case("self_hash rewrite (T-1)", tamper_self_hash)

    def tamper_tenant(c):
        c[1]["tenant_id"] = "tenant_other"
    case("cross-tenant injection (S-3)", tamper_tenant)

    failures = [n for n, ok, _ in cases if ok]
    if failures:
        print(f"\n✗ {len(failures)} tamper case(s) were NOT detected: {failures}")
        return 1

    print("\n" + "=" * 72)
    print("STEP 4 — Emit golden receipts for audit replay (pinned key)")
    print("=" * 72)
    emit_golden(chain, signer_key_priv)

    print("\n" + "=" * 72)
    print(f"STEP 5 — Ledger anchoring (§11.3, N={args.anchor_every}, every Nth entry)")
    print("=" * 72)
    anchored = build_anchored_chain(args.chain_size, args.anchor_every)
    ok, msg = verify_chain(anchored, signer_key_priv.public_key())
    print(f"  built {args.chain_size}-receipt chain for {ANCHOR_TENANT} "
          f"(heights 0..{args.chain_size - 1}, pinned key, anchor every "
          f"{args.anchor_every})")
    print(f"  verify(chain, {len(anchored)} receipts) -> {'PASS' if ok else 'FAIL'}: {msg}")
    if not ok:
        return 1

    rcp_errors = [e for r in anchored for e in validator.iter_errors(r)]
    print(f"  schema conformance ({len(anchored)} receipts): "
          f"{'PASS' if not rcp_errors else f'FAIL ({len(rcp_errors)} errors)'}")
    for e in rcp_errors[:5]:
        print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
    if rcp_errors:
        return 1

    anchors = compute_anchors(anchored, args.anchor_every)
    print(f"  anchor-eligible heights (chain_height % {args.anchor_every} == 0): "
          + ", ".join(str(a["chain_height"]) for a in anchors))

    an_validator = Draft202012Validator(
        json.loads(ANCHOR_CHAIN_SCHEMA.read_text(encoding="utf-8"))
    )
    an_errors = [e for a in anchors for e in an_validator.iter_errors(a)]
    print(f"  anchor schema (receipt-chain.schema.json, {len(anchors)} records): "
          f"{'PASS' if not an_errors else f'FAIL ({len(an_errors)} errors)'}")
    for e in an_errors[:5]:
        print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
    if an_errors:
        return 1

    ok, msg = verify_anchors(anchors, anchored, args.anchor_every)
    print(f"  verify(anchors vs chain) -> {'PASS' if ok else 'FAIL'}: {msg}")
    if not ok:
        return 1

    sok, smsg = verify_anchor_proofs(anchors, signer_key_priv.public_key())
    print(f"  verify(anchor signatures) -> {'PASS' if sok else 'FAIL'}: {smsg}")
    if not sok:
        return 1

    print("  tamper detection (each case MUST fail at least one check):")
    anchor_cases = [
        ("anchor head_hash rewrite (T-10)",
         lambda aa: aa[1].__setitem__("head_hash", "sha256:" + "f" * 64)),
        ("anchor last_anchor_hash rewrite (T-10)",
         lambda aa: aa[1].__setitem__("last_anchor_hash", "sha256:" + "e" * 64)),
        ("anchor chain_height rewrite (T-10)",
         lambda aa: aa[1].__setitem__("chain_height", aa[1]["chain_height"] - 1)),
        ("anchor dropped (T-10)",
         lambda aa: aa.pop(1)),
        ("anchor signature forged (S-4)",
         lambda aa: aa[1]["proof"].__setitem__("signature", "ed25519:" + "0" * 128)),
    ]
    for label, mutate in anchor_cases:
        ac = copy.deepcopy(anchors)
        mutate(ac)
        cok, cmsg = verify_anchors(ac, anchored, args.anchor_every)
        sok, smsg = verify_anchor_proofs(ac, signer_key_priv.public_key())
        detected = not cok or not sok
        print(f"  [{'PASS' if detected else 'FAIL'}] {label}")
        print(f"         chain-check: {'FAIL' if not cok else 'PASS':4} — {cmsg}")
        print(f"         sig-check:   {'FAIL' if not sok else 'PASS':4} — {smsg}")
        if not detected:
            return 1

    emit_anchors(anchors, args.chain_size, args.anchor_every)

    # Golden-set anchor: the demo chain's own ledger-anchor record (genesis,
    # height 0 — ledger_anchor_eligible per schema), emitted by STEP 4.
    golden_anchor = json.loads(GOLDEN_ANCHOR_FILE.read_text(encoding="utf-8"))
    g_errors = [e for e in an_validator.iter_errors(golden_anchor)]
    print(f"  golden anchor schema (receipt-chain.schema.json): "
          f"{'PASS' if not g_errors else f'FAIL ({len(g_errors)} errors)'}")
    for e in g_errors[:5]:
        print(f"         ✗ {'/'.join(str(p) for p in e.path)}: {e.message}")
    if g_errors:
        return 1
    gok, gmsg = verify_golden_anchor(golden_anchor, chain[0], signer_key_priv.public_key())
    print(f"  verify(golden anchor vs demo chain head) -> {'PASS' if gok else 'FAIL'}: {gmsg}")
    if not gok:
        return 1
    gt = copy.deepcopy(golden_anchor)
    gt["head_hash"] = "sha256:" + "f" * 64
    gtok, _ = verify_golden_anchor(gt, chain[0], signer_key_priv.public_key())
    print(f"  [{'PASS' if not gtok else 'FAIL'}] golden anchor head_hash rewrite (T-10): "
          f"{'detected' if not gtok else 'NOT DETECTED'}")
    if gtok:
        return 1

    print("\n✓ ALL CHECKS PASSED — receipt chain verifies end-to-end, tampering "
          "is detected, and ledger anchors (tenant_ledger + golden set) are "
          "written. Replay from disk with: "
          "python harness/contracts/verify_receipt_chain.py --replay")
    return 0


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    sys.exit(replay(args) if args.replay else main(args))
