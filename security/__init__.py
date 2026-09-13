# SPDX-License-Identifier: MIT
"""Security package for Camelot OS.

Provides zero-trust security warden, prompt injection defense,
and structured policy decision enforcement.
"""

from pathlib import Path

_repo_root = Path(__file__).resolve().parent
_ig_sec = _repo_root / "01_KERNEL" / "iron_gate" / "security"
_k_sec = _repo_root / "01_KERNEL" / "security"
for _p in [str(_ig_sec), str(_k_sec)]:
    if Path(_p).exists() and _p not in __path__:
        __path__.append(_p)

from security.warden import (
    SecurityDecision,
    SecurityException,
    SecurityWarden,
    warden,
)

__all__ = [
    "SecurityDecision",
    "SecurityException",
    "SecurityWarden",
    "warden",
]
