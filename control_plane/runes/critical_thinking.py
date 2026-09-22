# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    confidence: float = 0.5
    note: str = ""


@dataclass
class CriticalThinkingFrame:
    objective: str
    facts: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    def add_fact(self, fact: str) -> None:
        text = fact.strip()
        if text:
            self.facts.append(text)

    def add_assumption(self, assumption: str) -> None:
        text = assumption.strip()
        if text:
            self.assumptions.append(text)

    def add_risk(self, risk: str) -> None:
        text = risk.strip()
        if text:
            self.risks.append(text)

    def add_decision(self, decision: str) -> None:
        text = decision.strip()
        if text:
            self.decisions.append(text)

    def add_next_action(self, action: str) -> None:
        text = action.strip()
        if text:
            self.next_actions.append(text)


def assimilate_evidence(evidence: Iterable[Evidence]) -> list[str]:
    """Reduce evidence into a ranked list of critical-thinking observations.

    This is the universal skill-layer analog of Portkey's gateway behavior:
    keep the best-supported claims, retain fallback signals, and make the
    confidence boundary explicit.
    """

    ordered = sorted(evidence, key=lambda item: item.confidence, reverse=True)
    summaries: list[str] = []
    for item in ordered:
        confidence_label = "high" if item.confidence >= 0.8 else "medium" if item.confidence >= 0.5 else "low"
        note = f" ({item.note})" if item.note else ""
        summaries.append(f"[{confidence_label}] {item.claim} <- {item.source}{note}")
    return summaries


def build_thinking_frame(
    objective: str,
    *,
    evidence: Iterable[Evidence] | None = None,
    constraints: Iterable[str] | None = None,
) -> CriticalThinkingFrame:
    frame = CriticalThinkingFrame(objective=objective.strip())
    for item in evidence or []:
        frame.add_fact(f"{item.claim} [{item.source}]")
        if item.confidence < 0.5:
            frame.add_assumption(f"Low-confidence claim to verify: {item.claim}")
    for constraint in constraints or []:
        frame.add_risk(constraint)
    return frame


def qualify_frame(frame: CriticalThinkingFrame) -> list[str]:
    """Apply the PAUL-style plan/apply/unify loop to a thinking frame."""

    checks: list[str] = []
    if not frame.objective:
        checks.append("BLOCKED: objective is missing")
    if not frame.facts:
        checks.append("NEEDS_CONTEXT: no verified facts collected")
    if not frame.next_actions and not frame.decisions:
        checks.append("NEEDS_CONTEXT: no decision or next action recorded")
    if not checks:
        checks.append("DONE: frame is qualified")
    return checks


def universal_knight_protocol(
    objective: str,
    *,
    evidence: Iterable[Evidence] | None = None,
    constraints: Iterable[str] | None = None,
) -> CriticalThinkingFrame:
    """Create the shared critical-thinking frame for all Camelot knights."""

    frame = build_thinking_frame(objective, evidence=evidence, constraints=constraints)
    summaries = assimilate_evidence(evidence or [])
    for summary in summaries:
        frame.add_fact(summary)
    qualification = qualify_frame(frame)
    for item in qualification:
        frame.add_decision(item)
    if qualification and qualification[0].startswith("DONE"):
        frame.add_next_action("Proceed with verified implementation")
    else:
        frame.add_next_action("Collect missing context before execution")
    return frame


def deliberate_with_archmage_order(
    objective: str,
    *,
    evidence: Iterable[Evidence] | None = None,
    constraints: Iterable[str] | None = None,
    max_rounds: int = 3,
) -> tuple[CriticalThinkingFrame, list[Any], Any]:
    """Execute the composite deliberation loop fusing Critical Thinking, Think-Tank debate, and Grill-Me stress testing across the 9-Seat Archmage Order."""
    try:
        import sys
        from pathlib import Path
        kernel_path = str(Path(__file__).resolve().parent.parent.parent / "01_KERNEL")
        # Unconditional front-insertion: other sys.path entries may hold a
        # colliding top-level ``merlin.py`` (03_VAULT/training/configs).
        if kernel_path in sys.path:
            sys.path.remove(kernel_path)
        sys.path.insert(0, kernel_path)
        from merlin.council.critical_think_tank_order import ArchmageCriticalThinkTankEngine
    except ImportError:
        import importlib
        mod = importlib.import_module("01_KERNEL.merlin.council.critical_think_tank_order")
        ArchmageCriticalThinkTankEngine = getattr(mod, "ArchmageCriticalThinkTankEngine")

    engine = ArchmageCriticalThinkTankEngine()
    frame = universal_knight_protocol(objective, evidence=evidence, constraints=constraints)

    raw_evidence = [
        {"claim": e.claim, "source": e.source, "confidence": e.confidence, "note": e.note}
        for e in (evidence or [])
    ]
    raw_constraints = list(constraints or [])

    ct_state, rounds, verdict = engine.run_full_council_deliberation(
        objective=objective,
        evidence=raw_evidence,
        constraints=raw_constraints,
        max_rounds=max_rounds,
    )

    if verdict.reached:
        frame.decisions = [d for d in frame.decisions if not d.startswith("NEEDS_CONTEXT")]
        frame.add_decision("DONE: Archmage majority vote consensus achieved at Rigor L3")
        for invariant in verdict.ratified_invariants:
            frame.add_decision(f"ARCHMAGE_RATIFIED: {invariant}")
        frame.next_actions = ["Proceed with verified implementation under ratified invariants"]
    else:
        for invariant in verdict.ratified_invariants:
            frame.add_decision(f"ARCHMAGE_RATIFIED: {invariant}")

    return frame, rounds, verdict


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CAMELOT Critical Thinking & Archmage Think-Tank Deliberation Engine")
    parser.add_argument("--objective", type=str, default="Architectural verification of zero-latency voice & agent mesh under 4GB RAM ceiling", help="Objective statement")
    parser.add_argument("--archmages", action="store_true", help="Deliberate with the 9-Seat Archmage Order and Grill-Me Protocol")
    args = parser.parse_args()

    sample_ev = [
        Evidence(claim="Shared memory POSIX IPC latency < 15ms", source="Bifrost benchmark", confidence=0.95),
        Evidence(claim="Unpruned 56-agent resident memory reaches 8.2GB", source="Colony telemetry", confidence=0.90),
        Evidence(claim="Ternary 1.58-bit quantization retains 98.4% reasoning capacity", source="DeepSeek-Math eval", confidence=0.85),
    ]
    sample_con = [
        "Hard 4.0GB RAM host ceiling (Scarcity Protocol)",
        "Zero token leakage across security boundary",
        "Sub-100ms VAD voice response time",
    ]

    if args.archmages:
        print(f"=== Convening 9-Seat Archmage Council Deliberation for: {args.objective} ===")
        frame, rounds, verdict = deliberate_with_archmage_order(args.objective, evidence=sample_ev, constraints=sample_con)
        print(f"\n[CRITICAL THINKING QUALIFIED]: {frame.decisions}")
        print(f"\n[THINK-TANK VERDICT]: {verdict.summary_of_consensus}")
        print("\n[RATIFIED INVARIANTS]:")
        for inv in verdict.ratified_invariants:
            print(f"  * {inv}")
    else:
        f = universal_knight_protocol(args.objective, evidence=sample_ev, constraints=sample_con)
        print(f"Frame objective: {f.objective}")
        print(f"Facts: {f.facts}")
        print(f"Decisions: {f.decisions}")


