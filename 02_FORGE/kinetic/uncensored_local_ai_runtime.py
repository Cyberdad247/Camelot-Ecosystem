# SPDX-License-Identifier: MIT
"""02_FORGE/kinetic/uncensored_local_ai_runtime.py — Kinetic Uncensored Local AI Runtime.

Assimilates Uncensored-Local-AI-Multiplatform into Camelot-OS Kinetic Forge layer:
- Fast client & subprocess bridge for on-device OpenAI-compatible REST server (:4891).
- Offline GGUF/llama.cpp model execution protocols with Wakelock & zero-cloud air-gap.
- Direct invocation for kinetic code generation, uncensored synthesis, and multiplatform offline execution.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Iterator, List, Optional
import urllib.error
import urllib.parse
import urllib.request

from control_plane.infra.uncensored_local_ai_daemon import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_BASE_URL,
    AiModelInfo,
    ChatMessage,
    GenerationParams,
    LlamaEngineOffline,
    LocalModelManager,
    UncensoredLocalAiDaemon,
)


class UncensoredLocalAiKineticClient:
    """Kinetic client interface connecting to Uncensored Local AI (:4891)."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def check_health(self) -> Dict[str, Any]:
        url = f"{self.base_url.rsplit('/v1', 1)[0]}/healthz"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_models(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("data", [])

    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "local",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def stream_chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "local",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line or not line.startswith("data: "):
                    continue
                data_part = line[6:].strip()
                if data_part == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_part)
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                except Exception:
                    continue


class KineticUncensoredExecutor:
    """In-process standalone kinetic execution engine without network socket dependency."""

    def __init__(self, model_id: str = "gemma-2-2b-abliterated") -> None:
        self.engine = LlamaEngineOffline()
        self.model_manager = LocalModelManager()
        self.engine.load_model(model_id)

    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> str:
        messages = [ChatMessage(role="user", content=prompt)]
        params = GenerationParams(max_tokens=max_tokens, temperature=temperature)
        tokens = list(self.engine.generate(messages, params=params, system_prompt=system_prompt))
        return "".join(tokens).strip()
