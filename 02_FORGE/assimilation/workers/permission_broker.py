# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Inline Permission Broker — Human-In-The-Loop (HITL) Gatekeeper for Workers.
==============================================================================
Assimilates the OpenMausBot / openmausbotOS permission broker card pattern into
Camelot-OS's Dual-Gate security architecture.

Risk Tiers:
- R0_SAFE: In-sandbox read operations, metrics, status. (Auto-approved)
- R1_LOW: Reading allowed project files, non-destructive queries. (Auto-approved under policy)
- R2_MEDIUM: File changes <= 10 lines, running non-mutating test scripts.
- R3_HIGH: File edits > 10 lines, git commit/push, dependency installations, external network egress. (Requires Operator Approval)
- R4_CRITICAL: Shell execution with system/root privileges, touching 01_KERNEL, systemd, or crypto keys. (Requires Arthur/Merlin Handshake)

Flow:
Whenever a sandboxed background worker attempts an R2/R3/R4 action:
1. `evaluate_action()` intercepts the call.
2. A `PermissionRequest` is generated with cryptographic hash and details.
3. If risk >= R3 (or R2 by policy), execution is paused with status `BLOCKED_ON_HITL`.
4. An approval card is broadcast to the PWA Cockpit and Bifrost Bridge.
5. The operator clicks Allow or Deny, unlocking or aborting the milestone.
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("camelot.permission_broker")


class RiskTier(str, Enum):
    R0_SAFE = "R0_SAFE"
    R1_LOW = "R1_LOW"
    R2_MEDIUM = "R2_MEDIUM"
    R3_HIGH = "R3_HIGH"
    R4_CRITICAL = "R4_CRITICAL"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    AUTO_APPROVED = "AUTO_APPROVED"
    TIMED_OUT = "TIMED_OUT"


