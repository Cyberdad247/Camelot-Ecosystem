#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

# Mirrors of the authoritative root ledger, relative to the repo root.
# Every entry here is a byte-identical copy of PROVENANCE_LEDGER.md and is
# tracked by git. Adding a path here means `sync` overwrites it wholesale, so
# only add files that are genuinely copies of root.
#
# deploy/multivoice-router/PROVENANCE_LEDGER.md is deliberately NOT listed: it
# is an independent ledger for that sub-project, not a mirror of root.
MIRRORS = (
    "03_VAULT/PROVENANCE_LEDGER.md",
    "docs/PROVENANCE_LEDGER.md",
    "03_VAULT/training/configs/PROVENANCE_LEDGER.md",
    "03_VAULT/knowledge_vault/PROVENANCE_LEDGER.md",
    "control_plane/PROVENANCE_LEDGER.md",
    "docs/architecture/PROVENANCE_LEDGER.md",
)


def get_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def check(root_dir: Path) -> int:
    """Read-only drift audit: report each mirror's state vs root.

    Returns 1 if any mirror is stale, missing, or has diverged from root, so
    callers can gate on it. Never writes.
    """
    root_ledger = root_dir / "PROVENANCE_LEDGER.md"
    if not root_ledger.exists():
        print(f"Error: Authoritative root ledger not found at {root_ledger}")
        return 1

    root_hash = get_sha256(root_ledger)
    root_lines = root_ledger.read_text(encoding="utf-8", errors="replace").splitlines()
    root_set = set(root_lines)
    print(f"Authoritative Root Ledger size: {root_ledger.stat().st_size} bytes")
    print(f"SHA-256: {root_hash}  ({len(root_lines)} lines)\n")

    drift = 0
    for rel in MIRRORS:
        mirror = root_dir / rel
        if not mirror.exists():
            print(f"  MISSING  {rel}")
            drift += 1
            continue
        if get_sha256(mirror) == root_hash:
            print(f"  IN SYNC  {rel}")
            continue
        mirror_lines = mirror.read_text(encoding="utf-8", errors="replace").splitlines()
        mirror_set = set(mirror_lines)
        missing = sum(1 for line in root_lines if line not in mirror_set)
        extra = sum(1 for line in mirror_lines if line not in root_set)
        verdict = "DIVERGED" if extra else "STALE"
        print(f"  {verdict:<9} {rel}  ({len(mirror_lines)} lines, {missing} missing vs root, {extra} not in root)")
        drift += 1

    print()
    if drift:
        print(f"{drift}/{len(MIRRORS)} mirrors need reconciliation.")
        print("Reconcile by staging PROVENANCE_LEDGER.md and committing.")
    else:
        print(f"All {len(MIRRORS)} mirrors match root.")
    return 1 if drift else 0


def main():
    parser = argparse.ArgumentParser(description="Sync or audit PROVENANCE_LEDGER.md mirrors.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="read-only: report mirror drift and exit 1 if any mirror is stale",
    )
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    root_ledger = root_dir / "PROVENANCE_LEDGER.md"

    if not root_ledger.exists():
        print(f"Error: Authoritative root ledger not found at {root_ledger}")
        return

    if args.check:
        raise SystemExit(check(root_dir))

    mirrors = [root_dir / rel for rel in MIRRORS]

    print("Authoritative Root Ledger size:", root_ledger.stat().st_size, "bytes")

    # Syncing ledgers
    for mirror in mirrors:
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root_ledger, mirror)
        print(f"Copied authoritative ledger to: {mirror.relative_to(root_dir)} ({mirror.stat().st_size} bytes)")

    # Calculate hashes for status mapping
    files_to_hash = {
        "entiremap.md": root_dir / "entiremap.md",
        "03_VAULT/Missions/verification_ledger.jsonl": root_dir / "03_VAULT" / "Missions" / "verification_ledger.jsonl",
    }
    files_to_hash["PROVENANCE_LEDGER.md"] = root_ledger
    for rel in MIRRORS:
        files_to_hash[rel] = root_dir / rel

    hashes = {}
    for key, path in files_to_hash.items():
        hashes[key] = get_sha256(path)
        print(f"Hash for {key}: {hashes[key]}")

    status_path = root_dir / "logs" / "defense_grid" / "ledger_sync_status.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)

    # Read current sync status metadata if possible
    existing_data = {}
    if status_path.exists():
        try:
            with open(status_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass

    # Build new sync status
    run_id = f"ledger_mirror_sync_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    sync_status = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat() + "Z",
        "operator": "Antigravity",
        "command": "provenance ledger mirror synchronization",
        "notebook_id": existing_data.get("notebook_id", "8c656cfa-a189-409e-a72d-07692a47f17e"),
        "notebook_title": existing_data.get("notebook_title", "Camelot-OS v.1000"),
        "notebook_note_id": existing_data.get("notebook_note_id", "6c89b02b-798d-4243-b22e-8a139b00a3a0"),
        "hashes": hashes,
        "status": "SYNCED",
    }

    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(sync_status, f, indent=4)
    print(f"Updated sync status at: {status_path.relative_to(root_dir)}")
    print("--- LEDGER ALIGNMENT SUCCESSFUL ---")


if __name__ == "__main__":
    main()
