# SPDX-License-Identifier: MIT
"""Adversarial & Unit Test Suite — King Arthur Sovereign Resolution Governor (Phase 4).

Validates:
    1. Canonical `camelot-arthur-resolution/1` construction and Ed25519 Sovereign Seal.
    2. Verification of authentic resolutions and tamper detection.
    3. Revocation blocking ($R_{\text{revocation}} > 0$).
    4. Mandatory Sovereign Seal for high-risk tiers (T3, T4).
    5. Gideon block gating and Sovereign Override resolution authorization.
    6. Atomic append to `TenantReceiptChain` upon sovereign authorization.
"""
from __future__ import annotations

import pytest

from control_plane.security.arthur_resolution import (
    ArthurResolutionGovernor,
    ArthurResolutionError,
    ArthurResolution,
)
from control_plane.security.receipt_chain import TenantReceiptChain
from control_plane.security.sir_gideon import GideonVerifier, GideonVerdict


def make_sample_gideon_verdict(verdict: str = "pass") -> GideonVerdict:
    verifier = GideonVerifier()
    manifest = {
        "manifest_hash": "sha256:" + "b" * 64,
        "effect_class": "workspace.test",
        "declared_risk_tier": "T1",
        "target_paths": ["vfs/workspaces/test.py"],
        "requires_cleanup": True,
        "cleanup_plan_ref": "vfs://cleanup/plan_01",
    }
    return verifier.evaluate_manifest_and_evidence(
        task_id="task_arthur_01",
        tenant_id="tenant_omega_01",
        correlation_id="cor_arthur_01",
        manifest=manifest,
        evidence_envelopes=[],
    )


def test_arthur_resolution_creation_and_verification():
    gov = ArthurResolutionGovernor()
    res = gov.create_resolution(
        directive_type="CONSENSUS_RATIFICATION",
        target_scope="task_arthur_01",
        rationale="Unanimous 13-agent Crucible consensus verified.",
        authority_vector=[1, 1, 0, 1, 1, 1],
        seal_type="SOVEREIGN_GOLDEN_SEAL",
    )

    assert res.schema_version == "camelot-arthur-resolution/1"
    assert res.resolution_id.startswith("res_")
    assert res.directive_type == "CONSENSUS_RATIFICATION"
    assert res.sovereign_seal["king_id"] == "ARTHUR_OMEGA"
    assert res.sovereign_seal["seal_type"] == "SOVEREIGN_GOLDEN_SEAL"
    assert res.sovereign_seal["ed25519_signature"].startswith("ed25519:")

    # Verify signature
    assert gov.verify_resolution(res) is True

    # Tamper with rationale
    tampered = res.to_dict()
    tampered["rationale"] = "Modified rationale without re-signing."
    assert gov.verify_resolution(tampered) is False


def test_arthur_resolution_invalid_parameters():
    gov = ArthurResolutionGovernor()

    with pytest.raises(ArthurResolutionError):
        gov.create_resolution(
            directive_type="INVALID_DIRECTIVE",
            target_scope="task_1",
            rationale="test",
            authority_vector=[1, 1, 0, 1, 1, 1],
        )

    with pytest.raises(ArthurResolutionError):
        gov.create_resolution(
            directive_type="CONSENSUS_RATIFICATION",
            target_scope="task_1",
            rationale="test",
            authority_vector=[1, 1, -1, 1],  # wrong length and negative
        )


def test_authorize_and_commit_standard_success():
    gov = ArthurResolutionGovernor()
    chain = TenantReceiptChain("tenant_omega_01")
    verdict = make_sample_gideon_verdict(verdict="pass")

    assert chain.chain_height == 0

    receipt = gov.authorize_and_commit_receipt(
        chain=chain,
        task_id="task_arthur_01",
        correlation_id="cor_arthur_01",
        effect_class="workspace.test",
        declared_risk_tier="T1",
        gideon_verdict=verdict,
        authority_vector=[1, 1, 0, 1, 1, 1],
    )

    assert chain.chain_height == 1
    assert receipt.receipt_id.startswith("rec_")
    assert receipt.tenant_id == "tenant_omega_01"
    assert receipt.parent_hash.startswith("sha256:00000000")
    assert chain.head_hash == receipt.self_hash


