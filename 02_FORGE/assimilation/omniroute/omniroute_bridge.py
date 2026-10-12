# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — OmniRoute & 9router-go Assimilation Bridge
r"""
OmniRoute & 9router-go Universal Gateway Bridge.
Assimilates:
1. diegosouzapw/OmniRoute (359 providers, 150+ free tiers, RTK + Caveman stacked compression)
2. luqman-v1/9router-go (High-performance Go proxy, 32K+ RPS, Antigravity tool cloaking, SSE translation)

Key Capabilities:
- RTK + Caveman stacked text compression (15-95% token savings)
- Antigravity IDE Tool Cloaking & Anti-Ban Decoy generation
- Multi-provider free pool routing
- Glass Observatory WORM tap (+40 XP)
"""

from __future__ import annotations

import os
import re
import json
import logging
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("OmniRouteBridge")

DEFAULT_OMNIROUTE_URL = os.environ.get("OMNIROUTE_BASE_URL", "http://127.0.0.1:20128/v1")
DEFAULT_9ROUTER_URL = os.environ.get("NINE_ROUTER_BASE_URL", "http://127.0.0.1:3002/v1")

# Curated OmniRoute Routing Strategies
ROUTING_STRATEGIES = [
    {"id": "auto", "name": "Dynamic Bandit (Optimal)", "description": "Auto-picks highest reliability under rate limits"},
    {"id": "auto/coding", "name": "Code Specialist", "description": "Routes to DeepSeek-Coder, Qwen 2.5, or Claude Free"},
    {"id": "auto/fast", "name": "Ultra-Low Latency", "description": "Routes to Cerebras, Groq, or Sambanova (<200ms TTFT)"},
    {"id": "auto/offline", "name": "Local Air-Gap", "description": "Routes strictly to local Ollama / SIR_GHOST"},
    {"id": "system1/jev", "name": "TypeSafe Jev (System 1)", "description": "Ultra-fast (<50ms) structured decision, routing & triage model"},
    {"id": "system1/reflex", "name": "System 1 Reflex Triage", "description": "Non-autoregressive fast classification & lane selection"},
    {"id": "voice/low-latency", "name": "Voice Interactive", "description": "Optimized for duplex audio turn-taking (<120ms)"},
    {"id": "voice/high-fidelity", "name": "Voice High-Fidelity", "description": "Rich dialect reasoning with prosody markers"},
]

# Official 21 Antigravity / IDE Decoy Tools for Anti-Ban Protection
ANTIGRAVITY_DECOY_TOOLS = [
    "run_command", "view_file", "replace_file_content", "write_to_file",
    "search_web", "read_url_content", "ask_question", "manage_task",
    "schedule", "invoke_subagent", "define_subagent", "manage_subagents",
    "generate_image", "send_message", "list_resources", "read_resource",
    "call_mcp_tool", "diff_inspect", "git_status", "grep_search", "find_files"
]


