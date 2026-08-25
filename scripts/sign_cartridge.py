# SPDX-License-Identifier: MIT

"""Sign and verify Camelot v1.2 cartridge manifests (§8.2 / §8.3).

Implements the manifest signature policy from `packages/contracts/cartridge.schema.json`:

- Canonical serialization: JSON with sorted keys, compact separators, no
  trailing whitespace, over the manifest EXCLUDING the `artifact_hash` and
  `signature` fields (they are outputs of this tool, not inputs).
- `artifact_hash` = sha256 of the canonical bytes. For dev cartridges with no
  compiled artifact yet, the manifest itself is the artifact — this is a
  content self-fingerprint, documented as such.
- `signature` = ed25519 over the canonical bytes, signed with an ephemeral
  per-cartridge dev key whose PUBLIC half is written to
  `cartridges/<id>/signing_key.pub`. The private key is generated fresh on
  each sign and never persisted (re-signing after an edit regenerates a new
  keypair; admission verifies against the shipped public key).

Usage:
    python scripts/sign_cartridge.py <manifest.json>            # sign (writes artifact_hash + signature + signing_key.pub)
    python scripts/sign_cartridge.py --verify <manifest.json>   # verify signature + artifact_hash

The `--verify` mode must round-trip byte-identically with the canonicalization
used by `tests/test_cartridge_manifests.py` (it imports `canonical_bytes` from
here, so there is exactly one source of truth).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

# Fields produced by this tool; excluded from the signed/ hashed payload.
GENERATED_FIELDS = ("artifact_hash", "signature")

# Canonical JSON encoding shared by sign, verify, and the test suite.
CANONICAL_KWARGS = {
    "sort_keys": True,
    "separators": (",", ":"),
    "ensure_ascii": False,
}


def canonical_bytes(manifest: dict) -> bytes:
    """Deterministic serialization of the manifest minus generated fields."""
    payload = {k: v for k, v in manifest.items() if k not in GENERATED_FIELDS}
    return json.dumps(payload, **CANONICAL_KWARGS).encode("utf-8")


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sign_manifest(path: Path) -> tuple[dict, bytes]:
    """Return (signed manifest dict, public key PEM). Private key is ephemeral."""
    manifest = load_manifest(path)
    payload = canonical_bytes(manifest)

    artifact_hash = "sha256:" + hashlib.sha256(payload).hexdigest()

    private_key = ed25519.Ed25519PrivateKey.generate()
    signature = private_key.sign(payload)
    public_key = private_key.public_key()

    manifest["artifact_hash"] = artifact_hash
    manifest["signature"] = "ed25519:" + _b64u(signature)

    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return manifest, pub_pem


def verify_manifest(path: Path, public_key_pem: bytes | None = None) -> bool:
    """Verify signature + artifact_hash. Public key defaults to signing_key.pub next to the manifest."""
    manifest = load_manifest(path)
    payload = canonical_bytes(manifest)

    expected_hash = "sha256:" + hashlib.sha256(payload).hexdigest()
    if manifest.get("artifact_hash") != expected_hash:
        return False

    signature = manifest.get("signature", "")
    if not signature.startswith("ed25519:"):
        return False
    sig_bytes = _b64u_decode(signature.removeprefix("ed25519:"))

    if public_key_pem is None:
        pub_path = path.parent / "signing_key.pub"
        public_key_pem = pub_path.read_bytes()
    public_key = serialization.load_pem_public_key(public_key_pem)

    try:
        public_key.verify(sig_bytes, payload)  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def _b64u(data: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64u_decode(text: str) -> bytes:
    import base64

    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="verify instead of sign")
    parser.add_argument("manifest", help="path to cartridge manifest.json")
    args = parser.parse_args(argv)

    path = Path(args.manifest)
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 1

    if args.verify:
        pub_path = path.parent / "signing_key.pub"
        ok = pub_path.exists() and verify_manifest(path, pub_path.read_bytes())
        print(f"{'OK' if ok else 'INVALID'}: {path}")
        return 0 if ok else 1

    manifest, pub_pem = sign_manifest(path)
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (path.parent / "signing_key.pub").write_bytes(pub_pem)
    print(f"signed: {path}")
    print(f"  artifact_hash : {manifest['artifact_hash']}")
    print(f"  signature     : {manifest['signature'][:24]}…")
    print(f"  public key    : {path.parent / 'signing_key.pub'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
