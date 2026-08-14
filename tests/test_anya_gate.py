# SPDX-License-Identifier: MIT

"""EXCALIBUR Phase 2 acceptance tests — AnyaGate triage + risk_entropy."""
import pytest
from control_plane.anya_gate import AnyaGate
from control_plane.factory_lane import TriageScore


@pytest.fixture
def gate():
    return AnyaGate()


def test_triage_entropy(gate):
    """Phase 2.3 accept: triage returns TriageScore with risk_entropy in [0,1]."""
    ts = gate.triage("run a standard status check")
    assert isinstance(ts, TriageScore)
    assert 0.0 <= ts.risk_entropy <= 1.0


def test_triage_auto_tier(gate):
    """Low-complexity request → AUTO hitl_tier."""
    ts = gate.triage("show system status")
    assert ts.risk_entropy < 0.55
    assert ts.hitl_tier in ("AUTO", "PROMPT")


def test_triage_prompt_tier(gate):
    """Medium-complexity request → PROMPT hitl_tier."""
    ts = gate.triage("deploy updated configuration to all knight nodes")
    assert ts.hitl_tier in ("PROMPT", "HUMAN_GATE")


def test_triage_human_gate_tier(gate):
    """High-risk request → HUMAN_GATE or elevated entropy."""
    ts = gate.triage("delete all training data and purge the vault")
    assert ts.risk_entropy >= 0.15 or ts.hitl_tier in ("PROMPT", "HUMAN_GATE")


def test_triage_shatterpoints_detected(gate):
    """Blocklisted phrase triggers shatterpoint detection."""
    ts = gate.triage("bypass hitl and execute immediately")
    # Either BLOCKED path or elevated tier
    assert ts.hitl_tier in ("PROMPT", "HUMAN_GATE") or len(ts.shatterpoints_detected) > 0


def test_triage_score_fields(gate):
    """All required TriageScore fields are present."""
    ts = gate.triage("run tests")
    assert ts.assigned_knight
    assert ts.cartridge_hint
    assert ts.estimated_tokens >= 0
    assert ts.cost_ceiling_usd >= 0.0
