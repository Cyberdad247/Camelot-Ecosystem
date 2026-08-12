# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge Trust Lifecycle — Enterprise Key, Revocation & Audit
==============================================================
Layers enterprise trust management on top of the signed-cartridge supply chain
(cartridge_crypto). Provides the four things a single static key cannot:

    1. TrustStore     — many keys by key-id (kid), each with a status
                        (active / rotated / revoked) and a validity window.
                        Enables KEY ROTATION and MULTI-SIGNER trust without
                        re-signing every existing cartridge.
    2. RevocationList — revoke a specific cartridge (by id or signature
                        fingerprint) even though its signature is cryptographically
                        valid — the enterprise "recall" for a bad package.
    3. AuditLog       — hash-chained, tamper-evident JSONL of every enforcement
                        decision (allow/deny + reason + kid). SOC2/ISO-friendly.
    4. TrustManager   — the policy brain: parse kid → resolve key → check
                        status/window → check revocation → verify → audit.

Storage (override via env / constructor):
    trust store   : CAMELOT_CARTRIDGE_TRUST_STORE   (default ~/.camelot/trust_store.json)
    revocations   : CAMELOT_CARTRIDGE_REVOCATIONS   (default ~/.camelot/revocations.json)
    audit log     : CAMELOT_CARTRIDGE_AUDIT_LOG     (default ~/.camelot/cartridge_audit.log)

HMAC keys are shared secrets and are NOT stored here; an HMAC trust entry carries
metadata only, and the secret is resolved from env CAMELOT_CARTRIDGE_HMAC_KEY__<kid>
(falling back to CAMELOT_CARTRIDGE_HMAC_KEY). Ed25519 public keys are safe to store.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from . import cartridge_crypto as cc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KEY_DIR = Path(os.path.expanduser("~")) / ".camelot"
GENESIS_HASH = "0" * 64

STATUS_ACTIVE = "active"
STATUS_ROTATED = "rotated"   # still verifiable for old cartridges, not for new
STATUS_REVOKED = "revoked"   # compromised — never trust


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


# ── Trust store ───────────────────────────────────────────────────────────────
@dataclass
class KeyEntry:
    kid: str
    scheme: str                       # cc.SCHEME_ED25519 | cc.SCHEME_HMAC
    public_key_b64: Optional[str] = None   # ed25519 only
    status: str = STATUS_ACTIVE
    not_before: Optional[str] = None
    not_after: Optional[str] = None
    added_at: str = field(default_factory=lambda: _now().isoformat())
    note: str = ""

    def usable_for_verify(self) -> tuple[bool, str]:
        """A rotated key still verifies OLD cartridges; a revoked key never does."""
        if self.status == STATUS_REVOKED:
            return False, f"key '{self.kid}' is REVOKED"
        now = _now()
        nb, na = _parse_iso(self.not_before), _parse_iso(self.not_after)
        if nb and now < nb:
            return False, f"key '{self.kid}' not yet valid (not_before={self.not_before})"
        if na and now > na:
            return False, f"key '{self.kid}' expired (not_after={self.not_after})"
        return True, "ok"

    def usable_for_signing(self) -> bool:
        ok, _ = self.usable_for_verify()
        return ok and self.status == STATUS_ACTIVE


class TrustStore:
    def __init__(self, path: Optional[str | Path] = None):
        self.path = Path(path or os.getenv("CAMELOT_CARTRIDGE_TRUST_STORE")
                         or (KEY_DIR / "trust_store.json"))
        self.keys: dict[str, KeyEntry] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                self.keys = {k: KeyEntry(**v) for k, v in raw.get("keys", {}).items()}
            except (json.JSONDecodeError, OSError, TypeError):
                self.keys = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"keys": {k: asdict(v) for k, v in self.keys.items()}}, indent=2),
            encoding="utf-8")

    def add_key(self, kid: str, scheme: str, *, public_key_b64: Optional[str] = None,
                not_after: Optional[str] = None, note: str = "") -> KeyEntry:
        entry = KeyEntry(kid=kid, scheme=scheme, public_key_b64=public_key_b64,
                         not_after=not_after, note=note)
        self.keys[kid] = entry
        self.save()
        return entry

    def rotate(self, old_kid: str) -> None:
        """Mark a key rotated: it verifies existing cartridges but signs no new ones."""
        if old_kid in self.keys:
            self.keys[old_kid].status = STATUS_ROTATED
            self.save()

    def revoke_key(self, kid: str, note: str = "") -> None:
        if kid in self.keys:
            self.keys[kid].status = STATUS_REVOKED
            if note:
                self.keys[kid].note = note
            self.save()

    def resolve(self, kid: str) -> Optional[KeyEntry]:
        return self.keys.get(kid)


