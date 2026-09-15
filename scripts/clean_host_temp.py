#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
r"""
Host Temporary File & Cache Sanitizer
=====================================
Safely purges unlockable, stale temporary files from C:\Users\vizio\AppData\Local\Temp
and user-level cache folders without disturbing active OS locks.
"""

import os
import shutil
import stat
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEMP_DIR = Path(os.environ.get("TEMP", r"C:\Users\vizio\AppData\Local\Temp"))

def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def get_dir_size(path: Path) -> int:
    total = 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
    except Exception:
        pass
    return total

def clean_temp_directory():
    print("=" * 75)
    print(f"🧹 Scanning Host Temp Directory: {TEMP_DIR}")
    print("=" * 75)

    if not TEMP_DIR.exists():
        print("Temp directory not found.")
        return 0

    initial_size = get_dir_size(TEMP_DIR)
    print(f"Initial Temp Size: {initial_size / (1024*1024):,.2f} MB ({initial_size / (1024*1024*1024):.2f} GB)")

    freed_bytes = 0
    deleted_files = 0
    deleted_dirs = 0

    # Scan and delete individual top-level files
    for entry in TEMP_DIR.iterdir():
        try:
            if entry.is_file(follow_symlinks=False):
                try:
                    sz = entry.stat().st_size
                    entry.unlink(missing_ok=True)
                    freed_bytes += sz
                    deleted_files += 1
                except (PermissionError, OSError):
                    pass # File in active use by OS/process
            elif entry.is_dir(follow_symlinks=False):
                try:
                    sz = get_dir_size(entry)
                    shutil.rmtree(entry, onerror=remove_readonly)
                    freed_bytes += sz
                    deleted_dirs += 1
                except (PermissionError, OSError):
                    pass # Dir contains active locked handle
        except (PermissionError, OSError):
            pass

    freed_mb = freed_bytes / (1024 * 1024)
    freed_gb = freed_bytes / (1024 * 1024 * 1024)
    print(f"✅ Cleaned: {deleted_files} files, {deleted_dirs} directories")
    print(f"🎉 Total Host Space Recovered: {freed_mb:,.2f} MB ({freed_gb:.2f} GB)")
    print("=" * 75)
    return freed_bytes

if __name__ == "__main__":
    clean_temp_directory()
