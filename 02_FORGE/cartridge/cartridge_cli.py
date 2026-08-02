# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge CLI — Phase 2 pack + verify
======================================

Two subcommands for the local .cartridge format defined in ``cartridge_archive.py``.

    python -m cartridge.cartridge_cli pack  --source packages/AGENT_FLEET \
                                            --manifest packages/AGENT_FLEET/manifest.json \
                                            --output dist/AGENT_FLEET.cartridge \
                                            --publisher acme-cartridge-works

    python -m cartridge.cartridge_cli verify dist/AGENT_FLEET.cartridge

Exit codes
----------
    0  success (packed or verified)
    1  archive / schema / hash failure (the file is malformed or tampered)
    2  trust failure (signature, publisher, key status, or revocation)
    3  usage error (bad args, missing files)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from .cartridge_archive import (
    ArchiveError,
    pack as archive_pack,
    sha256_bytes,
    unpack as archive_unpack,
    format_archive_report,
)
from .cartridge_schemas import CartridgeManifestV2
from . import cartridge_crypto as cc
from .cartridge_trust import (
    PublisherRegistry,
    TrustManager,
    TrustStore,
    RevocationList,
    AuditLog,
    install_publisher_registry,
)


def _read_manifest(path: str | Path) -> CartridgeManifestV2:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return CartridgeManifestV2.model_validate(raw)


# ── pack ─────────────────────────────────────────────────────────────────────
def cmd_pack(args: argparse.Namespace) -> int:
    source_dir = Path(args.source).resolve()
    if not source_dir.is_dir():
        print(f"[pack] source directory not found: {source_dir}", file=sys.stderr)
        return 3

    manifest = _read_manifest(args.manifest)

    # If the operator passed --publisher, override the manifest field.
    if args.publisher:
        manifest = manifest.model_copy(update={"publisher_id": args.publisher})

    # Sign if a key is configured. The pack helper does NOT re-sign; signing
    # is the fabricator's job. If signature is missing/empty, we error.
    if not manifest.signature or not cc.is_signed(manifest.signature):
        print("[pack] manifest has no real signature; refusing to pack an unsigned archive", file=sys.stderr)
        return 3

    try:
        output = archive_pack(source_dir, manifest, args.output)
    except ArchiveError as e:
        print(f"[pack] archive error: {e}", file=sys.stderr)
        return 1

    size = Path(output).stat().st_size
    print(f"[pack] wrote {output} ({size} bytes)")
    print(f"       cartridge_id={manifest.cartridge_id} version={manifest.version}")
    print(f"       publisher_id={manifest.publisher_id}")
    print(f"       sha256={manifest.sha256}")
    return 0


# ── verify ───────────────────────────────────────────────────────────────────
def cmd_verify(args: argparse.Namespace) -> int:
    try:
        manifest, payload_bytes, raw_metadata = archive_unpack(args.archive)
    except ArchiveError as e:
        print(f"[verify] archive error: {e}", file=sys.stderr)
        return 1

    # Crypto + trust verification. Wire the publisher registry into the manager.
    store = TrustStore()
    revocations = RevocationList()
    audit = AuditLog()
    manager = TrustManager(store=store, revocations=revocations, audit=audit)
    registry = PublisherRegistry()
    install_publisher_registry(manager, registry)

    # V2 verify path. The V1 legacy short-circuit (sha256 == V1_LEGACY_SHA256)
    # is handled inside verify_v2 itself, so we always call through it.
    ok, why = manager.verify_v2(manifest)

    audit.append(
        "verify",
        cartridge_id=manifest.cartridge_id,
        decision="allow" if ok else "deny",
        reason=why,
    )

    if args.verbose:
        print(format_archive_report(manifest, payload_bytes, raw_metadata))

    if not ok:
        print(f"[verify] DENIED: {why}", file=sys.stderr)
        return 2

    print(f"[verify] OK: {manifest.cartridge_id} ({manifest.version}) — {why}")
    return 0


