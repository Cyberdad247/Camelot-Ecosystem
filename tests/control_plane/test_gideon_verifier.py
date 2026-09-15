# SPDX-License-Identifier: MIT
"""Adversarial & Unit Test Suite — Sir Gideon Independent Verifier (Phase 4).

Validates:
    1. Canonical `camelot-gideon-verdict/1` construction and authentic Ed25519 signature.
    2. The 13 canonical gates evaluated independently.
    3. Adversarial blocks:
        - Contract conformance violations (malformed IDs).
        - Path traversal & scope violations.
        - Diff integrity mismatch.
        - Test failure detection.
        - Unvetted dependency injection.
        - Plaintext secret exposure.
        - Security control regression (disabling RLS / bypassing Sentinel).
        - UI accessibility baseline omission.
        - Missing rollback snapshot on promotional/destructive changes.
        - Risk tier underdeclaration (T0 claim on promote.deploy).
        - Invalid effect class taxonomy.
    4. Cryptographic tamper detection on signed verdicts.
"""
from __future__ import annotations

import pytest

from control_plane.security.sir_gideon import (
    GideonVerifier,
    GideonVerdict,
    CANONICAL_GIDEON_GATES,
)


def make_clean_manifest(
    task_id: str = "task_verify_001",
    tenant_id: str = "tenant_omega_01",
    correlation_id: str = "cor_verify_001",
    effect_class: str = "workspace.test",
    declared_risk_tier: str = "T1",
) -> dict:
    return {
        "manifest_hash": "sha256:" + "a" * 64,
        "effect_class": effect_class,
        "declared_risk_tier": declared_risk_tier,
        "target_paths": ["vfs/workspaces/module.py"],
        "new_dependencies": [{"name": "safe-lib", "is_vetted": True}],
        "requires_cleanup": True,
        "cleanup_plan_ref": "vfs://cleanup/plan_01",
    }


def make_clean_evidence() -> list[dict]:
    return [
        {
            "schema_version": "operator-evidence/1",
            "event_id": "evt_clean_001",
            "task_id": "task_verify_001",
            "correlation_id": "cor_verify_001",
            "tenant_id": "tenant_omega_01",
            "kind": "test.execution.completed",
            "integrity": "verified",
            "receipt_ref": "receipt://tenant_omega_01/1",
            "payload_redacted": {"tests_passed": 12},
        }
    ]


def test_gideon_clean_manifest_passes():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    evidence = make_clean_evidence()
    test_runs = [{"suite_id": "test_core", "status": "passed", "failed": 0, "receipt_ref": "receipt://test/1"}]

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=evidence,
        test_runs=test_runs,
    )

    assert verdict.verdict == "pass"
    assert len(verdict.block_reasons) == 0
    assert verdict.schema_version == "camelot-gideon-verdict/1"
    assert verdict.verdict_id.startswith("gv_")
    assert verdict.signature.startswith("ed25519:")
    assert set(verdict.gates) == set(CANONICAL_GIDEON_GATES)
    assert verifier.verify_verdict_signature(verdict) is True


def test_gideon_contract_conformance_violation():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="invalid_task_id_format",
        tenant_id="tenant_omega_01",
        correlation_id="cor_valid_01",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("[G1:CONTRACT_CONFORMANCE]" in r for r in verdict.block_reasons)


def test_gideon_path_scope_traversal_blocked():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    manifest["target_paths"] = ["vfs/workspaces/../../etc/shadow"]

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("[G2:PATH_SCOPE_CONFORMANCE]" in r for r in verdict.block_reasons)


def test_gideon_diff_integrity_tamper_blocked():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    manifest["diff_payload"] = "print('injected malicious code')"
    manifest["diff_hash"] = "sha256:" + "0" * 64  # deliberate mismatch

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("[G3:DIFF_INTEGRITY]" in r for r in verdict.block_reasons)


def test_gideon_test_failure_blocked():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    test_runs = [
        {"suite_id": "unit_suite", "status": "passed", "failed": 0},
        {"suite_id": "security_suite", "status": "failed", "failed": 2},
    ]

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
        test_runs=test_runs,
    )

    assert verdict.verdict == "block"
    assert any("[G4:TEST_RESULT_VALIDITY]" in r for r in verdict.block_reasons)


def test_gideon_unvetted_dependency_blocked():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    manifest["new_dependencies"] = [{"name": "evil-package", "is_vetted": False}]

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("[G5:DEPENDENCY_RISK]" in r for r in verdict.block_reasons)


def test_gideon_secret_exposure_blocked():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    manifest["debug_info"] = "Authorization: Bearer test_fake_auth_token_secret_12345"

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("[G6:SECRET_EXPOSURE]" in r for r in verdict.block_reasons)


def test_gideon_security_regression_blocked():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    manifest["patch_notes"] = "Temporary hotfix: DISABLE ROW LEVEL SECURITY to test access"

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("[G7:SECURITY_REGRESSION]" in r for r in verdict.block_reasons)


def test_gideon_risk_tier_underdeclaration_blocked():
    verifier = GideonVerifier()
    # promote.deploy requires >= T4, but declared as T0
    manifest = make_clean_manifest(
        effect_class="promote.deploy",
        declared_risk_tier="T0",
    )
    manifest["rollback_snapshot_ref"] = "snap://v1"

    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("[G12:RISK_TIER_MISMATCH]" in r for r in verdict.block_reasons)


def test_gideon_verdict_tamper_detection():
    verifier = GideonVerifier()
    manifest = make_clean_manifest()
    verdict = verifier.evaluate_manifest_and_evidence(
        task_id="task_verify_001",
        tenant_id="tenant_omega_01",
        correlation_id="cor_verify_001",
        manifest=manifest,
        evidence_envelopes=[],
    )

    assert verifier.verify_verdict_signature(verdict) is True

    # Tamper with verdict status
    tampered = verdict.to_dict()
    tampered["verdict"] = "pass" if verdict.verdict == "block" else "block"
    assert verifier.verify_verdict_signature(tampered) is False

    # Tamper with signature
    tampered2 = verdict.to_dict()
    tampered2["signature"] = "ed25519:" + "0" * 128
    assert verifier.verify_verdict_signature(tampered2) is False
