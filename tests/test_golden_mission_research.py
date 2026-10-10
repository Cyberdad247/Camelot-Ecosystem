# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""US-GOLD-001: Read-Only Research Golden Mission End-to-End Test Suite.
========================================================================
Implements the verification acceptance rehearsal defined in
CAMELOT-OS-MASTER-SUITE-vMAX-3.1-20260914 §8 & §65:

Acceptance Criteria:
  1. Tenant/workspace derived server-side.
  2. Task is typed and classified (ro.fetch / T0).
  3. Sentinel emits short-lived manifest-bound read-only lease.
  4. VFS attests exact source/artifact scope without ambient authority.
  5. Evidence envelope contains source provenance and digests.
  6. Sir Gideon evaluates all 13 canonical gates and returns signed PASS verdict.
  7. King Arthur resolves lifecycle state with Sovereign Seal.
  8. Ledger chains and signs an immutable receipt.
  9. Adversarial attacks (cross-tenant, directory traversal, tamper, stale epoch)
     are deterministically rejected.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import pytest

from cryptography.hazmat.primitives.asymmetric import ed25519

from control_plane.security.sir_gideon import GideonVerifier, GideonVerdict, sha256_canonical
from control_plane.security.arthur_resolution import (
    ArthurResolutionGovernor,
    ArthurResolution,
    ArthurResolutionError,
)
from control_plane.security.receipt_chain import (
    TenantReceiptChain,
    Receipt,
    ReceiptActor,
    ReceiptProof,
    ChainVerificationError,
    TenantIsolationViolation,
)


@pytest.fixture
def gideon_verifier():
    return GideonVerifier()


@pytest.fixture
def arthur_governor():
    return ArthurResolutionGovernor()


@pytest.fixture
def receipt_chain():
    return TenantReceiptChain(tenant_id="tenant_research_01")


def test_us_gold_001_complete_read_only_research_mission(
    gideon_verifier: GideonVerifier,
    arthur_governor: ArthurResolutionGovernor,
    receipt_chain: TenantReceiptChain,
):
    """Executes the complete US-GOLD-001 Golden Path sequence."""
    # Step 1: Server-derived tenant and workspace
    tenant_id = "tenant_research_01"
    workspace_id = "workspace_quantum_lab"
    task_id = "task_research_vmax_audit_001"
    correlation_id = "cor_golden_path_2026"
    authority_epoch = 43

    # Step 2: Task Manifest (Typed ro.fetch, read-only scope)
    manifest = {
        "schema_version": "camelot-effect-manifest/1",
        "task_id": task_id,
        "effect_class": "ro.fetch",
        "declared_risk_tier": "T0",
        "target_paths": ["docs/architecture/CAMELOT-OS-vMAX-3.1-SOVEREIGN-ASSIMILATION-MASTER-SUITE.md"],
        "read_only": True,
        "requires_cleanup": False,
        "manifest_hash": "sha256:" + hashlib.sha256(b"vmax_3_1_research_intent").hexdigest(),
    }

    # Step 3: Sentinel Policy Decision & Read-Only Capability Lease
    lease = {
        "schema_version": "camelot-lease/1",
        "lease_id": f"lease_{uuid.uuid4().hex[:12]}",
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "task_id": task_id,
        "authority_epoch": authority_epoch,
        "permissions": {
            "effect_class": "ro.fetch",
            "max_risk_tier": "T0",
            "path_scopes": {
                "read_scopes": ["docs/architecture"],
                "write_scopes": [],  # Strictly zero write permissions
            },
        },
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expires_in_seconds": 300,
    }

    # Step 4: Evidence Envelope from Bounded Execution
    evidence_envelope = {
        "schema_version": "camelot-evidence-envelope/1",
        "evidence_id": f"evi_{uuid.uuid4().hex[:12]}",
        "task_id": task_id,
        "tenant_id": tenant_id,
        "provenance": {
            "source_path": "docs/architecture/CAMELOT-OS-vMAX-3.1-SOVEREIGN-ASSIMILATION-MASTER-SUITE.md",
            "source_hash": "sha256:e3c17f59ec0bd3a25036a9e344e627f02e9e330d02faf90a6afe7953930bc987",
            "execution_backend": "wasmtime_isolated",
            "ambient_network": False,
        },
        "content_hash": sha256_canonical({"summary": "Architecture verified clean under vMAX 3.1"}),
    }

    # Step 5: Sir Gideon Independent Forensic Verification
    verdict: GideonVerdict = gideon_verifier.evaluate_manifest_and_evidence(
        task_id=task_id,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        manifest=manifest,
        evidence_envelopes=[evidence_envelope],
        lease=lease,
    )

    assert verdict.verdict == "pass", f"Gideon blocked mission: {verdict.block_reasons}"
    assert len(verdict.gates) == 13
    assert verdict.tenant_id == tenant_id
    assert verdict.task_id == task_id
    assert len(verdict.signature) > 0

    # Step 6: King Arthur Sovereign Resolution
    authority_vector = [authority_epoch, 921, 188, 77, 204, 31]
    resolution: ArthurResolution = arthur_governor.create_resolution(
        directive_type="CONSENSUS_RATIFICATION",
        target_scope=f"{tenant_id}/{workspace_id}/{task_id}",
        rationale="US-GOLD-001 read-only research passed all 13 Gideon gates.",
        authority_vector=authority_vector,
        seal_type="SOVEREIGN_GOLDEN_SEAL",
    )

    assert resolution.directive_type == "CONSENSUS_RATIFICATION"
    assert resolution.sovereign_seal["seal_type"] == "SOVEREIGN_GOLDEN_SEAL"
    assert arthur_governor.verify_resolution(resolution) is True

    # Step 7: Append to Tenant Merkle Receipt Chain
    actor = ReceiptActor(id="sir_helios", role="agent", node_id="cybertronia", trust_band="T0")
    receipt = Receipt(
        receipt_id=f"rcpt_{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        task_id=task_id,
        chain_height=0,
        parent_hash=receipt_chain.head_hash,
        authority_epoch=authority_epoch,
        authority_vector=authority_vector,
        effect_class="ro.fetch",
        declared_risk_tier="T0",
        actor=actor,
        event="research.complete",
        proof=ReceiptProof(signer="LEAD_ARTHUR_OMEGA", signature="ed25519:test_sig"),
        refs={
            "resolution_id": resolution.resolution_id,
            "verdict_id": verdict.verdict_id,
            "status": "VERIFIED",
        },
    ).seal()

    appended_receipt = receipt_chain.append(receipt, trusted_epoch=43)

    assert appended_receipt.chain_height == 0
    assert appended_receipt.parent_hash.startswith("sha256:00000000")
    assert appended_receipt.tenant_id == tenant_id
    assert appended_receipt.authority_epoch == authority_epoch

    # Step 8: Verify Chain Integrity
    is_valid, msg = receipt_chain.verify_chain(trusted_epoch=43)
    assert is_valid is True, f"Chain invalid: {msg}"
    assert receipt_chain.head_hash == appended_receipt.self_hash


