# SPDX-License-Identifier: MIT
"""
Tests for Sir Kay (High Seneschal & Chief Engineering Director) and
the Department of Kinetic Engineering & Systems Implementation (DKESI) Runes:
- //ENGINEERING_SPRINT
- //DIRECT_BUILD
- //REGRESSION_AUDIT
- //HOTPATH_VERIFY
"""

import json
from pathlib import Path
import pytest
from control_plane.runes.runic_router import normalize_rune, route_rune, RUNIC_COMMANDS


def test_sir_kay_runes_present_in_table():
    assert "//ENGINEERING_SPRINT" in RUNIC_COMMANDS
    assert "//DIRECT_BUILD" in RUNIC_COMMANDS
    assert "//REGRESSION_AUDIT" in RUNIC_COMMANDS
    assert "//HOTPATH_VERIFY" in RUNIC_COMMANDS
    assert RUNIC_COMMANDS["//ENGINEERING_SPRINT"]["knight"] == "sir_kay"
    assert RUNIC_COMMANDS["//DIRECT_BUILD"]["knight"] == "sir_kay"
    assert RUNIC_COMMANDS["//REGRESSION_AUDIT"]["knight"] == "sir_kay"
    assert RUNIC_COMMANDS["//HOTPATH_VERIFY"]["knight"] == "sir_kay"


def test_sir_kay_runes_normalization():
    assert normalize_rune("//engineering-sprint") == "//ENGINEERING_SPRINT"
    assert normalize_rune("$engineering-sprint") == "//ENGINEERING_SPRINT"
    assert normalize_rune("//sprint") == "//ENGINEERING_SPRINT"
    assert normalize_rune("$sprint") == "//ENGINEERING_SPRINT"
    assert normalize_rune("/sprint") == "//ENGINEERING_SPRINT"

    assert normalize_rune("//direct-build") == "//DIRECT_BUILD"
    assert normalize_rune("$direct-build") == "//DIRECT_BUILD"
    assert normalize_rune("/direct-build") == "//DIRECT_BUILD"

    assert normalize_rune("//regression-audit") == "//REGRESSION_AUDIT"
    assert normalize_rune("$regression-audit") == "//REGRESSION_AUDIT"
    assert normalize_rune("/regression-audit") == "//REGRESSION_AUDIT"

    assert normalize_rune("//hotpath-verify") == "//HOTPATH_VERIFY"
    assert normalize_rune("$hotpath-verify") == "//HOTPATH_VERIFY"
    assert normalize_rune("/hotpath-verify") == "//HOTPATH_VERIFY"


def test_engineering_sprint_dispatch():
    res = route_rune("//ENGINEERING_SPRINT Deploy Core Go Router", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "SPRINT_INITIALIZED"
    assert res.metadata.get("action") == "engineering_sprint"
    assert res.metadata.get("director") == "SIR_KAY"
    assert "SIR_CODEX" in res.metadata.get("governed_knights", [])
    assert res.metadata.get("goal") == "Deploy Core Go Router"


def test_direct_build_dispatch():
    res = route_rune("//DIRECT_BUILD AST Transform Pipeline", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "BUILD_DIRECTED"
    assert res.metadata.get("director") == "SIR_KAY"
    assert "SIR_CODEX" in res.metadata.get("kinetic_leads", [])
    assert res.metadata.get("spec") == "AST Transform Pipeline"


def test_regression_audit_dispatch():
    res = route_rune("//REGRESSION_AUDIT 04_KINETIC", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "AUDIT_PASSED"
    assert res.metadata.get("director") == "SIR_KAY"
    assert res.metadata.get("diagnostic_lead") == "SIR_DEBUG"
    assert res.metadata.get("regression_risk") == 0.0


def test_hotpath_verify_dispatch():
    res = route_rune("//HOTPATH_VERIFY", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "HOTPATH_PURITY_CONFIRMED"
    assert res.metadata.get("director") == "SIR_KAY"
    assert res.metadata.get("hotpath_specialist") == "SIR_RUSTCLAW"
    assert res.metadata.get("python_node_leak_pct") == 0.0


def test_dkesi_department_config_integrity():
    dept_file = Path(__file__).resolve().parent.parent.parent / "control_plane" / "departments" / "engineering_development.json"
    assert dept_file.exists(), f"Department config missing: {dept_file}"
    with open(dept_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["department_id"] == "dept_kinetic_engineering"
    assert data["leadership"]["director"]["knight_id"] == "SIR_KAY"
    assert data["leadership"]["technical_lead"]["knight_id"] == "SIR_CODEX"
    roster_knights = [k["knight_id"] for k in data["roster"]]
    for expected in ["SIR_FORGE", "SIR_DEBUG", "SIR_RUSTCLAW", "SIR_ALEX"]:
        assert expected in roster_knights


def test_sir_kay_blueprint_and_tissue_exist():
    repo_root = Path(__file__).resolve().parent.parent.parent
    blueprint = repo_root / ".hive" / "agents" / "OMEGA_SIR_KAY_BLUEPRINT_v1.0.nkg.md"
    tissue = repo_root / "03_VAULT" / "runtime_state" / "open_notebook" / "sir_kay_tissue.json"
    arch_doc = repo_root / "docs" / "architecture" / "ENGINEERING_DEPARTMENT.md"

    assert blueprint.exists(), f"Blueprint missing: {blueprint}"
    assert tissue.exists(), f"Tissue missing: {tissue}"
    assert arch_doc.exists(), f"Architecture doc missing: {arch_doc}"

    with open(tissue, "r", encoding="utf-8") as f:
        tissue_data = json.load(f)
    assert len(tissue_data) >= 2
    assert tissue_data[0]["knight_id"] == "SIR_KAY"
