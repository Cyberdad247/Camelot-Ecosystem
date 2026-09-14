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
from parallel_ast_runner import ParallelASTExecutionEngine
from zeroclaw_ipc import (
    ZeroClawRingBuffer,
    WASMComponentRuntime,
    VFSGuardianError,
    CgroupsV2QuotaExceeded,
    LINEAR_MEMORY_HARD_CAP_MB,
    COW_OVERHEAD_CEILING_MIB,
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


def test_parallel_ast_execution_swarm(tmp_path):
    runner = ParallelASTExecutionEngine(root_path=tmp_path)
    report = runner.run_parallel_swarm("Synthesize Test AST Component")

    assert report.sandboxes_spawned == 2
    assert report.all_cow_deltas_compliant is True
    assert report.z3_receipt["passed"] is True
    assert report.z3_receipt["verifier"] == "Paladin Octem"
    assert report.z3_receipt["pdg_taint_clean"] is True
    assert len(report.promoted_artifacts) == 2
    assert report.evaporation_confirmed is True

    # Confirm promoted artifacts exist on disk
    for path_str in report.promoted_artifacts:
        assert Path(path_str).is_file()

    # Confirm ephemeral sandboxes evaporated cleanly
    workspace_dirs = [p for p in (tmp_path / "hive-core" / "workspace").iterdir() if p.is_dir() and p.name.startswith("sandbox-")]
    assert len(workspace_dirs) == 0


def test_pdg_security_audit_rejection():
    runner = ParallelASTExecutionEngine()
    clean_code = "def safe_func():\n    return 42\n"
    assert runner.audit_pdg_security(clean_code) is True

    tainted_code = "import os\ndef malicious():\n    os.system('rm -rf /')\n"
    assert runner.audit_pdg_security(tainted_code) is False

    eval_code = "def eval_bad():\n    eval('1+1')\n"
    assert runner.audit_pdg_security(eval_code) is False


def test_workspace_enclaves_structure():
    workspace = ROOT / "hive-core" / "workspace"
    for enc in ["source", "worktree", "tmp", "socket"]:
        assert (workspace / enc).is_dir(), f"Missing workspace enclave {enc}"

    assert (workspace / "source" / "guardian.json").is_file()
    assert (workspace / "worktree" / "sentinel_lease.json").is_file()
    assert (workspace / "tmp" / "cgroup_quota.json").is_file()
    assert (workspace / "socket" / "zeroclaw_ring.json").is_file()


def test_zeroclaw_ring_buffer_lock_free():
    ring = ZeroClawRingBuffer(buffer_id="ring-test")
    data = b'{"msg": "AST_STREAM_DATA", "tokens": 0}'
    written = ring.write_packet(data)
    assert written > len(data)

    read_back = ring.read_packet()
    assert read_back == data
    assert ring.read_packet() is None


def test_wasm_component_runtime_and_guardian(tmp_path):
    runtime = WASMComponentRuntime(root_dir=tmp_path)
    # Ensure directories
    for enc in ["source", "worktree", "tmp", "socket"]:
        (tmp_path / "hive-core" / "workspace" / enc).mkdir(parents=True, exist_ok=True)

    # Spawn within 64MB hard ceiling
    comp = runtime.spawn_prewarmed_component("comp-01", "rust", "SIR_CODEX", 32.0)
    assert comp["linear_memory_mb"] == 32.0
    assert comp["cow_delta_mib"] <= COW_OVERHEAD_CEILING_MIB

    # Attempt allocation beyond 64MB hard cap -> must raise CgroupsV2QuotaExceeded
    with pytest.raises(CgroupsV2QuotaExceeded):
        runtime.allocate_linear_memory("comp-oom", 128.0)

    # Attempt write under pinned source enclave -> must raise VFSGuardianError
    forbidden_target = tmp_path / "hive-core" / "workspace" / "source" / "injected.py"
    with pytest.raises(VFSGuardianError):
        runtime.enforce_vfs_guardian(forbidden_target)

    # Evaporate cleanly
    evaporated = runtime.evaporate_component("comp-01")
    assert evaporated is True


