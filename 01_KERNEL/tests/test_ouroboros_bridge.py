# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def bridge_client():
    repo_root = Path(__file__).resolve().parent.parent.parent
    bridge_path = repo_root / "01_KERNEL" / "reasoning" / "ouroboros_bridge.py"
    
    spec = importlib.util.spec_from_file_location("ouroboros_bridge", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    
    return bridge.OuroborosClient()

def test_kernel_ouroboros_handshake(bridge_client):
    assert bridge_client.health_check() is True

def test_omega_patch_capabilities(bridge_client):
    status = bridge_client.get_status()
    
    assert "ternary_logic" in status
    assert "mamba_firn_recurrence" in status
    assert status["ternary_logic"] == "active"
    assert status["mamba_firn_recurrence"] == "active"
