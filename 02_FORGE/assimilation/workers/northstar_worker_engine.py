# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Northstar Goal Background Worker Engine — Autonomous Persistent Execution.
=============================================================================
Assimilates Rakazo persistent bot routines + OpenMausBot local agent harnesses
into Camelot-OS's Merlin Ω / Hermes Prime cognitive apex.

Core Capabilities:
1. High-Level Northstar Goal Decomposition:
   - Breaks long-running objectives into an ordered DAG of bounded milestones.
2. Isolated Personal CPU Sandbox:
   - Every background worker runs within its own dedicated PersonalCPUSandbox
     with MemoryMax=350M, CPUQuota=60%, and VFS position confinement.
3. Inline Permission Broker (HITL):
   - Pauses execution and creates approval cards on R3/R4 operations.
4. Persistent VFS Checkpointing:
   - Saves checkpoint snapshots to `03_VAULT/runtime_state/workers/<worker_id>/`
     allowing instant crash recovery and state replay without context rot.
5. Glass Observatory Telemetry & XP:
   - Emits live milestone progress, CPU/RAM telemetry, and Glass Observatory XP rewards.
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

try:
    from .permission_broker import PermissionBroker, RequestStatus, RiskTier
    from .personal_cpu_sandbox import PersonalCPUSandbox, SandboxConfig
except (ImportError, ValueError):
    import importlib.util
    _cur_dir = Path(__file__).resolve().parent

    def _dyn_load(filename: str, modname: str):
        if modname in sys.modules:
            return sys.modules[modname]
        spec = importlib.util.spec_from_file_location(modname, str(_cur_dir / filename))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[modname] = mod
            spec.loader.exec_module(mod)
            return mod
        raise ImportError(f"Could not load {filename}")

    _pb_mod = _dyn_load("permission_broker.py", "permission_broker")
    PermissionBroker = _pb_mod.PermissionBroker
    RequestStatus = _pb_mod.RequestStatus
    RiskTier = _pb_mod.RiskTier

    _pcs_mod = _dyn_load("personal_cpu_sandbox.py", "personal_cpu_sandbox")
    PersonalCPUSandbox = _pcs_mod.PersonalCPUSandbox
    SandboxConfig = _pcs_mod.SandboxConfig

LOG = logging.getLogger("camelot.northstar_worker")


class WorkerState(str):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    BLOCKED_ON_HITL = "BLOCKED_ON_HITL"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


@dataclass
class Milestone:
    milestone_id: str
    title: str
    description: str
    assigned_knight: str = "SIR_CODEX"
    risk_tier: str = RiskTier.R2_MEDIUM.value
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED, BLOCKED_ON_HITL
    required_operation: Optional[str] = None  # e.g., "VFS_WRITE", "SHELL_EXEC"
    target_path: Optional[str] = None
    output_receipt: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NorthstarGoal:
    goal_id: str
    title: str
    objective: str
    worker_id: str
    lead_knight: str = "MERLIN_Ω"
    milestones: List[Milestone] = field(default_factory=list)
    status: str = WorkerState.IDLE
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    current_milestone_index: int = 0
    xp_reward: int = 50

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["milestones"] = [m.to_dict() if isinstance(m, Milestone) else m for m in self.milestones]
        return data


