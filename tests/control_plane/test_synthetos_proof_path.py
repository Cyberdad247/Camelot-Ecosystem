# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Test Suite for Sir Synthetos First Executable Proof Path.
=============================================================
Validates:
    1. νKG crystal input
    2. Deterministic decompression (lossless, hash-stable)
    3. Sir Synthetos synthetic reference agent
    4. Merlin Architecture Delta
    5. Anya Enterprise Impact (Delta M <= 0.12 MiB, zero bypass)
    6. Complexity & Safety budget measurement
    7. Sir Gideon 13-gate audit
    8. King Arthur Sovereign Resolution
    9. Immutable camelot-receipt/2 commit to TenantReceiptChain
    10. Canonical UKG registration
    11. Zero-mutation guarantees (0 host writes, 0 installs, 0 policy changes)
"""
import hashlib
import json
import pytest

from control_plane.pipeline.synthetos_proof import (
    CanonicalUKGRegistry,
    DecompressedNode,
    NkgCrystal,
    SynthetosProofResult,
    deterministic_decompression,
    execute_synthetos_first_proof,
)
from control_plane.security.receipt_chain import TenantReceiptChain


def sample_crystal() -> NkgCrystal:
    payload = {
        "schema_version": "v10001.00",
        "crystal_type": "NKG_REFERENCE_SPEC",
        "components": [
            {"id": "comp_alpha", "type": "KERNEL_MODULE", "status": "ATTESTED"},
            {"id": "comp_beta", "type": "VFS_TETHER", "status": "ATTESTED"},
        ],
        "invariants": {
            "pure_proof": True,
            "zero_mutation": True,
            "lineage_depth": 23,
        },
    }
    canonical_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
    
    return NkgCrystal(
        node_id="synthetos_ref_node_01",
        vfs_coordinate="vfs://worldtree/crystals/synthetos_ref_01.nkg",
        glyph_symbol="Ω_SYNTHETOS_V1",
        compressed_payload=canonical_str,
        expected_hash=expected_hash,
        metadata={"author": "MERLIN_Ω", "target": "SIR_SYNTHETOS"},
    )


def test_deterministic_decompression_success():
    crystal = sample_crystal()
    node = deterministic_decompression(crystal)
    
    assert isinstance(node, DecompressedNode)
    assert node.node_id == "synthetos_ref_node_01"
    assert node.glyph_symbol == "Ω_SYNTHETOS_V1"
    assert node.decompression_hash == crystal.expected_hash
    assert node.decompressed_bytes > 0
    assert "components" in node.ast_tree


def test_deterministic_decompression_detects_tamper():
    crystal = sample_crystal()
    tampered_crystal = NkgCrystal(
        node_id=crystal.node_id,
        vfs_coordinate=crystal.vfs_coordinate,
        glyph_symbol=crystal.glyph_symbol,
        compressed_payload='{"tampered": true}',
        expected_hash=crystal.expected_hash,  # Expects original hash!
    )
    
    with pytest.raises(ValueError, match="Deterministic decompression hash mismatch"):
        deterministic_decompression(tampered_crystal)


def test_full_synthetos_first_proof_execution():
    crystal = sample_crystal()
    tenant_id = "tenant_synthetos_test"
    chain = TenantReceiptChain(tenant_id)
    ukg = CanonicalUKGRegistry()

    result = execute_synthetos_first_proof(
        crystal=crystal,
        tenant_id=tenant_id,
        tenant_chain=chain,
        ukg_registry=ukg,
    )

    # 1. Result Structure
    assert isinstance(result, SynthetosProofResult)
    assert result.status == "PASSED_PURE_PROOF"
    assert result.zero_mutation_verified is True
    assert result.execution_duration_ms > 0

    # 2. Decompression Parity
    assert result.decompression_hash == crystal.expected_hash

    # 3. Sir Synthetos Verification
    assert result.synthetos_verdict == "SYNTHETOS_VERIFIED"

    # 4. Merlin Architecture Delta
    assert result.architecture_delta.invariants_preserved is True
    assert result.architecture_delta.dependency_graph_acyclic is True
    assert result.architecture_delta.lineage_height == 23

    # 5. Anya Enterprise Impact
    assert result.enterprise_impact.bypass_detected is False
    assert result.enterprise_impact.taint_detected is False
    assert result.enterprise_impact.delta_m_mib <= 0.12
    assert result.enterprise_impact.gate_verdict == "ANYA_IS_THE_GATE_CLEARED"

    # 6. Complexity & Safety
    assert result.complexity_safety.simulated_memory_mb <= 12.0
    assert result.complexity_safety.risk_tier == "T1"
    assert result.complexity_safety.safety_rating == 1.0

    # 7. Sir Gideon 13-Gate Audit
    assert result.gideon_verdict.verdict == "pass"
    assert len(result.gideon_verdict.gates) >= 13
    assert len(result.gideon_verdict.block_reasons) == 0

    # 8. Arthur Sovereign Crown Resolution
    assert result.arthur_resolution.directive_type == "CONSENSUS_RATIFICATION"
    assert result.arthur_resolution.resolution_id.startswith("res_")

    # 9. Merkle Receipt
    assert result.receipt.effect_class == "workspace.test"
    assert result.receipt.event == "workspace.test.committed"
    assert result.receipt.proof.signer == "king-arthur"
    assert chain.chain_height == 1

    # 10. Canonical UKG Commit
    assert result.ukg_commit.node_id == crystal.node_id
    assert result.ukg_commit.receipt_id == result.receipt.receipt_id
    assert ukg.get_node(crystal.node_id) is not None