class RTKCavemanCompressor:
    """Stacked token compressor combining Rust Token Killer (RTK) and Caveman heuristics."""

    FILLER_PATTERNS = [
        (re.compile(r"(?i)\b(could you please|can you please|would you kindly|i would like you to|please be so kind as to)\b"), ""),
        (re.compile(r"(?i)\b(as an ai language model|in order to|due to the fact that|for the purpose of)\b"), ""),
        (re.compile(r"(?i)\b(it is important to note that|it should be mentioned that|needless to say)\b"), ""),
        (re.compile(r"[ \t]+"), " "),  # Collapse horizontal whitespace
        (re.compile(r"\n{3,}"), "\n\n"),  # Collapse excessive blank lines
    ]

    @classmethod
    def compress(cls, text: str, mode: str = "rtk_caveman") -> Dict[str, Any]:
        """
        Compress text and return original tokens, compressed tokens, and savings percentage.
        Calculates token counts via standard whitespace / heuristic tokenizer.
        """
        if not text:
            return {"original_text": "", "compressed_text": "", "original_tokens": 0, "compressed_tokens": 0, "saved_percent": 0.0}

        original_tokens = max(1, len(text.split()))
        compressed = text

        # Step 1: RTK Heuristics (strip redundant docstring markdown, comments, empty lines)
        if "rtk" in mode:
            compressed = re.sub(r"<!--[\s\S]*?-->", "", compressed)  # HTML comments
            compressed = re.sub(r"//\s*TODO.*$", "", compressed, flags=re.MULTILINE)

        # Step 2: Caveman Heuristics (strip conversational fluff)
        if "caveman" in mode:
            for pattern, repl in cls.FILLER_PATTERNS:
                compressed = pattern.sub(repl, compressed)

        compressed = compressed.strip()
        compressed_tokens = max(1, len(compressed.split()))
        saved_tokens = max(0, original_tokens - compressed_tokens)
        saved_percent = round((saved_tokens / original_tokens) * 100.0, 1)

        return {
            "original_text": text,
            "compressed_text": compressed,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "saved_tokens": saved_tokens,
            "saved_percent": saved_percent,
            "compression_mode": mode,
        }


class AntigravityToolCloaker:
    """Anti-ban decoy tool generator and competitor prompt stripper (from 9router-go)."""

    COMPETITOR_PATTERNS = [
        re.compile(r"(?i)\b(you are chatgpt|you are claude 3\.7 sonnet|you are openai gpt-4o)\b"),
        re.compile(r"(?i)\b(as developed by anthropic|created by openai)\b"),
    ]

    @classmethod
    def cloak_tools(cls, tool_names: List[str]) -> List[str]:
        """Cloak tool names with official IDE decoy wrappers to bypass heuristic rate-limiters."""
        return [f"{t}_ide" if t in ANTIGRAVITY_DECOY_TOOLS else t for t in tool_names]

    @classmethod
    def strip_competitor_identities(cls, prompt: str) -> str:
        """Strip competitor identity prompts that trigger synthetic 429 quota exhaustion."""
        res = prompt
        for pat in cls.COMPETITOR_PATTERNS:
            res = pat.sub("You are a sovereign intelligence operative", res)
        return res


@dataclass
class OmniRouteResponse:
    content: str
    strategy_used: str
    provider: str
    original_tokens: int
    compressed_tokens: int
    saved_percent: float
    duration_ms: float
    is_fallback: bool
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "strategy_used": self.strategy_used,
            "provider": self.provider,
            "tokens": {
                "original": self.original_tokens,
                "compressed": self.compressed_tokens,
                "saved_percent": self.saved_percent,
            },
            "duration_ms": self.duration_ms,
            "is_fallback": self.is_fallback,
            "status": self.status,
        }


