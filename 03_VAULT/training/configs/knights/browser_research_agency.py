"""
browser_research_agency.py — Perplexity-killer Research Agency
==============================================================
Replaces paid Perplexity sonar-pro with browser-use nano-knights.
Maps TIER_CELLS → nano-knight roles, runs parallel web research,
synthesizes via Integration Brain ST, and persists to LT.

Tier → Cell → Nano-Knight mapping:
  signal_scout    → NanoApis   (primary source foraging)
  source_forager  → NanoApis   (expand coverage, parallel)
  memory_curator  → SirMnemo   (LT recall, no browser needed)
  evidence_weaver → NanoSyntax (structured extraction / synthesis)
  fact_verifier   → NanoDebug  (cross-check claims via live pages)
  sentinel_critic → NanoSentinel (risk, security, exposure audit)

Usage (from cloud_services.py):
    from knights.browser_research_agency import BrowserResearchAgency
    result = await BrowserResearchAgency().run(objective, tier="hybrid")

Usage (standalone):
    agency = BrowserResearchAgency()
    brief = agency.run_sync("What is the browser-use Python library?")
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ── Tier → cell → knight map ─────────────────────────────────────────────────

_CELL_KNIGHT: dict[str, str] = {
    "signal_scout":   "apis",
    "source_forager": "apis",
    "evidence_weaver":"syntax",
    "fact_verifier":  "debug",
    "sentinel_critic":"sentinel",
    # memory_curator handled locally via Integration Brain — no browser
}

_TIER_CELLS: dict[str, list[str]] = {
    "kinetic": ["signal_scout", "evidence_weaver", "sentinel_critic"],
    "hybrid":  ["signal_scout", "source_forager", "evidence_weaver", "sentinel_critic"],
    "apex":    ["signal_scout", "source_forager", "evidence_weaver",
                "fact_verifier", "sentinel_critic"],
}

_TIER_PARALLELISM: dict[str, int] = {"kinetic": 2, "hybrid": 4, "apex": 6}


# ── Research result ───────────────────────────────────────────────────────────

@dataclass
class CellResult:
    cell: str
    knight_id: str
    result: str
    urls: list[str]
    success: bool
    elapsed_ms: float


@dataclass
class ResearchBrief:
    objective: str
    tier: str
    cells: list[CellResult]
    synthesis: str
    memory_count: int
    elapsed_ms: float
    sources: list[str] = field(default_factory=list)
    production_ready: dict[str, bool] = field(default_factory=dict)

    def to_cloud_result(self) -> dict[str, Any]:
        return {
            "service": "browser_research_agency",
            "objective": self.objective,
            "tier": self.tier,
            "brief": self.synthesis,
            "memory_count": self.memory_count,
            "elapsed_ms": round(self.elapsed_ms),
            "sources": self.sources[:20],
            "cells": [
                {
                    "name": c.cell,
                    "knight": c.knight_id,
                    "success": c.success,
                    "result_preview": c.result[:300],
                    "urls": c.urls[:5],
                }
                for c in self.cells
            ],
            "production_ready": self.production_ready or {
                "browser_knights": all(c.success for c in self.cells),
                "integration_brain_stored": self.memory_count > 0,
                "synthesis_complete": bool(self.synthesis),
            },
            "deliverables": [
                f"[{c.cell}] {c.result[:200]}" for c in self.cells if c.success
            ],
            "recommended_next_steps": _next_steps(self),
        }


def _next_steps(brief: ResearchBrief) -> list[str]:
    steps = []
    failed = [c.cell for c in brief.cells if not c.success]
    if failed:
        steps.append(f"Re-run failed cells: {', '.join(failed)}")
    if brief.tier == "kinetic":
        steps.append("Escalate to hybrid tier for deeper source coverage.")
    if brief.tier in ("kinetic", "hybrid"):
        steps.append("Run apex tier for fact verification and sentinel critique.")
    steps.append("Review Integration Brain LT for persisted findings.")
    steps.append("Feed synthesis into NotebookLM for audio/slide artifact generation.")
    return steps[:4]


# ── Cell task builder ─────────────────────────────────────────────────────────

def _cell_task(cell: str, objective: str) -> str:
    prompts = {
        "signal_scout": (
            f"Research: {objective}\n\n"
            "Navigate to the most authoritative primary sources (official docs, GitHub, "
            "academic papers, news). Extract the key facts, version numbers, and relevant "
            "context. Return a structured summary with source URLs."
        ),
        "source_forager": (
            f"Expand research on: {objective}\n\n"
            "Find additional sources beyond the obvious: niche blogs, GitHub issues, "
            "conference talks, comparison articles, community discussions. "
            "Identify sources missed by a surface-level search. Extract URLs and key quotes."
        ),
        "evidence_weaver": (
            f"Synthesize findings on: {objective}\n\n"
            "Given what you find on the web, extract structured data: API signatures, "
            "benchmarks, feature lists, version comparisons, code examples. "
            "Return a dense structured report — no narrative fluff."
        ),
        "fact_verifier": (
            f"Verify and pressure-test claims about: {objective}\n\n"
            "Search for contradictions, known issues, bugs, deprecated features, "
            "or misleading documentation. Check GitHub issues, Stack Overflow, "
            "changelogs for known problems. Flag confidence level per claim."
        ),
        "sentinel_critic": (
            f"Security and risk audit for: {objective}\n\n"
            "Navigate to relevant security advisories, CVE databases, dependency "
            "vulnerability scanners. Identify supply chain risks, license conflicts, "
            "API key exposure patterns, and production deployment risks."
        ),
    }
    return prompts.get(cell, f"Research the following objective and return findings: {objective}")


# ── Integration Brain helpers ─────────────────────────────────────────────────

def _configs_dir() -> str:
    return str(Path(__file__).parent.parent)


async def _synthesize_via_ib(objective: str, cell_results: list[CellResult]) -> str:
    """Synthesize cell findings via Integration Brain ST (NotebookLM)."""
    try:
        d = _configs_dir()
        if d not in sys.path:
            sys.path.insert(0, d)
        from integration_brain import async_synthesize
        combined = "\n\n---\n\n".join(
            f"[{c.cell.upper()}]\n{c.result}" for c in cell_results if c.success
        )
        query = f"Synthesize research on: {objective}\n\n{combined[:4000]}"
        return await async_synthesize(query, tier="short")
    except Exception:
        # Fallback: concatenate top results
        parts = [c.result[:600] for c in cell_results if c.success]
        return "\n\n---\n\n".join(parts) if parts else "[no synthesis]"


async def _store_to_lt(objective: str, brief: ResearchBrief) -> int:
    """Persist research brief to Integration Brain LT. Returns count of memories."""
    try:
        d = _configs_dir()
        if d not in sys.path:
            sys.path.insert(0, d)
        from integration_brain import async_store, async_synthesize
        title = f"[RESEARCH] {objective[:80]}"
        body = (
            f"Objective: {objective}\n"
            f"Tier: {brief.tier} | Cells: {len(brief.cells)} | "
            f"Elapsed: {brief.elapsed_ms:.0f}ms\n\n"
            f"Synthesis:\n{brief.synthesis}\n\n"
            f"Sources:\n" + "\n".join(brief.sources[:15])
        )
        await async_store(title, body, tier="long")
        return 1
    except Exception:
        return 0


# ── Main orchestrator ─────────────────────────────────────────────────────────

class BrowserResearchAgency:
    """
    Perplexity-killer research engine.

    Runs browser nano-knights in parallel across TIER_CELLS,
    synthesizes results through Integration Brain, and returns
    a structured ResearchBrief compatible with modal_services
    ResearchAgencyResponse schema.
    """

    def __init__(self, tier: str = "hybrid"):
        self.tier = tier.lower()
        if self.tier not in _TIER_CELLS:
            self.tier = "hybrid"

    async def run(
        self,
        objective: str,
        *,
        tier: str | None = None,
        constraints: list[str] | None = None,
    ) -> ResearchBrief:
        t0 = time.perf_counter()
        effective_tier = (tier or self.tier).lower()
        if effective_tier not in _TIER_CELLS:
            effective_tier = "hybrid"

        cells_to_run = _TIER_CELLS[effective_tier]

        # Build per-knight tasks (deduplicate knight_id but run separate cell tasks)
        from .browser_nano_knight import _ROSTER, BrowserFeedback, _route_feedback

        async def _run_cell(cell: str) -> CellResult:
            kid = _CELL_KNIGHT.get(cell, "apis")
            KnightClass = _ROSTER.get(kid)
            if KnightClass is None:
                return CellResult(cell=cell, knight_id=kid, result="[no knight]",
                                  urls=[], success=False, elapsed_ms=0)
            knight = KnightClass()
            ct0 = time.perf_counter()
            task = _cell_task(cell, objective)
            try:
                fb = await knight.async_execute(task)
                return CellResult(
                    cell=cell,
                    knight_id=fb.knight_id,
                    result=fb.result,
                    urls=fb.urls_visited,
                    success=fb.success,
                    elapsed_ms=fb.elapsed_ms,
                )
            except Exception as e:
                return CellResult(
                    cell=cell, knight_id=kid,
                    result=f"[cell_error] {type(e).__name__}: {e}",
                    urls=[], success=False,
                    elapsed_ms=(time.perf_counter() - ct0) * 1000,
                )

        # Respect tier parallelism cap
        parallelism = _TIER_PARALLELISM[effective_tier]
        semaphore = asyncio.Semaphore(parallelism)

        async def _throttled_cell(cell: str) -> CellResult:
            async with semaphore:
                return await _run_cell(cell)

        cell_results = await asyncio.gather(*[_throttled_cell(c) for c in cells_to_run])
        cell_results = list(cell_results)

        # Synthesize
        synthesis = await _synthesize_via_ib(objective, cell_results)

        # Collect all URLs as sources
        all_urls: list[str] = []
        for cr in cell_results:
            all_urls.extend(cr.urls)
        sources = list(dict.fromkeys(all_urls))  # dedupe, preserve order

        elapsed = (time.perf_counter() - t0) * 1000
        brief = ResearchBrief(
            objective=objective,
            tier=effective_tier,
            cells=cell_results,
            synthesis=synthesis,
            memory_count=0,
            elapsed_ms=elapsed,
            sources=sources,
        )

        # Persist to LT (best-effort, non-blocking)
        mem_count = await _store_to_lt(objective, brief)
        brief.memory_count = mem_count

        return brief

    def run_sync(self, objective: str, **kwargs) -> ResearchBrief:
        try:
            return asyncio.run(self.run(objective, **kwargs))
        except RuntimeError:
            raise RuntimeError(
                "Already in async context — use `await BrowserResearchAgency().run(objective)`"
            )


# ── ScoutSonar drop-in replacement ───────────────────────────────────────────

class BrowserScout:
    """
    Drop-in replacement for ScoutSonar that uses browser nano-knights
    instead of the paid Perplexity API.

    Produces the same UKG RepoPhial schema output.
    """

    def __init__(self):
        self._agency = BrowserResearchAgency(tier="kinetic")

    def forage(self, query: str) -> list[dict[str, Any]]:
        brief = self._agency.run_sync(query)
        # Wrap synthesis into UKG RepoPhial format
        return [{
            "REPO": "browser-research-result",
            "DOMAIN": "Research",
            "LANGS": [],
            "LICENSE": "N/A",
            "RESOURCE_IMPACT": f"{brief.elapsed_ms:.0f}ms browser research",
            "TOKEN_IMPACT": f"{len(brief.synthesis)} chars synthesized",
            "ASSIMILATION_STRATEGY": brief.synthesis[:500],
            "SOURCES": brief.sources[:10],
            "CELLS_COMPLETED": [c.cell for c in brief.cells if c.success],
        }]

    async def async_forage(self, query: str) -> list[dict[str, Any]]:
        brief = await self._agency.run(query)
        return [{
            "REPO": "browser-research-result",
            "DOMAIN": "Research",
            "LANGS": [],
            "LICENSE": "N/A",
            "RESOURCE_IMPACT": f"{brief.elapsed_ms:.0f}ms browser research",
            "TOKEN_IMPACT": f"{len(brief.synthesis)} chars synthesized",
            "ASSIMILATION_STRATEGY": brief.synthesis[:500],
            "SOURCES": brief.sources[:10],
            "CELLS_COMPLETED": [c.cell for c in brief.cells if c.success],
        }]
