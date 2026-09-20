#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Sync the VERSION file tag into all known live carriers in one pass.

History files (ledgers, old log rows, snapshots, governance docs) are
deliberately excluded — they must keep their original tags.

Usage:
    python scripts/sync_max_version.py [--check]

--check only reports drift without writing. Exit code 0 = in sync.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
OLD_TAGS = ["v1000.54-EXCALIBUR-A"]

TARGETS = [
    "bin/cloudbrain_sync.py",
    "bin/cybertronia.py",
    "bin/verify_production.py",
    "control_plane/runners/excalibur_cicd_loop.py",
    "control_plane/runners/worldtree_vps_cloudbrain_sync.py",
    "scripts/optimize_cybertronia_worldtree_max.py",
    "scripts/verify_production_readiness.py",
    "scripts/forge_excalibur_entiremap.py",
    "scripts/forge_cybertronia_entiremap.py",
    "vfs/build_knight_system_instructions.py",
    "tests/test_cybertronia_entiremap_cicd.py",
    "tests/test_excalibur_cicd_loop.py",
    "tests/test_excalibur_entiremap_cicd.py",
    "03_VAULT/training/configs/config/saltare.toml",
    "01_KERNEL/EXCALIBUR/config/saltare.toml",
    "01_KERNEL/EXCALIBUR/boot_excalibur.ps1",
]

def main():
    check = "--check" in sys.argv
    drift = []
    for rel in TARGETS:
        p = ROOT / rel
        if not p.exists():
            drift.append(f"{rel}: MISSING")
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        new = text
        for old in OLD_TAGS:
            new = new.replace(old, VERSION)
        if new != text:
            drift.append(f"{rel}: stale tag")
            if not check:
                p.write_text(new, encoding="utf-8")
                print(f"SYNCED {rel}")
    if drift:
        print("DRIFT:" if check else "SYNCED:")
        for d in drift:
            print(f"  {d}")
        return 1 if check else 0
    print(f"IN SYNC ({VERSION})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
