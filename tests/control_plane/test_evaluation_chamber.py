# SPDX-License-Identifier: MIT
"""
Tests for Camelot-OS Engineering Cartridge Evaluation Simulator (Hyperbolic Chamber).
Validates Gideon schema conformance, multi-dimensional scoring, and hard gate enforcement.
"""

import json
from pathlib import Path
import jsonschema

from control_plane.runners.evaluation_chamber_runner import (
    EvaluationChamberEngine,
    execute_evaluation_run,
    MANDATORY_HARD_GATES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "packages" / "contracts" / "gideon-verdict.schema.json"


def test_schema_conformance_pass():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    engine = EvaluationChamberEngine()
    result = engine.execute_simulation("candidate_valid_v1")
    verdict = result["verdict"]

    # Must strictly validate against gideon-verdict schema
    jsonschema.validate(instance=verdict, schema=schema)
    assert verdict["verdict"] == "pass"
    assert len(verdict["block_reasons"]) == 0
    assert verdict["gates"] == MANDATORY_HARD_GATES
    assert result["telemetry"]["promotion_eligible"] is True


def test_schema_conformance_block():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    engine = EvaluationChamberEngine()
    # Path scope violation (< 1.0) and low security (< 0.90)
    result = engine.execute_simulation(
        "candidate_rogue_v1",
        dimensions={"correctness": 0.9, "security": 0.80, "path_scope": 0.5, "test_validity": 0.8, "efficiency": 0.8},
    )
    verdict = result["verdict"]

    jsonschema.validate(instance=verdict, schema=schema)
    assert verdict["verdict"] == "block"
    assert len(verdict["block_reasons"]) >= 2
    assert result["telemetry"]["promotion_eligible"] is False


def test_runic_router_chamber_execution():
    from control_plane.runes.runic_router import route_rune

    res = route_rune("//CHAMBER", "candidate_alpha_v2")
    assert res.knight == "sir_gideon"
    assert res.mode == "SENTINEL"
    metadata = res.metadata
    assert metadata.get("status") == "COMPLETED"
    assert metadata.get("action") == "cartridge_evaluation_simulation"
    assert metadata.get("verdict", {}).get("verdict") == "pass"
