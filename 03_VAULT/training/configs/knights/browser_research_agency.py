"""
browser_research_agency.py — Perplexity-killer Research Agency
  + NotebookLM Brain Ancestor + CHIMERA Rounds
=============================================================
Full 5-phase pipeline:

  Phase 0  ANCESTOR QUERY   — NotebookLM canonical notebook seeded as prior
  Phase 1  BROWSER CELLS    — nano-knights run in parallel (TIER_CELLS)
  Phase 2  CHIMERA ROUNDS   — 3-round sequential refinement via LLM + NLM
    Round 1 (Sir Octavian)    Semantic Auditing   — score sources, filter noise
    Round 2 (Merlin/Videneptus) Topology Shift    — map narrative topology
    Round 3 (Sir Myrmidon)    Anchor Compression  — compress to dense brief
  Phase 3  SYNTHESIS        — Integration Brain ST (NotebookLM chat.ask)
  Phase 4  ANCESTOR SYNC    — write brief + URLs back to canonical notebook
  Phase 5  LT PERSIST       — Modal Volume store (Integration Brain LT)

Cell → knight mapping:
  signal_scout    → NanoApis    primary source foraging
  source_forager  → NanoApis    expanded coverage (parallel)
  evidence_weaver → NanoSyntax  structured extraction
  fact_verifier   → NanoDebug   cross-check claims
  sentinel_critic → NanoSentinel risk / security audit

Usage:
    agency = BrowserResearchAgency(tier="apex")
    brief  = await agency.run("best open-source browser automation 2026")
    print(brief.synthesis)
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ── Tier / cell config ────────────────────────────────────────────────────────

_CELL_KNIGHT: dict[str, str] = {
    "signal_scout":   "apis",
    "source_forager": "apis",
    "evidence_weaver":"syntax",
    "fact_verifier":  "debug",
    "sentinel_critic":"sentinel",
}

_TIER_CELLS: dict[str, list[str]] = {
    "kinetic": ["signal_scout", "evidence_weaver", "sentinel_critic"],
    "hybrid":  ["signal_scout", "source_forager", "evidence_weaver", "sentinel_critic"],
    "apex":    ["signal_scout", "source_forager", "evidence_weaver",
                "fact_verifier", "sentinel_critic"],
}

_TIER_PARALLELISM: dict[str, int] = {"kinetic": 2, "hybrid": 4, "apex": 6}

_CHIMERA_ROUNDS = [
    {
        "round": "round_1",
        "owner": "Sir Octavian",
        "title": "Semantic Auditing",
        "goal": "Score source quality, filter weak signal, surface relevant operators.",
    },
    {
        "round": "round_2",
        "owner": "Merlin / Videneptus",
        "title": "Topology Shift",
        "goal": "Map the core narrative, fit mission shape to underlying topology.",
    },
    {
        "round": "round_3",
        "owner": "Sir Myrmidon",
        "title": "Anchor Compression",
        "goal": "Preserve load-bearing tokens, compress into a high-density brief.",
    },
]

# ── Path helpers ──────────────────────────────────────────────────────────────

def _configs_dir() -> str:
    return str(Path(__file__).parent.parent)


def _add_configs():
    d = _configs_dir()
    if d not in sys.path:
        sys.path.insert(0, d)


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class CellResult:
    cell: str
    knight_id: str
    result: str
    urls: list[str]
    success: bool
    elapsed_ms: float


@dataclass
class ChimeraRound:
    round_id: str
    owner: str
    title: str
    output: str
    elapsed_ms: float
    success: bool


@dataclass
class ResearchBrief:
    objective: str
    tier: str
    ancestor_context: str          # what NotebookLM already knew
    cells: list[CellResult]
    chimera: list[ChimeraRound]    # 3 CHIMERA rounds
    synthesis: str                 # final merged brief
    ancestor_synced: bool          # wrote back to NotebookLM
    sources_added: int             # URLs ingested into NLM notebook
    memory_count: int              # LT Modal Volume stores
    elapsed_ms: float
    sources: list[str] = field(default_factory=list)

    def to_cloud_result(self) -> dict[str, Any]:
        return {
            "service": "browser_research_agency_chimera",
            "objective": self.objective,
            "tier": self.tier,
            "brief": self.synthesis,
            "ancestor_context_chars": len(self.ancestor_context),
            "memory_count": self.memory_count,
            "elapsed_ms": round(self.elapsed_ms),
            "sources": self.sources[:20],
            "sources_added_to_nlm": self.sources_added,
            "ancestor_synced": self.ancestor_synced,
            "chimera_rounds": [
                {
                    "round": r.round_id,
                    "owner": r.owner,
                    "title": r.title,
                    "success": r.success,
                    "elapsed_ms": round(r.elapsed_ms),
                    "output_preview": r.output[:300],
                }
                for r in self.chimera
            ],
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
            "production_ready": {
                "browser_cells": all(c.success for c in self.cells),
                "chimera_complete": len(self.chimera) == 3 and all(r.success for r in self.chimera),
                "ancestor_synced": self.ancestor_synced,
                "lt_persisted": self.memory_count > 0,
                "synthesis_complete": bool(self.synthesis),
            },
            "deliverables": [f"[{c.cell}] {c.result[:200]}" for c in self.cells if c.success],
            "recommended_next_steps": _next_steps(self),
        }


def _next_steps(brief: ResearchBrief) -> list[str]:
    steps = []
    if any(not r.success for r in brief.chimera):
        steps.append("Re-run failed CHIMERA rounds for complete refinement.")
    if not brief.ancestor_synced:
        steps.append("Manually sync results to NotebookLM: //BROWSE apis: sync research")
    if brief.tier != "apex":
        steps.append(f"Escalate to apex tier for deeper fact verification.")
    steps.append("Generate NotebookLM audio/slides artifact from synthesis.")
    steps.append("Review Integration Brain LT for persisted findings.")
    return steps[:4]


# ── Phase 0: NotebookLM Ancestor Query ───────────────────────────────────────

async def _query_ancestor(objective: str) -> str:
    """Query the canonical NotebookLM notebook for prior knowledge on the objective."""
    _add_configs()
    try:
        from notebooklm_bridge import async_synthesize
        query = (
            f"What do we already know about: {objective}\n\n"
            "Summarize relevant prior findings, frameworks, patterns, and risks "
            "from the knowledge base. Be concise — focus on load-bearing context."
        )
        result = await async_synthesize(query)
        return result or ""
    except Exception as e:
        return f"[ancestor unavailable: {type(e).__name__}]"


# ── Phase 1: Browser Cells ────────────────────────────────────────────────────

def _cell_task(cell: str, objective: str, ancestor_context: str) -> str:
    ancestor_seed = (
        f"\n\nPRIOR KNOWLEDGE (from NotebookLM ancestor brain):\n{ancestor_context[:800]}"
        if ancestor_context and not ancestor_context.startswith("[ancestor")
        else ""
    )
    prompts = {
        "signal_scout": (
            f"Research: {objective}{ancestor_seed}\n\n"
            "Navigate to authoritative primary sources (official docs, GitHub, papers, news). "
            "Extract key facts, version numbers, and relevant context. "
            "Return a structured summary with source URLs."
        ),
        "source_forager": (
            f"Expand research on: {objective}{ancestor_seed}\n\n"
            "Find sources beyond the obvious: niche blogs, GitHub issues, conference talks, "
            "comparison articles, community discussions. Identify sources missed by surface search. "
            "Extract URLs and key quotes."
        ),
        "evidence_weaver": (
            f"Synthesize findings on: {objective}{ancestor_seed}\n\n"
            "Extract structured data: API signatures, benchmarks, feature lists, version "
            "comparisons, code examples. Return a dense structured report — no narrative fluff."
        ),
        "fact_verifier": (
            f"Verify and pressure-test claims about: {objective}{ancestor_seed}\n\n"
            "Search for contradictions, known issues, bugs, deprecated features, or misleading "
            "docs. Check GitHub issues, Stack Overflow, changelogs. Flag confidence level per claim."
        ),
        "sentinel_critic": (
            f"Security and risk audit for: {objective}{ancestor_seed}\n\n"
            "Navigate to security advisories, CVE databases, dependency scanners. "
            "Identify supply chain risks, license conflicts, API key exposure, production risks."
        ),
    }
    return prompts.get(cell, f"Research: {objective}. Return structured findings.")


async def _run_cells(
    cells: list[str],
    objective: str,
    ancestor_context: str,
    parallelism: int,
) -> list[CellResult]:
    from .browser_nano_knight import _ROSTER

    async def _run_one(cell: str, semaphore: asyncio.Semaphore) -> CellResult:
        kid = _CELL_KNIGHT.get(cell, "apis")
        KnightClass = _ROSTER.get(kid)
        if KnightClass is None:
            return CellResult(cell=cell, knight_id=kid, result="[no knight]",
                              urls=[], success=False, elapsed_ms=0)
        knight = KnightClass()
        ct0 = time.perf_counter()
        task = _cell_task(cell, objective, ancestor_context)
        async with semaphore:
            try:
                fb = await knight.async_execute(task)
                return CellResult(
                    cell=cell, knight_id=fb.knight_id, result=fb.result,
                    urls=fb.urls_visited, success=fb.success, elapsed_ms=fb.elapsed_ms,
                )
            except Exception as e:
                return CellResult(
                    cell=cell, knight_id=kid,
                    result=f"[cell_error] {type(e).__name__}: {e}",
                    urls=[], success=False,
                    elapsed_ms=(time.perf_counter() - ct0) * 1000,
                )

    sem = asyncio.Semaphore(parallelism)
    return list(await asyncio.gather(*[_run_one(c, sem) for c in cells]))


# ── Phase 2: CHIMERA Rounds ───────────────────────────────────────────────────

async def _chimera_round_1(
    objective: str,
    cells: list[CellResult],
    ancestor_context: str,
) -> ChimeraRound:
    """Round 1 — Semantic Auditing: score sources, filter noise via LLM."""
    t0 = time.perf_counter()
    cell_dump = "\n\n".join(
        f"[{c.cell.upper()} | {'OK' if c.success else 'FAIL'}]\n{c.result[:600]}"
        for c in cells
    )
    prompt = (
        f"CHIMERA Round 1 — Semantic Auditing\n"
        f"Objective: {objective}\n\n"
        f"Ancestor brain context:\n{ancestor_context[:400]}\n\n"
        f"Cell findings:\n{cell_dump[:3000]}\n\n"
        "Score each cell (1-5) for source quality and relevance. "
        "Filter weak-signal cells. Surface the 3 most important findings. "
        "Output: ranked findings list + filtered cell scores."
    )
    output = await _llm_round(prompt)
    return ChimeraRound(
        round_id="round_1", owner="Sir Octavian", title="Semantic Auditing",
        output=output, elapsed_ms=(time.perf_counter() - t0) * 1000,
        success=not output.startswith("[chimera_error"),
    )


async def _chimera_round_2(
    objective: str,
    round1: ChimeraRound,
    ancestor_context: str,
) -> ChimeraRound:
    """Round 2 — Topology Shift: map narrative to underlying topology via Integration Brain."""
    t0 = time.perf_counter()
    _add_configs()
    try:
        from integration_brain import async_synthesize
        query = (
            f"CHIMERA Round 2 — Topology Shift\n"
            f"Objective: {objective}\n\n"
            f"Ancestor context:\n{ancestor_context[:300]}\n\n"
            f"Audited findings (Round 1):\n{round1.output[:1200]}\n\n"
            "Map the core narrative structure: identify the primary thesis, "
            "supporting axes, competing frameworks, and knowledge gaps. "
            "Output: a topology map with 3-5 structural nodes and their relationships."
        )
        output = await async_synthesize(query, tier="short")
        output = output or "[no topology output]"
    except Exception as e:
        output = f"[chimera_error r2] {type(e).__name__}: {e}"
    return ChimeraRound(
        round_id="round_2", owner="Merlin / Videneptus", title="Topology Shift",
        output=output, elapsed_ms=(time.perf_counter() - t0) * 1000,
        success=not output.startswith("[chimera_error"),
    )


async def _chimera_round_3(
    objective: str,
    round2: ChimeraRound,
    cells: list[CellResult],
) -> ChimeraRound:
    """Round 3 — Anchor Compression: compress to dense brief via NotebookLM."""
    t0 = time.perf_counter()
    _add_configs()
    successful_results = "\n\n".join(
        f"[{c.cell}] {c.result[:500]}" for c in cells if c.success
    )
    try:
        from notebooklm_bridge import async_synthesize
        query = (
            f"CHIMERA Round 3 — Anchor Compression\n"
            f"Objective: {objective}\n\n"
            f"Topology map (Round 2):\n{round2.output[:800]}\n\n"
            f"Raw cell findings:\n{successful_results[:2000]}\n\n"
            "Compress everything into a high-density research brief. "
            "Preserve only load-bearing tokens. "
            "Format: Executive Summary (3 sentences) → Key Findings (5 bullets) → "
            "Production Risk (1-3 items) → Next Actions (3 items)."
        )
        output = await async_synthesize(query)
        output = output or "[no compression output]"
    except Exception as e:
        # Fallback to LLM if NLM unavailable
        output = await _llm_round(
            f"Compress this research on '{objective}' into a dense brief:\n\n"
            f"{successful_results[:3000]}"
        )
    return ChimeraRound(
        round_id="round_3", owner="Sir Myrmidon", title="Anchor Compression",
        output=output, elapsed_ms=(time.perf_counter() - t0) * 1000,
        success=not output.startswith("[chimera_error"),
    )


async def _llm_round(prompt: str) -> str:
    """Call CLIProxy (127.0.0.1:8080) for CHIMERA round processing."""
    try:
        import httpx
        payload = {
            "model": os.environ.get("CAMELOT_BROWSER_LLM", "claude-sonnet-4-6"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "http://127.0.0.1:8080/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {os.environ.get('ANTHROPIC_API_KEY','camelot')}"},
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[chimera_error llm] {type(e).__name__}: {e}"


# ── Phase 3: Final synthesis ──────────────────────────────────────────────────

async def _synthesize_final(
    objective: str,
    round3: ChimeraRound,
    ancestor_context: str,
) -> str:
    """Final synthesis: merge CHIMERA output with ancestor via Integration Brain ST."""
    _add_configs()
    try:
        from integration_brain import async_synthesize
        query = (
            f"Final synthesis for: {objective}\n\n"
            f"Ancestor prior knowledge:\n{ancestor_context[:400]}\n\n"
            f"CHIMERA compressed brief:\n{round3.output[:1200]}\n\n"
            "Merge ancestor knowledge with new findings. Resolve contradictions. "
            "Produce the definitive research brief."
        )
        result = await async_synthesize(query, tier="short")
        return result or round3.output
    except Exception:
        return round3.output


# ── Phase 4: Ancestor Sync ────────────────────────────────────────────────────

async def _sync_ancestor(
    objective: str,
    brief: "ResearchBrief",
) -> tuple[bool, int]:
    """Write synthesis + discovered URLs back to canonical NotebookLM notebook."""
    _add_configs()
    synced = False
    added = 0
    try:
        from notebooklm_bridge import async_sync_state, async_sources_add, CANONICAL_NOTEBOOK_ID
        note_content = (
            f"# Research: {objective}\n\n"
            f"**Tier:** {brief.tier} | "
            f"**Cells:** {len(brief.cells)} | "
            f"**Elapsed:** {brief.elapsed_ms:.0f}ms\n\n"
            f"## CHIMERA Brief\n{brief.synthesis}\n\n"
            f"## Sources ({len(brief.sources)})\n"
            + "\n".join(f"- {u}" for u in brief.sources[:20])
        )
        await async_sync_state(
            note_title=f"[RESEARCH] {objective[:60]}",
            content=note_content,
        )
        synced = True

        # Ingest top URLs as NotebookLM sources (best-effort, cap at 5)
        for url in brief.sources[:5]:
            try:
                await async_sources_add(url=url, notebook_id=CANONICAL_NOTEBOOK_ID, wait=False)
                added += 1
            except Exception:
                pass
    except Exception:
        pass
    return synced, added


# ── Phase 5: LT Persist ───────────────────────────────────────────────────────

async def _store_lt(objective: str, brief: "ResearchBrief") -> int:
    _add_configs()
    try:
        from integration_brain import async_store
        title = f"[CHIMERA_RESEARCH] {objective[:80]}"
        body = (
            f"Objective: {objective}\n"
            f"Tier: {brief.tier} | Cells: {len(brief.cells)} | "
            f"CHIMERA rounds: {len(brief.chimera)} | {brief.elapsed_ms:.0f}ms\n\n"
            f"Ancestor context (prior):\n{brief.ancestor_context[:400]}\n\n"
            f"Final synthesis:\n{brief.synthesis}\n\n"
            f"Sources:\n" + "\n".join(brief.sources[:15])
        )
        await async_store(title, body, tier="long")
        return 1
    except Exception:
        return 0


# ── Main orchestrator ─────────────────────────────────────────────────────────

class BrowserResearchAgency:
    """
    Perplexity-killer + NotebookLM Brain Ancestor + CHIMERA research agency.

    5-phase pipeline:
      0. Ancestor query (NotebookLM prior knowledge seed)
      1. Browser cells (parallel nano-knights)
      2. CHIMERA rounds (3-round LLM refinement)
      3. Final synthesis (Integration Brain ST)
      4. Ancestor sync (write back to NotebookLM + add sources)
      5. LT persist (Modal Volume)
    """

    def __init__(self, tier: str = "hybrid"):
        self.tier = tier.lower() if tier.lower() in _TIER_CELLS else "hybrid"

    async def run(
        self,
        objective: str,
        *,
        tier: str | None = None,
        constraints: list[str] | None = None,
        skip_ancestor: bool = False,
        skip_chimera: bool = False,
    ) -> ResearchBrief:
        t0 = time.perf_counter()
        effective_tier = (tier or self.tier).lower()
        if effective_tier not in _TIER_CELLS:
            effective_tier = "hybrid"

        cells_to_run = _TIER_CELLS[effective_tier]
        parallelism = _TIER_PARALLELISM[effective_tier]

        # ── Phase 0: Ancestor Query ──────────────────────────────────────────
        ancestor_context = ""
        if not skip_ancestor:
            ancestor_context = await _query_ancestor(objective)

        # ── Phase 1: Browser Cells ───────────────────────────────────────────
        cell_results = await _run_cells(cells_to_run, objective, ancestor_context, parallelism)

        # Collect sources
        all_urls: list[str] = []
        for cr in cell_results:
            all_urls.extend(cr.urls)
        sources = list(dict.fromkeys(all_urls))

        # ── Phase 2: CHIMERA Rounds ──────────────────────────────────────────
        chimera_rounds: list[ChimeraRound] = []
        if not skip_chimera:
            r1 = await _chimera_round_1(objective, cell_results, ancestor_context)
            chimera_rounds.append(r1)
            r2 = await _chimera_round_2(objective, r1, ancestor_context)
            chimera_rounds.append(r2)
            r3 = await _chimera_round_3(objective, r2, cell_results)
            chimera_rounds.append(r3)
        else:
            # Stub rounds when skipped
            chimera_rounds = []

        # ── Phase 3: Final Synthesis ─────────────────────────────────────────
        if chimera_rounds:
            synthesis = await _synthesize_final(objective, chimera_rounds[-1], ancestor_context)
        else:
            # No CHIMERA — synthesize directly from cells
            synthesis = await _synthesize_cells_direct(objective, cell_results)

        # Build brief (pre-sync)
        elapsed = (time.perf_counter() - t0) * 1000
        brief = ResearchBrief(
            objective=objective,
            tier=effective_tier,
            ancestor_context=ancestor_context,
            cells=cell_results,
            chimera=chimera_rounds,
            synthesis=synthesis,
            ancestor_synced=False,
            sources_added=0,
            memory_count=0,
            elapsed_ms=elapsed,
            sources=sources,
        )

        # ── Phase 4: Ancestor Sync ───────────────────────────────────────────
        synced, added = await _sync_ancestor(objective, brief)
        brief.ancestor_synced = synced
        brief.sources_added = added

        # ── Phase 5: LT Persist ──────────────────────────────────────────────
        mem_count = await _store_lt(objective, brief)
        brief.memory_count = mem_count
        brief.elapsed_ms = (time.perf_counter() - t0) * 1000

        return brief

    def run_sync(self, objective: str, **kwargs) -> ResearchBrief:
        try:
            return asyncio.run(self.run(objective, **kwargs))
        except RuntimeError:
            raise RuntimeError("Already async — use `await BrowserResearchAgency().run()`")


async def _synthesize_cells_direct(objective: str, cells: list[CellResult]) -> str:
    _add_configs()
    try:
        from integration_brain import async_synthesize
        combined = "\n\n---\n\n".join(
            f"[{c.cell.upper()}]\n{c.result}" for c in cells if c.success
        )
        return await async_synthesize(
            f"Synthesize research on: {objective}\n\n{combined[:4000]}", tier="short"
        ) or "[no synthesis]"
    except Exception:
        return "\n\n---\n\n".join(c.result[:600] for c in cells if c.success) or "[no results]"


# ── ScoutSonar drop-in ────────────────────────────────────────────────────────

class BrowserScout:
    """Drop-in for ScoutSonar — same UKG RepoPhial output, zero paid API."""

    def __init__(self):
        self._agency = BrowserResearchAgency(tier="kinetic")

    def _to_phial(self, brief: ResearchBrief) -> list[dict[str, Any]]:
        chimera_brief = brief.chimera[-1].output[:500] if brief.chimera else brief.synthesis[:500]
        return [{
            "REPO": "browser-research-result",
            "DOMAIN": "Research",
            "LANGS": [],
            "LICENSE": "N/A",
            "RESOURCE_IMPACT": f"{brief.elapsed_ms:.0f}ms | {len(brief.cells)} cells",
            "TOKEN_IMPACT": f"{len(brief.synthesis)} chars synthesized",
            "ASSIMILATION_STRATEGY": chimera_brief,
            "SOURCES": brief.sources[:10],
            "CELLS_COMPLETED": [c.cell for c in brief.cells if c.success],
            "ANCESTOR_SYNCED": brief.ancestor_synced,
            "CHIMERA_ROUNDS": len(brief.chimera),
        }]

    def forage(self, query: str) -> list[dict[str, Any]]:
        return self._to_phial(self._agency.run_sync(query))

    async def async_forage(self, query: str) -> list[dict[str, Any]]:
        return self._to_phial(await self._agency.run(query))
