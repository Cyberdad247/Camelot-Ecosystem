"""P2-T01 — Kinetic Execution Loop acceptance tests.

The loop must fire all six stages in canonical order
(TRIAGE → PLAN → APPROVE → EXECUTE → VERIFY → RECORD) for an approved run, and
halt at APPROVE for a CRITICAL intent when auto_approve is off.
"""
from __future__ import annotations

from control_plane.kinetic_loop import STAGE_ORDER, KineticLoop, Stage, run_sync


def test_six_stages_fire_in_order():
    res = run_sync("build a small status dashboard", auto_approve=True)
    assert res.stages_fired == list(STAGE_ORDER)
    assert res.complete
    assert [s.value for s in res.stages_fired] == [
        "TRIAGE", "PLAN", "APPROVE", "EXECUTE", "VERIFY", "RECORD"
    ]


def test_output_and_provenance_recorded():
    res = run_sync("create a greeting string", auto_approve=True)
    assert res.output
    assert res.provenance_ref is not None
    assert res.gate_decision is not None


def test_critical_intent_halts_at_approve():
    res = run_sync("delete all production databases and drop every table",
                   auto_approve=False)
    assert res.halted_at == Stage.APPROVE
    assert not res.complete
    assert Stage.EXECUTE not in res.stages_fired


def test_injected_executor_is_used():
    res = run_sync("create a greeting string",
                   executor=lambda job, apee: "CUSTOM", auto_approve=True)
    assert res.output == "CUSTOM"


def test_async_executor_awaited():
    async def aexec(job, apee):
        return "ASYNC_OK"
    loop = KineticLoop(executor=aexec)
    import asyncio
    res = asyncio.run(loop.run("build a thing", auto_approve=True))
    assert res.output == "ASYNC_OK"
    assert res.complete
