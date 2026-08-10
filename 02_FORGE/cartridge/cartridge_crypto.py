# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge Crypto — Signed Cartridge Supply Chain
================================================
Turns the cartridge ``signature`` field from a recomputable SHA-256 checksum
(anyone can forge) into a real cryptographic signature that only a holder of the
private signing key can produce, and that the sandbox can verify with a public
key it trusts.

Trust separation
----------------
* **Fabrication** (CartridgeFabricator) holds the PRIVATE key and signs manifests.
* **The sandbox** holds only the PUBLIC key and verifies. It can reject a forged
  or tampered manifest without ever being able to mint one.

Primary scheme is Ed25519 (asymmetric). If ``cryptography`` is unavailable, we
fall back to HMAC-SHA256 (symmetric shared secret) so the control still functions
in constrained environments — signatures are tagged with their scheme so a verifier
never confuses the two.

Signature wire format:  ``"<scheme>:<base64>"``   e.g. ``ed25519:AbC...`` / ``hmac:AbC...``
Legacy ``sha256:...`` / bare-hex signatures are treated as UNSIGNED (untrusted).

Key material resolution (first hit wins)
----------------------------------------
    private:  arg → env CAMELOT_CARTRIDGE_PRIVATE_KEY (b64) → ~/.camelot/cartridge_ed25519
    public:   arg → env CAMELOT_CARTRIDGE_PUBLIC_KEY  (b64) → ~/.camelot/cartridge_ed25519.pub
    hmac:     arg → env CAMELOT_CARTRIDGE_HMAC_KEY

CLI
---
    python -m cartridge.cartridge_crypto keygen            # generate + save a keypair
    python -m cartridge.cartridge_crypto pubkey            # print the public key (b64)
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    _HAVE_ED25519 = True
except Exception:  # pragma: no cover - environment dependent
    _HAVE_ED25519 = False

    class InvalidSignature(Exception):  # type: ignore
        pass


KEY_DIR = Path(os.path.expanduser("~")) / ".camelot"
PRIV_PATH = KEY_DIR / "cartridge_ed25519"
PUB_PATH = KEY_DIR / "cartridge_ed25519.pub"

SCHEME_ED25519 = "ed25519"
SCHEME_HMAC = "hmac"
_UNSIGNED_PREFIXES = ("sha256:", "pending", "")


class SigningError(RuntimeError):
    pass


# ── Canonicalization ──────────────────────────────────────────────────────────
def canonical_bytes(manifest: Any) -> bytes:
    """
    Deterministic byte representation of a manifest's *content*, excluding the
    volatile ``signature`` and ``created_at`` fields. Sign and verify MUST use this
    exact function or signatures will never match.
    """
    data = _to_plain_dict(manifest)
    data.pop("signature", None)
    data.pop("created_at", None)
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, default=str).encode("utf-8")


def _to_plain_dict(manifest: Any) -> dict[str, Any]:
    if isinstance(manifest, dict):
        # deep-copy via json round-trip so we never mutate the caller's dict
        return json.loads(json.dumps(manifest, default=str))
    if hasattr(manifest, "model_dump"):        # pydantic v2
        return manifest.model_dump(mode="json")
    if hasattr(manifest, "dict"):              # pydantic v1
        return json.loads(json.dumps(manifest.dict(), default=str))
    raise TypeError(f"cannot canonicalize manifest of type {type(manifest)!r}")


# ── Key management ────────────────────────────────────────────────────────────
def generate_keypair(save: bool = True) -> tuple[str, str]:
    """Return (private_b64, public_b64). Persist to ~/.camelot if save=True."""
    if not _HAVE_ED25519:
        raise SigningError("cryptography not installed; cannot generate Ed25519 keypair")
    priv = Ed25519PrivateKey.generate()
    priv_raw = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    priv_b64 = base64.b64encode(priv_raw).decode()
    pub_b64 = base64.b64encode(pub_raw).decode()
    if save:
        KEY_DIR.mkdir(parents=True, exist_ok=True)
        PRIV_PATH.write_text(priv_b64, encoding="utf-8")
        PUB_PATH.write_text(pub_b64, encoding="utf-8")
        try:
            os.chmod(PRIV_PATH, 0o600)  # best-effort on POSIX; no-op semantics on Windows
        except OSError:
            pass
    return priv_b64, pub_b64


