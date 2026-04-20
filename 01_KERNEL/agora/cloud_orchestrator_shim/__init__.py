# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Tier 3: Cloud Orchestrator
#
# Blueprint-compatible facade. The real Morgana Modal stack already lives
# under 02_FORGE/PORTAL_CORE/Modal/morgana/. This package points
# `cloud_orchestrator` at it without duplicating files.
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_MORGANA_ROOT = _REPO / "02_FORGE" / "PORTAL_CORE" / "Modal"
sys.path.insert(0, str(_MORGANA_ROOT))
sys.path.insert(0, str(_MORGANA_ROOT / "morgana"))

__all__ = ["MORGANA_ROOT", "REPO_ROOT"]
MORGANA_ROOT = _MORGANA_ROOT
REPO_ROOT = _REPO
