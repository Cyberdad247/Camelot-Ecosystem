# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for the Sovereign Enterprise Evolution Engine (vKG + //ASSIMILATION).
================================================================================
Tests the 1 -> M -> A -> S pipeline, P0 -> P11 promotion gates, complexity/safety
budgets, first-class RETREAT, cognitive depth routing, and UKG/3 compliance.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from control_plane.pipeline.evolution_engine import (
    CognitiveDepth,
    ComplexityBudget,
    EnterpriseEvolutionEngine,
    GlyphOperator,
    PromotionGate,
    SafetyBudget,
)
from control_plane.pipeline.synthetos_proof import NkgCrystal
from control_plane.runes.runic_router import route_rune


@pytest.fixture
def engine():
    return EnterpriseEvolutionEngine()


@pytest.fixture
def sample_crystal():
    node_id = "test_crystal_northstar"
    raw_payload = json.dumps({"components": ["//NORTHSTAR"], "doctrine": "1_TO_M_TO_A"})
    crystal = NkgCrystal(
        node_id=node_id,
        vfs_coordinate=f"vfs://worldtree/crystals/{node_id}",
        glyph_symbol="//NORTHSTAR",
        compressed_payload=raw_payload,
        expected_hash="",
    )
    yield crystal
    # Cleanup test node artifact
    test_node_file = Path(__file__).resolve().parent.parent / "03_VAULT" / "UKG" / "nodes" / f"{node_id}.json"
    if test_node_file.exists():
        test_node_file.unlink(missing_ok=True)


def test_evolution_pipeline_success(engine, sample_crystal):
    """Verify clean P0 -> P11 crystallization under valid complexity/safety budgets."""
    res = engine.evolve_capsule(
        sample_crystal,
        complexity_budget=ComplexityBudget(daemons=0, db_tables=1, network_hops=1),
        safety_budget=SafetyBudget(risk_score=10.0, memory_mb=25.0),
    )

    assert res["status"] == "CRYSTALLIZED_SUCCESS"
    assert res["current_gate"] == PromotionGate.P11_CRYSTALLIZED.value
    assert len(res["gates_passed"]) == 12
    assert "P0_CANDIDATE" in res["gates_passed"]
    assert "P11_CRYSTALLIZED" in res["gates_passed"]
    assert "capsule" in res
    capsule = res["capsule"]
    assert capsule["schema_version"] == "camelot-ukg/3"
    assert capsule["glyph_handle"] == "[✓//NORTHSTAR]"
    assert capsule["glyph_operator"] == "✓"
    assert len(capsule["architectural_lineage"]) == 23
    assert capsule["doctrine"] == "1_TO_M_TO_A"


def test_complexity_budget_rejection_at_p6(engine, sample_crystal):
    """Verify that exceeding complexity points (> 25) triggers First-Class RETREAT at P6."""
    # 2 daemons (20 pts) + 1 db table (8 pts) = 28 pts (> 25 ceiling)
    over_budget = ComplexityBudget(daemons=2, db_tables=1)
    
    res = engine.evolve_capsule(
        sample_crystal,
        complexity_budget=over_budget,
    )

    assert res["status"] == "RETREAT_EXECUTED"
    assert res["failed_gate"] == PromotionGate.P6_COMPLEXITY_AUDIT.value
    assert "Complexity budget exceeded" in res["reason"]
    assert res["blast_radius_contained"] is True
    assert res["glyph_status"] == GlyphOperator.REJECTED.value
    assert "P5_INVARIANT_PROOF" in res["gates_passed"]
    assert "P6_COMPLEXITY_AUDIT" not in res["gates_passed"]


def test_safety_budget_rejection_at_p7(engine, sample_crystal):
    """Verify that risk score >= 50 triggers First-Class RETREAT at P7."""
    high_risk = SafetyBudget(risk_score=75.0)  # Exceeds 50.0 threshold

    res = engine.evolve_capsule(
        sample_crystal,
        safety_budget=high_risk,
    )

    assert res["status"] == "RETREAT_EXECUTED"
    assert res["failed_gate"] == PromotionGate.P7_SAFETY_AUDIT.value
    assert "Safety budget exceeded" in res["reason"]
    assert res["blast_radius_contained"] is True


def test_unknown_glyph_decompression_blocked(engine):
    """Verify unknown glyphs not in ukg-dictionary/1 fail with DECOMPRESSION_BLOCKED at P1."""
    unknown_crystal = NkgCrystal(
        node_id="unknown_crystal",
        vfs_coordinate="vfs://worldtree/crystals/unknown_crystal",
        glyph_symbol="//UNREGISTERED_ROGUE_CAPABILITY",
        compressed_payload=json.dumps({"test": 1}),
        expected_hash="",
    )

    res = engine.evolve_capsule(unknown_crystal)
    assert res["status"] == "RETREAT_EXECUTED"
    assert res["failed_gate"] == PromotionGate.P1_DECOMPRESSED.value
    assert "DECOMPRESSION_BLOCKED" in res["reason"]


def test_cognitive_depth_routing(engine):
    """Verify adaptive cognitive depth routing D0 through D4."""
    # D0: Read-only lookup
    assert engine.route_cognitive_depth("READ_ONLY", "R0_SAFE") == CognitiveDepth.D0_DIRECT_FASTPATH
    # D1: Local non-consequential
    assert engine.route_cognitive_depth("LOCAL_EDIT", "R1_LOW") == CognitiveDepth.D1_STATIC_VERIFY
    # D2: Medium risk local sandbox
    assert engine.route_cognitive_depth("TASK", "R2_MEDIUM") == CognitiveDepth.D2_SYNTHETOS_VERIFIER
    # D3: External repo / high risk
    assert engine.route_cognitive_depth("TASK", "R3_HIGH", external_url="https://github.com/test/repo") == CognitiveDepth.D3_FOUR_KNIGHT_COUNCIL
    # D4: Touches kernel or critical
    assert engine.route_cognitive_depth("TASK", "R4_CRITICAL", touches_kernel=True) == CognitiveDepth.D4_ARCHMAGE_ARTHUR_HITL


def test_sentinel_lease_issuance(engine):
    """Verify Sentinel generates cryptographically signed HMAC-SHA256 leases."""
    lease = engine.issue_sentinel_lease(
        node_id="crystal_northstar",
        target_scope="vfs://worldtree/crystals/crystal_northstar",
        ttl_seconds=120,
    )
    assert lease["granter"] == "SIR_SENTINEL"
    assert lease["node_id"] == "crystal_northstar"
    assert len(lease["nonce"]) == 16
    assert len(lease["signature"]) == 64  # SHA256 hex digest
    assert lease["ttl_seconds"] == 120


def test_runic_dispatch_assimilate_evolve():
    """Verify runic dispatch via //ASSIMILATE_EVOLVE and //NKG_INSPECT."""
    res_inspect = route_rune("//NKG_INSPECT //NORTHSTAR")
    assert res_inspect.metadata["status"] == "DECOMPRESSION_SUCCESS"
    assert res_inspect.knight == "sir_helios"
    assert res_inspect.metadata["glyph"] == "//NORTHSTAR"

    res_evolve = route_rune("//ASSIMILATE_EVOLVE //NORTHSTAR")
    assert res_evolve.metadata["result"]["status"] == "CRYSTALLIZED_SUCCESS"
    assert res_evolve.knight == "sir_synthetos"
    assert res_evolve.metadata["result"]["current_gate"] == "P11_CRYSTALLIZED"
