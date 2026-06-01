"""SENTINEL squire — HITL gate. Blocks destructive operations pending human approval."""
from __future__ import annotations
import sys
from typing import Callable

from .judge import Verdict


class HITLBlocked(Exception):
    """Raised when user denies a SENTINEL gate."""


def gate(verdict: Verdict, action_label: str = "proceed", *, auto_approve: bool = False) -> bool:
    """
    Interactive HITL gate. Returns True if approved, raises HITLBlocked if denied.

    If auto_approve is True (e.g. CI mode), bypasses prompt and returns True.
    """
    if auto_approve:
        return True

    if not verdict.requires_hitl:
        return True

    _print_verdict(verdict)
    print(f"\n⚠️  SENTINEL GATE — Risk score {verdict.risk_score:.1f} ({verdict.risk_label})")
    print(f"   Action: {action_label}")
    print("   Approve? [y/N] ", end="", flush=True)

    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer in ("y", "yes"):
        print("✅ SENTINEL: Approved.")
        return True
    else:
        raise HITLBlocked(f"SENTINEL: '{action_label}' denied by operator.")


def _print_verdict(verdict: Verdict) -> None:
    labels = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
    icon = labels.get(verdict.risk_label, "⚪")
    print(f"\n{icon} Risk Assessment: {verdict.risk_label} ({verdict.risk_score:.1f}/100)")
    for f in verdict.findings:
        print(f"   • {f}")
    if verdict.recommendations:
        print("   Recommendations:")
        for r in verdict.recommendations:
            print(f"     → {r}")


def soft_gate(verdict: Verdict) -> None:
    """Non-blocking display of verdict. Used for read-only operations."""
    _print_verdict(verdict)
