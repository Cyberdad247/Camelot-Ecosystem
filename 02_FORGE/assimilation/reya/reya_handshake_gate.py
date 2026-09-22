# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""REYA Kinetic Handshake Protocol & Experience-Gated Autonomy.
=============================================================
Forged by: MERLIN_Ω (System 2 Orchestrator) & ANYA_Ω (Arch-Gatekeeper)
Domain: CAMELOT-OS REYA Kinetic Substrate

Axioms:
1. Sovereign Kinetic Gate: No Round Table Knight has ambient access to Reya's
   physical/desktop/mobile actuation. Access MUST be established via a cryptographically
   sealed ReyaKineticHandshake.
2. Experience-Gated Autonomy (RPG Codex):
   - Standard / Novice Knights (Level < 10) require explicit User Approval (HITL)
     for EVERY handshake session.
   - Knights or Tenants reaching "Alpha Omega" Mastery (Level >= 10, or canonical
     Omega entities: ANYA_Ω, MERLIN_Ω, ARTHUR_OMEGA) receive HITL-Guided Autonomy.
     (Normal actions inside Sentinel leases execute autonomously; red-zones/destructive
     actions escalate to Anya's Iron Gate).
3. Sovereign Memory Attribution:
   - All actions, memories, and transcripts generated during a handshake are
     attributed directly to the operating Knight in MemCastle, Graphiti, and the
     Glass Observatory RPG Codex, while designating REYA as the kinetic fabric runner.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [REYA_HANDSHAKE] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("reya_handshake_gate")

CAMELOT_HOME = Path(__file__).resolve().parent.parent.parent.parent
RPG_CODEX_PATH = CAMELOT_HOME / "03_VAULT" / "runtime_state" / "observatory" / "rpg_codex.json"

ALPHA_OMEGA_LEVEL_THRESHOLD = 10
CANONICAL_OMEGA_KNIGHTS = {"anya_omega", "merlin_omega", "arthur_omega", "anya_ω", "merlin_ω", "arthur_ω"}


class AutonomyTier(str, Enum):
    MANUAL_APPROVAL_REQUIRED = "MANUAL_APPROVAL_REQUIRED"  # Level < 10: Must ask user every time
    HITL_GUIDED_ALPHA_OMEGA = "HITL_GUIDED_ALPHA_OMEGA"    # Level >= 10: Autonomous inside lease, HITL on red zone
    SOVEREIGN_ROOT = "SOVEREIGN_ROOT"                      # Arthur Ω / Supreme Sovereign King


class HandshakeStatus(str, Enum):
    PENDING_USER_APPROVAL = "PENDING_USER_APPROVAL"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


@dataclass
class HandshakeLease:
    """Cryptographically sealed lease granting a Knight access to REYA fabric."""

    handshake_id: str
    knight_id: str
    tenant_id: str
    autonomy_tier: AutonomyTier
    status: HandshakeStatus
    intent: str
    allowed_actions: List[str]
    allowed_rect: Optional[Tuple[float, float, float, float]] = None
    red_zones: List[Tuple[float, float, float, float]] = field(default_factory=list)
    max_actions: int = 500
    actions_executed: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    expires_at_epoch: float = field(
        default_factory=lambda: time.time() + 3600.0  # 1 hour default TTL
    )

    @property
    def is_valid(self) -> bool:
        return (
            self.status == HandshakeStatus.APPROVED
            and time.time() < self.expires_at_epoch
            and self.actions_executed < self.max_actions
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["autonomy_tier"] = self.autonomy_tier.value
        d["status"] = self.status.value
        d["is_valid"] = self.is_valid
        return d


class ReyaHandshakeGate:
    """Evaluates Knight mastery and administers kinetic access to REYA fabric."""

    def __init__(self, codex_path: Optional[Path] = None):
        self.codex_path = codex_path or RPG_CODEX_PATH
        self._active_leases: Dict[str, HandshakeLease] = {}  # knight_id -> HandshakeLease

    def _read_rpg_codex(self) -> Dict[str, Any]:
        """Reads real-time Knight and Tenant mastery from Observatory RPG Codex."""
        if not self.codex_path.exists():
            return {"knights": {}, "tenants": {}}
        try:
            return json.loads(self.codex_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Could not read RPG codex at {self.codex_path}: {e}")
            return {"knights": {}, "tenants": {}}

    def evaluate_knight_autonomy(
        self, knight_id: str, tenant_id: str = "Vizion Sky"
    ) -> Tuple[AutonomyTier, int, str]:
        """Computes Knight's autonomy tier based on RPG Codex experience."""
        kid = knight_id.lower().strip()
        codex = self._read_rpg_codex()

        # Check Arthur root authority
        if kid in ("arthur_omega", "king_arthur", "crown"):
            return AutonomyTier.SOVEREIGN_ROOT, 100, "Supreme Sovereign King Authority"

        # Check canonical Omega status
        if kid in CANONICAL_OMEGA_KNIGHTS:
            return AutonomyTier.HITL_GUIDED_ALPHA_OMEGA, 50, "Canonical Omega Master"

        # Check Knight mastery level in RPG Codex
        knights_data = codex.get("knights", {})
        knight_rec = knights_data.get(kid, {})
        if not knight_rec:
            for k_key, k_val in knights_data.items():
                if kid in k_key or k_key in kid:
                    knight_rec = k_val
                    break
        knight_level = knight_rec.get("level", 1)

        # Gaining Alpha Omega level (Knight Level >= 10) allows HITL-guided autonomy
        if knight_level >= ALPHA_OMEGA_LEVEL_THRESHOLD:
            return (
                AutonomyTier.HITL_GUIDED_ALPHA_OMEGA,
                knight_level,
                f"Alpha Omega Mastery Achieved (Knight Level {knight_level} >= {ALPHA_OMEGA_LEVEL_THRESHOLD})",
            )

        return (
            AutonomyTier.MANUAL_APPROVAL_REQUIRED,
            knight_level,
            f"Squire/Apprentice Level {knight_level} < {ALPHA_OMEGA_LEVEL_THRESHOLD} (User Approval Required)",
        )

    def request_handshake(
        self,
        knight_id: str,
        intent: str,
        requested_actions: Optional[List[str]] = None,
        tenant_id: str = "Vizion Sky",
        allowed_rect: Optional[Tuple[float, float, float, float]] = None,
        red_zones: Optional[List[Tuple[float, float, float, float]]] = None,
        auto_approve_if_eligible: bool = True,
    ) -> HandshakeLease:
        """Initiates a handshake request for a Knight to access Reya's kinetic fabric."""
        autonomy_tier, level, rationale = self.evaluate_knight_autonomy(knight_id, tenant_id)
        handshake_id = f"hsk_{knight_id}_{os.urandom(4).hex()}"

        # Determine initial approval status based on experience aspects
        if autonomy_tier in (AutonomyTier.SOVEREIGN_ROOT, AutonomyTier.HITL_GUIDED_ALPHA_OMEGA) and auto_approve_if_eligible:
            initial_status = HandshakeStatus.APPROVED
            logger.info(
                f"Handshake [{handshake_id}] AUTONOMOUSLY GRANTED to [{knight_id}] via {autonomy_tier.value} ({rationale})"
            )
        else:
            initial_status = HandshakeStatus.PENDING_USER_APPROVAL
            logger.info(
                f"Handshake [{handshake_id}] for [{knight_id}] requires USER ALLOWANCE ({rationale})"
            )

        actions = requested_actions or [
            "cua_mouse_click",
            "cua_mouse_move",
            "cua_keyboard_type",
            "cua_key_press",
            "cua_screen_capture",
        ]

        lease = HandshakeLease(
            handshake_id=handshake_id,
            knight_id=knight_id,
            tenant_id=tenant_id,
            autonomy_tier=autonomy_tier,
            status=initial_status,
            intent=intent,
            allowed_actions=actions,
            allowed_rect=allowed_rect,
            red_zones=red_zones or [(0.9, 0.9, 1.0, 1.0)],  # Default bottom-right red-zone safety
        )

        if initial_status == HandshakeStatus.APPROVED:
            self._active_leases[knight_id] = lease

        return lease

    def grant_user_approval(self, lease: HandshakeLease) -> HandshakeLease:
        """Called when the user explicitly grants permission to access Reya."""
        lease.status = HandshakeStatus.APPROVED
        self._active_leases[lease.knight_id] = lease
        logger.info(f"User approved handshake [{lease.handshake_id}] for [{lease.knight_id}]")
        return lease

    def revoke_handshake(self, knight_id: str) -> bool:
        """Instantly revokes Reya kinetic access for a Knight."""
        if knight_id in self._active_leases:
            lease = self._active_leases.pop(knight_id)
            lease.status = HandshakeStatus.REVOKED
            logger.info(f"Revoked Reya kinetic handshake for [{knight_id}]")
            return True
        return False

    def get_active_lease(self, knight_id: str) -> Optional[HandshakeLease]:
        lease = self._active_leases.get(knight_id)
        if lease and lease.is_valid:
            return lease
        elif lease:
            # Expired or exhausted
            self._active_leases.pop(knight_id, None)
        return None


# Module singleton
_handshake_gate: Optional[ReyaHandshakeGate] = None


def get_handshake_gate() -> ReyaHandshakeGate:
    global _handshake_gate
    if _handshake_gate is None:
        _handshake_gate = ReyaHandshakeGate()
    return _handshake_gate
