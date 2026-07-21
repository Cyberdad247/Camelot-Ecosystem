"""control_plane/omniroute_policies.py — SELECT_OPTIMAL_FRAMEWORK_O1 lane signals.

Implements the Omni-Router Matrix lane-selection policy from the Camelot-OS
v1000 spec items 1a + 1b. Specifically:

* Item 1a — "Route low-latency, rapid boilerplate scaffolding through
  OmniRoute (:20128) directly to SIR_CODEX."  Lands at ``LANE_OMNI_ROUTE_CODEX``.
* Item 1b — "Route massive reasoning/deep-context tasks through
  CLIProxyAPI (:8080) for heavy Cloud Brain computing."  Lands at
  ``LANE_CLIPROXY_HEAVY_REASONING``.

This module is a **lane signal**, NOT a gate.  It composes with — and never
replaces — ``control_plane.soul_oversight.pre_execute`` (Iron Gate v2 three
tier HITL).  The Iron Gate is the only thing that can flip a HUMAN_GATE
class move to ``DENY``.  See ``AGENTS.md`` Iron Gate and the Father's Camelot
Compass for the binding ruling.

Conventions:

* Stdlib only — no pydantic import.  Consumers (factory_lane, runic_router)
  can wrap ``LaneSignal`` if they need a ``BaseModel`` compat layer; the
  underlying dataclass is intentionally minimal so this module can be
  loaded before any heavy deps (Tailscale node identity, pyo3 bindings,
  etc.) without import-order surprises.

* Stateless.  No global module state, no singletons.  ``select_lane`` is
  pure given its text input.

* Permission posture: a lane signal never escalates tier, never promotes
  AUTO → PROMPT → HUMAN_GATE.  Promotion is exclusively the Iron Gate's
  prerogative.

References:

* AGENTS.md Iron Gate ("Audit new third-party dependencies … do not invent
  unavailable skills").
* AGENTS.md Runic Command System (``//FORGE``, ``$//CODEX$``, ``$//STATUS$``,
  and the ``Omega_*`` dispatch lanes — the lane signal module respects
  them all).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

# ── Lane enum ──────────────────────────────────────────────────────────────

LANE_OMNI_ROUTE_CODEX: str = "omni_route_codex"
"""Low-latency, rapid boilerplate scaffold lane.  Selects SIR_CODEX via
OmniRoute :20128."""

LANE_CLIPROXY_HEAVY_REASONING: str = "cliproxy_heavy_reasoning"
"""Deep-context, >1M-context reasoning lane.  Selects the Polyglot Matrix
(typically SIR_BORIS / SIR_HELIOS / MERLIN_OMEGA) via CLIProxyAPI :8080."""

LANE_DEFAULT: str = "default"
"""No lane preference.  Punts to ``factory_lane``'s default dispatch."""

VALID_LANES: frozenset = frozenset(
    {LANE_OMNI_ROUTE_CODEX, LANE_CLIPROXY_HEAVY_REASONING, LANE_DEFAULT}
)

# ── Keyword sets (paper-derived from spec items 1a + 1b plus roster
#    dispatch keywords per `.claude/agents/sir-codex.md`).

SCAFFOLD_KEYWORDS: Tuple[str, ...] = (
    "scaffold",
    "boilerplate",
    "prototype",
    "rapid",
    "velocity",
    "codex",
    "fast_gen",
    "iteration",
)
"""Keywords that route to ``LANE_OMNI_ROUTE_CODEX``.  Aligned with the
SIR_CODEX dispatch keyword list."""

REASONING_KEYWORDS: Tuple[str, ...] = (
    "deep-context",
    "reasoning",
    "cloud_brain",
    "merlin",
    "1m-context",
    "context_window",
)
"""Keywords that route to ``LANE_CLIPROXY_HEAVY_REASONING``.  Aligned with
the deep-context / 1M-token reasoning cluster (SIR_HELIOS, MERLIN_OMEGA,
SIR_BORIS).

Priority note: ``deep-context`` precedes ``reasoning`` so the more specific
keyword wins when an intent contains both (e.g. "deep-context reasoning over
1M-context").  This keeps Cloud-Brain reasoning context for genuine
deep-context work and avoids the trivial "scaffold a reasoning demo" path
mis-classifying as heavy-reasoning.
"""


# ── LaneSignal: small, frozen, hashable, no pydantic ─────────────────────────


