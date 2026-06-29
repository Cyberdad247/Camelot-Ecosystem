#!/usr/bin/env python3
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

def get_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    root_dir = Path(__file__).resolve().parent.parent
    root_ledger = root_dir / "PROVENANCE_LEDGER.md"
    
    if not root_ledger.exists():
        print(f"Error: Authoritative root ledger not found at {root_ledger}")
        return

    mirrors = [
        root_dir / "03_VAULT" / "PROVENANCE_LEDGER.md",
        root_dir / "docs" / "PROVENANCE_LEDGER.md",
        root_dir / "03_VAULT" / "training" / "configs" / "PROVENANCE_LEDGER.md",
    ]

    print("Authoritative Root Ledger size:", root_ledger.stat().st_size, "bytes")
    
    # Syncing ledgers
    for mirror in mirrors:
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root_ledger, mirror)
        print(f"Copied authoritative ledger to: {mirror.relative_to(root_dir)} ({mirror.stat().st_size} bytes)")

    # Calculate hashes for status mapping
    files_to_hash = {
        "entiremap.md": root_dir / "entiremap.md",
        "PROVENANCE_LEDGER.md": root_ledger,
        "03_VAULT/Missions/verification_ledger.jsonl": root_dir / "03_VAULT" / "Missions" / "verification_ledger.jsonl",
        "03_VAULT/training/configs/PROVENANCE_LEDGER.md": root_dir / "03_VAULT" / "training" / "configs" / "PROVENANCE_LEDGER.md",
        "03_VAULT/PROVENANCE_LEDGER.md": root_dir / "03_VAULT" / "PROVENANCE_LEDGER.md",
        "docs/PROVENANCE_LEDGER.md": root_dir / "docs" / "PROVENANCE_LEDGER.md",
    }

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
        "status": "SYNCED"
    }

    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(sync_status, f, indent=4)
    print(f"Updated sync status at: {status_path.relative_to(root_dir)}")
    print("--- LEDGER ALIGNMENT SUCCESSFUL ---")

if __name__ == "__main__":
    main()
