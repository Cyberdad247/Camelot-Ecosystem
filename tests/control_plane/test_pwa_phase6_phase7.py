# SPDX-License-Identifier: MIT
"""
Tests for Phase 6 (Twin-Brain Node Management) and Phase 7 (Deployment & Gideon Z3 Verification).
"""

import json
from pathlib import Path
import jsonschema

from control_plane.runners.evaluation_chamber_runner import EvaluationChamberEngine

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "packages" / "contracts" / "gideon-verdict.schema.json"


def test_phase7_gideon_z3_verification():
    """Task 7.4: Ensure Gideon schema verification passes for PWA deployment candidate."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    engine = EvaluationChamberEngine()
    result = engine.execute_simulation(
        "pwa_ecosystem_release_v1",
        dimensions={
            "correctness": 0.96,
            "security": 0.99,
            "path_scope": 1.00,
            "test_validity": 0.95,
            "efficiency": 0.95,
        },
    )
    verdict = result["verdict"]

    jsonschema.validate(instance=verdict, schema=schema)
    assert verdict["verdict"] == "pass"
    assert verdict["schema_version"] == "camelot-gideon-verdict/1"
    assert result["telemetry"]["promotion_eligible"] is True


def test_phase7_caddy_security_headers():
    """Task 7.2: Verify Caddyfile contains required zero-trust security headers."""
    caddyfile_path = REPO_ROOT / "infra" / "caddy" / "Caddyfile"
    content = caddyfile_path.read_text(encoding="utf-8")

    assert "Strict-Transport-Security" in content
    assert "Content-Security-Policy" in content
    assert "Cross-Origin-Opener-Policy" in content
    assert "Cross-Origin-Embedder-Policy" in content
    assert "X-Content-Type-Options" in content
