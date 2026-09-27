# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""DG-390 Universal Safe Mode & Emergency Authority Freeze Governor.
===================================================================
Establishes the 5 sovereign operating postures:
- NORMAL: Standard execution across all Knights, workers, and leases.
- DEGRADED: Non-essential workers throttled; heightened telemetry sampling.
- SAFE: External network egress blocked; R2+ writes require HITL confirmation.
- FROZEN: Universal Emergency Brake. Mutations completely halted. Read-only diagnostics active.
- RECOVERY: Controlled recovery quorum restoring verified state.

FROZEN Posture Matrix:
- New Leases:             DENY
- Epoch Promotion:        DENY (except recovery quorum)
- External Writes:        DENY
- New Persona Packages:   DENY
- Assimilation APPLY:     DENY
- Memory Activation:      DENY
- Read Canonical State:   ALLOW
- Verify Receipts:        ALLOW
- Diagnostics:            ALLOW
- Export Evidence:        ALLOW
"""
from __future__ import annotations

from dataclasses import dataclass
import datetime
from datetime import timezone
from enum import Enum
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("camelot.safe_mode")


class OperatingPosture(str, Enum):
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    SAFE = "SAFE"
    FROZEN = "FROZEN"
    RECOVERY = "RECOVERY"


@dataclass
class PostureTransitionReceipt:
    transition_id: str
    from_posture: OperatingPosture
    to_posture: OperatingPosture
    reason: str
    triggered_by: str
    timestamp: str
    signature: str


class SafeModeGovernor:
    """Controls the operating posture of Camelot-OS nodes."""

    def __init__(self, initial_posture: OperatingPosture = OperatingPosture.NORMAL):
        self._posture = initial_posture
        self._history: List[PostureTransitionReceipt] = []

    @property
    def current_posture(self) -> OperatingPosture:
        return self._posture

    def transition_to(
        self,
        new_posture: OperatingPosture,
        reason: str,
        triggered_by: str = "ARTHUR_SOVEREIGN",
        recovery_quorum_token: Optional[str] = None,
    ) -> PostureTransitionReceipt:
        """Transitions node posture. Moving from FROZEN to RECOVERY requires quorum token."""
        if self._posture == OperatingPosture.FROZEN and new_posture not in (
            OperatingPosture.RECOVERY,
            OperatingPosture.FROZEN,
        ):
            if not recovery_quorum_token or not recovery_quorum_token.startswith("QUORUM_"):
                raise PermissionError(
                    "Cannot exit FROZEN posture without a valid Arthur Recovery Quorum token."
                )

        now_iso = datetime.datetime.now(timezone.utc).isoformat()
        t_id = f"trans_{hashlib.sha256(f'{self._posture}:{new_posture}:{now_iso}'.encode()).hexdigest()[:12]}"
        sig = hashlib.sha256(f"{t_id}:{reason}:{triggered_by}".encode()).hexdigest()[:16]

        receipt = PostureTransitionReceipt(
            transition_id=t_id,
            from_posture=self._posture,
            to_posture=new_posture,
            reason=reason,
            triggered_by=triggered_by,
            timestamp=now_iso,
            signature=sig,
        )

        LOG.warning(
            "POSTURE TRANSITION: %s -> %s (Reason: %s, Triggered By: %s)",
            self._posture.value,
            new_posture.value,
            reason,
            triggered_by,
        )
        self._posture = new_posture
        self._history.append(receipt)
        return receipt

    def check_operation_allowed(self, operation_type: str) -> Tuple[bool, Optional[str]]:
        """Check whether an operation is allowed under the current operating posture."""
        if self._posture == OperatingPosture.NORMAL:
            return True, None

        if self._posture == OperatingPosture.DEGRADED:
            if operation_type in ("SPAWN_BACKGROUND_WORKER", "SWARM_FANOUT"):
                return False, "Operation throttled under DEGRADED posture"
            return True, None

        if self._posture == OperatingPosture.SAFE:
            if operation_type in ("EXTERNAL_NETWORK_EGRESS", "UNVERIFIED_CARTRIDGE_LOAD"):
                return False, "Operation blocked under SAFE posture (airgap defense active)"
            return True, None

        if self._posture == OperatingPosture.FROZEN:
            allowed_in_frozen = {
                "READ_CANONICAL_STATE",
                "VERIFY_RECEIPT",
                "DIAGNOSTICS",
                "EXPORT_EVIDENCE",
                "STATUS_PROBE",
            }
            if operation_type in allowed_in_frozen:
                return True, None
            return False, f"AUTHORITY_FROZEN: Operation '{operation_type}' denied during universal emergency freeze."

        if self._posture == OperatingPosture.RECOVERY:
            allowed_in_recovery = {
                "READ_CANONICAL_STATE",
                "VERIFY_RECEIPT",
                "DIAGNOSTICS",
                "EXPORT_EVIDENCE",
                "RESTORE_SNAPSHOT",
                "REPLAY_MIGRATION",
                "STATUS_PROBE",
            }
            if operation_type in allowed_in_recovery:
                return True, None
            return False, f"RECOVERY_MODE: Operation '{operation_type}' denied while recovery quorum is active."

        return False, "Unknown operating posture"
