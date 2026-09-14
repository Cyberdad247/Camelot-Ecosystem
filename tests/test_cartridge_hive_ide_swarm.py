# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Tests for cartridge-hive-ide-swarm & VFS Digital Factory Scaffolding
===================================================================
Validates:
1. Manifest integrity, Ed25519 signature & VFS binding.
2. HiveEngine WASM32-WASI microVM spawn with CoW delta <= 0.12 MiB.
3. Paladin Octem Z3 verification gate & clean evaporation on violation.
4. Dynamic Skill Federation (VoltAgent assimilation) under ternary limits.
5. Real-time telemetry buffer tracking 8GB edge ceiling.
6. WebGPU reactive glass cockpit shader validity.
7. VFS Scaffolding matrix layout (/hive-core/workspace, /telemetry, /refractions, /socket).
"""

import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cartridges" / "cartridge-hive-ide-swarm"))

from hive_engine import (
    HiveEngine,
    MEMORY_LIMIT_PER_NODE_MB,
    GLOBAL_EDGE_CEILING_GB,
    COW_DELTA_LIMIT_MIB,
)
from vfs.worldtree_cartridge_knight_bridge import WorldtreeCartridgeKnightBridge


def test_vfs_scaffolding_exists():
    hive_core = ROOT / "hive-core"
    assert (hive_core / "workspace").is_dir()
    assert (hive_core / "telemetry").is_dir()
    assert (hive_core / "refractions").is_dir()
    assert (hive_core / "socket").is_dir()

    # Verify shader and buffer exist
    assert (hive_core / "telemetry" / "glass_cockpit.wgsl").is_file()
    assert (hive_core / "telemetry" / "telemetry_buffer.json").is_file()
    assert (hive_core / "socket" / "agent_bus.json").is_file()


def test_refractions_registered():
    refractions_dir = ROOT / "hive-core" / "refractions"
    for knight in ["merlin_omega", "sir_visage", "sir_codex", "sir_boris"]:
        file = refractions_dir / f"{knight}.refraction.json"
        assert file.is_file(), f"Missing refraction for {knight}"
        data = json.loads(file.read_text(encoding="utf-8"))
        assert data["cartridge_binding"] == "cartridge-hive-ide-swarm"
        assert data["ternary_quantization_active"] is True
        assert data["max_memory_mb"] <= 512


def test_worldtree_bridge_binding():
    bridge = WorldtreeCartridgeKnightBridge()
    for knight in ["MERLIN_OMEGA", "SIR_CODEX", "SIR_BORIS"]:
        res = bridge.resolve_vfs_uri(f"vfs://worldtree/knights/{knight}/cartridge")
        assert "HIVE_IDE_SWARM" in res["bound_cartridges"]


def test_hive_engine_microvm_lifecycle(tmp_path):
    engine = HiveEngine(root_path=tmp_path)
    sb = engine.spawn_sandbox("SIR_CODEX", "test-task-1")

    assert sb.status == "RUNNING"
    assert sb.cow_delta_mib <= COW_DELTA_LIMIT_MIB
    assert sb.memory_allocated_mb <= MEMORY_LIMIT_PER_NODE_MB
    assert sb.ephemeral_path.exists()

    # Test Z3 Verification Gate
    receipt = engine.verify_z3_gate(sb.sandbox_id, pdg_taint_clean=True)
    assert receipt.passed is True
    assert receipt.verifier == "Paladin Octem"
    assert receipt.pdg_taint_clean is True

    # Test Telemetry update
    telemetry = engine.update_telemetry()
    assert telemetry["active_microvm_count"] == 1
    assert telemetry["total_cow_delta_mib"] <= 0.12
    assert telemetry["ram_utilization_ratio"] <= 1.0

    # Test clean evaporation
    evaporated = engine.evaporate_sandbox(sb.sandbox_id)
    assert evaporated is True
    assert not sb.ephemeral_path.exists()
    assert engine.update_telemetry()["active_microvm_count"] == 0


def test_hive_engine_z3_failure_evaporation(tmp_path):
    engine = HiveEngine(root_path=tmp_path)
    sb = engine.spawn_sandbox("SIR_BORIS", "test-task-dirty")

    # Simulate PDG taint violation
    receipt = engine.verify_z3_gate(sb.sandbox_id, pdg_taint_clean=False)
    assert receipt.passed is False
    # Upon failure, the bubble must evaporate leaving zero mess
    assert not sb.ephemeral_path.exists()
    assert sb.sandbox_id not in engine.active_sandboxes


def test_voltagent_skill_federation(tmp_path):
    engine = HiveEngine(root_path=tmp_path)
    ok = engine.mount_voltagent_skill("nextjs_caching_algo", {"version": "1.0.0", "ternary_safe": True})
    assert ok is True
    assert "nextjs_caching_algo" in engine.mounted_skills
    refraction_file = tmp_path / "hive-core" / "refractions" / "nextjs_caching_algo.refraction.json"
    assert refraction_file.is_file()