def test_authorize_and_commit_blocked_by_active_revocation():
    gov = ArthurResolutionGovernor()
    chain = TenantReceiptChain("tenant_omega_01")
    verdict = make_sample_gideon_verdict(verdict="pass")

    # Authority vector has R_revocation = 2 (active revocation)
    with pytest.raises(ArthurResolutionError) as exc_info:
        gov.authorize_and_commit_receipt(
            chain=chain,
            task_id="task_arthur_01",
            correlation_id="cor_arthur_01",
            effect_class="workspace.test",
            declared_risk_tier="T1",
            gideon_verdict=verdict,
            authority_vector=[1, 1, 2, 1, 1, 1],
        )

    assert "[REVOCATION_BLOCKED]" in str(exc_info.value)
    assert chain.chain_height == 0


def test_high_risk_tier_requires_arthur_resolution():
    gov = ArthurResolutionGovernor()
    chain = TenantReceiptChain("tenant_omega_01")
    verdict = make_sample_gideon_verdict(verdict="pass")

    # T4 action (promote.deploy) without resolution must fail
    with pytest.raises(ArthurResolutionError) as exc_info:
        gov.authorize_and_commit_receipt(
            chain=chain,
            task_id="task_arthur_01",
            correlation_id="cor_arthur_01",
            effect_class="promote.deploy",
            declared_risk_tier="T4",
            gideon_verdict=verdict,
            authority_vector=[1, 1, 0, 1, 1, 1],
            resolution=None,
        )

    assert "[ARTHUR_CROWN_REQUIRED]" in str(exc_info.value)

    # Now create authentic Arthur Resolution
    res = gov.create_resolution(
        directive_type="PROMOTION_AUTHORIZATION",
        target_scope="task_arthur_01",
        rationale="Production deployment authorized by King Arthur.",
        authority_vector=[1, 1, 0, 1, 1, 1],
        seal_type="SOVEREIGN_GOLDEN_SEAL",
    )

    receipt = gov.authorize_and_commit_receipt(
        chain=chain,
        task_id="task_arthur_01",
        correlation_id="cor_arthur_01",
        effect_class="promote.deploy",
        declared_risk_tier="T4",
        gideon_verdict=verdict,
        authority_vector=[1, 1, 0, 1, 1, 1],
        resolution=res,
    )

    assert chain.chain_height == 1
    assert receipt.declared_risk_tier == "T4"


def test_sovereign_override_of_gideon_block():
    gov = ArthurResolutionGovernor()
    verifier = GideonVerifier()
    chain = TenantReceiptChain("tenant_omega_01")

    # Manifest with a flaw that causes Gideon to block
    flawed_manifest = {
        "manifest_hash": "sha256:" + "c" * 64,
        "effect_class": "workspace.patch",
        "declared_risk_tier": "T2",
        "patch_notes": "Emergency hotfix bypassing test temporarily",
    }
    test_runs = [{"suite_id": "flaky_test", "status": "failed", "failed": 1}]

    gideon_verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_arthur_01",
        tenant_id="tenant_omega_01",
        correlation_id="cor_arthur_01",
        manifest=flawed_manifest,
        evidence_envelopes=[],
        test_runs=test_runs,
    )
    assert gideon_verdict.verdict == "block"

    # Attempting to commit without override raises error
    with pytest.raises(ArthurResolutionError) as exc_info:
        gov.authorize_and_commit_receipt(
            chain=chain,
            task_id="task_arthur_01",
            correlation_id="cor_arthur_01",
            effect_class="workspace.patch",
            declared_risk_tier="T2",
            gideon_verdict=gideon_verdict,
            authority_vector=[1, 1, 0, 1, 1, 1],
        )
    assert "[GIDEON_GATE_BLOCKED]" in str(exc_info.value)

    # King Arthur issues explicit SOVEREIGN_OVERRIDE
    override_res = gov.create_resolution(
        directive_type="SOVEREIGN_OVERRIDE",
        target_scope="task_arthur_01",
        rationale="Emergency disaster recovery patch authorized with audited rollback plan.",
        authority_vector=[1, 1, 0, 1, 1, 1],
        seal_type="SOVEREIGN_GOLDEN_SEAL",
    )

    receipt = gov.authorize_and_commit_receipt(
        chain=chain,
        task_id="task_arthur_01",
        correlation_id="cor_arthur_01",
        effect_class="workspace.patch",
        declared_risk_tier="T2",
        gideon_verdict=gideon_verdict,
        authority_vector=[1, 1, 0, 1, 1, 1],
        resolution=override_res,
    )

    assert chain.chain_height == 1
    assert receipt.self_hash.startswith("sha256:")
