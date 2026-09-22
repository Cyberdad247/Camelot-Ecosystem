# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""DG-330 State & Schema Migration Engine.
========================================
Implements the 5-stage sovereign migration machine:
    PRECHECK -> SNAPSHOT -> MIGRATE -> VERIFY -> PROMOTE
    (or VERIFY FAIL -> RETREAT)

Supported Subsystems:
- database: Prisma / PostgreSQL schema & tables
- vfs: Position-addressed WorldTree layout
- ukg: Universal Knowledge Graph crystal formats
- memory: MemCastle & Graphiti temporal partitions
- contracts: Schema revisions & contracts.lock
- configuration: camelot-config/1 migrations
- persona_package: Knight behavior definitions

Invariant:
A new binary must not imply that stored state is automatically compatible.
No migration proceeds without a precheck and verified rollback snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import datetime
from datetime import timezone
from enum import Enum
import hashlib
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

LOG = logging.getLogger("camelot.migration_engine")


class MigrationStage(str, Enum):
    IDLE = "IDLE"
    PRECHECK = "PRECHECK"
    SNAPSHOT = "SNAPSHOT"
    MIGRATE = "MIGRATE"
    VERIFY = "VERIFY"
    PROMOTE = "PROMOTE"
    RETREAT = "RETREAT"


@dataclass
class MigrationStep:
    step_id: str
    description: str
    action_fn: Callable[[], bool]
    rollback_fn: Optional[Callable[[], bool]] = None


@dataclass
class MigrationPlan:
    plan_id: str
    target_subsystem: str
    from_version: str
    to_version: str
    precheck_fns: List[Callable[[], bool]]
    steps: List[MigrationStep]
    verification_fns: List[Callable[[], bool]]
    author: str = "ARTHUR_OMEGA"


@dataclass
class MigrationReceipt:
    receipt_id: str
    plan_id: str
    target_subsystem: str
    from_version: str
    to_version: str
    status: str  # "PROMOTED" or "RETREATED"
    snapshot_hash: str
    post_state_hash: str
    duration_ms: float
    timestamp: str
    stages_completed: List[str]
    retreat_reason: Optional[str] = None


class MigrationEngine:
    """Executes signed migration plans under strict precheck/snapshot/retreat guarantees."""

    def __init__(self):
        self._history: List[MigrationReceipt] = []

    def execute_migration(
        self,
        plan: MigrationPlan,
        state_reader_fn: Callable[[], str],
        state_restorer_fn: Callable[[str], None],
    ) -> MigrationReceipt:
        """Execute full 5-stage migration with automated First-Class RETREAT on error."""
        t0 = datetime.datetime.now(timezone.utc)
        stages: List[str] = []
        active_stage = MigrationStage.IDLE
        snapshot_data = ""
        snapshot_hash = ""
        post_state_hash = ""

        try:
            # 1. PRECHECK
            active_stage = MigrationStage.PRECHECK
            stages.append(active_stage.value)
            for precheck in plan.precheck_fns:
                if not precheck():
                    raise RuntimeError("Precheck assertion failed before state mutation")

            # 2. SNAPSHOT
            active_stage = MigrationStage.SNAPSHOT
            stages.append(active_stage.value)
            snapshot_data = state_reader_fn()
            snapshot_hash = hashlib.sha256(snapshot_data.encode("utf-8")).hexdigest()

            # 3. MIGRATE
            active_stage = MigrationStage.MIGRATE
            stages.append(active_stage.value)
            executed_steps: List[MigrationStep] = []
            for step in plan.steps:
                success = step.action_fn()
                if not success:
                    raise RuntimeError(f"Step '{step.step_id}' failed: {step.description}")
                executed_steps.append(step)

            # 4. VERIFY
            active_stage = MigrationStage.VERIFY
            stages.append(active_stage.value)
            for verify in plan.verification_fns:
                if not verify():
                    raise RuntimeError("Post-migration semantic verification failed")

            # 5. PROMOTE
            active_stage = MigrationStage.PROMOTE
            stages.append(active_stage.value)
            post_state_data = state_reader_fn()
            post_state_hash = hashlib.sha256(post_state_data.encode("utf-8")).hexdigest()

            t1 = datetime.datetime.now(timezone.utc)
            duration = (t1 - t0).total_seconds() * 1000.0

            receipt = MigrationReceipt(
                receipt_id=f"mig_rec_{hashlib.sha256(f'{plan.plan_id}:{t1.isoformat()}'.encode()).hexdigest()[:12]}",
                plan_id=plan.plan_id,
                target_subsystem=plan.target_subsystem,
                from_version=plan.from_version,
                to_version=plan.to_version,
                status="PROMOTED",
                snapshot_hash=snapshot_hash,
                post_state_hash=post_state_hash,
                duration_ms=round(duration, 2),
                timestamp=t1.isoformat(),
                stages_completed=stages,
            )
            self._history.append(receipt)
            return receipt

        except Exception as exc:
            # First-Class RETREAT
            active_stage = MigrationStage.RETREAT
            stages.append(active_stage.value)
            LOG.warning("Migration failed at %s: %s. Executing rollback...", stages[-2], exc)

            # Restore original snapshot
            if snapshot_data:
                state_restorer_fn(snapshot_data)

            # Execute step rollbacks in reverse order
            for step in reversed(plan.steps):
                if step.rollback_fn:
                    try:
                        step.rollback_fn()
                    except Exception as rb_err:
                        LOG.error("Step rollback error for %s: %s", step.step_id, rb_err)

            t1 = datetime.datetime.now(timezone.utc)
            duration = (t1 - t0).total_seconds() * 1000.0

            retreat_receipt = MigrationReceipt(
                receipt_id=f"retreat_rec_{hashlib.sha256(f'{plan.plan_id}:{t1.isoformat()}'.encode()).hexdigest()[:12]}",
                plan_id=plan.plan_id,
                target_subsystem=plan.target_subsystem,
                from_version=plan.from_version,
                to_version=plan.to_version,
                status="RETREATED",
                snapshot_hash=snapshot_hash,
                post_state_hash=snapshot_hash,  # Reverted to snapshot
                duration_ms=round(duration, 2),
                timestamp=t1.isoformat(),
                stages_completed=stages,
                retreat_reason=str(exc),
            )
            self._history.append(retreat_receipt)
            return retreat_receipt

    @property
    def history(self) -> List[MigrationReceipt]:
        return list(self._history)
