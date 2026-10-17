# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for Camelot-OS Production Readiness Verification Suite."""

import pytest
from scripts.verify_production_readiness import (
    run_full_production_verification,
    verify_pillar_1_process_governance,
    verify_pillar_2_webmcp_integrity,
    verify_pillar_3_offline_and_mesh_assets,
    verify_pillar_4_telemetry_and_log_rotation,
    verify_pillar_5_provenance_mirror_parity,
)


def test_pillar_1_process_governance():
    res = verify_pillar_1_process_governance()
    assert res.status == "PASS"
    assert res.details["docker_detected"] == 0


def test_pillar_2_webmcp_integrity():
    res = verify_pillar_2_webmcp_integrity()
    assert res.status == "PASS"
    assert res.details["rate_limiting_enforced"] is True
    assert res.details["cryptographic_receipts_enforced"] is True


def test_pillar_3_offline_assets():
    res = verify_pillar_3_offline_and_mesh_assets()
    assert res.status == "PASS"
    assert res.details["dark_mesh_offline_page_present"] is True


def test_pillar_4_telemetry_rotation():
    res = verify_pillar_4_telemetry_and_log_rotation()
    assert res.status == "PASS"
    assert res.details["sir_ghost_redaction_verified"] is True
    assert res.details["resident_memory_sampled"] is True


def test_pillar_5_provenance_mirror_parity():
    res = verify_pillar_5_provenance_mirror_parity()
    assert res.status == "PASS"
    assert len(res.details["mismatches"]) == 0


def test_full_production_readiness_pass():
    receipt = run_full_production_verification()
    assert receipt.overall_status == "PRODUCTION_READY"
    assert len(receipt.pillars) == 5
    assert len(receipt.receipt_hash) == 64