@dataclass(frozen=True)
class LaneSignal:
    """A lane selection recommendation.  NEVER a gate decision.

    Attributes:
        lane:             one of ``VALID_LANES``.
        rationale:        human-readable explanation (cite-friendly).
        matched_keyword:  the keyword that triggered the selection, or
                          empty string for ``LANE_DEFAULT``.
    """

    lane: str
    rationale: str
    matched_keyword: str = ""

    def __post_init__(self) -> None:
        if self.lane not in VALID_LANES:
            # sorted(frozenset) is non-deterministic across Python runs; use
            # a hand-typed tuple for stable error strings.
            _expected = (
                "cliproxy_heavy_reasoning",
                "default",
                "omni_route_codex",
            )
            raise ValueError(
                f"unknown lane {self.lane!r}; expected one of "
                f"{list(_expected)}"
            )

    @classmethod
    def default(cls) -> "LaneSignal":
        """The default lane signal — no policy triggered."""
        return cls(
            lane=LANE_DEFAULT,
            rationale="no SELECT_OPTIMAL framework_o1 policy triggered",
            matched_keyword="",
        )


# ── Selector ────────────────────────────────────────────────────────────────


def _match_first(text_lower: str, keywords: Tuple[str, ...]) -> Tuple[bool, str]:
    """Return ``(True, kw)`` for the first keyword matched in ``text_lower``,
    else ``(False, "")``.  Iteration order of the keyword tuple is therefore
    the canonical priority order."""
    for kw in keywords:
        if kw in text_lower:
            return True, kw
    return False, ""


def select_lane(intent_text: str) -> LaneSignal:
    """SELECT_OPTIMAL_FRAMEWORK_O1 selector.  Pure function.  Lane only.

    Args:
        intent_text: the runic / harness / void-edge directive text.  May be
            ``None`` or empty — handled by short-circuiting to default.

    Returns:
        ``LaneSignal`` whose ``lane`` is one of ``VALID_LANES``.  Never raises
        on ordinary input (only on unknown lane strings, which should never
        happen if you construct ``LaneSignal(lane=...)`` correctly).
    """
    if not intent_text:
        return LaneSignal.default()

    needle = intent_text.lower()
    matched, kw = _match_first(needle, SCAFFOLD_KEYWORDS)
    if matched:
        return LaneSignal(
            lane=LANE_OMNI_ROUTE_CODEX,
            rationale=(
                f"scaffold keyword {kw!r} matched -> OmniRoute (:20128) -> "
                "SIR_CODEX (Velocity Forge); fast boilerplate lane [paper ref 1, 2]"
            ),
            matched_keyword=kw,
        )
    matched, kw = _match_first(needle, REASONING_KEYWORDS)
    if matched:
        return LaneSignal(
            lane=LANE_CLIPROXY_HEAVY_REASONING,
            rationale=(
                f"deep-context keyword {kw!r} matched -> CLIProxyAPI (:8080) -> "
                "Polyglot Matrix; heavy Cloud Brain lane [paper ref 4]"
            ),
            matched_keyword=kw,
        )
    return LaneSignal.default()


# ── Self-test (run via ``python -m control_plane.omniroute_policies --test``) ──


def _run_self_test() -> int:
    """Surface ALL four lane categorisations + one invariant.

    Returns:
        0 on success, 1 on any failure.
    """
    cases = [
        ("//CODEX scaffold a hello-world Rust project", LANE_OMNI_ROUTE_CODEX, "scaffold"),
        ("MERLIN deep-context reasoning over 1m-context window",
         LANE_CLIPROXY_HEAVY_REASONING, "deep-context"),
        ("//STATUS", LANE_DEFAULT, ""),
        ("", LANE_DEFAULT, ""),        ("   ", LANE_DEFAULT, ""),
        (
            "iterate a prototype crud stub",
            LANE_OMNI_ROUTE_CODEX,
            "prototype",
        ),  # SCAFFOLD_KEYWORDS tuple order: prototype precedes iteration
    ]   
    failures = 0
    for text, expected_lane, expected_kw in cases:
        sig = select_lane(text)
        ok = sig.lane == expected_lane and sig.matched_keyword == expected_kw
        prefix = "[OK]" if ok else "[FAIL]"
        print(
            f"{prefix} input={text!r:50s} -> lane={sig.lane!r:30s} "
            f"kw={sig.matched_keyword!r:12s} rationale={sig.rationale}"
        )
        if not ok:
            failures += 1

    # ── Invariant: select_lane is pure ─────────────────────────────────────
    a = select_lane("//CODEX scaffold")
    b = select_lane("//CODEX scaffold")
    if a != b:
        print(f"[FAIL] select_lane not pure (a={a!r}, b={b!r})")
        failures += 1
    else:
        print("[OK] select_lane is idempotent (a == b on repeat call)")

    if failures == 0:
        print("\nomniroute_policies self-test: 6/6 PASS")
        return 0
    print(f"\nomniroute_policies self-test: {failures} FAIL(s)")
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(_run_self_test())
