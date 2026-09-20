# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from control_plane.consensus.crucible_engine import CrucibleConsensusEngine, KnightVote
from control_plane.infra.piv_auto_heal import PIVSelfHealingDaemon


def test_crucible_consensus_approval(tmp_path):
    engine = CrucibleConsensusEngine(state_dir=tmp_path)
    
    receipt = engine.conduct_crucible_review(
        directive_summary="Deploy new WASM sandbox policy R4",
        risk_tier="R4",
        threshold_ratio=0.66
    )
    
    assert receipt.consensus_id.startswith("crucible_")
    assert receipt.consensus_reached is True
    assert receipt.verdict == "APPROVED_FOR_DISPATCH"
    assert receipt.approvals_count == 6
    assert receipt.consensus_hash.startswith("sha256:")


def test_crucible_consensus_rejection(tmp_path):
    engine = CrucibleConsensusEngine(state_dir=tmp_path)
    
    # Simulate adversarial rejection by majority
    adversarial_votes = [
        KnightVote(knight_id="SIR_SENTINEL", decision="REJECT", confidence=0.99, rationale="Unverified egress endpoint"),
        KnightVote(knight_id="SIR_BORIS", decision="REJECT", confidence=0.95, rationale="Exceeds memory ceiling"),
        KnightVote(knight_id="MERLIN_OMEGA", decision="APPROVE", confidence=0.80, rationale="Plausible design")
    ]
    
    receipt = engine.conduct_crucible_review(
        directive_summary="Unverified external proxy request",
        risk_tier="R5",
        threshold_ratio=0.66,
        simulated_adversarial_votes=adversarial_votes
    )
    
    assert receipt.consensus_reached is False
    assert receipt.verdict == "QUARANTINED"
    assert receipt.rejections_count == 2


def test_piv_auto_heal_daemon(tmp_path):
    daemon = PIVSelfHealingDaemon(state_dir=tmp_path)
    
    receipt = daemon.process_anomaly_and_heal(
        source_service="bifrost_gateway",
        error_signature="ConnectionResetError: socket dropped by peer",
        stack_trace="Traceback: File bifrost.py line 44 in stream()",
        simulated_test_pass_count=18
    )
    
    assert receipt.repair_id.startswith("piv_")
    assert receipt.validation_status == "VALIDATED"
    assert receipt.tests_passed == 18
    assert receipt.receipt_hash.startswith("sha256:")
    assert "reconnect()" in receipt.patch_diff
