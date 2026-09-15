#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
r"""
Camelot-OS Resource Reduction & Safe Directory Purge Engine
============================================================
Safely purges non-functional, stale, and duplicate directories:
1. Stale Rust build target caches (cargo cleanable)
2. Stale duplicate node_modules (e.g. 02_FORGE/node_modules)
3. Stale duplicate / nested repository clones
4. Temporary test / build / go caches
"""

import os
import shutil
import stat
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]

# Handle Windows read-only file removal
def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def get_dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    total += os.path.getsize(fp)
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError):
        pass
    return total

PURGE_TARGETS = [
    # 1. Stale Rust Build Targets
    REPO_ROOT / "target",
    REPO_ROOT / "02_FORGE" / "KINETIC_ARMORY" / "target",
    REPO_ROOT / "02_FORGE" / "kinetic" / "target",
    REPO_ROOT / "02_FORGE" / "excalibur-dev" / "target",
    REPO_ROOT / "kinetic_edge" / "target",

    # 2. Stale Duplicate node_modules
    REPO_ROOT / "02_FORGE" / "node_modules",

    # 3. Redundant Nested Clones & Backups
    REPO_ROOT / "kickbox-audio",
    REPO_ROOT / "free-claude-code",
    REPO_ROOT / "Camelot-OS_vMAX_Singularity",
    REPO_ROOT / "camelot-fable-25",
    REPO_ROOT / "_tmp",
    REPO_ROOT / "Next development",

    # 4. Ephemeral Caches
    REPO_ROOT / ".cache",
    REPO_ROOT / "data" / "go-build",
    REPO_ROOT / "data" / ".pytest_temp",
    REPO_ROOT / ".pytest_cache",
]

def main():
    print("=" * 80)
    print("  ⚔️  CAMELOT-OS RESOURCE PURGE & OPTIMIZATION ROUTINE  ⚔️")
    print("=" * 80)

    total_bytes_freed = 0
    purged_items = []

    for target in PURGE_TARGETS:
        if target.exists() and target.is_dir():
            sz = get_dir_size(target)
            sz_mb = sz / (1024 * 1024)
            rel_path = str(target.relative_to(REPO_ROOT))
            print(f"Purging: {rel_path:<45} ({sz_mb:>8.2f} MB)...", end="", flush=True)
            
            try:
                shutil.rmtree(target, onerror=remove_readonly)
                total_bytes_freed += sz
                purged_items.append((rel_path, sz_mb))
                print(" ✅ DONE")
            except Exception as e:
                print(f" ⚠️ ERROR: {e}")

    # Clean __pycache__ across root
    pycache_count = 0
    pycache_bytes = 0
    for root, dirs, _ in os.walk(REPO_ROOT):
        if "__pycache__" in dirs and ".venv" not in root:
            p = Path(root) / "__pycache__"
            sz = get_dir_size(p)
            try:
                shutil.rmtree(p, onerror=remove_readonly)
                pycache_count += 1
                pycache_bytes += sz
            except Exception:
                pass

    if pycache_count > 0:
        total_bytes_freed += pycache_bytes
        print(f"Purged {pycache_count} __pycache__ directories ({pycache_bytes / (1024*1024):.2f} MB)")

    freed_mb = total_bytes_freed / (1024 * 1024)
    freed_gb = total_bytes_freed / (1024 * 1024 * 1024)

    print("=" * 80)
    print(f"🎉 RESOURCE PURGE COMPLETE: Recovered {freed_mb:,.2f} MB ({freed_gb:.2f} GB) of Disk Space!")
    print("=" * 80)

if __name__ == "__main__":
    main()
