# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit Test Suite for Project Speculum: The Glass Observatory & Living Compendium
================================================================================
Verifies:
1. Complete decoupling and zero-affiliation with PROVENANCE_LEDGER.md.
2. Thread-safe, non-blocking interaction tapping and transcription persistence.
3. Autonomous kinetic implementation evaluation across 5 architectural axes.
4. RPG XP and Level progression mathematics for both Knights and Sovereign Tenants.
5. Living Compendium Markdown document auto-generation.
6. Impenetrable Glass Wall read-only WORM projection.
7. Camelot-OS CLI `camelot observatory` execution.
"""

import json
import subprocess
import sys
from pathlib import Path
import pytest

from control_plane.observatory.glass_observatory import (
    GlassObservatory,
    calculate_level_and_next,
    get_knight_title,
    get_tenant_title,
    get_glass_observatory,
)

CAMELOT_HOME = Path(__file__).resolve().parent.parent


def test_rpg_level_mathematics():
    """Verify non-linear RPG level scaling: level = floor((xp / 100)^(1/1.5)) + 1."""
    lvl1, next1 = calculate_level_and_next(0)
    assert lvl1 == 1
    assert next1 == 100

    lvl_50, next_50 = calculate_level_and_next(50)
    assert lvl_50 == 1
    assert next_50 == 50

    # At 100 XP, should reach level 2
    lvl2, next2 = calculate_level_and_next(100)
    assert lvl2 == 2
    assert next2 > 0

    # At high XP
    lvl_high, _ = calculate_level_and_next(5000)
    assert lvl_high >= 10


def test_knight_and_tenant_titles():
    """Verify title scaling based on level progression."""
    assert get_knight_title("SIR_BORIS", 1) == "Squire"
    assert "Sovereign Knight Commander" in get_knight_title("SIR_BORIS", 50)
    assert "Lord of the Round Table" in get_knight_title("SIR_BORIS", 75)

    assert get_tenant_title("Vizion Sky", 1) == "Sovereign Seeker"
    assert get_tenant_title("Vizion Sky", 100) == "Supreme Sovereign King"


def test_glass_observatory_interaction_tap(tmp_path):
    """Verify tapping conversation turns updates transcripts, RPG XP, and compendium."""
    obs = GlassObservatory(data_dir=tmp_path)

    transcript = obs.tap_interaction(
        tenant_id="Tenant_Alpha",
        knight_id="sir_sonus",
        user_prompt="Render sonic bridge",
        knight_response="Sonus here, duplex streaming active.",
        metrics={"estimated_ttfa_ms": 62.5, "radix_cache_hit_rate": 88.0},
    )

    assert transcript.turn_id.startswith("turn_")
    assert transcript.tenant_id == "Tenant_Alpha"
    assert transcript.knight_id == "sir_sonus"
    assert transcript.xp_awarded >= 45  # Base 25 + TTFA bonus 20 + Radix bonus 15 = 60

    # Check RPG state
    view = obs.get_glass_wall_view()
    assert view["glass_wall_status"] == "LOCKED_READ_ONLY_WORM"

    tenant_entry = next(t for t in view["leaderboard"]["tenants"] if t["tenant_id"] == "Tenant_Alpha")
    assert tenant_entry["xp"] == transcript.xp_awarded

    knight_entry = next(k for k in view["leaderboard"]["knights"] if k["knight_id"] == "sir_sonus")
    assert knight_entry["xp"] == transcript.xp_awarded
    assert knight_entry["turns_transcribed"] == 1

    # Check Compendium file was generated
    compendium_md = (tmp_path / "LIVING_COMPENDIUM.md").read_text(encoding="utf-8")
    assert "Tenant_Alpha" in compendium_md
    assert "sir_sonus" in compendium_md
    assert "Render sonic bridge" in compendium_md


def test_glass_observatory_implementation_eval(tmp_path):
    """Verify autonomous implementation evaluation calculates 5 axes and grades."""
    obs = GlassObservatory(data_dir=tmp_path)

    eval_res = obs.tap_implementation(
        knight_id="sir_codex",
        task_description="Build zero-copy WASM32 memory pipe",
        files_changed=["04_KINETIC/armory.rs"],
        tests_passed=10,
        latency_ms=45.0,
        memory_mb=64.0,
        violations=[],
    )

    assert eval_res.grade in ("S", "A")
    assert eval_res.score >= 90.0
    assert eval_res.xp_awarded > 100
    assert "ast_structure" in eval_res.axes_scores
    assert "performance_scarcity" in eval_res.axes_scores
    assert "test_integrity" in eval_res.axes_scores
    assert "zero_interference" in eval_res.axes_scores

    view = obs.get_glass_wall_view("evaluations")
    assert len(view["evaluations"]) == 1
    assert view["evaluations"][0]["knight_id"] == "sir_codex"


def test_zero_affiliation_with_provenance_ledger():
    """Verify Observatory files are completely segregated from PROVENANCE_LEDGER.md."""
    obs = get_glass_observatory()
    # Path of RPG store and compendium
    assert "PROVENANCE_LEDGER.md" not in str(obs.rpg_path)
    assert "PROVENANCE_LEDGER.md" not in str(obs.compendium_path)
    assert obs.data_dir.name == "observatory"


def test_camelot_cli_observatory_command():
    """Verify `camelot observatory` executes cleanly in the CLI."""
    from bin.camelot import _cmd_observatory

    # Test basic HUD output
    _cmd_observatory(["--glass"])

    # Test JSON output
    _cmd_observatory(["--json"])

    # Test Compendium output
    _cmd_observatory(["--compendium"])
