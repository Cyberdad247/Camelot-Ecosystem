# SPDX-License-Identifier: MIT
"""02_FORGE/kinetic/xinference_kinetic_runtime.py — Kinetic Xinference Multi-Engine Runtime.

Assimilates Xorbits Inference (Xinference) into Camelot-OS Kinetic Forge layer:
- Fast client & subprocess bridge for multi-model cluster and OpenAI-compatible REST server (:9997).
- Multi-backend engine orchestration (xllamacpp, vLLM, SGLang, Transformers).
- Distributed cluster topology querying, dynamic model lifecycle (launch/terminate), and streaming inference.
- Zero external dependencies outside Python stdlib.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, Iterator, List, Optional, Union
import urllib.error
import urllib.parse
import urllib.request

from control_plane.infra.xinference_engine_adapter import (
    XINFERENCE_DEFAULT_BASE_URL,
    XINFERENCE_DEFAULT_HOST,
    XINFERENCE_DEFAULT_PORT,
    EngineBackend,
    ModelSpec,
    ModelType,
    XinferenceClusterSupervisor,
    XinferenceRestDaemon,
    get_xinference_daemon,
    get_xinference_supervisor,
)


class XinferenceKineticClient:
    """Kinetic client interface connecting to Xinference cluster & REST API (:9997)."""

    def __init__(
        self,
        base_url: str = XINFERENCE_DEFAULT_BASE_URL,
        timeout_seconds: float = 30.0,
        auto_start_daemon: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        if auto_start_daemon:
            self._ensure_daemon()

    def _ensure_daemon(self) -> None:
        """Start local daemon if unreachable."""
        try:
            self.check_health()
        except Exception:
            get_xinference_daemon()

    def check_health(self) -> Dict[str, Any]:
        """Check daemon health status."""
        url = f"{self.base_url.rsplit('/v1', 1)[0]}/healthz"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_cluster_status(self) -> Dict[str, Any]:
        """Retrieve cluster topology and capacity status."""
        url = f"{self.base_url}/cluster/info"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_workers(self) -> List[Dict[str, Any]]:
        """List active worker nodes in cluster."""
        url = f"{self.base_url}/cluster/workers"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("workers", [])

    def list_models(self) -> List[Dict[str, Any]]:
        """List active models on cluster."""
        url = f"{self.base_url}/models"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("data", [])

    def describe_model(self, model_uid: str) -> Dict[str, Any]:
        """Describe specific active model."""
        url = f"{self.base_url}/models/{model_uid}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def launch_model(
        self,
        model_name: str,
        model_type: str = "LLM",
        engine: str = "xllamacpp",
        quantization: str = "none",
        context_length: int = 4096,
        gpu_layers: int = -1,
        model_uid: Optional[str] = None,
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """Launch model replica on cluster."""
        url = f"{self.base_url}/models"
        payload = {
            "model_name": model_name,
            "model_type": model_type,
            "engine": engine,
            "quantization": quantization,
            "context_length": context_length,
            "gpu_layers": gpu_layers,
            "extra_params": extra_params,
        }
        if model_uid:
            payload["model_uid"] = model_uid

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def terminate_model(self, model_uid: str) -> Dict[str, Any]:
        """Terminate model on cluster."""
        url = f"{self.base_url}/models/{model_uid}"
        req = urllib.request.Request(url, method="DELETE")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "default-llm",
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Send chat completion request to Xinference."""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if tools is not None:
            payload["tools"] = tools

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
        model: str = "default-llm",
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Stream chat completion text deltas from SSE stream."""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
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
            for line in response:
                decoded = line.decode("utf-8").strip()
                if not decoded:
                    continue
                if decoded == "data: [DONE]":
                    break
                if decoded.startswith("data: "):
                    chunk_json = decoded[len("data: "):]
                    try:
                        chunk_obj = json.loads(chunk_json)
                        choices = chunk_obj.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except Exception:
                        pass

    def text_complete(
        self,
        prompt: str,
        model: str = "default-cmpl",
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Send legacy text completion request."""
        url = f"{self.base_url}/completions"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
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

    def embed(
        self,
        texts: Union[str, List[str]],
        model: str = "bge-large-en-v1.5",
    ) -> List[List[float]]:
        """Generate text embeddings."""
        url = f"{self.base_url}/embeddings"
        payload = {
            "model": model,
            "input": texts if isinstance(texts, list) else [texts],
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
            return [item["embedding"] for item in data.get("data", [])]

    def rerank(
        self,
        query: str,
        documents: List[str],
        model: str = "bge-reranker-large",
    ) -> List[Dict[str, Any]]:
        """Rerank candidate documents against query."""
        url = f"{self.base_url}/rerank"
        payload = {
            "model": model,
            "query": query,
            "documents": documents,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("results", [])
