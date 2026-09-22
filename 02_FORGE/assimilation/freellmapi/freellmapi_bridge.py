# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — FreeLLMAPI Zero-Cost Universal Gateway Bridge
r"""
FreeLLMAPI Assimilation Bridge.
Integrates tashfeenahmed/freellmapi into Camelot-OS as a zero-cost LLM fallback
tier for Round Table Knights, background Squire swarms, and high-volume tasks.

Key Features:
- Multi-provider pooling (~34 free-tier backends: Groq, Cerebras, ModelScope, OpenRouter, Pollinations, etc.)
- Multi-Armed Bandit fallback routing
- Strict Air-Gap Secret Sanitizer: blocks any tokens/keys/passwords and redirects to SIR_GHOST
- Local-first fallback & simulated resilience when offline
- Optional Glass Observatory interaction tap (+35 XP)
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

logger = logging.getLogger("FreeLLMAPIBridge")

# Default environment configuration
DEFAULT_FREELLMAPI_URL = os.environ.get("FREELLMAPI_BASE_URL", "http://127.0.0.1:3001/v1")
DEFAULT_API_KEY = os.environ.get("FREELLMAPI_API_KEY", "freellmapi-local")

# Sovereign secret detection pattern (Strict rule: Zero secrets through public proxies)
SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|bearer\s+[a-zA-Z0-9_\-\.]{16,}|ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{32,})"
)

# Canonical catalog of curated free models supported across upstream providers
FREE_MODEL_CATALOG = [
    {"id": "auto", "provider": "bandit_router", "tier": "frontier_free", "desc": "Thompson-sampling optimal model"},
    {"id": "deepseek-chat", "provider": "deepseek/modelscope", "tier": "frontier", "desc": "DeepSeek-V3 / V4 Free Tier"},
    {"id": "deepseek-reasoner", "provider": "deepseek/airforce", "tier": "reasoning", "desc": "DeepSeek-R1 CoT Reasoning"},
    {"id": "qwen-2.5-72b", "provider": "modelscope/groq", "tier": "high", "desc": "Qwen 2.5 72B Instruct"},
    {"id": "llama-3.3-70b", "provider": "cerebras/groq", "tier": "high_speed", "desc": "Llama 3.3 70B Ultra-Fast (Cerebras)"},
    {"id": "gemini-2.5-flash", "provider": "google/openrouter", "tier": "multimodal", "desc": "Gemini 2.5 Flash Free Tier"},
    {"id": "mistral-small", "provider": "mistral/pollinations", "tier": "general", "desc": "Mistral Small 3.1"},
    {"id": "glm-4-flash", "provider": "zhipu", "tier": "high_throughput", "desc": "GLM-4 Flash Zero-Cost API"},
]


class SecretSanitizationViolation(ValueError):
    """Raised when a prompt contains credentials, tokens, or private secrets."""
    pass


@dataclass
class FreeLLMResponse:
    content: str
    model_used: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_ms: float
    is_fallback: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model_used": self.model_used,
            "provider": self.provider,
            "usage": {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
            },
            "duration_ms": self.duration_ms,
            "is_fallback": self.is_fallback,
            "metadata": self.metadata,
        }


class FreeLLMAPIBridge:
    """Universal Zero-Cost LLM Gateway Bridge for Camelot-OS."""

    def __init__(
        self,
        base_url: str = DEFAULT_FREELLMAPI_URL,
        api_key: str = DEFAULT_API_KEY,
        timeout_seconds: float = 30.0,
        enable_observatory_tap: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.enable_observatory_tap = enable_observatory_tap

    def sanitize_prompt(self, text: str) -> None:
        """
        Validate that the prompt does not contain secrets, tokens, or credentials.
        Strict Camelot-OS mandate: public proxies must never receive sovereign secrets.
        """
        if SECRET_PATTERN.search(text):
            logger.error("Security fence triggered: sovereign secret detected in FreeLLMAPI prompt payload.")
            raise SecretSanitizationViolation(
                "Security Fence Alert: Prompt contains sensitive tokens, keys, or credentials. "
                "Per Camelot-OS policy, all secret-bearing operations must route to SIR_GHOST (local air-gapped container)."
            )

    def is_alive(self) -> Tuple[bool, str]:
        """Check if local FreeLLMAPI instance is responsive."""
        test_url = f"{self.base_url}/models"
        req = urllib.request.Request(
            test_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Camelot-OS-Sentinel/v10001",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    return True, "ONLINE"
                return False, f"HTTP_{resp.status}"
        except urllib.error.URLError as e:
            return False, f"UNREACHABLE: {e.reason}"
        except Exception as e:
            return False, f"ERROR: {str(e)}"

    def list_models(self) -> List[Dict[str, Any]]:
        """Return available models from gateway or fall back to curated catalog."""
        alive, _ = self.is_alive()
        if alive:
            try:
                url = f"{self.base_url}/models"
                req = urllib.request.Request(
                    url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if "data" in data and isinstance(data["data"], list):
                        return data["data"]
            except Exception as e:
                logger.warning(f"Failed to fetch live models from FreeLLMAPI: {e}")

        # Return static curated catalog
        return FREE_MODEL_CATALOG

    def chat_completion(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful sovereign intelligence assistant in Camelot-OS.",
        model: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        calling_knight: str = "SIR_HELIOS",
    ) -> FreeLLMResponse:
        """
        Execute chat completion through FreeLLMAPI gateway.
        Guarantees prompt sanitization and graceful fallback if gateway is offline.
        """
        # Step 1: Strict Secret Fence
        self.sanitize_prompt(prompt)
        if system_prompt:
            self.sanitize_prompt(system_prompt)

        start_time = datetime.now(timezone.utc)

        # Step 2: Attempt upstream dispatch to FreeLLMAPI
        alive, status_msg = self.is_alive()
        if alive:
            try:
                endpoint = f"{self.base_url}/chat/completions"
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                body_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    endpoint,
                    data=body_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                        "User-Agent": f"Camelot-OS-{calling_knight}",
                    },
                    method="POST",
                )

                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                    raw_data = resp.read().decode("utf-8")
                    data = json.loads(raw_data)
                    choice = data.get("choices", [{}])[0]
                    content = choice.get("message", {}).get("content", "")
                    usage = data.get("usage", {})
                    model_resolved = data.get("model", model)

                    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0

                    response = FreeLLMResponse(
                        content=content,
                        model_used=model_resolved,
                        provider=data.get("provider", "freellmapi_pooled"),
                        prompt_tokens=usage.get("prompt_tokens", len(prompt.split())),
                        completion_tokens=usage.get("completion_tokens", len(content.split())),
                        total_tokens=usage.get("total_tokens", len(prompt.split()) + len(content.split())),
                        duration_ms=round(elapsed, 2),
                        is_fallback=False,
                        metadata={"gateway_status": "ONLINE", "status_code": resp.status},
                    )

                    self._tap_observatory_if_enabled(calling_knight, prompt, response)
                    return response

            except Exception as e:
                logger.warning(f"FreeLLMAPI live call failed ({e}); engaging zero-cost synthetic fallback.")

        # Step 3: Standby / Synthetic Resilience Mode (when daemon is inactive)
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000.0
        synthetic_content = (
            f"[FreeLLMAPI Offline Standby - Model: {model}]\n"
            f"The FreeLLMAPI gateway ({self.base_url}) is currently in standby ({status_msg}).\n"
            f"Prompt processed under zero-cost policy for Knight {calling_knight}.\n"
            f"Echo/Digest: {prompt[:200]}..." if len(prompt) > 200 else f"[Echo/Digest: {prompt}]"
        )

        response = FreeLLMResponse(
            content=synthetic_content,
            model_used=f"{model}-synthetic-fallback",
            provider="freellmapi_standby",
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(synthetic_content.split()),
            total_tokens=len(prompt.split()) + len(synthetic_content.split()),
            duration_ms=round(elapsed, 2),
            is_fallback=True,
            metadata={"gateway_status": status_msg},
        )

        self._tap_observatory_if_enabled(calling_knight, prompt, response)
        return response

    def _tap_observatory_if_enabled(
        self,
        knight_id: str,
        prompt: str,
        response: FreeLLMResponse,
    ) -> None:
        """Tap Glass Observatory for non-blocking RPG progression."""
        if not self.enable_observatory_tap:
            return

        try:
            from control_plane.observatory.glass_observatory import get_glass_observatory
            obs = get_glass_observatory()
            obs.tap_interaction(
                tenant_id="Vizion Sky",
                knight_id=knight_id,
                channel="FREELLMAPI_GATEWAY",
                prompt_snippet=prompt[:140],
                response_snippet=response.content[:140],
                status="COMPLETED" if not response.is_fallback else "FALLBACK_STANDBY",
                token_count=response.total_tokens,
                latency_ms=response.duration_ms,
            )
        except Exception as e:
            logger.debug(f"Glass Observatory tap non-critical skip: {e}")


# Global Singleton instance
_bridge_instance: Optional[FreeLLMAPIBridge] = None


def get_freellmapi_bridge() -> FreeLLMAPIBridge:
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = FreeLLMAPIBridge()
    return _bridge_instance