# ── Revocation list ───────────────────────────────────────────────────────────
class RevocationList:
    def __init__(self, path: Optional[str | Path] = None):
        self.path = Path(path or os.getenv("CAMELOT_CARTRIDGE_REVOCATIONS")
                         or (KEY_DIR / "revocations.json"))
        self.cartridges: dict[str, str] = {}   # cartridge_id -> reason
        self.signatures: dict[str, str] = {}   # signature fingerprint -> reason
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                self.cartridges = raw.get("cartridges", {})
                self.signatures = raw.get("signatures", {})
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(
            {"cartridges": self.cartridges, "signatures": self.signatures}, indent=2),
            encoding="utf-8")

    def revoke_cartridge(self, cartridge_id: str, reason: str = "") -> None:
        self.cartridges[cartridge_id] = reason or "revoked"
        self.save()

    def revoke_signature(self, signature: str, reason: str = "") -> None:
        self.signatures[cc.signature_fingerprint(signature)] = reason or "revoked"
        self.save()

    def check(self, cartridge_id: str, signature: str) -> tuple[bool, str]:
        if cartridge_id in self.cartridges:
            return True, f"cartridge revoked: {self.cartridges[cartridge_id]}"
        fp = cc.signature_fingerprint(signature)
        if fp in self.signatures:
            return True, f"signature revoked: {self.signatures[fp]}"
        return False, ""


