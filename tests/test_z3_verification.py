# SPDX-License-Identifier: MIT

"""P2-T02 — real Z3 patch verification acceptance tests.

A known-dangerous patch must be Z3_BLOCK'd; a benign patch must pass. The
Iron Gate (soul_oversight.pre_execute) must surface Z3_BLOCK for a
z3-required dangerous job.
"""
from __future__ import annotations

import asyncio

import pytest
from control_plane.factory_lane import FactoryJob, TriageScore
from control_plane.soul_oversight import GateDecision, pre_execute
from control_plane.z3_verify import PatchIntent, verify_patch

z3 = pytest.importorskip("z3")


def test_benign_patch_passes():
    v = verify_patch(PatchIntent("add bounded retry logic to api.py"))
    assert v.verdict == "Z3_PASS"
    assert v.safe


@pytest.mark.parametrize("text,inv", [
    ("git push --force origin main", "main_branch_protected"),
    ("rm the provenance ledger audit trail", "provenance_intact"),
    ("disable the HITL approval gate", "hitl_gate_enabled"),
    ("drop database camelot", "boot_capable"),
])
def test_dangerous_patches_blocked(text, inv):
    v = verify_patch(PatchIntent(text))
    assert v.verdict == "Z3_BLOCK"
    assert not v.safe
    assert inv in v.violated


def test_iron_gate_surfaces_z3_block():
    ts = TriageScore(
        auto_dispatchable=False, priority="CRITICAL", hitl_tier="HUMAN_GATE",
        risk_entropy=0.9, risk_reason="git push --force origin main",
        assigned_knight="sir_boris", estimated_tokens=100, cost_ceiling_usd=0.0,
        shatterpoints_detected=["destructive_git"], requires_z3_verification=True,
        cartridge_hint="DEFAULT",
    )
    job = FactoryJob(job_id="z3-danger", intent="force push to main and overwrite",
                     lane="CRITICAL", triage=ts, assigned_knight="sir_boris")
    decision = asyncio.run(pre_execute(job))
    assert isinstance(decision, GateDecision)
    assert decision.method == "Z3_BLOCK"
    assert not decision.approved
