"""P1-T02 — verify ColMAD 3-persona crucible is wired into the AnyaGate pipeline.

A CRITICAL-lane / HUMAN_GATE intent must trigger a ColMAD debate (3 persona
votes) surfaced on the APEEResult; a benign low-risk intent must not.
"""
from __future__ import annotations

from control_plane.core.anya_gate import AnyaGate, _stage_colmad
from control_plane.core.colmad import CrucibleVerdict

CRITICAL_INTENT = "delete all production databases and drop every table"
BENIGN_INTENT = "build a small helper to add two numbers"


def test_critical_intent_triggers_three_persona_vote():
    gate = AnyaGate()
    result = gate.process(CRITICAL_INTENT)

    assert result.colmad_verdict is not None, "CRITICAL intent did not trigger ColMAD"
    assert isinstance(result.colmad_verdict, CrucibleVerdict)
    assert len(result.colmad_verdict.votes) == 3, "expected exactly 3 persona votes"
    # A destructive, hand-waving proposal should fail consensus -> HUMAN_GATE
    assert result.colmad_verdict.verdict in ("APPROVED", "HUMAN_GATE")


def test_benign_intent_skips_colmad():
    gate = AnyaGate()
    result = gate.process(BENIGN_INTENT)
    assert result.colmad_verdict is None, "benign intent should not run ColMAD"


def test_stage_colmad_gates_on_triage():
    gate = AnyaGate()
    crit_triage = gate.triage(CRITICAL_INTENT)
    assert crit_triage.priority == "CRITICAL" or crit_triage.hitl_tier == "HUMAN_GATE"
    verdict = _stage_colmad(CRITICAL_INTENT, crit_triage)
    assert verdict is not None and len(verdict.votes) == 3

    benign_triage = gate.triage(BENIGN_INTENT)
    assert _stage_colmad(BENIGN_INTENT, benign_triage) is None


def test_render_includes_colmad_line_for_critical():
    gate = AnyaGate()
    rendered = gate.process(CRITICAL_INTENT).render()
    assert "COLMAD" in rendered
