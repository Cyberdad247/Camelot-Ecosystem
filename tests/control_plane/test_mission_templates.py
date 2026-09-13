# SPDX-License-Identifier: MIT
"""Tests for canonical mission templates and objective scoring (Tracks C4, C5)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure control_plane is importable from repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from control_plane.infra.mission_templates import (
    CANONICAL_MISSION_TEMPLATES,
    MissionTemplate,
    ObjectiveScoring,
    calculate_blueprint_scoring,
    calculate_northstar_scoring,
    get_mission_template,
    list_mission_templates,
    resolve_template_parameters,
)


# ---------------------------------------------------------------------------
# Template catalog
# ---------------------------------------------------------------------------

class TestListMissionTemplates:
    def test_returns_five_templates(self):
        templates = list_mission_templates()
        assert len(templates) == 5

    def test_all_are_mission_template_instances(self):
        for t in list_mission_templates():
            assert isinstance(t, MissionTemplate)

    def test_expected_names_present(self):
        names = {t.name for t in list_mission_templates()}
        assert names == {"research", "architecture", "audit", "operations", "growth"}

    def test_canonical_dict_has_five_keys(self):
        assert len(CANONICAL_MISSION_TEMPLATES) == 5


# ---------------------------------------------------------------------------
# get_mission_template
# ---------------------------------------------------------------------------

class TestGetMissionTemplate:
    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_known_names_return_template(self, name: str):
        tmpl = get_mission_template(name)
        assert tmpl is not None
        assert tmpl.name == name

    def test_unknown_name_returns_none(self):
        assert get_mission_template("unknown_xyz") is None

    def test_empty_string_returns_none(self):
        assert get_mission_template("") is None

    def test_case_insensitive_lookup(self):
        tmpl = get_mission_template("AUDIT")
        assert tmpl is not None
        assert tmpl.name == "audit"

    def test_whitespace_stripped(self):
        tmpl = get_mission_template("  growth  ")
        assert tmpl is not None
        assert tmpl.name == "growth"

    def test_audit_compute_tier_is_apex(self):
        tmpl = get_mission_template("audit")
        assert tmpl.compute_tier == "apex"

    def test_audit_browser_isolation_is_agency(self):
        tmpl = get_mission_template("audit")
        assert tmpl.browser_isolation == "agency"

    def test_research_cartridge_is_ant(self):
        tmpl = get_mission_template("research")
        assert tmpl.cartridge == "ANT"

    def test_operations_cartridge_is_spider(self):
        tmpl = get_mission_template("operations")
        assert tmpl.cartridge == "SPIDER"


# ---------------------------------------------------------------------------
# MissionTemplate structure validation
# ---------------------------------------------------------------------------

class TestMissionTemplateStructure:
    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_template_has_three_chimera_rounds(self, name: str):
        tmpl = get_mission_template(name)
        assert len(tmpl.chimera_rounds) == 3

    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_template_has_deliverables(self, name: str):
        tmpl = get_mission_template(name)
        assert len(tmpl.deliverables) >= 1

    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_template_has_success_criteria(self, name: str):
        tmpl = get_mission_template(name)
        assert len(tmpl.success_criteria) >= 1

    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_template_has_recommended_knights(self, name: str):
        tmpl = get_mission_template(name)
        assert len(tmpl.recommended_knights) >= 1

    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_compute_tier_is_valid(self, name: str):
        tmpl = get_mission_template(name)
        assert tmpl.compute_tier in {"kinetic", "hybrid", "apex"}

    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_browser_isolation_is_valid(self, name: str):
        tmpl = get_mission_template(name)
        assert tmpl.browser_isolation in {"stealth", "team", "agency"}

    @pytest.mark.parametrize("name", ["research", "architecture", "audit", "operations", "growth"])
    def test_chimera_rounds_have_required_keys(self, name: str):
        tmpl = get_mission_template(name)
        for rnd in tmpl.chimera_rounds:
            assert "round" in rnd
            assert "owner" in rnd
            assert "title" in rnd
            assert "goal" in rnd


# ---------------------------------------------------------------------------
# resolve_template_parameters
# ---------------------------------------------------------------------------

class TestResolveTemplateParameters:
    def test_research_with_custom_objective(self):
        params = resolve_template_parameters("research", "My custom research goal")
        assert params["objective"] == "My custom research goal"
        assert params["template"] == "research"
        assert params["aspect"] == "research"

    def test_audit_uses_default_when_no_objective(self):
        params = resolve_template_parameters("audit")
        tmpl = get_mission_template("audit")
        assert params["objective"] == tmpl.default_objective

    def test_blank_objective_uses_default(self):
        params = resolve_template_parameters("operations", "   ")
        tmpl = get_mission_template("operations")
        assert params["objective"] == tmpl.default_objective

    def test_overrides_applied(self):
        params = resolve_template_parameters("growth", overrides={"compute_tier": "apex"})
        assert params["compute_tier"] == "apex"

    def test_none_override_value_ignored(self):
        tmpl = get_mission_template("architecture")
        params = resolve_template_parameters("architecture", overrides={"compute_tier": None})
        # None override should NOT overwrite the template default
        assert params["compute_tier"] == tmpl.compute_tier

    def test_unknown_template_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown mission template"):
            resolve_template_parameters("nonexistent_template")

    def test_returns_deliverables_list(self):
        params = resolve_template_parameters("audit")
        assert isinstance(params["deliverables"], list)
        assert len(params["deliverables"]) > 0

    def test_returns_chimera_rounds_list(self):
        params = resolve_template_parameters("research")
        assert len(params["chimera_rounds"]) == 3


# ---------------------------------------------------------------------------
# ObjectiveScoring model
# ---------------------------------------------------------------------------

class TestObjectiveScoring:
    def test_valid_construction(self):
        sc = ObjectiveScoring(confidence_score=0.85, risk_score=0.30, completeness_score=0.90)
        assert sc.confidence_score == pytest.approx(0.85)

    def test_to_dict_has_pct_keys(self):
        sc = ObjectiveScoring(confidence_score=0.75, risk_score=0.25, completeness_score=0.80)
        d = sc.to_dict()
        assert "confidence_pct" in d
        assert "risk_pct" in d
        assert "completeness_pct" in d

    def test_to_dict_pct_format(self):
        sc = ObjectiveScoring(confidence_score=0.90, risk_score=0.10, completeness_score=1.0)
        d = sc.to_dict()
        assert d["confidence_pct"] == "90%"
        assert d["risk_pct"] == "10%"
        assert d["completeness_pct"] == "100%"

    def test_scores_clamped_by_pydantic(self):
        with pytest.raises(Exception):
            ObjectiveScoring(confidence_score=1.5, risk_score=0.5, completeness_score=0.5)

    def test_negative_scores_rejected(self):
        with pytest.raises(Exception):
            ObjectiveScoring(confidence_score=-0.1, risk_score=0.5, completeness_score=0.5)


# ---------------------------------------------------------------------------
# calculate_northstar_scoring
# ---------------------------------------------------------------------------

_NORTHSTAR_BASE = dict(
    compute_tier="hybrid",
    aspect="research",
    memory_count=5,
    browser_isolation="team",
    multilogin_enabled=True,
    assigned_knights=["sir_boris", "merlin_omega", "lady_apis"],
    mission_tracks=[{"id": "C1"}, {"id": "C2"}, {"id": "C3"}],
)


class TestCalculateNorthstarScoring:
    def test_returns_objective_scoring_instance(self):
        sc = calculate_northstar_scoring(**_NORTHSTAR_BASE)
        assert isinstance(sc, ObjectiveScoring)

    def test_scores_in_range(self):
        sc = calculate_northstar_scoring(**_NORTHSTAR_BASE)
        assert 0.0 <= sc.confidence_score <= 1.0
        assert 0.0 <= sc.risk_score <= 1.0
        assert 0.0 <= sc.completeness_score <= 1.0

    def test_apex_tier_higher_confidence_than_kinetic(self):
        apex = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "compute_tier": "apex"})
        kinetic = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "compute_tier": "kinetic"})
        assert apex.confidence_score > kinetic.confidence_score

    def test_audit_aspect_lowers_risk(self):
        audit_sc = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "aspect": "audit"})
        research_sc = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "aspect": "research"})
        assert audit_sc.risk_score <= research_sc.risk_score

    def test_multilogin_disabled_increases_risk(self):
        with_ml = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "multilogin_enabled": True})
        without_ml = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "multilogin_enabled": False})
        assert without_ml.risk_score > with_ml.risk_score

    def test_more_tracks_improves_completeness(self):
        few = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "mission_tracks": [{"id": "C1"}]})
        many = calculate_northstar_scoring(**{
            **_NORTHSTAR_BASE,
            "mission_tracks": [{"id": f"C{i}"} for i in range(5)],
        })
        assert many.completeness_score >= few.completeness_score

    def test_more_memory_increases_confidence(self):
        low_mem = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "memory_count": 0})
        high_mem = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "memory_count": 20})
        assert high_mem.confidence_score >= low_mem.confidence_score

    def test_rationale_has_three_keys(self):
        sc = calculate_northstar_scoring(**_NORTHSTAR_BASE)
        assert "confidence" in sc.rationale
        assert "risk" in sc.rationale
        assert "completeness" in sc.rationale

    def test_rationale_strings_are_non_empty(self):
        sc = calculate_northstar_scoring(**_NORTHSTAR_BASE)
        for key, val in sc.rationale.items():
            assert len(val) > 0, f"Rationale key '{key}' is empty"

    def test_unknown_tier_uses_fallback_confidence(self):
        sc = calculate_northstar_scoring(**{**_NORTHSTAR_BASE, "compute_tier": "unknown_tier"})
        # fallback is 0.80; no bonuses should be nil, score should be in range
        assert 0.0 <= sc.confidence_score <= 1.0


# ---------------------------------------------------------------------------
# calculate_blueprint_scoring
# ---------------------------------------------------------------------------

_BLUEPRINT_BASE = dict(
    compute_tier="hybrid",
    budget_mode="balanced",
    team_size=3,
    horizon_days=14,
    prioritize_local_first=True,
    execution_phases=[{"phase": 1}, {"phase": 2}, {"phase": 3}],
)


class TestCalculateBlueprintScoring:
    def test_returns_objective_scoring_instance(self):
        sc = calculate_blueprint_scoring(**_BLUEPRINT_BASE)
        assert isinstance(sc, ObjectiveScoring)

    def test_scores_in_range(self):
        sc = calculate_blueprint_scoring(**_BLUEPRINT_BASE)
        assert 0.0 <= sc.confidence_score <= 1.0
        assert 0.0 <= sc.risk_score <= 1.0
        assert 0.0 <= sc.completeness_score <= 1.0

    def test_local_first_increases_confidence(self):
        with_lf = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "prioritize_local_first": True})
        without_lf = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "prioritize_local_first": False})
        assert with_lf.confidence_score > without_lf.confidence_score

    def test_aggressive_budget_higher_risk_than_lean(self):
        aggressive = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "budget_mode": "aggressive"})
        lean = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "budget_mode": "lean"})
        assert aggressive.risk_score > lean.risk_score

    def test_large_team_increases_risk(self):
        small = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "team_size": 2})
        large = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "team_size": 12})
        assert large.risk_score > small.risk_score

    def test_tight_horizon_improves_completeness(self):
        tight = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "horizon_days": 14})
        long = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "horizon_days": 90})
        assert tight.completeness_score >= long.completeness_score

    def test_apex_tier_highest_confidence(self):
        apex = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "compute_tier": "apex"})
        kinetic = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "compute_tier": "kinetic"})
        assert apex.confidence_score > kinetic.confidence_score

    def test_rationale_has_three_keys(self):
        sc = calculate_blueprint_scoring(**_BLUEPRINT_BASE)
        assert set(sc.rationale.keys()) >= {"confidence", "risk", "completeness"}

    def test_more_phases_improves_completeness(self):
        few = calculate_blueprint_scoring(**{**_BLUEPRINT_BASE, "execution_phases": [{"phase": 1}]})
        many = calculate_blueprint_scoring(**{
            **_BLUEPRINT_BASE,
            "execution_phases": [{"phase": i} for i in range(6)],
        })
        assert many.completeness_score >= few.completeness_score


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------

_CLI_ENTRY = str(_REPO_ROOT / "control_plane" / "camelot_cli.py")


class TestCLITemplatesSmoke:
    def test_templates_json_exit_zero(self):
        result = subprocess.run(
            [sys.executable, _CLI_ENTRY, "templates", "--json"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_templates_json_output_parseable(self):
        result = subprocess.run(
            [sys.executable, _CLI_ENTRY, "templates", "--json"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        payload = json.loads(result.stdout)
        assert "templates" in payload
        assert len(payload["templates"]) == 5

    def test_templates_name_audit_json(self):
        result = subprocess.run(
            [sys.executable, _CLI_ENTRY, "templates", "--name", "audit", "--json"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        payload = json.loads(result.stdout)
        # Either a single-template dict or a filtered list is acceptable
        assert payload  # non-empty

    def test_templates_hud_exit_zero(self):
        """Plain HUD rendering (no --json) must also exit cleanly."""
        result = subprocess.run(
            [sys.executable, _CLI_ENTRY, "templates"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
