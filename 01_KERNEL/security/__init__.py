# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

# init
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[2]
_root_sec = _repo_root / "security"
_ig_sec = _repo_root / "01_KERNEL" / "iron_gate" / "security"
for _p in [str(_root_sec), str(_ig_sec)]:
    if Path(_p).exists() and _p not in __path__:
        __path__.append(_p)

try:
    from security.warden import (
        SecurityDecision,
        SecurityException,
        SecurityWarden,
        warden,
    )
except ImportError:
    pass

