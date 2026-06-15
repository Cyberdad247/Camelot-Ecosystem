# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Kernel package initialization.
"""

from pathlib import Path
import sys  # noqa: F401
import os  # noqa: F401

# --- LAW OF ANTIGRAVITY: SAFE I/O INJECTION ---
try:
    from .forge.tools import antigravity_safe  # noqa: F401
    # Antigravity safe already patches builtins.open upon import
    print("[KERNEL] Antigravity Safe I/O Active.")
except ImportError:
    print("[KERNEL WARNING] Antigravity Safe I/O not found. Proceeding with caution.")

KERNEL_ROOT = Path(__file__).parent
STORAGE_ROOT = KERNEL_ROOT.parent / "Titan_Omega_Hypergraph"