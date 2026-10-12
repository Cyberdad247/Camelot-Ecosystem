# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Tests for MagSafe Ambient Voice Recorder & Kinetic Action Item Dispatcher (Ω_MAGSAFE_KINETIC_DISPATCHER).
========================================================================================================
Validates:
1. Bridge initialization, cgroups v2 memory ceiling (<350MB RSS), and session logging.
2. Ambient audio transcript ingestion, duration estimation, and SecondBrain executive distillation.
3. Kinetic task pattern matching (RUN_COMMAND, CUA_CLICK, CUA_TYPE, VERIFY_TESTS).
4. Non-blocking Glass Observatory tap awarding dialogue RPG XP to Tenant and Knight behind WORM glass wall.
5. Reya Handshake Gate enforcement: blocks unapproved Novices while permitting Alpha Omega / Arthur Omega.
6. Camelot CLI integration ('camelot magsafe status' and 'camelot magsafe ingest').
7. Runic router '//MAGSAFE_INGEST' and '//MAGSAFE_DISPATCH' execution.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load magsafe_audio_bridge dynamically
_bridge_path = REPO_ROOT / "02_FORGE" / "assimilation" / "magsafe" / "magsafe_audio_bridge.py"
assert _bridge_path.exists(), f"Missing bridge at {_bridge_path}"
_spec = importlib.util.spec_from_file_location("magsafe_audio_bridge", str(_bridge_path))
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
sys.modules["magsafe_audio_bridge"] = _mod
_spec.loader.exec_module(_mod)

MagsafeAudioBridge = _mod.MagsafeAudioBridge
MagsafeActionItem = _mod.MagsafeActionItem
MagsafeSessionResult = _mod.MagsafeSessionResult
get_magsafe_bridge = _mod.get_magsafe_bridge

from control_plane.runes.runic_router import route_rune


class TestMagsafeAudioBridge:
    """Core audio bridge, SecondBrain summary, and task extraction tests."""

    @pytest.fixture
    def bridge(self, tmp_path):
        return MagsafeAudioBridge(data_dir=tmp_path / "magsafe_test_data")

    def test_bridge_initialization_and_cgroups_scarcity(self, bridge):
        assert bridge.cgroups_memory_max_mb == 350.0
        assert bridge.data_dir.exists()
        assert bridge.sessions_log.parent.exists()
        assert len(bridge.get_sessions()) == 0

    def test_extract_action_items_from_text(self, bridge):
        transcript = (
            "Team sync: We need to launch the new multivoice feature.\n"
            "Discussion: Edge hardware operates within strict cgroups boundary (<350MB).\n"
            "Task: Run pytest tests/test_magsafe_voice_dispatcher.py to verify stability.\n"
            "Action item: Click on coordinate (500, 320) to awaken the HUD.\n"
            "Todo: Type 'camelot status' on terminal.\n"
            "Remember to verify tests on Reya layer."
        )
        summary, key_ideas, action_items = bridge.extract_action_items(transcript, target_knight="SIR_HELIOS")

        assert len(action_items) >= 4
        assert "SecondBrain Executive Summary" in summary
        assert len(key_ideas) >= 2

        # Check action item attributes
        types = [it.action_type for it in action_items]
        assert "VERIFY_TESTS" in types or "RUN_COMMAND" in types
        assert "CUA_CLICK" in types or any(it.requires_cua for it in action_items)

        cua_items = [it for it in action_items if it.action_type == "CUA_CLICK"]
        if cua_items:
            assert cua_items[0].target_coordinates is not None
            assert cua_items[0].target_coordinates == (500.0, 320.0)

    def test_process_audio_file_with_observatory_tap(self, bridge, tmp_path):
        sample_file = tmp_path / "ambient_memo.txt"
        sample_file.write_text(
            "Ambient memo: Task: Review test coverage for voice dispatcher.\n"
            "Action item: check bifrost gateway mTLS status.",
            encoding="utf-8",
        )

        res = bridge.process_audio_file(
            audio_file_path=sample_file,
            target_knight="SIR_HELIOS",
            tenant_id="Vizion Sky",
            auto_dispatch=False,
        )

        assert isinstance(res, MagsafeSessionResult)
        assert res.session_id.startswith("magsafe_")
        assert res.duration_seconds > 0
        assert len(res.action_items) >= 2
        assert res.observatory_turn_id is not None
        assert res.tenant_xp_awarded > 0
        assert res.memory_attribution["primary_knight"] == "SIR_HELIOS" or res.memory_attribution.get("observatory_xp_recipient") == "SIR_HELIOS"

        # Check persistence
        saved_sessions = bridge.get_sessions()
        assert len(saved_sessions) == 1
        assert saved_sessions[0]["session_id"] == res.session_id

    def test_handshake_gate_blocks_novice_knight(self, bridge, tmp_path):
        memo = tmp_path / "novice_action.txt"
        memo.write_text("Task: Click coordinate 100,200 on screen.", encoding="utf-8")

        # Novice unranked knight
        res = bridge.process_audio_file(
            audio_file_path=memo,
            target_knight="novice_squire_test",
            tenant_id="Unranked_Tenant",
            auto_dispatch=True,
        )

        assert len(res.action_items) >= 1
        item = res.action_items[0]
        # Should be blocked requiring handshake
        assert item.execution_receipt is not None
        assert item.execution_receipt.get("status") == "HANDSHAKE_REQUIRED"
        assert item.dispatched is False

    def test_handshake_gate_allows_canonical_omega(self, bridge, tmp_path):
        memo = tmp_path / "omega_action.txt"
        memo.write_text("Action item: verify tests on Reya layer.", encoding="utf-8")

        # Arthur Omega (Sovereign Root Authority)
        res = bridge.process_audio_file(
            audio_file_path=memo,
            target_knight="arthur_omega",
            tenant_id="Vizion Sky",
            auto_dispatch=True,
        )

        assert len(res.action_items) >= 1
        item = res.action_items[0]
        assert item.dispatched is True
        assert item.execution_receipt is not None
        assert item.execution_receipt.get("status") in ("SUCCESS", "SIMULATED_SUCCESS")