# ── add-publisher ────────────────────────────────────────────────────────────
def cmd_add_publisher(args: argparse.Namespace) -> int:
    # Phase 3: validate every --public-key BEFORE registering the publisher
    # so a malformed key doesn't leave a half-registered publisher on disk.
    # argparse with action="append" + nargs="+" produces a list of lists;
    # flatten to a flat list of "KID:PUBKEY_B64" strings.
    public_keys_flat: list[str] = []
    for item in getattr(args, "public_key", []) or []:
        if isinstance(item, list):
            public_keys_flat.extend(item)
        else:
            public_keys_flat.append(item)
    public_keys: list[tuple[str, str]] = []
    for pk in public_keys_flat:
        if ":" not in pk:
            print(
                f"[add-publisher] invalid --public-key '{pk}' (expected KID:PUBKEY_B64, standard base64 not URL-safe)",
                file=sys.stderr,
            )
            return 3
        kid, pubkey_b64 = pk.split(":", 1)
        if not kid or not pubkey_b64:
            print(
                f"[add-publisher] invalid --public-key '{pk}' (both KID and PUBKEY_B64 must be non-empty)",
                file=sys.stderr,
            )
            return 3
        public_keys.append((kid, pubkey_b64))

    # Pre-check: every public-key's kid must be in --kids (fail loud before save).
    kids_set = set(args.kids)
    for kid, _ in public_keys:
        if kid not in kids_set:
            print(
                f"[add-publisher] public key references kid '{kid}' which is not in --kids {args.kids}",
                file=sys.stderr,
            )
            return 3

    registry = PublisherRegistry()
    try:
        registry.add_publisher(
            publisher_id=args.publisher_id,
            kids=args.kids,
            note=args.note or "",
        )
    except ValueError as e:
        print(f"[add-publisher] {e}", file=sys.stderr)
        return 3
    # All pre-checks passed; register the public keys (which now can't fail
    # because we validated the kids above, but we keep the try/except for
    # defense in depth).
    for kid, pubkey_b64 in public_keys:
        try:
            registry.add_public_key_to_publisher(args.publisher_id, kid, pubkey_b64)
        except (KeyError, ValueError) as e:
            print(f"[add-publisher] {e}", file=sys.stderr)
            return 3
    keys_str = f", public_keys={len(public_keys)}" if public_keys else ""
    print(f"[add-publisher] registered '{args.publisher_id}' with kids={args.kids}{keys_str}")
    return 0


def cmd_export_bundle(args: argparse.Namespace) -> int:
    """Export the publisher registry as a browser-loadable JSON bundle.

    The bundle shape is consumed by ``loadTrustedPublishers`` in
    ``src/lib/v2/cartridge-platform.ts``. Use this to ship the trusted
    publisher set + Ed25519 public keys to the cockpit at build time
    or at runtime via ``bootstrapPublishersFromBundle``.

    The deterministic ``legacy-v1`` seed is unconditionally filtered out
    (it is bootstrapped lazily on first ``getTrustedPublisher()`` call
    in the browser, and ``loadTrustedPublishers`` refuses to overwrite
    existing publishers).
    """
    registry = PublisherRegistry()
    bundle = registry.to_bundle_dict()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print(
        f"[export-bundle] wrote {output} "
        f"({len(bundle['publishers'])} publishers, version={bundle['version']})"
    )
    return 0


# ── keygen (delegate to cartridge_crypto) ────────────────────────────────────
def cmd_keygen(args: argparse.Namespace) -> int:
    from .cartridge_crypto import generate_keypair
    if Path(cc.PRIV_PATH).exists() and not args.force:
        print(f"[keygen] key already exists at {cc.PRIV_PATH}. Use --force to overwrite.",
              file=sys.stderr)
        return 3
    priv_b64, pub_b64 = generate_keypair(save=True)
    print(f"[keygen] ed25519 keypair written to {cc.KEY_DIR}")
    print(f"         private: {cc.PRIV_PATH}")
    print(f"         public : {cc.PUB_PATH}")
    print(f"")
    print(f"  Set CAMELOT_CARTRIDGE_PUBLIC_KEY on the verifier to:")
    print(f"  {pub_b64}")
    return 0


# ── top-level ────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="cartridge_cli", description="Camelot .cartridge pack/verify")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pack", help="Pack a source directory + V2 manifest into a .cartridge")
    p.add_argument("--source", required=True, help="Source directory whose tree becomes payload.zip")
    p.add_argument("--manifest", required=True, help="Path to a V2 manifest.json")
    p.add_argument("--output", required=True, help="Output .cartridge file path")
    p.add_argument("--publisher", help="Override the manifest's publisher_id (does not re-sign)")
    p.set_defaults(func=cmd_pack)

    v = sub.add_parser("verify", help="Verify a .cartridge archive")
    v.add_argument("archive", help="Path to the .cartridge file")
    v.add_argument("-v", "--verbose", action="store_true", help="Print a detailed report")
    v.set_defaults(func=cmd_verify)

    ap_pub = sub.add_parser("add-publisher", help="Register a trusted publisher identity")
    ap_pub.add_argument("publisher_id")
    ap_pub.add_argument("--kids", nargs="+", required=True, help="Key ids the publisher owns")
    ap_pub.add_argument(
        "--public-key",
        action="append",
        nargs="+",
        default=[],
        metavar="KID:PUBKEY_B64",
        help="Ed25519 public key for a kid (repeatable, accepts multiple KID:PUBKEY_B64 per flag, format: KID:base64pubkey)",
    )
    ap_pub.add_argument("--note", default="")
    ap_pub.set_defaults(func=cmd_add_publisher)

    eb = sub.add_parser(
        "export-bundle",
        help="Export the publisher registry as a browser-loadable JSON bundle",
    )
    eb.add_argument(
        "--output",
        default="./publishers.json",
        help="Output JSON file path (default: ./publishers.json)",
    )
    eb.set_defaults(func=cmd_export_bundle)

    kg = sub.add_parser("keygen", help="Generate an ed25519 keypair for cartridge signing")
    kg.add_argument("--force", action="store_true", help="Overwrite an existing keypair")
    kg.set_defaults(func=cmd_keygen)

    return ap


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
