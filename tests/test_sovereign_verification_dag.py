# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
End-to-End Test Suite for Sovereign System Verification DAG.
Tests topological execution, gate enforcement, error handling, and DAG hash generation.
"""

import pytest
from control_plane.infra.sovereign_verification_dag import (
    SovereignVerificationDAG,
    Node01_HardwareScarcity,
    Node02_SecurityIngress,
    Node03_MemoryVFS,
    Node04_CognitiveRouting,
    Node05_LocalA2UINexus,
)


def test_sovereign_dag_full_execution_passes():
    dag = SovereignVerificationDAG(is_server=False, remediate=False)
    receipt = dag.execute_all()

    assert receipt.overall_status == "ALL_GATES_PASSED"
    assert len(receipt.gate_results) == 5
    assert all(g.passed for g in receipt.gate_results)
    assert len(receipt.dag_hash) == 64
    assert receipt.execution_time_ms > 0


def test_node01_hardware_scarcity_node_and_server_boundaries():
    # Node evaluation (4096 MB)
    res_node = Node01_HardwareScarcity.evaluate(is_server=False)
    assert res_node.passed is True
    assert res_node.metrics["ceiling_mb"] == 4096.0
    assert res_node.metrics["working_set_mb"] < 4096.0

    # Server evaluation (8192 MB)
    res_server = Node01_HardwareScarcity.evaluate(is_server=True)
    assert res_server.passed is True
    assert res_server.metrics["ceiling_mb"] == 8192.0


def test_node02_security_ingress_blocks_danger():
    res = Node02_SecurityIngress.evaluate(sample_payload="git push --force origin main")
    assert res.passed is False
    assert "destructive_force_push" in res.error_message


def test_node03_memory_vfs_lookup_within_72us():
    res = Node03_MemoryVFS.evaluate()
    assert res.passed is True
    assert res.latency_us < 72.0
    assert res.metrics["uri_scheme_canonical"] is True


def test_node04_z3_cognitive_routing_invariants():
    res = Node04_CognitiveRouting.evaluate()
    assert res.passed is True
    assert res.metrics["benign_sat_proof"] == "Z3_PASS"
    assert res.metrics["malicious_unsat_proof"] == "Z3_BLOCK"
    assert "provenance_intact" in res.metrics["invariants_protected"]


def test_node05_local_a2ui_nexus_cls():
    res = Node05_LocalA2UINexus.evaluate()
    assert res.passed is True
    assert res.metrics["cumulative_layout_shift"] == 0.00
