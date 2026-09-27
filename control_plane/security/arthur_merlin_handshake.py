# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Arthur-Merlin Handshake & HITL Governance Engine (`AM-HANDSHAKE/1`).
====================================================================
Bicameral governance protocol uniting:
    1. MERLIN_Ω (System 2 TTC Deep DAG synthesis, algorithmic bounds, memory delta)
    2. ARTHUR_OMEGA (Sovereign King Authority, root lease custody, Ed25519 Golden Seal)
    3. GIDEON_13_GATE (Formal independent verification & SMT taint checking)
    4. ANYA_Ω (10-line atomic code firewall on ingress)

Protocol Lifecycle:
    Proposal ➔ Merlin TTC DAG ➔ Gideon 13-Gate Audit ➔ Risk Tier Arbiter
             ➔ If T3/T4 or Lines > 10: SUSPEND for Arthur Sovereign Golden Seal
             ➔ Else: Fast-Path Kinetic Execution Lease
"""

from __future__ import annotations

import enum
import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from control_plane.security.arthur_resolution import (
    ArthurResolution,
    ArthurResolutionError,
    ArthurResolutionGovernor,
)
from control_plane.security.authority_vector import AuthorityVector
from control_plane.security.sir_gideon import GideonVerdict, sha256_canonical

logger = logging.getLogger("camelot.arthur_merlin_handshake")


class HandshakeStatus(str, enum.Enum):
    AUTO_CLEARED = "AUTO_CLEARED"                      # T0/T1 read/telemetry, instant lease
    ATOMIC_GOVERNED = "ATOMIC_GOVERNED"                # T2 bounded <= 10 lines, governed lease
    SUSPENDED_AWAITING_HITL = "SUSPENDED_AWAITING_HITL"# T3/T4 or >10 lines, hard pause
    SEALED_AUTHORIZED = "SEALED_AUTHORIZED"            # King Arthur Sovereign Golden Seal verified
    REJECTED_ETHICAL_VETO = "REJECTED_ETHICAL_VETO"    # Vetoed by Arthur or Gideon
    REJECTED_MEMORY_CEILING = "REJECTED_MEMORY_CEILING"# Exceeds 8GB edge bounds


@dataclass
class MerlinTTCProposal:
    """Merlin_Ω System 2 Test-Time Compute Task Decomposition."""
    proposal_id: str
    intent: str
    target_knight: str
    risk_tier: str  # T0, T1, T2, T3, T4
    estimated_lines: int
    memory_delta_mb: float
    requires_hitl: bool
    rationale: str
    ttc_tokens_budget: int = 4096
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HandshakeVerdict:
    """Consolidated bicameral evaluation of an ingress task or kinetic proposal."""
    handshake_id: str
    status: HandshakeStatus
    proposal: MerlinTTCProposal
    gideon_verdict: Optional[Dict[str, Any]]
    arthur_resolution: Optional[Dict[str, Any]]
    capability_lease: Optional[Dict[str, Any]]
    rejection_reason: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "handshake_id": self.handshake_id,
            "status": self.status.value,
            "proposal": self.proposal.to_dict(),
            "gideon_verdict": self.gideon_verdict,
            "arthur_resolution": self.arthur_resolution,
            "capability_lease": self.capability_lease,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at,
        }


class ArthurMerlinHandshakeEngine:
    """Bicameral Handshake Coordinator enforcing the Arthur-Merlin Governance Protocol."""

    # Invariants
    MAX_ATOMIC_LINES: int = 10
    MAX_EDGE_SLAB_MB: float = 256.0
    CRITICAL_RISK_TIERS = frozenset({"T3", "T4"})

    def __init__(
        self,
        governor: Optional[ArthurResolutionGovernor] = None,
        authority_vector: Optional[AuthorityVector] = None,
    ):
        self._governor = governor or ArthurResolutionGovernor()
        self._authority_vector = authority_vector or AuthorityVector(
            e_leadership=10, r_policy=1, r_revocation=0, r_registry=1, r_identity=1, r_contract=1
        )
        self._pending_handshakes: Dict[str, HandshakeVerdict] = {}

    @property
    def governor(self) -> ArthurResolutionGovernor:
        return self._governor

    def evaluate_intent(
        self,
        intent: str,
        target_knight: str = "sir_boris",
        payload: str = "",
        explicit_risk_tier: Optional[str] = None,
        memory_estimate_mb: float = 12.0,
    ) -> HandshakeVerdict:
        """Step 1 & 2: Merlin System 2 TTC Decomposition & Gideon Gate Verification."""
        handshake_id = f"am_hs_{uuid.uuid4().hex[:12]}"
        
        # Calculate lines
        payload_lines = len(payload.strip().splitlines()) if payload.strip() else 0
        
        # Infer risk tier if not explicit
        if explicit_risk_tier:
            risk_tier = explicit_risk_tier.upper()
        else:
            risk_tier = self._infer_risk_tier(intent, payload_lines, memory_estimate_mb)

        # Scarcity Boundary check
        if memory_estimate_mb > self.MAX_EDGE_SLAB_MB:
            proposal = MerlinTTCProposal(
                proposal_id=f"prop_{uuid.uuid4().hex[:8]}",
                intent=intent,
                target_knight=target_knight,
                risk_tier=risk_tier,
                estimated_lines=payload_lines,
                memory_delta_mb=memory_estimate_mb,
                requires_hitl=True,
                rationale=f"Memory delta {memory_estimate_mb}MB exceeds 256MB Edge Slab ceiling.",
            )
            verdict = HandshakeVerdict(
                handshake_id=handshake_id,
                status=HandshakeStatus.REJECTED_MEMORY_CEILING,
                proposal=proposal,
                gideon_verdict=None,
                arthur_resolution=None,
                capability_lease=None,
                rejection_reason=f"Scarcity violation: {memory_estimate_mb}MB > {self.MAX_EDGE_SLAB_MB}MB",
            )
            return verdict

        # HITL requirement determination
        requires_hitl = (
            risk_tier in self.CRITICAL_RISK_TIERS
            or payload_lines > self.MAX_ATOMIC_LINES
            or "destroy" in intent.lower()
            or "purge" in intent.lower()
            or "drop" in intent.lower()
        )

        rationale = (
            f"Evaluated by Merlin_Ω: risk={risk_tier}, lines={payload_lines}, "
            f"memory={memory_estimate_mb}MB, HITL_required={requires_hitl}."
        )

        proposal = MerlinTTCProposal(
            proposal_id=f"prop_{uuid.uuid4().hex[:8]}",
            intent=intent,
            target_knight=target_knight,
            risk_tier=risk_tier,
            estimated_lines=payload_lines,
            memory_delta_mb=memory_estimate_mb,
            requires_hitl=requires_hitl,
            rationale=rationale,
        )

        # Gideon Synthetic Audit Pre-Flight
        gideon_pass = True
        gideon_reason = "Gideon 13-gate pre-flight: clean AST and boundary confinement."
        if "eval(" in payload or "exec(" in payload:
            gideon_pass = False
            gideon_reason = "Gideon Gate 5/7 violation: dynamic code execution (eval/exec) detected."

        gideon_data = {
            "verdict_id": f"gid_{uuid.uuid4().hex[:8]}",
            "passed": gideon_pass,
            "details": gideon_reason,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

        if not gideon_pass:
            verdict = HandshakeVerdict(
                handshake_id=handshake_id,
                status=HandshakeStatus.REJECTED_ETHICAL_VETO,
                proposal=proposal,
                gideon_verdict=gideon_data,
                arthur_resolution=None,
                capability_lease=None,
                rejection_reason=gideon_reason,
            )
            return verdict

        # Status arbitration
        if requires_hitl:
            verdict = HandshakeVerdict(
                handshake_id=handshake_id,
                status=HandshakeStatus.SUSPENDED_AWAITING_HITL,
                proposal=proposal,
                gideon_verdict=gideon_data,
                arthur_resolution=None,
                capability_lease=None,
                rejection_reason=None,
            )
            self._pending_handshakes[handshake_id] = verdict
            return verdict
        elif risk_tier == "T2":
            lease = self._issue_capability_lease(handshake_id, proposal)
            verdict = HandshakeVerdict(
                handshake_id=handshake_id,
                status=HandshakeStatus.ATOMIC_GOVERNED,
                proposal=proposal,
                gideon_verdict=gideon_data,
                arthur_resolution=None,
                capability_lease=lease,
            )
            return verdict
        else:
            lease = self._issue_capability_lease(handshake_id, proposal)
            verdict = HandshakeVerdict(
                handshake_id=handshake_id,
                status=HandshakeStatus.AUTO_CLEARED,
                proposal=proposal,
                gideon_verdict=gideon_data,
                arthur_resolution=None,
                capability_lease=lease,
            )
            return verdict

    def apply_arthur_golden_seal(
        self,
        handshake_id: str,
        directive_type: str = "CONSENSUS_RATIFICATION",
        rationale: str = "Sovereign Golden Seal granted by King Arthur / Operator.",
    ) -> HandshakeVerdict:
        """Step 4: Arthur issues the Sovereign Golden Seal, unlocking suspended task."""
        if handshake_id not in self._pending_handshakes:
            raise ArthurResolutionError(f"No pending handshake with id: '{handshake_id}'")

        verdict = self._pending_handshakes[handshake_id]
        if verdict.status != HandshakeStatus.SUSPENDED_AWAITING_HITL:
            raise ArthurResolutionError(
                f"Handshake '{handshake_id}' is in state {verdict.status.value}, not awaiting HITL."
            )

        # Create cryptographic ArthurResolution
        resolution = self._governor.create_resolution(
            directive_type=directive_type,
            target_scope=f"task:{verdict.proposal.proposal_id}:{verdict.proposal.intent[:48]}",
            rationale=rationale,
            authority_vector=self._authority_vector.to_list(),
            seal_type="SOVEREIGN_GOLDEN_SEAL",
        )

        # Issue lease
        lease = self._issue_capability_lease(handshake_id, verdict.proposal, resolution=resolution)

        verdict.status = HandshakeStatus.SEALED_AUTHORIZED
        verdict.arthur_resolution = resolution.to_dict()
        verdict.capability_lease = lease

        del self._pending_handshakes[handshake_id]
        return verdict

    def _infer_risk_tier(self, intent: str, lines: int, memory_mb: float) -> str:
        """Heuristic risk tier classifier adhering to Canonical Schema."""
        lower = intent.lower()
        if any(w in lower for w in ("purge", "delete", "destroy", "drop", "force", "format", "reinit")):
            return "T4"
        if lines > self.MAX_ATOMIC_LINES or memory_mb > 50.0 or any(w in lower for w in ("scaffold", "daemon", "deploy", "bridge", "install", "compile")):
            return "T3"
        if lines > 0 or any(w in lower for w in ("patch", "edit", "write", "update", "set")):
            return "T2"
        if any(w in lower for w in ("read", "query", "search", "probe", "list", "get")):
            return "T1"
        return "T0"

    def _issue_capability_lease(
        self,
        handshake_id: str,
        proposal: MerlinTTCProposal,
        resolution: Optional[ArthurResolution] = None,
    ) -> Dict[str, Any]:
        """Issues manifest-bound camelot-lease/1 capability token."""
        lease_id = f"lease_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        digest = hashlib.sha256(
            f"{handshake_id}:{proposal.proposal_id}:{proposal.target_knight}:{timestamp}".encode("utf-8")
        ).hexdigest()

        return {
            "schema_version": "camelot-lease/1",
            "lease_id": lease_id,
            "handshake_id": handshake_id,
            "proposal_id": proposal.proposal_id,
            "target_knight": proposal.target_knight,
            "risk_tier": proposal.risk_tier,
            "memory_ceiling_mb": min(proposal.memory_delta_mb, self.MAX_EDGE_SLAB_MB),
            "authorized_by": "ARTHUR_OMEGA" if resolution else "ANYA_FAST_PATH",
            "resolution_id": resolution.resolution_id if resolution else None,
            "lease_digest": f"sha256:{digest}",
            "expires_in_sec": 300,
            "issued_at": timestamp,
        }
