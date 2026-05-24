import pytest
import sys
import os
import importlib.util
from pathlib import Path

def test_kernel_ouroboros_handshake():
    repo_root = Path(__file__).resolve().parent.parent.parent
    bridge_path = repo_root / "01_KERNEL" / "reasoning" / "ouroboros_bridge.py"
    
    spec = importlib.util.spec_from_file_location("ouroboros_bridge", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    
    client = bridge.OuroborosClient()
    assert client.health_check() == True

def test_omega_patch_capabilities():
    repo_root = Path(__file__).resolve().parent.parent.parent
    bridge_path = repo_root / "01_KERNEL" / "reasoning" / "ouroboros_bridge.py"
    
    spec = importlib.util.spec_from_file_location("ouroboros_bridge", bridge_path)
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    
    client = bridge.OuroborosClient()
    status = client.get_status()
    
    assert "ternary_logic" in status
    assert "mamba_firn_recurrence" in status
    assert status["ternary_logic"] == "active"
    assert status["mamba_firn_recurrence"] == "active"