def _resolve_private_b64(explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit
    env = os.getenv("CAMELOT_CARTRIDGE_PRIVATE_KEY")
    if env:
        return env.strip()
    if PRIV_PATH.exists():
        return PRIV_PATH.read_text(encoding="utf-8").strip()
    return None


def _resolve_public_b64(explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit
    env = os.getenv("CAMELOT_CARTRIDGE_PUBLIC_KEY")
    if env:
        return env.strip()
    if PUB_PATH.exists():
        return PUB_PATH.read_text(encoding="utf-8").strip()
    return None


def _hmac_key(explicit: Optional[str]) -> Optional[bytes]:
    val = explicit or os.getenv("CAMELOT_CARTRIDGE_HMAC_KEY")
    return val.encode("utf-8") if val else None


# ── Sign / Verify ─────────────────────────────────────────────────────────────
DEFAULT_KID = "default"


def parse_signature(signature: Optional[str]) -> Optional[tuple[str, str, bytes]]:
    """
    Parse a signature into (scheme, key_id, raw_bytes).

    Wire format is ``"<scheme>:<kid>:<base64>"``. For backward compatibility a
    2-part ``"<scheme>:<base64>"`` signature is read with kid=DEFAULT_KID. Returns
    None for legacy/blank/malformed signatures.
    """
    if not signature or not isinstance(signature, str):
        return None
    parts = signature.split(":")
    if len(parts) == 3:
        scheme, kid, b64 = parts
    elif len(parts) == 2:
        scheme, b64, kid = parts[0], parts[1], DEFAULT_KID
    else:
        return None
    if scheme not in (SCHEME_ED25519, SCHEME_HMAC):
        return None
    try:
        return scheme, kid, base64.b64decode(b64)
    except Exception:
        return None


def signature_fingerprint(signature: str) -> str:
    """Stable short id for a signature — used by revocation lists."""
    return hashlib.sha256(signature.encode("utf-8")).hexdigest()[:16]


def sign(manifest: Any, *, kid: str = DEFAULT_KID,
         private_key_b64: Optional[str] = None,
         hmac_key: Optional[str] = None) -> str:
    """
    Produce a ``"<scheme>:<kid>:<base64>"`` signature over the manifest content.
    ``kid`` identifies which key signed it, enabling rotation and multi-signer trust.
    Prefers Ed25519 (asymmetric); falls back to HMAC if no Ed25519 key is available.
    """
    payload = canonical_bytes(manifest)

    priv_b64 = _resolve_private_b64(private_key_b64)
    if _HAVE_ED25519 and priv_b64:
        try:
            priv = Ed25519PrivateKey.from_private_bytes(base64.b64decode(priv_b64))
        except Exception as e:
            raise SigningError(f"invalid Ed25519 private key: {e}") from e
        sig = priv.sign(payload)
        return f"{SCHEME_ED25519}:{kid}:{base64.b64encode(sig).decode()}"

    key = _hmac_key(hmac_key)
    if key:
        mac = hmac.new(key, payload, hashlib.sha256).digest()
        return f"{SCHEME_HMAC}:{kid}:{base64.b64encode(mac).decode()}"

    raise SigningError(
        "no signing key available. Run `python -m cartridge.cartridge_crypto keygen` "
        "or set CAMELOT_CARTRIDGE_PRIVATE_KEY / CAMELOT_CARTRIDGE_HMAC_KEY."
    )


def is_signed(signature: Optional[str]) -> bool:
    """True if the signature carries a real cryptographic scheme (not legacy/blank)."""
    return parse_signature(signature) is not None


def key_id(signature: Optional[str]) -> Optional[str]:
    """Extract the key id a signature claims to be signed with."""
    parsed = parse_signature(signature)
    return parsed[1] if parsed else None


def verify(manifest: Any, signature: Optional[str], *,
           public_key_b64: Optional[str] = None,
           hmac_key: Optional[str] = None) -> bool:
    """
    Verify a manifest's signature against explicitly-provided key material. Returns
    True only for a valid, correctly-scheme'd signature over the current manifest
    content. Legacy ``sha256:`` / blank signatures return False (untrusted).

    Key *identity, rotation, expiry, and revocation* are the trust store's job — see
    cartridge_trust.TrustManager, which resolves the key id before calling this.
    """
    parsed = parse_signature(signature)
    if parsed is None:
        return False
    scheme, _kid, raw = parsed
    payload = canonical_bytes(manifest)

    if scheme == SCHEME_ED25519:
        if not _HAVE_ED25519:
            return False
        pub_b64 = _resolve_public_b64(public_key_b64)
        if not pub_b64:
            return False
        try:
            pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(pub_b64))
            pub.verify(raw, payload)
            return True
        except (InvalidSignature, Exception):
            return False

    if scheme == SCHEME_HMAC:
        key = _hmac_key(hmac_key)
        if not key:
            return False
        expected = hmac.new(key, payload, hashlib.sha256).digest()
        return hmac.compare_digest(raw, expected)  # constant-time

    return False


# ── CLI ───────────────────────────────────────────────────────────────────────
def _main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "help"

    if cmd == "keygen":
        if PRIV_PATH.exists() and "--force" not in argv:
            print(f"Key already exists at {PRIV_PATH}. Use --force to overwrite.")
            return 1
        _, pub = generate_keypair(save=True)
        print(f"Ed25519 keypair written to {KEY_DIR}")
        print(f"  private: {PRIV_PATH} (keep secret, chmod 600)")
        print(f"  public : {PUB_PATH}")
        print(f"\nPublic key (set on verifiers as CAMELOT_CARTRIDGE_PUBLIC_KEY):\n{pub}")
        return 0

    if cmd == "pubkey":
        pub = _resolve_public_b64(None)
        if not pub:
            print("No public key found. Run keygen first.")
            return 1
        print(pub)
        return 0

    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
