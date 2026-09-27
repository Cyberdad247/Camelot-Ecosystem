# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for PaladinCrucibleEngine (Phase 4 Z3 Formal Prover).
"""
from __future__ import annotations

from control_plane.infra.paladin_crucible import PaladinCrucibleEngine

def test_paladin_crucible_memory_boundedness():
    engine = PaladinCrucibleEngine()
    obligation = engine.prove_memory_boundedness()
    assert obligation.verified is True
    assert "Memory bounds verified" in obligation.detail or "cgroups" in obligation.detail

def test_paladin_crucible_rls_isolation():
    engine = PaladinCrucibleEngine()
    obligation = engine.prove_rls_isolation()
    assert obligation.verified is True
    assert "Zero cross-tenant leakage" in obligation.detail or "static AST" in obligation.detail

def test_paladin_crucible_cloud_decapitation():
    engine = PaladinCrucibleEngine()
    obligation = engine.prove_cloud_decapitation()
    assert obligation.verified is True
    assert obligation.obligation_id == "OBLIGATION_4_CLOUD_DECAPITATION"

def test_paladin_crucible_full_run():
    engine = PaladinCrucibleEngine()
    verdict = engine.execute_crucible()
    assert verdict.status == "Z3_PASS"
    assert verdict.all_obligations_satisfied is True
    assert len(verdict.proof_obligations) == 4
    assert len(verdict.ed25519_seal_hash) == 64
