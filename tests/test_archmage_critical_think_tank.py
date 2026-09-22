# SPDX-License-Identifier: MIT
"""
Unit test for the 9-Seat Archmage Order Critical Thinking & Think-Tank Deliberation Engine.
Fuses //Critical Thinking, //Think-Tank, grill-me skill, and majority vote consensus.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure 01_KERNEL is importable at the FRONT of sys.path (unconditional).
# The full suite collects modules that prepend other entries containing a
# colliding top-level ``merlin.py`` (03_VAULT/training/configs); a guarded
# insert would leave 01_KERNEL behind it and ``import merlin`` would bind
# the file module instead of the 01_KERNEL/merlin package.
repo_root = Path(__file__).resolve().parent.parent
kernel_path = str(repo_root / "01_KERNEL")
if kernel_path in sys.path:
    sys.path.remove(kernel_path)
sys.path.insert(0, kernel_path)

from control_plane.runes.critical_thinking import Evidence, deliberate_with_archmage_order
from merlin.council.critical_think_tank_order import (
    ARCHMAGE_ORDER,
    FORMAL_ORACLE_SOLVERS,
    VOTING_MODELS,
    ArchmageCriticalThinkTankEngine,
    RigorLevel,
    VoteDecision,
)


def test_archmage_order_roster():
    """Verify all 9 Archmage seats, 5 voting models, and 5 formal solvers are present."""
    assert len(ARCHMAGE_ORDER) == 9
    assert len(VOTING_MODELS) == 5
    assert len(FORMAL_ORACLE_SOLVERS) == 5

    seat_names = [s.name for s in ARCHMAGE_ORDER]
    assert "Arithmos the Quantizer" in seat_names
    assert "Geometra the Tensor Mage" in seat_names
    assert "Chronos the Scheduler" in seat_names
    assert "Entropia the Oracle" in seat_names
    assert "Graphael the Cartographer" in seat_names
    assert "Cypherion the Cryptarch" in seat_names
    assert "Controlia the Steerswoman" in seat_names
    assert "Formalis the Runekeeper" in seat_names
    assert "Optimus the Summoner" in seat_names


def test_critical_thinking_and_think_tank_loop():
    """Test full deliberation loop with grill-me questions and majority consensus."""
    engine = ArchmageCriticalThinkTankEngine()

    objective = "Ensure zero-latency voice routing under 4GB RAM ceiling"
    evidence = [
        {"claim": "Shared memory IPC is < 15ms", "source": "Bifrost benchmark", "confidence": 0.95},
        {"claim": "Unpruned 56-agent state takes 8.2GB", "source": "Colony telemetry", "confidence": 0.90},
    ]
    constraints = [
        "Host RAM ceiling <= 4.0GB",
        "Sub-100ms voice response latency",
    ]

    ct_state, rounds, verdict = engine.run_full_council_deliberation(
        objective=objective,
        evidence=evidence,
        constraints=constraints,
        max_rounds=2,
    )

    assert ct_state.qualified is True
    assert len(ct_state.assumptions_grilled) >= 2
    assert len(rounds) >= 1
    assert len(rounds[0].cross_grill_dialogue) >= 4

    # Verify Majority Vote Consensus
    assert verdict.reached is True
    assert verdict.archmage_tally["AYE"] >= 5
    assert verdict.model_tally["AYE"] >= 3
    assert verdict.rigor_tier == RigorLevel.L3_MACHINE_CHECKED_PROOF
    assert len(verdict.ratified_invariants) >= 5


def test_control_plane_deliberation_integration():
    """Test integration via control_plane.runes.critical_thinking."""
    objective = "Verify formal mathematical bounds on memory and scheduling"
    evidence = [
        Evidence(claim="IPC latency bounded at 12ms", source="POSIX shm", confidence=0.92),
    ]
    constraints = ["Strict zero-leakage security boundary"]

    frame, rounds, verdict = deliberate_with_archmage_order(
        objective=objective,
        evidence=evidence,
        constraints=constraints,
    )

    assert frame.objective == objective
    assert any("DONE: Archmage majority vote consensus achieved" in d for d in frame.decisions)
    assert verdict.reached is True
    assert len(verdict.ratified_invariants) > 0
