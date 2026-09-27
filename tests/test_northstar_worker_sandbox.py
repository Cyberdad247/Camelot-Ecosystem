# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit & Integration Tests for Northstar Goal Background Workers & Personal CPU Sandboxes.
========================================================================================
Validates assimilation of OpenMausBot / openmausbotOS and Rakazo into Camelot-OS:
- Personal CPU Sandbox hardware quotas and VFS path confinement
- Inline Permission Broker risk assessment and HITL Allow/Deny gates
- Merlin Ω Northstar Goal DAG decomposition and milestone execution
- Persistent VFS checkpointing and recovery without context rot
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_module(rel_path: str, module_name: str):
    full_path = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(module_name, str(full_path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def worker_modules():
    sandbox_mod = _load_module("02_FORGE/assimilation/workers/personal_cpu_sandbox.py", "personal_cpu_sandbox")
    broker_mod = _load_module("02_FORGE/assimilation/workers/permission_broker.py", "permission_broker")
    engine_mod = _load_module("02_FORGE/assimilation/workers/northstar_worker_engine.py", "northstar_worker_engine")
    return {
        "sandbox": sandbox_mod,
        "broker": broker_mod,
        "engine": engine_mod,
    }


def test_sandbox_vfs_confinement_and_quotas(worker_modules):
    """Ensure PersonalCPUSandbox confines files to staging root and prevents directory traversal."""
    SandboxConfig = worker_modules["sandbox"].SandboxConfig
    PersonalCPUSandbox = worker_modules["sandbox"].PersonalCPUSandbox
    SandboxSecurityError = worker_modules["sandbox"].SandboxSecurityError

    with tempfile.TemporaryDirectory() as tmp_dir:
        config = SandboxConfig(
            worker_id="WRK-TEST01",
            knight_id="SIR_CODEX",
            max_memory_mb=350.0,
            cpu_quota_pct=60.0,
            local_staging_base=Path(tmp_dir) / "staging"
        )
        sandbox = PersonalCPUSandbox(config)

        # 1. Normal isolated write & read
        receipt = sandbox.vfs_write("src/core/test.py", "print('hello sovereign world')\n")
        assert receipt["status"] == "QUARANTINED"
        assert receipt["bytes_written"] > 0
        assert "vfs://worldtree/knights/SIR_CODEX/sandbox/WRK-TEST01" in receipt["vfs_path"]

        content = sandbox.vfs_read("src/core/test.py")
        assert "hello sovereign world" in content

        # 2. Prevent path traversal
        with pytest.raises(SandboxSecurityError):
            sandbox.vfs_write("../../../evil.sh", "malicious payload")

        # 3. Verify metrics
        metrics = sandbox.collect_metrics()
        assert metrics.worker_id == "WRK-TEST01"
        assert metrics.vfs_files_count >= 1
        assert metrics.memory_max_mb == 350.0
        assert metrics.cpu_quota_pct == 60.0


def test_permission_broker_risk_tiers_and_auto_approve(worker_modules):
    """Ensure PermissionBroker properly evaluates R0-R4 risk tiers and applies auto-approval threshold."""
    PermissionBroker = worker_modules["broker"].PermissionBroker
    RiskTier = worker_modules["broker"].RiskTier
    RequestStatus = worker_modules["broker"].RequestStatus

    with tempfile.TemporaryDirectory() as tmp_dir:
        persist_file = Path(tmp_dir) / "perms.json"
        broker = PermissionBroker(persistence_file=persist_file, auto_approve_threshold=RiskTier.R1_LOW)

        # Safe read operation -> R0 Auto Approved
        req_safe = broker.request_permission(
            worker_id="WRK-TEST02",
            knight_id="SIR_HELIOS",
            operation_type="VFS_READ",
            target="logs/status.txt",
            summary="Read telemetry"
        )
        assert req_safe.risk_tier == RiskTier.R0_SAFE.value
        assert req_safe.status == RequestStatus.AUTO_APPROVED.value

        # High risk: write > 10 lines -> R3 PENDING
        req_high = broker.request_permission(
            worker_id="WRK-TEST02",
            knight_id="SIR_CODEX",
            operation_type="VFS_WRITE",
            target="apps/core/runtime.ts",
            summary="Modify runtime logic",
            details={"lines_count": 45}
        )
        assert req_high.risk_tier == RiskTier.R3_HIGH.value
        assert req_high.status == RequestStatus.PENDING.value

        # Critical risk: touching kernel -> R4 PENDING
        req_crit = broker.request_permission(
            worker_id="WRK-TEST02",
            knight_id="SIR_SENTINEL",
            operation_type="SHELL_EXEC",
            target="01_KERNEL/core/aegis.rs",
            summary="Modify Aegis kernel shield"
        )
        assert req_crit.risk_tier == RiskTier.R4_CRITICAL.value
        assert req_crit.status == RequestStatus.PENDING.value

        # Verify pending list
        pending = broker.list_pending(worker_id="WRK-TEST02")
        assert len(pending) == 2
        assert pending[0].request_id in [req_high.request_id, req_crit.request_id]


def test_permission_broker_operator_approval(worker_modules):
    """Ensure operator can approve or deny pending HITL permission requests."""
    PermissionBroker = worker_modules["broker"].PermissionBroker
    RiskTier = worker_modules["broker"].RiskTier
    RequestStatus = worker_modules["broker"].RequestStatus

    with tempfile.TemporaryDirectory() as tmp_dir:
        persist_file = Path(tmp_dir) / "perms.json"
        broker = PermissionBroker(persistence_file=persist_file, auto_approve_threshold=RiskTier.R1_LOW)

        req = broker.request_permission(
            worker_id="WRK-TEST03",
            knight_id="SIR_CODEX",
            operation_type="GIT_ACTION",
            target="git push origin main",
            summary="Push commit to main"
        )
        assert req.status == RequestStatus.PENDING.value

        # Approve
        ok = broker.approve(req.request_id, operator_id="Arthur_Omega", reason="Verified by Arthur")
        assert ok is True
        updated = broker.get_request(req.request_id)
        assert updated.status == RequestStatus.APPROVED.value
        assert updated.decided_by == "Arthur_Omega"


def test_northstar_goal_lifecycle_and_stepping(worker_modules):
    """Test full Northstar goal decomposition, HITL pause, operator approval, and completion."""
    NorthstarWorkerEngine = worker_modules["engine"].NorthstarWorkerEngine
    WorkerState = worker_modules["engine"].WorkerState
    RequestStatus = worker_modules["broker"].RequestStatus

    with tempfile.TemporaryDirectory() as tmp_dir:
        engine = NorthstarWorkerEngine(persistence_root=Path(tmp_dir) / "workers")

        # Decompose a Northstar goal
        goal = engine.decompose_goal(
            title="Deploy Zero-Copy Ringbuffer Audio Pipeline",
            objective="Synthesize zero-copy ringbuffer in Rust for multivoice bridge",
            worker_id="WRK-AUDIO-01"
        )
        assert goal.worker_id == "WRK-AUDIO-01"
        assert len(goal.milestones) == 5
        assert goal.status == WorkerState.IDLE

        # Step 1: Pre-flight inspection (R0, auto-approved)
        res1 = engine.step_worker("WRK-AUDIO-01")
        assert res1["status"] in (WorkerState.RUNNING, WorkerState.IDLE)
        assert res1["milestone_completed"] == "WRK-AUDIO-01-M1"

        # Step 2: Architectural blueprint (R1, auto-approved)
        res2 = engine.step_worker("WRK-AUDIO-01")
        assert res2["milestone_completed"] == "WRK-AUDIO-01-M2"

        # Step 3: Kinetic code synthesis (R3, requires HITL approval)
        res3 = engine.step_worker("WRK-AUDIO-01")
        assert res3["status"] == WorkerState.BLOCKED_ON_HITL
        req_id = res3["permission_request_id"]

        # Operator reviews and approves
        approved = engine.broker.approve(req_id, operator_id="Arthur_Omega", reason="Blueprint verified")
        assert approved is True

        # Re-step milestone 3 after approval
        res3_retry = engine.step_worker("WRK-AUDIO-01")
        assert res3_retry["milestone_completed"] == "WRK-AUDIO-01-M3"

        # Step 4: Verification (R2, auto-approved)
        res4 = engine.step_worker("WRK-AUDIO-01")
        assert res4["milestone_completed"] == "WRK-AUDIO-01-M4"

        # Step 5: Ledger Inscription (R1, auto-approved)
        res5 = engine.step_worker("WRK-AUDIO-01")
        assert res5["milestone_completed"] == "WRK-AUDIO-01-M5"
        assert res5["status"] == WorkerState.COMPLETED

        # Check status and checkpoint persistence
        status = engine.get_worker_status("WRK-AUDIO-01")
        assert status["status"] == WorkerState.COMPLETED
        assert status["progress_pct"] == 100.0


def test_northstar_worker_recovery_from_disk(worker_modules):
    """Ensure worker state can be cleanly recovered from disk checkpoint after interruption."""
    NorthstarWorkerEngine = worker_modules["engine"].NorthstarWorkerEngine
    WorkerState = worker_modules["engine"].WorkerState

    with tempfile.TemporaryDirectory() as tmp_dir:
        storage_dir = Path(tmp_dir) / "workers"
        engine_a = NorthstarWorkerEngine(persistence_root=storage_dir)

        goal = engine_a.decompose_goal(
            title="Refactor SQLite-Vec KNN Engine",
            objective="Enhance vector cosine similarity indexing",
            worker_id="WRK-KNN-01"
        )
        engine_a.step_worker("WRK-KNN-01")  # Step M1

        status_before = engine_a.get_worker_status("WRK-KNN-01")
        assert status_before["current_milestone_index"] == 1

        # Simulate fresh daemon reboot
        engine_b = NorthstarWorkerEngine(persistence_root=storage_dir)
        status_after = engine_b.get_worker_status("WRK-KNN-01")
        assert status_after["worker_id"] == "WRK-KNN-01"
        assert status_after["current_milestone_index"] == 1
        assert status_after["title"] == "Refactor SQLite-Vec KNN Engine"
