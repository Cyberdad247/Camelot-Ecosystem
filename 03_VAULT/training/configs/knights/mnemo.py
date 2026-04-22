"""SIR_MNEMO — Memory Routing Knight
L4 Semantic layer guardian. Owns all Integration Brain routing decisions.
Score-based tier resolution: ST (NotebookLM) | LT (Modal/Appwrite) | both.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any

from .base import BaseKnight


# ── Routing signals ──────────────────────────────────────────────────────────

_LT_STRONG = frozenset({
    "archive", "permanent", "sovereign", "ledger", "long-term",
    "persist", "remember forever", "store permanently",
})
_LT_WEAK = frozenset({
    "store", "recall", "search", "history", "catalog", "index",
    "vault", "remember", "log", "record",
})
_ST_STRONG = frozenset({
    "now", "current", "session", "quick", "synthesize", "plan",
    "summarize", "draft", "today", "this task",
})

# Content size thresholds
_SIZE_LT_BYTES   = 8_000   # > 8KB → prefer LT
_SIZE_BOTH_BYTES = 2_000   # > 2KB → both


@dataclass
class RouteSignal:
    """Scoring vector for a single routing decision."""
    lt_score: float = 0.0
    st_score: float = 0.0
    reasons:  list[str] = field(default_factory=list)

    @property
    def tier(self) -> str:
        if self.lt_score >= 6.0:
            return "long"
        if self.lt_score >= 3.0:
            return "both"
        return "short"


@dataclass
class MemoryRoute:
    tier:    str          # "short" | "long" | "both"
    score:   RouteSignal
    latency: float        # ms


class SirMnemo(BaseKnight):
    name      = "SIR_MNEMO"
    title     = "Memory Routing Knight"
    specialty = "Integration Brain tier routing — ST/LT/both signal scoring"
    icon      = "[M]"

    # ── Public routing API ───────────────────────────────────────────────────

    def route_query(self, query: str, context: dict | None = None) -> MemoryRoute:
        """Score a synthesis/read query and return the optimal memory tier."""
        t0 = time.perf_counter()
        sig = RouteSignal()
        self._score_keywords(query, sig)
        self._score_context(context or {}, sig)
        lat = (time.perf_counter() - t0) * 1000
        return MemoryRoute(tier=sig.tier, score=sig, latency=lat)

    def route_store(self, content: str, tags: list[str] | None = None) -> MemoryRoute:
        """Score a write operation and return the optimal storage tier."""
        t0 = time.perf_counter()
        sig = RouteSignal()
        tags = [t.lower() for t in (tags or [])]

        # Size signal
        size = len(content.encode())
        if size > _SIZE_LT_BYTES:
            sig.lt_score += 4.0
            sig.reasons.append(f"content large ({size}B > {_SIZE_LT_BYTES}B)")
        elif size > _SIZE_BOTH_BYTES:
            sig.lt_score += 2.0
            sig.reasons.append(f"content medium ({size}B)")

        # Tag signals
        for tag in tags:
            if tag in _LT_STRONG:
                sig.lt_score += 5.0
                sig.reasons.append(f"LT-strong tag: {tag}")
            elif tag in _LT_WEAK:
                sig.lt_score += 2.0
                sig.reasons.append(f"LT-weak tag: {tag}")

        # Keyword scan on content header (first 200 chars)
        self._score_keywords(content[:200], sig)
        lat = (time.perf_counter() - t0) * 1000
        return MemoryRoute(tier=sig.tier, score=sig, latency=lat)

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        route = self.route_query(directive, context=intent)
        return {
            "status":        "success",
            "output":        f"Memory routed → tier={route.tier} (lt_score={route.score.lt_score:.1f})",
            "tier":          route.tier,
            "reasons":       route.score.reasons,
            "latency_ms":    round(route.latency, 2),
            "files_created": [],
        }

    # ── Internal scoring ─────────────────────────────────────────────────────

    def _score_keywords(self, text: str, sig: RouteSignal) -> None:
        lower = text.lower()
        for kw in _LT_STRONG:
            if kw in lower:
                sig.lt_score += 4.0
                sig.reasons.append(f"LT-strong kw: {kw}")
        for kw in _LT_WEAK:
            if kw in lower:
                sig.lt_score += 1.5
                sig.reasons.append(f"LT-weak kw: {kw}")
        for kw in _ST_STRONG:
            if kw in lower:
                sig.st_score += 2.0
                # ST signals reduce LT score
                sig.lt_score = max(0.0, sig.lt_score - 1.0)
                sig.reasons.append(f"ST-strong kw: {kw}")

    def _score_context(self, ctx: dict, sig: RouteSignal) -> None:
        # Explicit tier hint from caller
        hint = str(ctx.get("tier", "")).lower()
        if hint in ("long", "both", "archive"):
            sig.lt_score += 6.0
            sig.reasons.append(f"explicit tier hint: {hint}")
        elif hint == "short":
            sig.st_score += 6.0
            sig.reasons.append("explicit tier hint: short")

        # Complexity signal — high complexity → long-term
        complexity = float(ctx.get("complexity", 0.0))
        if complexity >= 0.8:
            sig.lt_score += 2.0
            sig.reasons.append(f"high complexity: {complexity}")

        # Knight identity — sentinel/archivist always goes to LT
        knight = str(ctx.get("knight", "")).lower()
        if "archivist" in knight or "sentinel" in knight:
            sig.lt_score += 3.0
            sig.reasons.append(f"archivist/sentinel knight: {knight}")


# Module-level singleton
_mnemo = SirMnemo()


def route_query(query: str, context: dict | None = None) -> MemoryRoute:
    return _mnemo.route_query(query, context)


def route_store(content: str, tags: list[str] | None = None) -> MemoryRoute:
    return _mnemo.route_store(content, tags)
