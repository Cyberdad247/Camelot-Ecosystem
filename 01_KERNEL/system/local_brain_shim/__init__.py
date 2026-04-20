# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Tier 1: Local Brain (Kinetic Edge)
#
# Blueprint-compatible facade. The actual FastAPI app already lives at
# 01_KERNEL/EXCALIBUR/core/excalibur.py. This package re-exports it under
# the blueprint's `local_brain` namespace so `python -m local_brain` and
# `from local_brain import app` both work without file duplication.
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "01_KERNEL"))
sys.path.insert(0, str(_REPO / "01_KERNEL" / "EXCALIBUR" / "core"))

try:
    from excalibur import app  # type: ignore  # noqa: F401
except Exception as _exc:
    app = None
    _import_error = _exc
else:
    _import_error = None

__all__ = ["app"]
