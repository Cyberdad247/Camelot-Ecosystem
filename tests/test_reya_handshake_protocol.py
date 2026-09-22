# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Tests for REYA Kinetic Handshake Protocol & Experience-Gated Autonomy.
========================================================================
Validates:
1. Autonomy Tier evaluation based on RPG Codex experience (Alpha Omega threshold).
2. Mandatory user approval for novice Knights before kinetic execution.
3. HITL-guided autonomous clearance for Alpha Omega entities.
4. Sovereign dual-attribution & memory routing (MemCastle, Graphiti, RPG XP).
5. Dynamic revocation and lease expiry.
6. Runic router //REYA_HANDSHAKE dispatch.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load reya_handshake_gate
_hsk_path = REPO_ROOT / "02_FORGE" / "assimilation" / "reya" / "reya_handshake_gate.py"
_hsk_spec = importlib.util.spec_from_file_location("reya_handshake_gate", str(_hsk_path))
assert _hsk_spec is not None and _hsk_spec.loader is not None
_hsk_mod = importlib.util.module_from_spec(_hsk_spec)
sys.modules["reya_handshake_gate"] = _hsk_mod
_hsk_spec.loader.exec_module(_hsk_mod)

ReyaHandshakeGate = _hsk_mod.ReyaHandshakeGate
HandshakeLease = _hsk_mod.HandshakeLease
HandshakeStatus = _hsk_mod.HandshakeStatus
AutonomyTier = _hsk_mod.AutonomyTier
get_handshake_gate = _hsk_mod.get_handshake_gate

# Load reya_fabric_layer
_reya_path = REPO_ROOT / "02_FORGE" / "assimilation" / "reya" / "reya_fabric_layer.py"
_reya_spec = importlib.util.spec_from_file_location("reya_fabric_layer", str(_reya_path))
assert _reya_spec is not None and _reya_spec.loader is not None
_reya_mod = importlib.util.module_from_spec(_reya_spec)
sys.modules["reya_fabric_layer"] = _reya_mod
_reya_spec.loader.exec_module(_reya_mod)

ReyaUniversalFabric = _reya_mod.ReyaUniversalFabric
get_reya_fabric = _reya_mod.get_reya_fabric

from control_plane.runes.runic_router import route_rune


class TestReyaHandshakeGate:
    def test_evaluate_novice_knight_requires_approval(self):
        gate = ReyaHandshakeGate()
        # Test a hypothetical novice knight (Level 1)
        tier, level, rationale = gate.evaluate_knight_autonomy("novice_squire", tenant_id="Unranked_Tenant")
        assert tier == AutonomyTier.MANUAL_APPROVAL_REQUIRED
        assert "User Approval Required" in rationale

    def test_evaluate_canonical_omega_knights(self):
        gate = ReyaHandshakeGate()
        # Merlin Omega
        tier, level, rationale = gate.evaluate_knight_autonomy("merlin_omega")
        assert tier == AutonomyTier.HITL_GUIDED_ALPHA_OMEGA
        assert "Canonical Omega Master" in rationale

        # Arthur Omega
        tier_a, level_a, rat_a = gate.evaluate_knight_autonomy("arthur_omega")
        assert tier_a == AutonomyTier.SOVEREIGN_ROOT
        assert "Supreme Sovereign" in rat_a

    def test_request_handshake_requires_user_approval(self):
        gate = ReyaHandshakeGate()
        # Request for a standard Knight with low level
        lease = gate.request_handshake(
            "apprentice_knight",
            intent="Test UI click",
            tenant_id="Unranked_Tenant",
            auto_approve_if_eligible=True,
        )
        assert lease.status == HandshakeStatus.PENDING_USER_APPROVAL
        assert lease.is_valid is False

        # Grant user approval
        approved = gate.grant_user_approval(lease)
        assert approved.status == HandshakeStatus.APPROVED
        assert approved.is_valid is True
        assert gate.get_active_lease("apprentice_knight") is approved

    def test_revoke_handshake(self):
        gate = ReyaHandshakeGate()
        lease = gate.request_handshake(
            "temp_knight",
            intent="Temp run",
            auto_approve_if_eligible=True,
        )
        gate.grant_user_approval(lease)
        assert gate.get_active_lease("temp_knight") is not None

        revoked = gate.revoke_handshake("temp_knight")
        assert revoked is True
        assert gate.get_active_lease("temp_knight") is None


class TestReyaFabricHandshakeProtocol:
    def test_novice_knight_blocked_without_handshake(self):
        fabric = ReyaUniversalFabric()
        fabric.switch_knight("boris")
        fabric.revoke_kinetic_handshake("sir_boris")

        res = fabric.execute_fabric_action("cua_mouse_click", {"norm_x": 0.5, "norm_y": 0.5})
        assert res["status"] == "HANDSHAKE_REQUIRED"
        assert res["error"] == "KINETIC_HANDSHAKE_REQUIRED"
        assert "handshake_prompt" in res

    def test_novice_knight_succeeds_with_user_approval(self):
        fabric = ReyaUniversalFabric()
        fabric.switch_knight("boris")
        # Explicit user grant
        fabric.grant_kinetic_handshake("sir_boris")

        res = fabric.execute_fabric_action("cua_mouse_click", {"norm_x": 0.5, "norm_y": 0.5})
        assert res["status"] == "SUCCESS"
        assert "attribution" in res
        attr = res["attribution"]
        assert attr["initiating_knight"] == "sir_boris"
        assert attr["speaking_name"] == "Sir Boris"
        assert attr["kinetic_fabric"] == "REYA_EDGE_FABRIC"
        assert attr["memory_routing"]["memcastle_partition"] == "SIR_BORIS"
        assert attr["memory_routing"]["graphiti_partition"] == "sir_boris_graphiti.db"

    def test_alpha_omega_knight_autonomously_executes(self):
        fabric = ReyaUniversalFabric()
        fabric.switch_knight("merlin")

        res = fabric.execute_fabric_action("cua_keyboard_type", {"text": "cargo test"})
        assert res["status"] == "SUCCESS"
        assert res["attribution"]["initiating_knight"] == "merlin_omega"
        assert res["attribution"]["handshake_status"] == "ALPHA_OMEGA_AUTONOMOUS"
        assert res["attribution"]["memory_routing"]["memcastle_partition"] == "MERLIN_OMEGA"


class TestRunicRouterHandshake:
    def test_route_rune_reya_handshake_inspect(self):
        res = route_rune("//REYA_HANDSHAKE", "inspect")
        assert res.rune == "//REYA_HANDSHAKE"
        assert res.metadata["action"] == "reya_handshake"
        assert res.metadata["status"] == "HANDSHAKE_EVALUATED"

    def test_route_rune_reya_handshake_grant(self):
        res = route_rune("//REYA_HANDSHAKE", "grant")
        assert res.rune == "//REYA_HANDSHAKE"
        assert res.metadata["status"] == "HANDSHAKE_GRANTED"
        assert res.metadata["lease"]["status"] == "APPROVED"