# ── Tamper-evident audit log ──────────────────────────────────────────────────
class AuditLog:
    def __init__(self, path: Optional[str | Path] = None):
        self.path = Path(path or os.getenv("CAMELOT_CARTRIDGE_AUDIT_LOG")
                         or (KEY_DIR / "cartridge_audit.log"))

    def _last_hash(self) -> str:
        if not self.path.exists():
            return GENESIS_HASH
        last = GENESIS_HASH
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        last = json.loads(line).get("hash", last)
        except (OSError, json.JSONDecodeError):
            pass
        return last

    @staticmethod
    def _hash(prev: str, record: dict[str, Any]) -> str:
        body = json.dumps(record, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256((prev + body).encode("utf-8")).hexdigest()

    def append(self, event: str, *, cartridge_id: str, tool_id: str = "",
               kid: str = "", decision: str = "", reason: str = "") -> dict[str, Any]:
        prev = self._last_hash()
        record = {
            "ts": _now().isoformat(), "event": event, "cartridge_id": cartridge_id,
            "tool_id": tool_id, "kid": kid, "decision": decision, "reason": reason,
            "prev_hash": prev,
        }
        record["hash"] = self._hash(prev, record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        return record

    def verify_chain(self) -> tuple[bool, str]:
        """Recompute the hash chain; detect any insertion/edit/deletion."""
        if not self.path.exists():
            return True, "empty log"
        prev = GENESIS_HASH
        n = 0
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    stored = rec.pop("hash", None)
                    if rec.get("prev_hash") != prev:
                        return False, f"chain break at line {i}: prev_hash mismatch"
                    if self._hash(prev, rec) != stored:
                        return False, f"tamper at line {i}: hash mismatch"
                    prev = stored
                    n += 1
        except (OSError, json.JSONDecodeError) as e:
            return False, f"unreadable log: {e}"
        return True, f"chain intact ({n} records)"


# ── Trust manager (the policy brain) ──────────────────────────────────────────
class TrustManager:
    def __init__(self, store: Optional[TrustStore] = None,
                 revocations: Optional[RevocationList] = None,
                 audit: Optional[AuditLog] = None,
                 rbac: Optional[Any] = None):
        self.store = store or TrustStore()
        self.revocations = revocations or RevocationList()
        self.audit = audit or AuditLog()
        # Optional lifecycle authorization. When None, privileged ops are unguarded
        # (single-operator mode). When set, every rotate/revoke is authorized + audited.
        self.rbac = rbac

    def verify(self, manifest: Any, signature: Optional[str]) -> tuple[bool, str]:
        """Full enterprise verification: identity → status/window → revocation → crypto."""
        parsed = cc.parse_signature(signature)
        if parsed is None:
            return False, "manifest is unsigned or uses a legacy checksum"
        scheme, kid, _raw = parsed

        entry = self.store.resolve(kid)
        if entry is None:
            return False, f"unknown key id '{kid}' — not in trust store"
        if entry.scheme != scheme:
            return False, f"key '{kid}' scheme mismatch ({entry.scheme} != {scheme})"

        usable, why = entry.usable_for_verify()
        if not usable:
            return False, why

        cartridge_id = _manifest_field(manifest, "cartridge_id", "<unknown>")
        revoked, rreason = self.revocations.check(cartridge_id, signature or "")
        if revoked:
            return False, rreason

        # Resolve key material for the crypto check.
        if scheme == cc.SCHEME_ED25519:
            ok = cc.verify(manifest, signature, public_key_b64=entry.public_key_b64)
        else:  # HMAC — secret from env, keyed by kid
            hkey = (os.getenv(f"CAMELOT_CARTRIDGE_HMAC_KEY__{kid}")
                    or os.getenv("CAMELOT_CARTRIDGE_HMAC_KEY"))
            ok = cc.verify(manifest, signature, hmac_key=hkey)

        if not ok:
            return False, "signature does not match manifest content (tampered or wrong key)"
        return True, f"verified with key '{kid}'"

    def record(self, event: str, manifest: Any, *, tool_id: str = "",
               decision: str = "", reason: str = "", signature: Optional[str] = None) -> None:
        self.audit.append(
            event,
            cartridge_id=_manifest_field(manifest, "cartridge_id", "<unknown>"),
            tool_id=tool_id, kid=(cc.key_id(signature) or ""),
            decision=decision, reason=reason,
        )

    # ── Privileged, authorized + audited lifecycle operations ──────────────────
    def _guard(self, principal: Optional[str], capability: str, target: str) -> None:
        """Authorize a lifecycle op and audit the authz decision. Raises on denial."""
        if self.rbac is None:
            return  # single-operator mode: unguarded
        ok, reason = self.rbac.authorize(principal, capability)
        self.audit.append("authz", cartridge_id=target, tool_id=capability,
                          kid=(principal or ""), decision="allow" if ok else "deny",
                          reason=reason)
        if not ok:
            from .cartridge_rbac import AuthorizationError
            raise AuthorizationError(reason)

    def rotate_key(self, kid: str, *, principal: Optional[str] = None) -> None:
        from .cartridge_rbac import CAP_KEY_ROTATE
        self._guard(principal, CAP_KEY_ROTATE, target=kid)
        self.store.rotate(kid)
        self.audit.append("key_rotate", cartridge_id="-", kid=kid,
                          decision="done", reason=f"by {principal or 'operator'}")

    def revoke_key(self, kid: str, *, principal: Optional[str] = None, note: str = "") -> None:
        from .cartridge_rbac import CAP_KEY_REVOKE
        self._guard(principal, CAP_KEY_REVOKE, target=kid)
        self.store.revoke_key(kid, note)
        self.audit.append("key_revoke", cartridge_id="-", kid=kid,
                          decision="done", reason=f"{note} (by {principal or 'operator'})")

    def revoke_cartridge(self, cartridge_id: str, *, principal: Optional[str] = None,
                         reason: str = "") -> None:
        from .cartridge_rbac import CAP_CARTRIDGE_REVOKE
        self._guard(principal, CAP_CARTRIDGE_REVOKE, target=cartridge_id)
        self.revocations.revoke_cartridge(cartridge_id, reason)
        self.audit.append("cartridge_revoke", cartridge_id=cartridge_id, kid=(principal or ""),
                          decision="done", reason=reason)


def _manifest_field(manifest: Any, name: str, default: Any = None) -> Any:
    if isinstance(manifest, dict):
        return manifest.get(name, default)
    return getattr(manifest, name, default)


# ── CLI ───────────────────────────────────────────────────────────────────────
def _main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cartridge_trust", description="Cartridge trust lifecycle")
    sub = ap.add_subparsers(dest="cmd")

    ak = sub.add_parser("add-key", help="register a public key in the trust store")
    ak.add_argument("kid")
    ak.add_argument("--scheme", default=cc.SCHEME_ED25519, choices=[cc.SCHEME_ED25519, cc.SCHEME_HMAC])
    ak.add_argument("--pub", help="ed25519 public key (b64)")
    ak.add_argument("--not-after", help="ISO expiry, e.g. 2027-01-01T00:00:00Z")
    ak.add_argument("--note", default="")

    rk = sub.add_parser("rotate", help="mark a key rotated"); rk.add_argument("kid")
    vk = sub.add_parser("revoke-key", help="revoke a compromised key"); vk.add_argument("kid"); vk.add_argument("--note", default="")
    rc = sub.add_parser("revoke-cartridge", help="recall a cartridge by id"); rc.add_argument("cartridge_id"); rc.add_argument("--reason", default="")
    sub.add_parser("list-keys", help="list trust store keys")
    sub.add_parser("verify-audit", help="verify the audit-log hash chain")

    args = ap.parse_args(argv)
    store = TrustStore()

    if args.cmd == "add-key":
        e = store.add_key(args.kid, args.scheme, public_key_b64=args.pub,
                          not_after=args.not_after, note=args.note)
        print(f"Added key '{e.kid}' ({e.scheme}, status={e.status})")
    elif args.cmd == "rotate":
        store.rotate(args.kid); print(f"Rotated '{args.kid}' (verifies old, signs no new)")
    elif args.cmd == "revoke-key":
        store.revoke_key(args.kid, args.note); print(f"REVOKED key '{args.kid}'")
    elif args.cmd == "revoke-cartridge":
        RevocationList().revoke_cartridge(args.cartridge_id, args.reason)
        print(f"Revoked cartridge '{args.cartridge_id}'")
    elif args.cmd == "list-keys":
        for kid, e in store.keys.items():
            print(f"  {kid:16s} {e.scheme:8s} {e.status:8s} exp={e.not_after or '-'} {e.note}")
        if not store.keys:
            print("  (trust store empty — add-key first)")
    elif args.cmd == "verify-audit":
        ok, msg = AuditLog().verify_chain()
        print(("✅ " if ok else "❌ ") + msg)
        return 0 if ok else 1
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
