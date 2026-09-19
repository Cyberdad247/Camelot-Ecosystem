# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Recommendations & Sir Arthur Scarcity Governance Test Suite

from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "control_plane"))
sys.path.insert(0, str(REPO_ROOT / "vfs"))


def test_redis_persistence_and_snapshot_creation(tmp_path):
    """Verify Redis L1 hot cache persistence, snapshot creation, and restoration."""
    from control_plane.infra.redis_persistence import RedisPersistenceManager

    mgr = RedisPersistenceManager(snapshot_dir=tmp_path)
    mgr.set_key("working_context:turn_1", {"agent": "sir_sonus", "intent": "voice_route"})
    mgr.set_key("working_context:turn_2", {"agent": "sir_hermes", "intent": "bifrost_dispatch"})

    assert mgr.get_key("working_context:turn_1")["agent"] == "sir_sonus"

    # Create atomic snapshot
    snap_meta = mgr.create_snapshot(trigger_reason="unit_test")
    assert snap_meta.key_count == 2
    assert snap_meta.persistence_mode == "AOF_HYBRID"
    assert (tmp_path / f"{snap_meta.snapshot_id}.json").exists()
    assert (tmp_path / "latest_snapshot.json").exists()

    # Test restoration
    new_mgr = RedisPersistenceManager(snapshot_dir=tmp_path)
    restored_count = new_mgr.restore_from_latest()
    assert restored_count == 2
    assert new_mgr.get_key("working_context:turn_2")["agent"] == "sir_hermes"


def test_symbolect_decompiler_and_visualizer():
    """Verify Dirac bra-ket Symbolect decompiler, token reduction metrics, and ASCII visualization."""
    from scripts.symbolect_transpiler import SymbolectDecompiler

    expression = "|🧠⊗(⚡💬)⟩ ⟨Omega: AUTH ⊗ SYNC ⊗ NOTEBOOKLM ⊗ REDIS⟩"
    decomp = SymbolectDecompiler.decompile(expression)

    assert decomp["status"] == "DECOMPILED_TRANSPARENT"
    assert len(decomp["detected_glyphs"]) == 3
    assert len(decomp["anchor_tokens"]) == 4
    assert "token_metrics" in decomp
    assert float(decomp["token_metrics"]["token_reduction_pct"].replace("%", "")) > 70.0
    assert "COGNITION" in [g["category"] for g in decomp["detected_glyphs"]]

    viz = SymbolectDecompiler.visualize(expression)
    assert "CAMELOT-OS SYMBOLECT DECOMPILER" in viz
    assert "token savings" in viz


def test_sir_arthur_scarcity_governor_role_and_character_sheet():
    """Verify Sir Arthur's World Tree promotion to VPS Scarcity Governor."""
    sheets_path = REPO_ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
    with open(sheets_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "SIR_ARTHUR" in data["knights"]
    arthur = data["knights"]["SIR_ARTHUR"]
    assert arthur["role"] == "VPS Scarcity Governor, 256MB RSS Ceiling Enforcer, Nano-Squire High Command"
    assert arthur["cloudbrain_uuid"] == "a0a4bfb9-e847-4c38-be39-7aee398f0795", "Sir Arthur anchored to World Tree Root"
    assert len(arthur["responsibilities"]) == 4
    assert any("256MB RSS" in r for r in arthur["responsibilities"])

    # Verify vps_fallback_governing_law
    from control_plane.dispatch.vps_fallback_governing_law import GOVERNING_KNIGHT, GOVERNOR_TITLE
    assert GOVERNING_KNIGHT == "SIR_ARTHUR"
    assert "Scarcity Governor" in GOVERNOR_TITLE


def test_merlin_forge_nano_squire_and_reporting_chain():
    """Verify Merlin Omega //FORGE runic symbolect workflow and nano-squire hierarchical escalation."""
    from control_plane.runes.runic_router import route_rune
    from control_plane.infra.nano_squire_forge import nano_squire_forge

    # 1. Dispatch //FORGE_SQUIRE via runic router
    res = route_rune("//FORGE_SQUIRE", "node=fleet type=scarcity_sentry")
    assert res.knight == "merlin_omega"
    assert res.metadata["forge_master"] == "MERLIN_OMEGA"
    assert res.metadata["governor_commander"] == "SIR_ARTHUR"
    assert res.metadata["sovereign_recipient"] == "KING_ARTHUR_VIZION"
    assert "|🧙‍♂️⚒️(🛡️⚡)⟩" in res.metadata["symbolect_expression"]
    assert len(res.metadata["squires_deployed"]) >= 6, "Must forge nano-squires across all fleet nodes"

    # 2. Test Hierarchical Reporting Chain: NanoSquire -> Sir Arthur -> King Arthur / Sovereign
    fleet_squires = list(nano_squire_forge.squires.values())
    assert len(fleet_squires) >= 6
    sample_squire = fleet_squires[0]

    # Test Nominal Vitals (<256MB)
    rep_normal = nano_squire_forge.report_node_vitals(sample_squire.squire_id, current_rss_mb=45.0)
    assert rep_normal.commander == "SIR_ARTHUR"
    assert rep_normal.sovereign == "KING_ARTHUR_VIZION"
    assert rep_normal.scarcity_status == "NORMAL_OPTIMAL"
    assert rep_normal.delivered_to_sovereign is True

    # Test Scarcity Violation (>256MB)
    rep_breach = nano_squire_forge.report_node_vitals(sample_squire.squire_id, current_rss_mb=285.0)
    assert rep_breach.scarcity_status == "CRITICAL_EVICTION"
    assert "SIR ARTHUR ALERT" in rep_breach.governor_assessment
    assert "exceeds 256MB hard ceiling" in rep_breach.governor_assessment
    assert rep_breach.delivered_to_sovereign is True


def test_runic_scarcity_gov_command():
    """Verify //SCARCITY_GOV evaluates node scarcity status under Sir Arthur."""
    from control_plane.runes.runic_router import route_rune

    res = route_rune("//SCARCITY_GOV", "health_probe")
    assert res.knight == "sir_arthur"
    assert res.metadata["governor"] == "SIR_ARTHUR"
    assert res.metadata["rss_ceiling_mb"] == 256.0
    assert res.metadata["evaluation"]["allowed"] is True
    assert res.metadata["managed_squires_count"] >= 6
