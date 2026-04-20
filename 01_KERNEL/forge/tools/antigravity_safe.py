# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
ANTIGRAVITY: The Kinetic I/O Safety Layer
Part of Camelot Apex v100.0 (Kinetic Injection)

This module replaces the standard Python `open()` logs file operations,
and creates automatic backups before destructive writes.
"""

import builtins
import shutil
import time
from pathlib import Path
from typing import IO

# Save original open just in case
_original_open = builtins.open


def _backup_file(path: str):
    """Creates a timestamped backup of the file."""
    p = Path(path)
    if not p.exists():
        return

    timestamp = int(time.time())
    backup_dir = p.parent / ".antigravity_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / f"{p.name}.{timestamp}.bak"
    shutil.copy2(p, backup_path)
    # print(f"[ANTIGRAVITY] 🛡️ Backed up {p.name} -> {backup_path.name}")


def antigravity_open(file: str | Path, mode: str = "r", *args, **kwargs) -> IO:
    """
    middleware replacement for builtins.open.
    Intercepts write modes ('w', 'a', 'x', '+') to perform safety checks.
    """
    str_mode = str(mode)
    if any(m in str_mode for m in ["w", "a", "x", "+"]):
        # Safety Check 1: Creating backup
        try:
            _backup_file(file)
        except Exception as e:
            print(f"[ANTIGRAVITY] ⚠️ Backup failed for {file}: {e}")
            # We proceed, but warn.

        # Safety Check 2: Logging (Conceptual - could connect to Morgana)
        # print(f"[ANTIGRAVITY] ✍️ Opening {file} in mode '{mode}'")

    return _original_open(file, mode, *args, **kwargs)


# Expose as 'open' for easy drop-in replacement
open = antigravity_open