@dataclass
class PermissionRequest:
    request_id: str
    worker_id: str
    knight_id: str
    operation_type: str  # "SHELL_EXEC", "VFS_WRITE", "FILE_MUTATION", "GIT_ACTION", "NETWORK_EGRESS"
    target: str
    summary: str
    details: Dict[str, Any]
    risk_tier: str
    status: str = RequestStatus.PENDING.value
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None
    decision_reason: Optional[str] = None
    signature: str = ""

    def __post_init__(self):
        if not self.signature:
            raw = f"{self.request_id}:{self.worker_id}:{self.operation_type}:{self.target}:{self.created_at}"
            self.signature = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PermissionBroker:
    """Manages evaluation and interactive approval of sandboxed operations."""

    def __init__(self, persistence_file: Optional[Path] = None, auto_approve_threshold: RiskTier = RiskTier.R1_LOW):
        self.auto_approve_threshold = auto_approve_threshold
        camelot_root = Path(__file__).resolve().parent.parent.parent.parent
        self.persistence_file = persistence_file or (
            camelot_root / "03_VAULT" / "runtime_state" / "workers" / "permission_requests.json"
        )
        self._requests: Dict[str, PermissionRequest] = {}
        self._load()

    def _load(self) -> None:
        if self.persistence_file.exists():
            try:
                data = json.loads(self.persistence_file.read_text(encoding="utf-8"))
                for req_dict in data.get("requests", []):
                    req = PermissionRequest(**req_dict)
                    self._requests[req.request_id] = req
            except Exception as e:
                LOG.warning("Failed to load permission requests: %s", e)

    def _save(self) -> None:
        self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "camelot-permission-broker/1",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "requests": [req.to_dict() for req in self._requests.values()]
        }
        self.persistence_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def assess_risk(self, operation_type: str, target: str, details: Dict[str, Any]) -> RiskTier:
        """Classify operation risk tier according to Camelot Iron Gate rules."""
        target_lower = target.lower()

        # Critical: Kernel, infrastructure, crypto keys, admin
        if any(k in target_lower for k in ["01_kernel", "systemd", "id_rsa", "secret", "token", "password"]):
            return RiskTier.R4_CRITICAL
        if operation_type == "SHELL_EXEC" and any(cmd in target_lower for cmd in ["sudo", "rm -rf", "format", "dd"]):
            return RiskTier.R4_CRITICAL

        # High: Writes > 10 lines, git commit/push, npm install, external net egress
        lines_changed = details.get("lines_count", 0)
        if operation_type in ("VFS_WRITE", "FILE_MUTATION") and lines_changed > 10:
            return RiskTier.R3_HIGH
        if operation_type == "GIT_ACTION" and any(act in target_lower for act in ["push", "merge", "rebase", "reset"]):
            return RiskTier.R3_HIGH
        if operation_type == "SHELL_EXEC" and any(cmd in target_lower for cmd in ["pip install", "npm install", "cargo build"]):
            return RiskTier.R3_HIGH
        if operation_type == "NETWORK_EGRESS":
            domain = details.get("domain", "")
            if domain not in ["github.com", "pypi.org", "registry.npmjs.org"]:
                return RiskTier.R3_HIGH

        # Medium: Small file mutations, git status/diff, local tests
        if operation_type in ("VFS_WRITE", "FILE_MUTATION") and lines_changed <= 10:
            return RiskTier.R2_MEDIUM
        if operation_type == "SHELL_EXEC" and any(cmd in target_lower for cmd in ["pytest", "npm test", "cargo test", "git status"]):
            return RiskTier.R2_MEDIUM

        # Low / Safe: read operations
        if operation_type in ("VFS_READ", "FILE_READ", "METRICS_QUERY"):
            return RiskTier.R0_SAFE

        return RiskTier.R2_MEDIUM

    def request_permission(
        self,
        worker_id: str,
        knight_id: str,
        operation_type: str,
        target: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None
    ) -> PermissionRequest:
        """Evaluate an operation and record a permission request."""
        op_details = details or {}
        risk = self.assess_risk(operation_type, target, op_details)
        req_id = f"PR-{uuid.uuid4().hex[:8].upper()}"

        req = PermissionRequest(
            request_id=req_id,
            worker_id=worker_id,
            knight_id=knight_id,
            operation_type=operation_type,
            target=target,
            summary=summary,
            details=op_details,
            risk_tier=risk.value
        )

        # Auto-approve if risk is at or below threshold
        risk_levels = [RiskTier.R0_SAFE, RiskTier.R1_LOW, RiskTier.R2_MEDIUM, RiskTier.R3_HIGH, RiskTier.R4_CRITICAL]
        req_idx = risk_levels.index(risk)
        threshold_idx = risk_levels.index(self.auto_approve_threshold)

        if req_idx <= threshold_idx:
            req.status = RequestStatus.AUTO_APPROVED.value
            req.decided_by = "POLICY_AUTO_GATE"
            req.decided_at = datetime.now(timezone.utc).isoformat()
            req.decision_reason = f"Risk tier {risk.value} is within auto-approve threshold ({self.auto_approve_threshold.value})"
            LOG.info("[BROKER] Auto-approved %s (%s)", req_id, summary)
        else:
            req.status = RequestStatus.PENDING.value
            LOG.warning("[BROKER] HITL approval required for %s: %s [Risk: %s]", req_id, summary, risk.value)

        self._requests[req_id] = req
        self._save()
        return req

    def approve(self, request_id: str, operator_id: str = "Arthur_Omega", reason: str = "Approved by operator") -> bool:
        """Operator explicitly approves an operation."""
        req = self._requests.get(request_id)
        if not req:
            raise KeyError(f"Permission request {request_id} not found")
        if req.status != RequestStatus.PENDING.value:
            return False

        req.status = RequestStatus.APPROVED.value
        req.decided_by = operator_id
        req.decided_at = datetime.now(timezone.utc).isoformat()
        req.decision_reason = reason
        self._save()
        LOG.info("[BROKER] Approved %s by %s: %s", request_id, operator_id, reason)
        return True

    def deny(self, request_id: str, operator_id: str = "Arthur_Omega", reason: str = "Rejected by operator") -> bool:
        """Operator explicitly denies an operation."""
        req = self._requests.get(request_id)
        if not req:
            raise KeyError(f"Permission request {request_id} not found")
        if req.status != RequestStatus.PENDING.value:
            return False

        req.status = RequestStatus.DENIED.value
        req.decided_by = operator_id
        req.decided_at = datetime.now(timezone.utc).isoformat()
        req.decision_reason = reason
        self._save()
        LOG.warning("[BROKER] Denied %s by %s: %s", request_id, operator_id, reason)
        return True

    def get_request(self, request_id: str) -> Optional[PermissionRequest]:
        return self._requests.get(request_id)

    def list_pending(self, worker_id: Optional[str] = None) -> List[PermissionRequest]:
        pending = [
            req for req in self._requests.values()
            if req.status == RequestStatus.PENDING.value
        ]
        if worker_id:
            pending = [req for req in pending if req.worker_id == worker_id]
        return sorted(pending, key=lambda x: x.created_at, reverse=True)

    def list_all(self, limit: int = 50) -> List[PermissionRequest]:
        return sorted(self._requests.values(), key=lambda x: x.created_at, reverse=True)[:limit]
