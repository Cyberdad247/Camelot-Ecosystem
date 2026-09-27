# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit and Integration Tests for Enterprise Production Package v2 (DG-310 through DG-440).
========================================================================================
Validates the full continuum P0 -> P24, the 5 Architectural Zeros, Disposable Sandbox
Restore Drills, Observe-Only Shadow Canary Variance, and First-Class RETREAT.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from control_plane.pipeline.evolution_engine import (
    ComplexityBudget,
    EnterpriseEvolutionEngine,
    PromotionGate,
    SafetyBudget,
)
from control_plane.pipeline.synthetos_proof import NkgCrystal
from control_plane.production.restore_drill import RestoreDrillEngine
from control_plane.production.shadow_canary import ShadowCanaryProver
from control_plane.production.slo_monitor import ArchitecturalSLOMonitor


def _create_test_crystal(node_id: str) -> NkgCrystal:
    raw_payload = json.dumps({"components": ["//NORTHSTAR"], "doctrine": "1_TO_M_TO_A"})
    return NkgCrystal(
        node_id=node_id,
        vfs_coordinate=f"vfs://worldtree/crystals/{node_id}",
        glyph_symbol="//NORTHSTAR",
        compressed_payload=raw_payload,
        expected_hash="",
    )


def _cleanup_crystal(node_id: str):
    repo_root = Path(__file__).resolve().parent.parent
    test_node_file = repo_root / "03_VAULT" / "UKG" / "nodes" / f"{node_id}.json"
    if test_node_file.exists():
        test_node_file.unlink(missing_ok=True)


def test_restore_drill_engine_bit_identical():
    """P20: Verify restore drill destroys disposable sandbox, restores, and proves bit-identical Merkle equality."""
    engine = RestoreDrillEngine()
    source_state = {
        "schema_version": "camelot-ukg/3",
        "partitions": {
            "kernel": {"merkle_root": "0xabc123", "nodes_count": 42},
            "vault": {"crystals": ["crystal_a", "crystal_b"]},
        },
        "signer_epoch": 1,
    }

    receipt = engine.execute_restore_drill("test_partition_kernel", source_state)

    assert receipt.status == "RESTORE_VERIFIED"
    assert receipt.verified_bit_identical is True
    assert receipt.source_merkle_root == receipt.restored_merkle_root
    assert receipt.recovery_time_ms >= 0.0
    assert receipt.signature != ""


def test_shadow_canary_prover_zero_variance():
    """P22: Verify observe-only shadow execution proves 0% mutation variance and output equivalence."""
    prover = ShadowCanaryProver()
    input_data = {"request_id": "req_101", "action": "CALCULATE_HASH", "seed": "0xbeef"}

    canonical_fn = lambda d: {"result": f"processed_{d['seed']}", "status": "OK"}
    candidate_fn = lambda d: {"result": f"processed_{d['seed']}", "status": "OK"}

    receipt = prover.compare_execution("hash_service", input_data, canonical_fn, candidate_fn)

    assert receipt.status == "SHADOW_CANARY_PROVED"
    assert receipt.variance_score == 0.0
    assert receipt.mutation_count_observed == 0
    assert receipt.canonical_digest == receipt.shadow_digest


def test_shadow_canary_prover_variance_exceeded():
    """P22: Verify shadow canary catches unauthorized candidate mutation or divergent output."""
    prover = ShadowCanaryProver()
    input_data = {"request_id": "req_102", "action": "INSPECT"}

    canonical_fn = lambda d: {"version": "v1", "status": "OK"}
    candidate_fn = lambda d: {"version": "v2_mutated", "status": "OK"}

    receipt = prover.compare_execution("inspect_service", input_data, canonical_fn, candidate_fn)

    assert receipt.status == "VARIANCE_EXCEEDED"
    assert receipt.variance_score > 0.0
    assert receipt.canonical_digest != receipt.shadow_digest


def test_slo_monitor_five_zeros_compliant():
    """P18: Verify compliance when all 5 Architectural Zeros have 0 incidents."""
    monitor = ArchitecturalSLOMonitor()
    cert = monitor.evaluate_compliance(
        stale_authority_events=0,
        cross_tenant_events=0,
        unreceipted_promotions=0,
        authority_memory_events=0,
        unverified_adoptions=0,
        total_operations=5000,
    )

    assert cert.is_compliant is True
    assert cert.stale_authority_rate == 0.0
    assert cert.cross_tenant_leakage_rate == 0.0
    assert cert.unreceipted_promotion_rate == 0.0
    assert cert.authority_memory_rate == 0.0
    assert cert.unverified_adoption_rate == 0.0
    assert cert.signature != ""


def test_slo_monitor_violation_fails():
    """P18: Any single violation in the 5 Zeros fails compliance immediately."""
    monitor = ArchitecturalSLOMonitor()
    cert = monitor.evaluate_compliance(
        stale_authority_events=1,  # 1 stale authority event
        cross_tenant_events=0,
        unreceipted_promotions=0,
        authority_memory_events=0,
        unverified_adoptions=0,
    )

    assert cert.is_compliant is False
    assert cert.stale_authority_rate > 0.0


