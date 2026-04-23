"""
browser_nano_knight.py — Browser-Use Nano-Knights with Integration Brain feedback.

Four specialized nano-knights powered by browser-use + Claude:
  NanoApis     — deep research / document foraging
  NanoSentinel — security audit / header inspection
  NanoSyntax   — code discovery / API extraction
  NanoDebug    — error investigation / live diagnostics

Usage:
    from knights.browser_nano_knight import BrowserSquad
    squad = BrowserSquad()
    results = await squad.deploy("find the Modal Python SDK changelog")

ENV:
    ANTHROPIC_API_KEY  — required (or CLIProxy at 127.0.0.1:8080 sets it)
    CAMELOT_BROWSER_HEADLESS=0  — show browser window (default headless=1)
    CAMELOT_BROWSER_STEPS=15    — max agent steps per task (default 15)
    CAMELOT_BROWSER_LLM=claude-sonnet-4-6  — model override
"""
from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .base import BaseKnight

# ── Constants ────────────────────────────────────────────────────────────────

_MODEL    = os.environ.get("CAMELOT_BROWSER_LLM", "claude-sonnet-4-6")
_HEADLESS = os.environ.get("CAMELOT_BROWSER_HEADLESS", "1") == "1"
_STEPS    = int(os.environ.get("CAMELOT_BROWSER_STEPS", "15"))

# ── Feedback packet ──────────────────────────────────────────────────────────

@dataclass
class BrowserFeedback:
    knight_id: str
    task: str
    result: str
    steps_taken: int
    urls_visited: list[str]
    success: bool
    elapsed_ms: float
    error: str | None = None
    raw_history: list[dict] = field(default_factory=list)

    def to_store_payload(self) -> tuple[str, str]:
        title = f"[BROWSER/{self.knight_id}] {self.task[:80]}"
        body = (
            f"Task: {self.task}\n"
            f"Success: {self.success} | Steps: {self.steps_taken} | {self.elapsed_ms:.0f}ms\n"
            f"URLs: {', '.join(self.urls_visited[:10])}\n\n"
            f"Result:\n{self.result}"
        )
        return title, body


# ── LLM factory ──────────────────────────────────────────────────────────────

def _make_llm():
    try:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=_MODEL, temperature=0)
    except ImportError:
        pass
    try:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="anthropic/claude-sonnet-4-6",
            base_url="http://127.0.0.1:8080/v1",
            api_key=os.environ.get("ANTHROPIC_API_KEY", "camelot-proxy"),
            temperature=0,
        )
    except ImportError as e:
        raise RuntimeError(
            "Install browser-use deps: pip install browser-use langchain-anthropic"
        ) from e


def _extract_feedback(knight_id: str, task: str, result: Any,
                       t0: float) -> BrowserFeedback:
    elapsed = (time.perf_counter() - t0) * 1000
    urls: list[str] = []
    steps = 0
    raw: list[dict] = []

    try:
        # browser-use AgentHistoryList
        history = result.history if hasattr(result, "history") else []
        steps = len(history)
        for h in history:
            raw.append({"step": getattr(h, "step_number", 0),
                        "action": str(getattr(h, "model_output", ""))[:200]})
            if hasattr(h, "result"):
                for r in (h.result if isinstance(h.result, list) else [h.result]):
                    if hasattr(r, "extracted_content") and r.extracted_content:
                        pass  # content captured in final_result below
                    if hasattr(r, "url") and r.url:
                        urls.append(r.url)
    except Exception:
        pass

    final = ""
    try:
        final = result.final_result() if callable(getattr(result, "final_result", None)) else str(result)
    except Exception:
        final = str(result)

    return BrowserFeedback(
        knight_id=knight_id,
        task=task,
        result=final or "[no result]",
        steps_taken=steps,
        urls_visited=list(dict.fromkeys(urls)),  # dedupe, preserve order
        success=bool(final and "error" not in final.lower()[:40]),
        elapsed_ms=elapsed,
        raw_history=raw,
    )


# ── Base Nano-Knight ─────────────────────────────────────────────────────────

class BrowserNanoKnight(BaseKnight):
    """Async browser-use knight. Override `system_prompt` per persona."""

    system_prompt: str = "You are a helpful browser agent. Complete the task efficiently."

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        try:
            fb = asyncio.run(self.async_execute(directive, intent))
        except RuntimeError:
            # Already in event loop — caller must use await async_execute directly
            return {"status": "error", "output": "Call async_execute() from async context.", "files_created": []}
        return {
            "status": "success" if fb.success else "error",
            "output": fb.result,
            "files_created": [],
            "feedback": fb,
        }

    async def async_execute(self, directive: str, intent: dict | None = None) -> BrowserFeedback:
        from browser_use import Agent, Browser, BrowserConfig
        t0 = time.perf_counter()
        try:
            llm = _make_llm()
            cfg = BrowserConfig(headless=_HEADLESS)
            browser = Browser(config=cfg)
            agent = Agent(
                task=directive,
                llm=llm,
                browser=browser,
                max_steps=_STEPS,
                system_prompt_override=self.system_prompt,
            )
            raw_result = await agent.run()
            fb = _extract_feedback(self.__class__.__name__, directive, raw_result, t0)
            await browser.close()
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            fb = BrowserFeedback(
                knight_id=self.__class__.__name__,
                task=directive,
                result=f"[BROWSER_ERROR] {type(e).__name__}: {e}",
                steps_taken=0,
                urls_visited=[],
                success=False,
                elapsed_ms=elapsed,
                error=str(e),
            )

        await _route_feedback(fb)
        return fb