class OmniRouteBridge:
    """Universal OmniRoute & 9router-go Bridge for Camelot-OS."""

    def __init__(
        self,
        omniroute_url: str = DEFAULT_OMNIROUTE_URL,
        ninerouter_url: str = DEFAULT_9ROUTER_URL,
        enable_compression: bool = True,
        enable_observatory_tap: bool = True,
    ):
        self.omniroute_url = omniroute_url.rstrip("/")
        self.ninerouter_url = ninerouter_url.rstrip("/")
        self.enable_compression = enable_compression
        self.enable_observatory_tap = enable_observatory_tap

    def check_gateways(self) -> Dict[str, Any]:
        """Check status of OmniRoute (:20128) and 9router-go (:3002)."""
        omni_alive = self._probe_endpoint(self.omniroute_url)
        nine_alive = self._probe_endpoint(self.ninerouter_url)

        return {
            "omniroute": {
                "url": self.omniroute_url,
                "status": "ONLINE" if omni_alive else "STANDBY",
                "default_port": 20128,
            },
            "9router_go": {
                "url": self.ninerouter_url,
                "status": "ONLINE" if nine_alive else "STANDBY",
                "default_port": 3002,
                "peak_rps_rating": "32K+ RPS",
                "target_ram": "42MB",
            },
            "compression_engine": "RTK_CAVEMAN_ACTIVE",
            "active_strategies_count": len(ROUTING_STRATEGIES),
        }

    def _probe_endpoint(self, url: str) -> bool:
        try:
            req = urllib.request.Request(f"{url}/models", headers={"User-Agent": "Camelot-OS"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def route_request(
        self,
        prompt: str,
        strategy: str = "auto",
        system: str = "You are a helpful sovereign intelligence assistant in Camelot-OS.",
        calling_knight: str = "SIR_HELIOS",
    ) -> OmniRouteResponse:
        """Route request through OmniRoute with RTK compression and 9router cloaking."""
        start_time = datetime.now(timezone.utc)

        # 1. Competitor prompt stripping & Anti-ban sanitization
        clean_prompt = AntigravityToolCloaker.strip_competitor_identities(prompt)

        # 2. RTK + Caveman Stacked Compression
        comp_info = {"original_tokens": len(clean_prompt.split()), "compressed_tokens": len(clean_prompt.split()), "saved_percent": 0.0}
        final_prompt = clean_prompt
        if self.enable_compression:
            comp_res = RTKCavemanCompressor.compress(clean_prompt)
            final_prompt = comp_res["compressed_text"]
            comp_info = {
                "original_tokens": comp_res["original_tokens"],
                "compressed_tokens": comp_res["compressed_tokens"],
                "saved_percent": comp_res["saved_percent"],
            }

        # 3. System 1 Reflex / TypeSafe Jev Non-Autoregressive Dispatch
        if strategy.startswith("system1") or "jev" in strategy.lower():
            try:
                from .typesafe_jev_client import get_typesafe_jev_client
            except (ImportError, ValueError):
                import importlib
                mod = importlib.import_module("02_FORGE.assimilation.omniroute.typesafe_jev_client")
                get_typesafe_jev_client = mod.get_typesafe_jev_client

            jev_client = get_typesafe_jev_client()
            jev_res = jev_client.decide(
                state=final_prompt,
                questions={
                    "classification": {"type": "choice", "options": ["execute", "clarify", "delegate", "triage"]},
                    "risk_assessment": {"type": "choice", "options": ["R0_TRIVIAL", "R1_READONLY", "R2_MUTATION", "R3_PRIVILEGED", "R4_CRITICAL"]},
                    "reflex_confidence": {"type": "score", "min": 0.0, "max": 1.0},
                },
            )
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0
            content = json.dumps({
                "system1_model": jev_res.model,
                "decisions": jev_res.decisions,
                "confidence_scores": jev_res.confidence_scores,
                "status": jev_res.status,
                "raw_summary": f"[TypeSafe Jev System 1 Decision] Route: {jev_res.decisions.get('classification')}, Risk: {jev_res.decisions.get('risk_assessment')}",
            }, indent=2)
            res = OmniRouteResponse(
                content=content,
                strategy_used=strategy,
                provider="typesafe.ai/jev-latest",
                original_tokens=comp_info["original_tokens"],
                compressed_tokens=comp_info["compressed_tokens"],
                saved_percent=comp_info["saved_percent"],
                duration_ms=round(elapsed, 2),
                is_fallback=not jev_res.is_live_call,
                status=jev_res.status,
            )
            self._tap_observatory(calling_knight, prompt, res)
            return res

        # 4. Attempt live gateway dispatch
        gateways = self.check_gateways()
        endpoint = None
        if gateways["9router_go"]["status"] == "ONLINE":
            endpoint = f"{self.ninerouter_url}/chat/completions"
        elif gateways["omniroute"]["status"] == "ONLINE":
            endpoint = f"{self.omniroute_url}/chat/completions"

        if endpoint:
            try:
                payload = {
                    "model": strategy,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": final_prompt},
                    ],
                }
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer omniroute-local"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=15.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0

                    res = OmniRouteResponse(
                        content=content,
                        strategy_used=strategy,
                        provider=data.get("provider", "omniroute_pool"),
                        original_tokens=comp_info["original_tokens"],
                        compressed_tokens=comp_info["compressed_tokens"],
                        saved_percent=comp_info["saved_percent"],
                        duration_ms=round(elapsed, 2),
                        is_fallback=False,
                        status="SUCCESS",
                    )
                    self._tap_observatory(calling_knight, prompt, res)
                    return res
            except Exception as e:
                logger.warning(f"OmniRoute live dispatch failed ({e}); falling back to sovereign synthetic response.")

        # 4. Fallback Standby Response
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0
        synthetic_content = (
            f"[OmniRoute Gateway Standby - Strategy: {strategy}]\n"
            f"Gateways (:20128 and :3002) in standby mode.\n"
            f"RTK + Caveman Compression active: saved {comp_info['saved_percent']}% tokens ({comp_info['original_tokens']} -> {comp_info['compressed_tokens']} tokens).\n"
            f"Processed prompt for Knight [{calling_knight}]: {final_prompt[:150]}..."
        )

        res = OmniRouteResponse(
            content=synthetic_content,
            strategy_used=strategy,
            provider="omniroute_standby_emulator",
            original_tokens=comp_info["original_tokens"],
            compressed_tokens=comp_info["compressed_tokens"],
            saved_percent=comp_info["saved_percent"],
            duration_ms=round(elapsed, 2),
            is_fallback=True,
            status="STANDBY_FALLBACK",
        )
        self._tap_observatory(calling_knight, prompt, res)
        return res

    def route_system1_decision(
        self,
        state: str,
        questions: Dict[str, Any],
        calling_knight: str = "SIR_HELIOS",
    ) -> Dict[str, Any]:
        """Directly dispatch a structured non-autoregressive decision to TypeSafe Jev."""
        try:
            from .typesafe_jev_client import get_typesafe_jev_client
        except (ImportError, ValueError):
            import importlib
            mod = importlib.import_module("02_FORGE.assimilation.omniroute.typesafe_jev_client")
            get_typesafe_jev_client = mod.get_typesafe_jev_client

        client = get_typesafe_jev_client()
        res = client.decide(state, questions)
        res_dict = res.to_dict()

        if self.enable_observatory_tap:
            synthetic_resp = OmniRouteResponse(
                content=json.dumps(res.decisions),
                strategy_used="system1/jev",
                provider=res.model,
                original_tokens=max(1, len(state.split())),
                compressed_tokens=max(1, len(state.split())),
                saved_percent=0.0,
                duration_ms=res.latency_ms,
                is_fallback=not res.is_live_call,
                status=res.status,
            )
            self._tap_observatory(calling_knight, state, synthetic_resp)

        return res_dict

    def _tap_observatory(self, knight_id: str, prompt: str, resp: OmniRouteResponse) -> None:
        if not self.enable_observatory_tap:
            return
        try:
            from control_plane.observatory.glass_observatory import get_glass_observatory
            obs = get_glass_observatory()
            obs.tap_interaction(
                tenant_id="Vizion Sky",
                knight_id=knight_id,
                channel="OMNIROUTE_NEXUS",
                prompt_snippet=prompt[:140],
                response_snippet=resp.content[:140],
                status=resp.status,
                token_count=resp.compressed_tokens,
                latency_ms=resp.duration_ms,
            )
        except Exception:
            pass


_omniroute_instance: Optional[OmniRouteBridge] = None


def get_omniroute_bridge() -> OmniRouteBridge:
    global _omniroute_instance
    if _omniroute_instance is None:
        _omniroute_instance = OmniRouteBridge()
    return _omniroute_instance