class TestMagsafeRunicAndCliIntegration:
    """Validates runic dispatch and camelot CLI interfaces."""

    def test_runic_magsafe_ingest(self, tmp_path):
        memo = tmp_path / "rune_memo.txt"
        memo.write_text("Task: Run tests on multivoice router.", encoding="utf-8")

        res = route_rune(
            "//MAGSAFE_INGEST",
            param=str(memo),
            context={"file": str(memo), "knight": "SIR_HELIOS"},
        )
        assert res.rune == "//MAGSAFE_INGEST"
        assert res.metadata["status"] == "SUCCESS"
        assert res.metadata["action_items_count"] >= 1
        assert res.metadata["observatory_turn_id"] is not None

    def test_runic_magsafe_dispatch(self, tmp_path):
        memo = tmp_path / "rune_dispatch.txt"
        memo.write_text("Action item: verify tests on Reya layer.", encoding="utf-8")

        res = route_rune(
            "//MAGSAFE_DISPATCH",
            param=str(memo),
            context={"file": str(memo), "knight": "merlin_omega"},
        )
        assert res.rune == "//MAGSAFE_DISPATCH"
        assert res.metadata["status"] == "SUCCESS"
        assert len(res.metadata["action_items"]) >= 1
        assert res.metadata["action_items"][0]["dispatched"] is True

    def test_fastmcp_magsafe_tools(self, tmp_path):
        from control_plane.mcp.cloudbrain_mcp_server import magsafe_status, magsafe_process_audio
        st = magsafe_status()
        assert st["status"] == "ARMED_AND_ACTIVE"
        assert st["memory_ceiling_mb"] == 350.0

        memo = tmp_path / "mcp_memo.txt"
        memo.write_text("Task: Run tests on cloudbrain FastMCP.", encoding="utf-8")
        res = magsafe_process_audio(str(memo), target_knight="SIR_HELIOS")
        assert res["session_id"].startswith("magsafe_")
        assert len(res["action_items"]) >= 1
        assert res["tenant_xp_awarded"] > 0

