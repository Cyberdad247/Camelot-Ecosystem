# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Tests for Firnflow Spill Gate, StateService Authority Spine, and VFS CAS Promoter
================================================================================
Verifies:
1. FirnFlow 90% RAM spill gate and cache flush to L3 disk.
2. StateService 5-point authority spine sequential progression.
3. StateService rejection of client-inferred completion (STATE_SERVICE_ONLY).
4. VFSPromoter content-addressed snapshot, atomic CAS head swap, and receipt generation.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest

from control_plane.infra.firnflow import FirnFlow
from control_plane.services.state_service import StateService, VALID_UI_STATES
from control_plane.services.vfs_promoter import VFSPromoter


def test_firnflow_spill_gate_and_flush():
    """Verify Firnflow flushes active L1 memory to L3 on trigger."""
    ff = FirnFlow()
    ff.anchor("session_alpha", "active context prompt text", "L1")
    assert len(ff._l1) >= 1

    # Force spill flush
    flush_res = ff.firnflow_cache_flush()
    assert flush_res["status"] == "FIRNFLOW_CACHE_FLUSH_COMPLETE"
    assert len(ff._l1) == 0
    assert ff._l1_tokens == 0

    # Test spill gate evaluation
    gate_res = ff.evaluate_spill_gate(force=True, is_server=False)
    assert gate_res["spill_gate_triggered"] is True
    assert gate_res["threshold_mb"] == 4096.0 * 0.90


def test_state_service_authority_spine_progression():
    """Verify full 5-point authority spine from PENDING to VERIFIED."""
    svc = StateService()
    proj_init = svc.register_mission("MSN-001", "SIR_HELIOS", "vfs://worldtree/crystals/crys_01.json")
    assert proj_init.state == "PENDING"
    assert proj_init.authority_cleared is False

    # 1. Sentinel lease
    proj_sentinel = svc.advance_authority_spine("MSN-001", "SENTINEL")
    assert proj_sentinel.state == "PENDING"

    # 2. Excalibur approval
    proj_excalibur = svc.advance_authority_spine("MSN-001", "EXCALIBUR")
    assert proj_excalibur.state == "APPROVED"

    # 3. Execution & Gideon proof
    proj_gideon = svc.advance_authority_spine("MSN-001", "GIDEON")
    assert proj_gideon.state == "EXECUTING"

    # 4. Arthur resolution
    proj_arthur = svc.advance_authority_spine("MSN-001", "ARTHUR")
    assert proj_arthur.state == "APPROVED"

    # 5. Ledger receipt admission
    proj_ledger = svc.advance_authority_spine("MSN-001", "LEDGER")
    assert proj_ledger.state == "VERIFIED"
    assert proj_ledger.authority_cleared is True
    assert proj_ledger.receipt_digest is not None
    assert "badge-MSN-001" in proj_ledger.badge_html


def test_state_service_rejects_client_inferred_completion():
    """Verify that StateService rejects client claims of VERIFIED without ledger receipt."""
    svc = StateService()
    svc.register_mission("MSN-002", "UNTRUSTED_CLIENT", "vfs://worldtree/target")

    # Client attempts to claim VERIFIED unilaterally
    proj = svc.project_ui_state("MSN-002", client_claimed_state="VERIFIED")
    assert proj.state == "DENIED"
    assert proj.authority_cleared is False


def test_vfs_promoter_cas_and_receipt():
    """Verify content-addressed snapshot and atomic CAS head swap."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        crystals_dir = tmp_path / "crystals"
        receipts_dir = tmp_path / "receipts"
        promoter = VFSPromoter(crystals_dir=crystals_dir, receipts_dir=receipts_dir)

        # Create staged source file
        source_file = tmp_path / "staged_crystal.json"
        source_file.write_text('{"pattern": "omega_leech_lattice"}', encoding="utf-8")

        # Promote
        receipt = promoter.promote_artifact(
            source_path=source_file,
            target_name="crystal_target.json",
            promoter_knight="SIR_HELIOS",
            expected_head_hash=None,
        )

        assert receipt.receipt_id.startswith("RCPT-PROMOTE-")
        assert receipt.target_uri == "vfs://worldtree/crystals/crystal_target.json"
        assert (crystals_dir / "crystal_target.json").exists()
        assert (receipts_dir / f"{receipt.receipt_id}.json").exists()

        # Test CAS mismatch error
        with pytest.raises(ValueError, match="CAS_HEAD_SWAP_CONFLICT"):
            promoter.promote_artifact(
                source_path=source_file,
                target_name="crystal_target.json",
                promoter_knight="SIR_HELIOS",
                expected_head_hash="incorrect_hash",
            )