def test_evolution_engine_full_p24_promotion_success():
    """Full continuum P0 -> P24 promotion into Enterprise Sovereign Ratification."""
    node_id = "crystal_enterprise_promoted_v2"
    engine = EnterpriseEvolutionEngine()
    crystal = _create_test_crystal(node_id)

    try:
        result = engine.evolve_capsule(
            crystal=crystal,
            target_gate=PromotionGate.P24_ENTERPRISE_PROMOTED,
        )

        assert result["status"] == "ENTERPRISE_PROMOTED_SUCCESS"
        assert result["current_gate"] == PromotionGate.P24_ENTERPRISE_PROMOTED.value
        assert len(result["gates_passed"]) == 25  # P0 through P24

        # Verify key enterprise evidence artifacts
        assert "release_proof" in result
        assert result["release_proof"]["schema_version"] == "camelot-release-proof/1"
        assert "restoration_receipt" in result
        assert result["restoration_receipt"].status == "RESTORE_VERIFIED"
        assert "shadow_canary_receipt" in result
        assert result["shadow_canary_receipt"].status == "SHADOW_CANARY_PROVED"
        assert "slo_certificate" in result
        assert result["slo_certificate"].is_compliant is True
        assert "sovereign_crown_seal" in result
        assert len(result["sovereign_crown_seal"]) == 64  # SHA-256 hex
    finally:
        _cleanup_crystal(node_id)


def test_evolution_engine_retreat_at_p14_config():
    """First-Class RETREAT at P14: Invalid ConfigContract with missing authority critical keys."""
    node_id = "crystal_retreat_config"
    engine = EnterpriseEvolutionEngine()
    crystal = _create_test_crystal(node_id)

    # Missing mandatory authority keys
    invalid_config = {
        "schema_version": "camelot-config/1",
        "entries": {
            "LOG_LEVEL": {"value": "DEBUG", "classification": "RELOADABLE"},
        },
    }

    try:
        result = engine.evolve_capsule(
            crystal=crystal,
            target_gate=PromotionGate.P24_ENTERPRISE_PROMOTED,
            custom_config=invalid_config,
        )

        assert result["status"] == "RETREAT_EXECUTED"
        assert result["failed_gate"] == PromotionGate.P14_CONFIG_VALIDATED.value
        assert "Config contract validation failed" in result["reason"]
        assert result["blast_radius_contained"] is True
        assert result["glyph_status"] == "ø"
    finally:
        _cleanup_crystal(node_id)


def test_evolution_engine_retreat_at_p18_slo():
    """First-Class RETREAT at P18: Architectural SLO violation."""
    node_id = "crystal_retreat_slo"
    engine = EnterpriseEvolutionEngine()
    crystal = _create_test_crystal(node_id)

    try:
        result = engine.evolve_capsule(
            crystal=crystal,
            target_gate=PromotionGate.P24_ENTERPRISE_PROMOTED,
            simulate_slo_failure=True,
        )

        assert result["status"] == "RETREAT_EXECUTED"
        assert result["failed_gate"] == PromotionGate.P18_SLO_COMPLIANT.value
        assert "SLO violated" in result["reason"]
        assert result["blast_radius_contained"] is True
    finally:
        _cleanup_crystal(node_id)


def test_evolution_engine_retreat_at_p20_restore():
    """First-Class RETREAT at P20: Restore drill failure."""
    node_id = "crystal_retreat_restore"
    engine = EnterpriseEvolutionEngine()
    crystal = _create_test_crystal(node_id)

    try:
        result = engine.evolve_capsule(
            crystal=crystal,
            target_gate=PromotionGate.P24_ENTERPRISE_PROMOTED,
            simulate_restore_failure=True,
        )

        assert result["status"] == "RETREAT_EXECUTED"
        assert result["failed_gate"] == PromotionGate.P20_RESTORE_VERIFIED.value
        assert "Restoration drill" in result["reason"]
        assert result["blast_radius_contained"] is True
    finally:
        _cleanup_crystal(node_id)


def test_evolution_engine_retreat_at_p22_canary():
    """First-Class RETREAT at P22: Shadow canary mutation variance observed."""
    node_id = "crystal_retreat_canary"
    engine = EnterpriseEvolutionEngine()
    crystal = _create_test_crystal(node_id)

    try:
        result = engine.evolve_capsule(
            crystal=crystal,
            target_gate=PromotionGate.P24_ENTERPRISE_PROMOTED,
            simulate_canary_divergence=True,
        )

        assert result["status"] == "RETREAT_EXECUTED"
        assert result["failed_gate"] == PromotionGate.P22_SHADOW_CANARY_PROVED.value
        assert "Shadow canary observed unauthorized mutation variance" in result["reason"]
        assert result["blast_radius_contained"] is True
    finally:
        _cleanup_crystal(node_id)
