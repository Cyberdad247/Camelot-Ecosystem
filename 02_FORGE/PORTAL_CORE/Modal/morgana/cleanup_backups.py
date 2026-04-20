# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Morgana Backup Retention — keeps the N most recent deployment backups.
Usage: python cleanup_backups.py [--keep 3] [--dry-run]
"""

import argparse
import shutil
from pathlib import Path


BACKUP_DIR = Path(__file__).parent / "backups"
DEFAULT_KEEP = 3


def cleanup(keep: int = DEFAULT_KEEP, dry_run: bool = False) -> list[str]:
    if not BACKUP_DIR.exists():
        print(f"No backup directory at {BACKUP_DIR}")
        return []

    dirs = sorted(
        [d for d in BACKUP_DIR.iterdir() if d.is_dir() and d.name.startswith("deployment_")],
        key=lambda d: d.name,
        reverse=True,
    )

    to_keep = dirs[:keep]
    to_purge = dirs[keep:]

    if not to_purge:
        print(f"Nothing to purge ({len(dirs)} backups, keeping {keep})")
        return []

    purged = []
    for d in to_purge:
        if dry_run:
            print(f"[DRY-RUN] Would purge: {d.name}")
        else:
            shutil.rmtree(d)
            print(f"[PURGED] {d.name}")
        purged.append(d.name)

    print(f"\nKept: {[d.name for d in to_keep]}")
    print(f"Purged: {len(purged)} backup(s)")
    return purged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Morgana backup retention")
    parser.add_argument("--keep", type=int, default=DEFAULT_KEEP, help=f"Backups to keep (default: {DEFAULT_KEEP})")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be purged without deleting")
    args = parser.parse_args()
    cleanup(keep=args.keep, dry_run=args.dry_run)
