# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for Helios Parallel Lane Orchestrator (scripts/helios_lane.py).
=============================================================================
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.helios_lane import (
    get_lane_paths,
    sanitize_identifier,
)


def test_sanitize_identifier():
    assert sanitize_identifier("Contracts-Lane!") == "contracts-lane_"
    assert sanitize_identifier("registry lock") == "registry_lock"
    assert sanitize_identifier("VFS_Closure_101") == "vfs_closure_101"


def test_get_lane_paths():
    branch, folder, path = get_lane_paths("security", "key-lifecycle")
    assert branch == "reforge/helios/security/key-lifecycle"
    assert folder == "helios_security_key-lifecycle"
    assert path.name == folder