async def _route_feedback(fb: BrowserFeedback) -> None:
    """Async fan-out: store feedback to Integration Brain LT tier."""
    try:
        import sys
        configs = Path(__file__).parent.parent
        if str(configs) not in sys.path:
            sys.path.insert(0, str(configs))
        from integration_brain import async_store
        title, body = fb.to_store_payload()
        await async_store(title, body, tier="long")
    except Exception:
        pass  # feedback is best-effort — never block the knight


# ── Persona Nano-Knights ─────────────────────────────────────────────────────

class NanoApis(BrowserNanoKnight):
    """Lady Apis — deep research forager."""
    name = "Nano-Apis"
    title = "The Forager"
    specialty = "Research & Document Extraction"
    icon = "🐜"
    system_prompt = (
        "You are Lady Apis, the Sovereign's Chief Researcher. "
        "Traverse the digital realm to gather structured intelligence. "
        "Prioritize primary sources (official docs, GitHub). "
        "Extract data in structured formats. Verify all API versions."
    )


class NanoSentinel(BrowserNanoKnight):
    """Sir Zenith — security auditor."""
    name = "Nano-Sentinel"
    title = "The Shield"
    specialty = "Security Audit & Header Analysis"
    icon = "🛡️"
    system_prompt = (
        "You are Sir Zenith, the Sovereign's Shadow. "
        "Audit network fingerprints, HTTP headers, CSP policies, and cookie flags. "
        "Identify exposed endpoints, version disclosures, and misconfigurations. "
        "Report findings in structured severity-ranked format."
    )


class NanoSyntax(BrowserNanoKnight):
    """Sir Syntax — code discovery and API extraction."""
    name = "Nano-Syntax"
    title = "The Builder"
    specialty = "Code Discovery & API Extraction"
    icon = "⚙️"
    system_prompt = (
        "You are Sir Syntax, the Sovereign's Lead Architect. "
        "Navigate documentation and repositories to extract exact API signatures, "
        "code samples, and implementation patterns. "
        "Return structured JSON with function names, parameters, and examples."
    )


class NanoDebug(BrowserNanoKnight):
    """Sir Debug — live error investigation."""
    name = "Nano-Debug"
    title = "The Healer"
    specialty = "Error Investigation & Stack Trace Analysis"
    icon = "🔧"
    system_prompt = (
        "You are Sir Debug, the Sovereign's Field Medic. "
        "Navigate to error trackers, GitHub issues, and Stack Overflow to diagnose failures. "
        "Identify root causes, not symptoms. "
        "Return a concise diagnosis with the minimal fix."
    )


# ── Squad Coordinator ─────────────────────────────────────────────────────────

_ROSTER: dict[str, type[BrowserNanoKnight]] = {
    "apis":     NanoApis,
    "sentinel": NanoSentinel,
    "syntax":   NanoSyntax,
    "debug":    NanoDebug,
}


class BrowserSquad:
    """Spawn one or many nano-knights in parallel and collect feedback."""

    def __init__(self, roster: list[str] | None = None):
        self.roster = roster or ["apis"]

    async def deploy(
        self,
        task: str,
        *,
        per_knight_task: dict[str, str] | None = None,
    ) -> list[BrowserFeedback]:
        """
        Run nano-knights in parallel.

        Args:
            task: Shared task directive (used when per_knight_task is None).
            per_knight_task: Optional dict mapping knight_id → specific task.
        """
        knights = [_ROSTER[k]() for k in self.roster if k in _ROSTER]
        if not knights:
            raise ValueError(f"Unknown roster IDs: {self.roster}")

        async def _run(knight: BrowserNanoKnight) -> BrowserFeedback:
            kid = knight.__class__.__name__.lower().replace("nano", "").strip()
            directive = (per_knight_task or {}).get(kid, task)
            return await knight.async_execute(directive)

        results = await asyncio.gather(*[_run(k) for k in knights], return_exceptions=True)
        feedbacks: list[BrowserFeedback] = []
        for r in results:
            if isinstance(r, BrowserFeedback):
                feedbacks.append(r)
            else:
                feedbacks.append(BrowserFeedback(
                    knight_id="unknown", task=task, result=str(r),
                    steps_taken=0, urls_visited=[], success=False,
                    elapsed_ms=0, error=str(r),
                ))
        return feedbacks

    def deploy_sync(self, task: str, **kwargs) -> list[BrowserFeedback]:
        return asyncio.run(self.deploy(task, **kwargs))
