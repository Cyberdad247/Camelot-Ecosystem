# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge Archive — Phase 2 .cartridge format
==============================================

A ``.cartridge`` file is a **standard uncompressed ZIP** with this layout:

    /manifest.json   serialized CartridgeManifestV2 (includes ``signature``)
    /payload.zip     nested ZIP of the cartridge's source files + assets

Why uncompressed ZIP?
- Pure-stdlib Python (``zipfile``) and pure-JS browser parsing without a WASM
  zlib dependency. The browser-side hydrator in ``src/lib/v2/cartridge-zip.ts``
  reads the central directory at end-of-file, walks to each Local File Header,
  and slices the file data out of the byte buffer directly.
- Phase 2 is local-archive: the operator packs on their workstation and the
  cockpit fetches or imports the file. The size penalty vs compressed is
  bounded by the typical cartridge (~ a few hundred KB of TSX/JS) and
  acceptable for the trust-gain of a single-format envelope.

SHA-256 scope
--------------
The ``sha256`` field in the manifest hashes the **bytes of payload.zip**, NOT
the bytes of the outer .cartridge. This way the operator can repack the
manifest (e.g. update the routes table, bump the version, rotate the signature)
without re-hashing the source tree. The signature covers the manifest content
(excluding ``signature`` and ``created_at``) per ``cartridge_crypto.canonical_bytes``.

Tamper detection
----------------
``unpack`` verifies, in order:
  1. The outer ZIP has exactly two members: ``manifest.json`` and ``payload.zip``.
  2. The manifest parses as JSON.
  3. ``sha256`` in the manifest matches ``hashlib.sha256(payload_bytes).hexdigest()``.
  4. The ``manifest.sha256`` is not the V1_LEGACY_SHA256 magic string
     (V1 legacy manifests do not have a payload.zip; the runtime hydrator
     handles them separately — see ``cartridge_v2_adapter.py``).

A failure raises ``ArchiveError`` with a precise reason. The pack/verify CLI
translates this to a non-zero exit code so CI can gate on it.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from .cartridge_schemas import CartridgeManifestV2, V1_LEGACY_SHA256

MANIFEST_NAME = "manifest.json"
PAYLOAD_NAME = "payload.zip"


class ArchiveError(RuntimeError):
    """Raised when a .cartridge archive fails validation or packing."""


