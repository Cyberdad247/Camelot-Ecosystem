# SPDX-License-Identifier: MIT

"""Unit & regression coverage for vLLM model serving integration in Sovereign Inference Engine."""

from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from control_plane.dispatch.sovereign_inference import VLLMBackend, SovereignInferenceEngine


class _VLLMFixture(BaseHTTPRequestHandler):
    requests: list[dict] = []

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _json(self, body: dict) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        assert self.path == "/v1/models"
        self._json({"data": [{"id": "deepseek-ai/DeepSeek-V4.1-Flash"}, {"id": "qwen-7b"}]})

    def do_POST(self) -> None:  # noqa: N802
        raw = self.rfile.read(int(self.headers["Content-Length"]))
        self.requests.append({"headers": dict(self.headers), "body": json.loads(raw)})
        if self.path == "/v1/chat/completions":
            self._json({"choices": [{"message": {"content": "Once upon a time in Camelot"}}]})
        elif self.path == "/v1/completions":
            self._json({"choices": [{"text": "Once upon a time in Camelot"}]})
        else:
            self.send_response(404)
            self.end_headers()


@pytest.fixture
def vllm_server_url():
    _VLLMFixture.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _VLLMFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1"
    finally:
        server.shutdown()
        thread.join()


async def _collect(stream):
    return [chunk async for chunk in stream]


def test_vllm_discovers_models_and_streams_chat(vllm_server_url):
    backend = VLLMBackend(base_url=vllm_server_url)
    assert backend.health() is True
    assert backend.list_models() == ["deepseek-ai/DeepSeek-V4.1-Flash", "qwen-7b"]

    chunks = asyncio.run(_collect(backend.stream("deepseek-ai/DeepSeek-V4.1-Flash", "Once upon a time,", "", 512)))
    assert "".join(chunks) == "Once upon a time in Camelot"
    assert len(_VLLMFixture.requests) == 1
    req = _VLLMFixture.requests[0]["body"]
    assert req["model"] == "deepseek-ai/DeepSeek-V4.1-Flash"
    assert req["messages"] == [{"role": "user", "content": "Once upon a time,"}]
    assert req["max_tokens"] == 512


def test_vllm_routing_via_engine(vllm_server_url):
    engine = SovereignInferenceEngine()
    engine.register_backend("vllm", VLLMBackend(base_url=vllm_server_url))

    # 1. Via prefix
    result_prefix = "".join(asyncio.run(_collect(engine.generate_stream("vllm:deepseek-ai/DeepSeek-V4.1-Flash", "Hello"))))
    assert result_prefix == "Once upon a time in Camelot"

    # 2. Via registered manifest name
    result_manifest = "".join(asyncio.run(_collect(engine.generate_stream("deepseek-flash", "Hello"))))
    assert result_manifest == "Once upon a time in Camelot"


def test_vllm_manifest_and_bifrost_registry_configured():
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / "03_VAULT/training/configs/sovereign_models.json").read_text(encoding="utf-8"))
    registry = json.loads((root / "01_KERNEL/memory/bifrost_knight_llm_registry.json").read_text(encoding="utf-8"))

    assert "deepseek-flash" in manifest["models"]
    assert manifest["models"]["deepseek-flash"]["backend"] == "vllm"
    assert manifest["models"]["deepseek-flash"]["tag"] == "deepseek-ai/DeepSeek-V4.1-Flash"

    knight_pill_ids = [p["knight_id"] for p in registry["knight_pill_allocations"]]
    assert "DEEPSEEK_FLASH_ENGINE" in knight_pill_ids


def test_vllm_curl_exact_payload(vllm_server_url):
    """Verify exact curl payload matching user specification:
    curl -X POST "http://localhost:8000/v1/completions"
      -H "Content-Type: application/json"
      --data '{"model": "deepseek-ai/DeepSeek-V4.1-Flash", "prompt": "Once upon a time,", "max_tokens": 512, "temperature": 0.5}'
    """
    import urllib.request

    endpoint = f"{vllm_server_url}/completions"
    payload = {
        "model": "deepseek-ai/DeepSeek-V4.1-Flash",
        "prompt": "Once upon a time,",
        "max_tokens": 512,
        "temperature": 0.5,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        res = json.loads(resp.read().decode("utf-8"))
        assert "choices" in res
        assert res["choices"][0]["text"] == "Once upon a time in Camelot"

    # Verify fixture received exact parameters
    assert len(_VLLMFixture.requests) > 0
    last_req = _VLLMFixture.requests[-1]["body"]
    assert last_req["model"] == "deepseek-ai/DeepSeek-V4.1-Flash"
    assert last_req["prompt"] == "Once upon a time,"
    assert last_req["max_tokens"] == 512
    assert last_req["temperature"] == 0.5


def test_vllm_hermes_prime_fallback_on_offline():
    """Verify Hermes Prime fallback path when vLLM is offline or port 8000 is unreachable."""
    offline_backend = VLLMBackend(base_url="http://127.0.0.1:59999/v1", timeout_seconds=0.5)
    assert offline_backend.health() is False
    assert offline_backend.list_models() == []

    # Stream yields structured error message rather than unhandled exception
    chunks = asyncio.run(_collect(offline_backend.stream("deepseek-ai/DeepSeek-V4.1-Flash", "Test prompt", "", 128)))
    assert len(chunks) == 1
    assert "[SIE/vLLM]" in chunks[0]
    assert "URLError" in chunks[0] or "OSError" in chunks[0]