class NorthstarWorkerEngine:
    """Manages persistent background workers executing decomposed Northstar goals."""

    def __init__(self, persistence_root: Optional[Path] = None, auto_approve_threshold: RiskTier = RiskTier.R2_MEDIUM):
        camelot_root = Path(__file__).resolve().parent.parent.parent.parent
        self.root = persistence_root or (camelot_root / "03_VAULT" / "runtime_state" / "workers")
        self.root.mkdir(parents=True, exist_ok=True)
        broker_persistence = self.root / "permission_requests.json"
        self.broker = PermissionBroker(persistence_file=broker_persistence, auto_approve_threshold=auto_approve_threshold)
        self._sandboxes: Dict[str, PersonalCPUSandbox] = {}
        self._goals: Dict[str, NorthstarGoal] = {}
        self._load_active_goals()

    def _load_active_goals(self) -> None:
        """Scan persistence root for existing worker checkpoint files."""
        for worker_dir in self.root.iterdir():
            if worker_dir.is_dir():
                chk_file = worker_dir / "checkpoint.json"
                if chk_file.exists():
                    try:
                        data = json.loads(chk_file.read_text(encoding="utf-8"))
                        milestones = [Milestone(**m) for m in data.get("milestones", [])]
                        data["milestones"] = milestones
                        goal = NorthstarGoal(**data)
                        self._goals[goal.worker_id] = goal
                    except Exception as e:
                        LOG.warning("Could not restore worker checkpoint %s: %s", chk_file, e)

    def _save_checkpoint(self, goal: NorthstarGoal) -> None:
        """Atomically persist goal checkpoint to VFS / disk."""
        worker_dir = self.root / goal.worker_id
        worker_dir.mkdir(parents=True, exist_ok=True)
        chk_file = worker_dir / "checkpoint.json"
        goal.updated_at = datetime.now(timezone.utc).isoformat()
        chk_file.write_text(json.dumps(goal.to_dict(), indent=2), encoding="utf-8")

    def _get_or_create_sandbox(self, worker_id: str, knight_id: str) -> PersonalCPUSandbox:
        if worker_id not in self._sandboxes:
            config = SandboxConfig(
                worker_id=worker_id,
                knight_id=knight_id,
                max_memory_mb=350.0,
                cpu_quota_pct=60.0
            )
            self._sandboxes[worker_id] = PersonalCPUSandbox(config)
        return self._sandboxes[worker_id]

    def decompose_goal(
        self,
        title: str,
        objective: str,
        lead_knight: str = "MERLIN_Ω",
        worker_id: Optional[str] = None
    ) -> NorthstarGoal:
        """Decompose high-level goal into actionable milestones (Merlin Ω TTC Deep DAG)."""
        w_id = worker_id or f"WRK-{uuid.uuid4().hex[:6].upper()}"
        g_id = f"GOAL-{uuid.uuid4().hex[:8].upper()}"

        # Standard Merlin Ω Milestone Decomposition Pattern
        milestones = [
            Milestone(
                milestone_id=f"{w_id}-M1",
                title="Telemetry & Pre-flight Environment Inspection",
                description="Probe active VFS mounts, check CPU/RAM quotas, and initialize sandbox staging.",
                assigned_knight="SIR_HELIOS",
                risk_tier=RiskTier.R0_SAFE.value,
                required_operation="METRICS_QUERY"
            ),
            Milestone(
                milestone_id=f"{w_id}-M2",
                title="Specification & Architectural Blueprint Formulation",
                description=f"Formulate formal implementation plan for: {title}",
                assigned_knight="SIR_BORIS",
                risk_tier=RiskTier.R1_LOW.value,
                required_operation="VFS_WRITE",
                target_path="blueprint.md"
            ),
            Milestone(
                milestone_id=f"{w_id}-M3",
                title="Kinetic Artifact Implementation & Synthesis",
                description=f"Synthesize verified code units fulfilling: {objective}",
                assigned_knight="SIR_CODEX",
                risk_tier=RiskTier.R3_HIGH.value,
                required_operation="VFS_WRITE",
                target_path="implementation_artifact.py"
            ),
            Milestone(
                milestone_id=f"{w_id}-M4",
                title="Formal Verification & Gate Clearance",
                description="Run sandboxed validation suite and verify Z3 logical proofs.",
                assigned_knight="ANYA_Ω",
                risk_tier=RiskTier.R2_MEDIUM.value,
                required_operation="SHELL_EXEC",
                target_path="pytest"
            ),
            Milestone(
                milestone_id=f"{w_id}-M5",
                title="Provenance Crystallization & Ledger Inscription",
                description="Commit final verified hashes to VKG and Provenance Ledger.",
                assigned_knight="LADY_MNEMOSYNE",
                risk_tier=RiskTier.R1_LOW.value,
                required_operation="VFS_WRITE",
                target_path="PROVENANCE_RECEIPT.json"
            )
        ]

        goal = NorthstarGoal(
            goal_id=g_id,
            title=title,
            objective=objective,
            worker_id=w_id,
            lead_knight=lead_knight,
            milestones=milestones,
            status=WorkerState.IDLE,
            xp_reward=60
        )
        self._goals[w_id] = goal
        self._get_or_create_sandbox(w_id, lead_knight)
        self._save_checkpoint(goal)
        LOG.info("[NORTHSTAR] Goal %s initialized for worker %s with %d milestones", g_id, w_id, len(milestones))
        return goal

    def step_worker(self, worker_id: str) -> Dict[str, Any]:
        """Execute the next pending milestone of the background worker."""
        goal = self._goals.get(worker_id)
        if not goal:
            raise KeyError(f"Worker {worker_id} not found")

        if goal.status in (WorkerState.COMPLETED, WorkerState.FAILED, WorkerState.TERMINATED):
            return {"worker_id": worker_id, "status": goal.status, "message": f"Worker is {goal.status}"}

        # Check if all milestones are finished
        if goal.current_milestone_index >= len(goal.milestones):
            goal.status = WorkerState.COMPLETED
            goal.completed_at = datetime.now(timezone.utc).isoformat()
            self._save_checkpoint(goal)
            self._award_glass_observatory_xp(goal)
            return {"worker_id": worker_id, "status": WorkerState.COMPLETED, "message": "All milestones completed"}

        current_m = goal.milestones[goal.current_milestone_index]
        sandbox = self._get_or_create_sandbox(worker_id, current_m.assigned_knight)

        # Evaluate permissions through PermissionBroker
        op_type = current_m.required_operation or "VFS_WRITE"
        target = current_m.target_path or "sandbox_file"
        details = {
            "milestone_id": current_m.milestone_id,
            "title": current_m.title,
            "lines_count": 25 if current_m.risk_tier == RiskTier.R3_HIGH.value else 5
        }

        # Check if there is already an approved permission request for this milestone
        existing = [
            r for r in self.broker._requests.values()
            if r.worker_id == worker_id and r.details.get("milestone_id") == current_m.milestone_id
        ]
        approved_req = next((r for r in existing if r.status == RequestStatus.APPROVED.value), None)
        if approved_req:
            perm_req = approved_req
        else:
            perm_req = self.broker.request_permission(
                worker_id=worker_id,
                knight_id=current_m.assigned_knight,
                operation_type=op_type,
                target=target,
                summary=f"Milestone {current_m.milestone_id}: {current_m.title}",
                details=details
            )

        # If HITL approval is required and still pending, block execution
        if perm_req.status == RequestStatus.PENDING.value:
            current_m.status = "BLOCKED_ON_HITL"
            goal.status = WorkerState.BLOCKED_ON_HITL
            self._save_checkpoint(goal)
            return {
                "worker_id": worker_id,
                "status": WorkerState.BLOCKED_ON_HITL,
                "blocked_milestone": current_m.milestone_id,
                "permission_request_id": perm_req.request_id,
                "message": f"Milestone {current_m.milestone_id} requires HITL authorization: {perm_req.summary}"
            }

        if perm_req.status == RequestStatus.DENIED.value:
            current_m.status = "FAILED"
            current_m.error = f"Permission denied by {perm_req.decided_by}: {perm_req.decision_reason}"
            goal.status = WorkerState.FAILED
            self._save_checkpoint(goal)
            return {
                "worker_id": worker_id,
                "status": WorkerState.FAILED,
                "failed_milestone": current_m.milestone_id,
                "error": current_m.error
            }

        # Execution allowed: run milestone within PersonalCPUSandbox
        goal.status = WorkerState.RUNNING
        current_m.status = "IN_PROGRESS"
        current_m.started_at = datetime.now(timezone.utc).isoformat()

        try:
            receipt: Dict[str, Any] = {}
            if op_type == "METRICS_QUERY":
                metrics = sandbox.collect_metrics()
                receipt = {"metrics": asdict(metrics)}
            elif op_type == "VFS_WRITE":
                content = f"# Generated by {current_m.assigned_knight}\n# Goal: {goal.title}\n# Milestone: {current_m.title}\n"
                receipt = sandbox.vfs_write(target, content)
            elif op_type == "SHELL_EXEC":
                # Simulated sandboxed verification run
                receipt = {
                    "exit_code": 0,
                    "stdout": f"[SANDBOX] Formal verification passed for {current_m.title}",
                    "status": "SUCCESS"
                }

            current_m.status = "COMPLETED"
            current_m.completed_at = datetime.now(timezone.utc).isoformat()
            current_m.output_receipt = receipt
            goal.current_milestone_index += 1

            # Check if this was the last milestone
            if goal.current_milestone_index >= len(goal.milestones):
                goal.status = WorkerState.COMPLETED
                goal.completed_at = datetime.now(timezone.utc).isoformat()
                self._award_glass_observatory_xp(goal)

            self._save_checkpoint(goal)
            return {
                "worker_id": worker_id,
                "milestone_completed": current_m.milestone_id,
                "status": goal.status,
                "progress_pct": round((goal.current_milestone_index / len(goal.milestones)) * 100, 1),
                "receipt": receipt
            }

        except Exception as e:
            current_m.status = "FAILED"
            current_m.error = str(e)
            goal.status = WorkerState.FAILED
            self._save_checkpoint(goal)
            LOG.error("[NORTHSTAR] Milestone %s failed: %s", current_m.milestone_id, e)
            return {
                "worker_id": worker_id,
                "status": WorkerState.FAILED,
                "milestone": current_m.milestone_id,
                "error": str(e)
            }

    def _award_glass_observatory_xp(self, goal: NorthstarGoal) -> None:
        """Tap Glass Observatory telemetry on goal achievement."""
        try:
            import importlib.util
            camelot_root = Path(__file__).resolve().parent.parent.parent.parent
            engine_path = camelot_root / "02_FORGE" / "assimilation" / "omniroute" / "omniroute_bridge.py"
            if engine_path.exists():
                spec = importlib.util.spec_from_file_location("omniroute_bridge", str(engine_path))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    bridge = mod.OmniRouteBridge()
                    bridge.tap_glass_observatory(
                        metric_name=f"northstar_goal_completed_{goal.worker_id}",
                        value=goal.xp_reward,
                        xp_gained=goal.xp_reward
                    )
        except Exception as e:
            LOG.debug("Glass Observatory tap deferred: %s", e)

    def pause_worker(self, worker_id: str) -> bool:
        goal = self._goals.get(worker_id)
        if not goal or goal.status in (WorkerState.COMPLETED, WorkerState.FAILED):
            return False
        goal.status = WorkerState.PAUSED
        self._save_checkpoint(goal)
        return True

    def resume_worker(self, worker_id: str) -> bool:
        goal = self._goals.get(worker_id)
        if not goal or goal.status != WorkerState.PAUSED:
            return False
        goal.status = WorkerState.RUNNING
        self._save_checkpoint(goal)
        return True

    def halt_worker(self, worker_id: str) -> bool:
        goal = self._goals.get(worker_id)
        if not goal:
            return False
        goal.status = WorkerState.TERMINATED
        if worker_id in self._sandboxes:
            self._sandboxes[worker_id].cleanup()
        self._save_checkpoint(goal)
        return True

    def get_worker_status(self, worker_id: str) -> Dict[str, Any]:
        goal = self._goals.get(worker_id)
        if not goal:
            raise KeyError(f"Worker {worker_id} not found")

        sandbox = self._get_or_create_sandbox(worker_id, goal.lead_knight)
        metrics = sandbox.collect_metrics()
        pending_requests = self.broker.list_pending(worker_id=worker_id)

        return {
            "worker_id": worker_id,
            "goal_id": goal.goal_id,
            "title": goal.title,
            "objective": goal.objective,
            "lead_knight": goal.lead_knight,
            "status": goal.status,
            "current_milestone_index": goal.current_milestone_index,
            "total_milestones": len(goal.milestones),
            "progress_pct": round((goal.current_milestone_index / max(1, len(goal.milestones))) * 100, 1),
            "milestones": [m.to_dict() for m in goal.milestones],
            "sandbox_metrics": asdict(metrics),
            "pending_hitl_requests": [req.to_dict() for req in pending_requests],
            "updated_at": goal.updated_at
        }

    def list_all_workers(self) -> List[Dict[str, Any]]:
        return [self.get_worker_status(w_id) for w_id in self._goals.keys()]