# ── SHA-256 helpers ──────────────────────────────────────────────────────────
def sha256_bytes(data: bytes) -> str:
    """Stable hex SHA-256 of a byte buffer."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Stable hex SHA-256 of a file (streamed, not loaded into memory)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Payload zip build (shared by pack and tests) ─────────────────────────────
def compute_payload_bytes(source_dir: str | Path) -> bytes:
    """Build the payload.zip bytes that pack() would produce from ``source_dir``.

    Single source of truth for the zip-walk + STORE compression + relative
    path layout. Both ``pack()`` and the test suite call this so the test
    helper cannot silently diverge from the production writer.

    Phase 2 is uncompressed-only (STORE method) so a deterministic
    byte-for-byte output is possible.
    """
    source_dir = Path(source_dir).resolve()
    if not source_dir.is_dir():
        raise ArchiveError(f"source directory does not exist: {source_dir}")
    payload_buf = io.BytesIO()
    with zipfile.ZipFile(payload_buf, "w", compression=zipfile.ZIP_STORED) as zf:
        for root, _dirs, files in os.walk(source_dir):
            for name in files:
                full = Path(root) / name
                rel = full.relative_to(source_dir).as_posix()
                zf.write(full, arcname=rel)
    return payload_buf.getvalue()


def compute_payload_sha256(source_dir: str | Path) -> str:
    """SHA-256 hex of the payload.zip bytes that pack() would produce.

    Convenience wrapper used by tests that need to pre-set
    ``manifest.sha256`` so pack() does not overwrite it.
    """
    return sha256_bytes(compute_payload_bytes(source_dir))


# ── Pack ─────────────────────────────────────────────────────────────────────
def pack(
    source_dir: str | Path,
    manifest: CartridgeManifestV2,
    output_path: str | Path,
) -> str:
    """
    Build a .cartridge archive from a source directory and a V2 manifest.

    Steps:
      1. Zip ``source_dir`` into an in-memory payload.zip (uncompressed).
      2. Compute sha256 of payload.zip bytes.
      3. If ``manifest.sha256`` is unset (or still the V1 magic), set it now.
      4. Serialize the manifest to JSON.
      5. Write manifest.json + payload.zip into the outer .cartridge zip
         (uncompressed) at ``output_path``.

    Returns the absolute output path.
    """
    payload_bytes = compute_payload_bytes(source_dir)

    # 2 + 3. SHA-256
    if not manifest.sha256 or manifest.sha256 == V1_LEGACY_SHA256:
        manifest = manifest.model_copy(update={"sha256": sha256_bytes(payload_bytes)})
    elif manifest.sha256 != sha256_bytes(payload_bytes):
        raise ArchiveError(
            f"manifest.sha256 ({manifest.sha256[:16]}…) does not match payload "
            f"({sha256_bytes(payload_bytes)[:16]}…); refusing to repack with a stale hash"
        )

    # 4. Serialize
    manifest_json = manifest.model_dump_json(indent=2).encode("utf-8")

    # 5. Outer archive
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_STORED) as outer:
        outer.writestr(MANIFEST_NAME, manifest_json)
        outer.writestr(PAYLOAD_NAME, payload_bytes)

    return str(output_path)


# ── Unpack / verify ──────────────────────────────────────────────────────────
def unpack(archive_path: str | Path) -> Tuple[CartridgeManifestV2, bytes, dict]:
    """
    Parse a .cartridge and return ``(manifest, payload_bytes, raw_metadata)``.

    ``raw_metadata`` is the dict of zip member metadata for both files, useful
    for the CLI's verbose output (sizes, compression, dates).

    Raises ``ArchiveError`` on any structural or hash failure.
    """
    archive_path = Path(archive_path)
    if not archive_path.is_file():
        raise ArchiveError(f"archive not found: {archive_path}")

    raw_metadata: dict = {}
    manifest_json: Optional[bytes] = None
    payload_bytes: Optional[bytes] = None

    try:
        with zipfile.ZipFile(archive_path, "r") as outer:
            members = outer.namelist()
            if sorted(members) != sorted([MANIFEST_NAME, PAYLOAD_NAME]):
                raise ArchiveError(
                    f"archive must contain exactly {MANIFEST_NAME!r} and {PAYLOAD_NAME!r}; "
                    f"found {members!r}"
                )
            for info in outer.infolist():
                if info.is_dir():
                    continue
                raw_metadata[info.filename] = {
                    "file_size": info.file_size,
                    "compress_size": info.compress_size,
                    "compress_type": info.compress_type,
                    "date_time": list(info.date_time),
                }
                if info.filename == MANIFEST_NAME:
                    manifest_json = outer.read(info)
                elif info.filename == PAYLOAD_NAME:
                    payload_bytes = outer.read(info)
    except zipfile.BadZipFile as e:
        raise ArchiveError(f"not a valid zip file: {e}") from e

    if manifest_json is None or payload_bytes is None:
        raise ArchiveError("manifest.json or payload.zip missing from archive")

    try:
        manifest_dict = json.loads(manifest_json.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ArchiveError(f"manifest.json is not valid UTF-8 JSON: {e}") from e

    try:
        manifest = CartridgeManifestV2.model_validate(manifest_dict)
    except Exception as e:
        raise ArchiveError(f"manifest failed V2 schema validation: {e}") from e

    # V1 legacy manifests intentionally do not carry a payload.zip. The
    # V1_LEGACY_SHA256 sentinel tells the runtime hydrator to delegate to
    # the V1 trusted loader; the archive layer treats it as a structural
    # V2 manifest that just happens to be a thin shim around V1.
    if manifest.sha256 == V1_LEGACY_SHA256:
        return manifest, payload_bytes, raw_metadata

    actual = sha256_bytes(payload_bytes)
    if actual != manifest.sha256:
        raise ArchiveError(
            f"sha256 mismatch: manifest declares {manifest.sha256[:16]}…, "
            f"payload.zip is {actual[:16]}… (archive is TAMPERED or REPACKED without rehash)"
        )

    return manifest, payload_bytes, raw_metadata


# ── CLI helpers ──────────────────────────────────────────────────────────────
def format_archive_report(manifest: CartridgeManifestV2, payload_bytes: bytes,
                          raw_metadata: dict) -> str:
    """Human-readable summary for the verify CLI."""
    lines = [
        f"  cartridge_id    : {manifest.cartridge_id}",
        f"  version         : {manifest.version}",
        f"  hostApiVersion  : {manifest.hostApiVersion}",
        f"  publisher_id    : {manifest.publisher_id}",
        f"  entry           : {manifest.entry}",
        f"  sha256          : {manifest.sha256[:32]}…" if len(manifest.sha256) == 64 else f"  sha256          : {manifest.sha256}",
        f"  signature       : {manifest.signature[:32]}…" if manifest.signature else "  signature       : (none)",
        f"  routes          : {len(manifest.routes)}",
    ]
    for r in manifest.routes:
        lines.append(f"    - {r.mount}  ->  {r.component}")
    if "payload.zip" in raw_metadata:
        m = raw_metadata["payload.zip"]
        lines.append(
            f"  payload.zip     : {m['file_size']} bytes "
            f"(stored, compress_type={m['compress_type']})"
        )
    return "\n".join(lines)