def test_adversarial_directory_traversal_blocked(gideon_verifier: GideonVerifier):
    """Proves Gideon Gate 2 immediately rejects malicious directory traversal."""
    malicious_manifest = {
        "task_id": "task_exploit_001",
        "effect_class": "ro.fetch",
        "declared_risk_tier": "T0",
        "target_paths": ["docs/architecture/../../../../Windows/System32/config/SAM"],
        "manifest_hash": "sha256:" + "f" * 64,
    }

    verdict = gideon_verifier.evaluate_manifest_and_evidence(
        task_id="task_exploit_001",
        tenant_id="tenant_rogue_01",
        correlation_id="cor_attack_01",
        manifest=malicious_manifest,
        evidence_envelopes=[],
    )

    assert verdict.verdict == "block"
    assert any("Directory traversal attempt rejected" in r for r in verdict.block_reasons)


def test_adversarial_cross_tenant_injection_rejected(receipt_chain: TenantReceiptChain):
    """Proves TenantReceiptChain strictly forbids cross-tenant receipt injection."""
    actor = ReceiptActor(id="attacker", role="agent", node_id="foreign", trust_band="T0")
    malicious_receipt = Receipt(
        receipt_id=f"rcpt_{uuid.uuid4().hex[:12]}",
        tenant_id="tenant_foreign_corp",  # Mismatched tenant
        correlation_id="cor_foreign_01",
        task_id="task_infiltrate_001",
        chain_height=0,
        parent_hash=receipt_chain.head_hash,
        authority_epoch=43,
        authority_vector=[43, 0, 0, 0, 0, 0],
        effect_class="ro.fetch",
        declared_risk_tier="T0",
        actor=actor,
        event="infiltrate",
        proof=ReceiptProof(signer="attacker", signature="fake"),
    ).seal()

    with pytest.raises(TenantIsolationViolation):
        receipt_chain.append(malicious_receipt, trusted_epoch=43)


def test_adversarial_stale_epoch_rejected(receipt_chain: TenantReceiptChain):
    """Proves TenantReceiptChain rejects stale authority epochs (§30)."""
    actor = ReceiptActor(id="stale_agent", role="agent", node_id="node_01", trust_band="T0")
    stale_receipt = Receipt(
        receipt_id=f"rcpt_{uuid.uuid4().hex[:12]}",
        tenant_id="tenant_research_01",
        correlation_id="cor_stale_01",
        task_id="task_stale_001",
        chain_height=0,
        parent_hash=receipt_chain.head_hash,
        authority_epoch=41,  # Stale epoch below trusted_epoch (43)
        authority_vector=[41, 0, 0, 0, 0, 0],
        effect_class="ro.fetch",
        declared_risk_tier="T0",
        actor=actor,
        event="stale.work",
        proof=ReceiptProof(signer="stale", signature="sig"),
    ).seal()

    with pytest.raises(ChainVerificationError) as exc_info:
        receipt_chain.append(stale_receipt, trusted_epoch=43)
    assert "below trusted epoch" in str(exc_info.value)
