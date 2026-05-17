# -*- coding: utf-8 -*-
"""
[S4-01] Intent Router — dynamic knight hot-swap via semantic intent classification.

Replaces pure weight-based routing in switchboard.py with intent-aware dispatch:
  1. classify_intent(text) → IntentCategory  (keyword heuristic, <1ms, no LLM)
  2. route_by_intent(text, board) → Terminal  (probes live terminals in priority order)

Maps each intent category to an ordered list of preferred terminal IDs. The first
live terminal in the list wins; falls back to switchboard.best_for() if all preferred
terminals are dark.
"""
from __future__ import annotations

import re
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from control_plane.switchboard import Switchboard, Terminal


class IntentCategory(Enum):
    FORGE        = "forge"        # implement, build, scaffold
    CODE         = "code"         # debug, fix, refactor, review
    RESEARCH     = "research"     # search, explain, look up
    MEMORY       = "memory"       # recall, context, history
    OPS          = "ops"          # status, metrics, health, factory
    SECURITY     = "security"     # audit, scan, armor
    VOICE        = "voice"        # tts, audio, speak (cascaded pipeline)
    NATIVE_AUDIO = "native_audio" # omni realtime audio (GPT-4o/Gemini Live)
    GENERAL      = "general"      # fallback


# Ordered keyword lists — first match wins within each category
_INTENT_KEYWORDS: dict[IntentCategory, list[str]] = {
    IntentCategory.FORGE: [
        "forge", "implement", "build", "create", "generate", "scaffold",
        "write code", "develop", "author", "draft",
    ],
    IntentCategory.CODE: [
        "debug", "fix", "refactor", "review code", "test", "error",
        "bug", "exception", "trace", "lint", "syntax",
    ],
    IntentCategory.RESEARCH: [
        "search", "find", "look up", "research", "what is", "explain",
        "summarize", "analyze", "investigate", "survey",
    ],
    IntentCategory.MEMORY: [
        "remember", "recall", "memory", "context", "history",
        "stored", "ledger", "archive", "retrieve",
    ],
    IntentCategory.OPS: [
        "status", "metrics", "health", "monitor", "throughput",
        "uptime", "factory", "dashboard", "telemetry", "alerts",
    ],
    IntentCategory.SECURITY: [
        "audit", "scan", "security", "vulnerability", "sentinel",
        "armor", "threat", "exploit", "secrets", "compliance",
    ],
    IntentCategory.VOICE: [
        "speak", "tts", "audio", "voice", "say", "pronounce",
        "synthesize", "narrate", "kitten",
    ],
    IntentCategory.NATIVE_AUDIO: [
        "realtime audio", "omni", "native audio", "live voice", "audio-in",
        "voice call", "webrtc", "livekit", "gemini live", "gpt-4o realtime",
        "no text", "direct audio",
    ],
}

# Preferred terminal IDs per category — ordered by priority (first = most preferred)
INTENT_TERMINAL_MAP: dict[IntentCategory, list[str]] = {
    IntentCategory.FORGE:    ["sir_boris", "sir_forge", "sir_helio"],
    IntentCategory.CODE:     ["sir_boris", "sir_codex", "sir_forge"],
    IntentCategory.RESEARCH: ["sir_helio", "sir_mnemo", "sir_boris"],
    IntentCategory.MEMORY:   ["sir_mnemo", "sir_helio", "sir_boris"],
    IntentCategory.OPS:      ["sir_octavian", "sir_link", "sir_boris"],
    IntentCategory.SECURITY: ["sir_sentinel", "sir_gideon", "sir_ghost"],
    IntentCategory.VOICE:        ["sir_sonus", "sir_link", "sir_boris"],
    IntentCategory.NATIVE_AUDIO: ["sir_link", "sir_helio", "sir_alex"],
    IntentCategory.GENERAL:      ["sir_alex", "sir_boris", "sir_helio", "sir_link"],
}


def classify_intent(text: str) -> tuple[IntentCategory, float]:
    """Classify intent from text using keyword heuristic.

    Returns (IntentCategory, confidence) where confidence is 0.0–1.0.
    Scoring: 0.9 for exact phrase match, 0.7 for word boundary match,
    0.5 for substring match. Ties broken by category priority order.
    """
    lower = text.lower()
    scores: dict[IntentCategory, float] = {}

    for category, keywords in _INTENT_KEYWORDS.items():
        best = 0.0
        for kw in keywords:
            if kw in lower:
                if re.search(r"\b" + re.escape(kw) + r"\b", lower):
                    # Multi-word phrases get a specificity bonus to win ties
                    score = 0.9 + 0.02 * (len(kw.split()) - 1)
                else:
                    score = 0.5
                if score > best:
                    best = score
        if best > 0:
            scores[category] = best

    if not scores:
        return IntentCategory.GENERAL, 0.3

    best_cat = max(scores, key=lambda c: scores[c])
    return best_cat, scores[best_cat]


async def route_by_intent(
    text: str,
    board: "Switchboard",
) -> tuple[Optional["Terminal"], IntentCategory, float]:
    """Route a user utterance to the best live terminal.

    Returns (terminal, category, confidence).
    Terminal is None only if no live terminals exist at all.
    """
    category, confidence = classify_intent(text)
    preferred_ids = INTENT_TERMINAL_MAP.get(category, INTENT_TERMINAL_MAP[IntentCategory.GENERAL])

    # Try preferred terminals in order
    for tid in preferred_ids:
        t = await board.probe_one(tid)
        if t and t.status in ("live", "assumed_live"):
            return t, category, confidence

    # Fallback: capability-based best_for
    capability_map = {
        IntentCategory.FORGE:    ["forge", "orchestration"],
        IntentCategory.CODE:     ["code_gen", "velocity"],
        IntentCategory.RESEARCH: ["research", "context"],
        IntentCategory.MEMORY:   ["memory", "recall"],
        IntentCategory.OPS:      ["ops", "monitoring"],
        IntentCategory.SECURITY:     ["security", "audit"],
        IntentCategory.VOICE:        ["bridge", "audio"],
        IntentCategory.NATIVE_AUDIO: ["bridge", "context"],
        IntentCategory.GENERAL:      ["orchestration", "cognitive"],
    }
    fallback = await board.best_for(capability_map.get(category, ["orchestration"]))
    return fallback, category, confidence * 0.5  # reduced confidence on fallback


def explain_routing(text: str) -> dict:
    """Debug helper — show classification result without probing."""
    category, confidence = classify_intent(text)
    return {
        "text": text[:80],
        "category": category.value,
        "confidence": round(confidence, 2),
        "preferred_terminals": INTENT_TERMINAL_MAP.get(category, []),
    }
