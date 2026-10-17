# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Unit and Integration Test Suite for Master Production DAG (vMAX).
Verifies all 7 phases, VFS scaffolding, process governor, mesh bridge,
Z3 formal gate, 10-line diff firewall, and ledger commit anchoring.
"""

import pytest
from control_plane.infra.master_production_dag import MasterProductionDAG
from control_plane.infra.process_governor import BareMetalProcessGovernor
from control_plane.infra.vfs_scaffolder import VFSScaffolder
from control_plane.infra.bifrost_mesh_bridge import BifrostMeshBridge


def test_vfs_scaffolder_contract_files_materialized():
    scaffolder = VFSScaffolder()
    receipt = scaffolder.scaffold()
    assert receipt.status == "SCAFFOLD_CONVERGED"
    assert len(receipt.missing_files) == 0
    assert "blueprint.md" in receipt.contract_files_verified
    assert "tasks.md" in receipt.contract_files_verified
    assert "verification.md" in receipt.contract_files_verified
    assert "task.md" in receipt.contract_files_verified
    assert "harness.md" in receipt.contract_files_verified


def test_process_governor_enforces_boundaries():
    # Node profile (4096 MB)
    gov_node = BareMetalProcessGovernor(is_server=False)
    audit_node = gov_node.inspect_system()
    assert audit_node.ceiling_mb == 4096.0
    assert audit_node.current_working_set_mb < 4096.0
    assert audit_node.status in ("BOUNDARIES_NOMINAL", "PRESSURE_THROTTLED")

    # Server profile (8192 MB)
    gov_server = BareMetalProcessGovernor(is_server=True)
    audit_server = gov_server.inspect_system()
    assert audit_server.ceiling_mb == 8192.0


def test_bifrost_mesh_bridge_kyber_handshake():
    bridge = BifrostMeshBridge()
    audit = bridge.audit_mesh()
    assert audit.kyber_handshake_verified is True
    assert "cybertronia" in audit.active_mesh_peers
    assert "vashawns-s26-ultra" in audit.active_mesh_peers


def test_master_production_dag_full_pipeline_active():
    engine = MasterProductionDAG(is_server=False)
    receipt = engine.execute_full_pipeline(staged_diff_lines=5, dry_run=True)
    assert receipt.overall_status == "PRODUCTION_DEPLOY_ACTIVE"
    assert len(receipt.phases) == 7
    assert all(p.passed for p in receipt.phases)
    assert receipt.cryptographic_seal.startswith("0x")


def test_iron_gate_2_diff_firewall_blocks_large_diff_without_token():
    engine = MasterProductionDAG(is_server=False, operator_token=None)
    # Diff of 25 lines exceeds the 10-line firewall
    receipt = engine.execute_full_pipeline(staged_diff_lines=25)
    assert receipt.overall_status == "DEPLOYMENT_HALTED"
    p6 = next(p for p in receipt.phases if p.phase_id == "P6_EXCALIBUR_WARRANT")
    assert p6.passed is False
    assert "exceeds 10-line limit" in p6.error_message


def test_iron_gate_2_diff_firewall_allows_large_diff_with_token():
    engine = MasterProductionDAG(is_server=False, operator_token="OPERATOR_AUTHORIZED_SECRET")
    receipt = engine.execute_full_pipeline(staged_diff_lines=25)
    assert receipt.overall_status == "PRODUCTION_DEPLOY_ACTIVE"
    p6 = next(p for p in receipt.phases if p.phase_id == "P6_EXCALIBUR_WARRANT")
    assert p6.passed is True
    assert p6.details["hitl_approval_status"] == "AUTHORIZED_VIA_TOKEN"
