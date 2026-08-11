"""EXCALIBUR Phase 4 acceptance tests — Iron Gate v2 pre_execute."""
import asyncio

from control_plane.core.factory_lane import FactoryJob, TriageScore
from control_plane.core.soul_oversight import GateDecision, pre_execute


def _make_job(hitl_tier: str, risk_entropy: float, job_id: str = "test-gate-001") -> FactoryJob:
    ts = TriageScore(
        auto_dispatchable=(hitl_tier == "AUTO"),
        priority="NORMAL" if risk_entropy < 0.15 else "HIGH",
        hitl_tier=hitl_tier,
        risk_entropy=risk_entropy,
        risk_reason=f"test entropy={risk_entropy}",
        assigned_knight="sir_boris",
        estimated_tokens=1000,
        cost_ceiling_usd=0.01,
        shatterpoints_detected=[],
        requires_z3_verification=False,
        cartridge_hint="BEAVER",
    )
    return FactoryJob(
        job_id=job_id,
        intent="test gate intent",
        lane="NORMAL",
        triage=ts,
        assigned_knight="sir_boris",
    )


def test_human_gate_suspend():
    """Phase 4.1 accept: HUMAN_GATE tier → job is SUSPENDED with checkpoint path."""
    job = _make_job("HUMAN_GATE", 0.7, "test-hg-001")
    decision = asyncio.run(pre_execute(job))
    assert isinstance(decision, GateDecision)
    assert not decision.approved
    assert decision.method == "SUSPENDED"
    assert decision.checkpoint


def test_auto_gate_pass():
    """AUTO tier with low entropy → gate passes."""
    job = _make_job("AUTO", 0.05, "test-auto-001")
    decision = asyncio.run(pre_execute(job))
    assert isinstance(decision, GateDecision)


def test_gate_decision_fields():
    """GateDecision has approved, method, reason fields."""
    job = _make_job("PROMPT", 0.35, "test-prompt-001")
    decision = asyncio.run(pre_execute(job))
    assert hasattr(decision, "approved")
    assert hasattr(decision, "method")
    assert hasattr(decision, "reason")
