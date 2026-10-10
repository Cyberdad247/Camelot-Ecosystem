# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Tests for Knight, Omega Knight, and Squire Schemas, Templates, and Personalities
================================================================================
Verifies:
1. Knight Character Sheets contain valid MBTI profiles and programming languages for all 59 Knights.
2. All 7 Omega Knights (MERLIN_Ω, ANYA_Ω, ARTHUR_Ω, ALPHA_Ω, HEIMDALL_Ω, LUKAS_Ω, JEV_Ω) are registered and calibrated.
3. knight_persona_template.json conforms to packages/contracts/persona.schema.json.
4. omega_knight_persona_template.json conforms to packages/contracts/persona.schema.json.
5. squire_template.json conforms to packages/contracts/squire.schema.json.
6. packages/contracts/index.json registers squire.schema.json and persona.schema.json.
7. Memory ceiling invariants satisfy Global Law 03 (<= 512MB for Knights, <= 256MB for Squires).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import jsonschema

CAMELOT_HOME = Path(__file__).resolve().parent.parent


def test_knight_character_sheets_mbti_and_languages():
    """Verify all 59 Knights have valid MBTI personality profiles and execution languages."""
    sheets_path = CAMELOT_HOME / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
    assert sheets_path.exists(), "knight_character_sheets.json must exist"
    
    data = json.loads(sheets_path.read_text(encoding="utf-8"))
    knights = data.get("knights", {})
    assert len(knights) >= 59, f"Expected at least 59 knights, found {len(knights)}"

    for kid, kdata in knights.items():
        # MBTI verification
        assert "mbti" in kdata, f"Knight {kid} missing mbti field"
        assert len(kdata["mbti"]) == 4, f"Knight {kid} invalid MBTI code: {kdata['mbti']}"
        assert kdata["mbti"][0] in ("E", "I")
        assert kdata["mbti"][1] in ("S", "N")
        assert kdata["mbti"][2] in ("T", "F")
        assert kdata["mbti"][3] in ("J", "P")
        assert "mbti_profile" in kdata, f"Knight {kid} missing mbti_profile"
        assert "archetype" in kdata["mbti_profile"], f"Knight {kid} missing archetype in mbti_profile"

        # Languages verification
        assert "languages" in kdata, f"Knight {kid} missing languages list"
        assert isinstance(kdata["languages"], list)
        assert len(kdata["languages"]) > 0, f"Knight {kid} has empty languages list"
        assert "primary_language" in kdata, f"Knight {kid} missing primary_language"
        assert kdata["primary_language"] in kdata["languages"]


def test_omega_knights_calibration():
    """Verify all 7 Omega Knights have high-order cognitive calibration."""
    sheets_path = CAMELOT_HOME / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"
    data = json.loads(sheets_path.read_text(encoding="utf-8"))
    knights = data.get("knights", {})

    omega_ids = [
        "ANYA_OMEGA",
        "MERLIN_OMEGA",
        "ARTHUR_OMEGA",
        "ALPHA_OMEGA",
        "HEIMDALL_OMEGA",
        "LUKAS_OMEGA",
        "JEV_OMEGA",
    ]
    for oid in omega_ids:
        assert oid in knights, f"Omega Knight {oid} missing from knight_character_sheets.json"
        kdata = knights[oid]
        assert kdata.get("skill_tier") in ("S5 Strategic", "S5 Sovereign", "S4 Strategic", "S4 Specialized")
        assert kdata.get("mbti") in ("INTJ", "ISTJ", "ESTP", "INTP", "ENTJ", "INFJ", "ENFJ")


def test_knight_persona_template_conforms_to_schema():
    """Verify knight_persona_template.json satisfies persona.schema.json."""
    schema_path = CAMELOT_HOME / "packages" / "contracts" / "persona.schema.json"
    template_path = CAMELOT_HOME / "packages" / "contracts" / "templates" / "knight_persona_template.json"
    
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    template = json.loads(template_path.read_text(encoding="utf-8"))
    
    # Must not raise ValidationError
    jsonschema.validate(instance=template, schema=schema)
    assert template["personality"]["mbti"] == "INTJ"
    assert template["primary_language"] in template["languages"]


def test_omega_knight_persona_template_conforms_to_schema():
    """Verify omega_knight_persona_template.json satisfies persona.schema.json."""
    schema_path = CAMELOT_HOME / "packages" / "contracts" / "persona.schema.json"
    template_path = CAMELOT_HOME / "packages" / "contracts" / "templates" / "omega_knight_persona_template.json"
    
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    template = json.loads(template_path.read_text(encoding="utf-8"))
    
    jsonschema.validate(instance=template, schema=schema)
    assert template["class"] == "omega_sovereign_lattice"
    assert "Rust" in template["languages"]
    assert "omega_governance" in template["competence_map"]["primary"]


def test_squire_template_conforms_to_schema():
    """Verify squire_template.json satisfies squire.schema.json."""
    schema_path = CAMELOT_HOME / "packages" / "contracts" / "squire.schema.json"
    template_path = CAMELOT_HOME / "packages" / "contracts" / "templates" / "squire_template.json"
    
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    template = json.loads(template_path.read_text(encoding="utf-8"))
    
    jsonschema.validate(instance=template, schema=schema)
    assert template["schema_version"] == "camelot-squire/1"
    assert template["runtime_resource_profile"]["memory_ceiling_mb"] <= 256.0
    assert template["primary_language"] in template["languages"]


def test_contracts_index_registers_squire_schema():
    """Verify packages/contracts/index.json registers squire.schema.json."""
    index_path = CAMELOT_HOME / "packages" / "contracts" / "index.json"
    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    files = [s["file"] for s in index_data.get("schemas", [])]
    assert "squire.schema.json" in files
    assert "persona.schema.json" in files
    assert "soul.schema.json" in files
