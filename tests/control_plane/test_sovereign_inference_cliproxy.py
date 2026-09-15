# SPDX-License-Identifier: MIT

"""Regression coverage for the local CLIProxyAPI SIE provider."""

from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from control_plane.dispatch.sovereign_inference import CLIProxyBackend, SovereignInferenceEngine


class _ProxyFixture(BaseHTTPRequestHandler):
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
        self._json({"data": [{"id": "reasoner"}, {"id": "codex"}]})

    def do_POST(self) -> None:  # noqa: N802
        raw = self.rfile.read(int(self.headers["Content-Length"]))
        self.requests.append({"headers": dict(self.headers), "body": json.loads(raw)})
        assert self.path == "/v1/chat/completions"
        self._json({"choices": [{"message": {"content": "proxy response"}}]})


@pytest.fixture
def proxy_url():
    _ProxyFixture.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _ProxyFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1"
    finally:
        server.shutdown()
        thread.join()


def test_cliproxy_discovers_models_and_uses_openai_chat_shape(proxy_url):
    backend = CLIProxyBackend(base_url=proxy_url, api_key="fixture-proxy-key")
    assert backend.list_models() == ["reasoner", "codex"]
    result = "".join(asyncio.run(_collect(backend.stream("reasoner", "prompt", "system", 12))))
    assert result == "proxy response"
    request = _ProxyFixture.requests[-1]
    assert request["body"] == {"model": "reasoner", "messages": [{"role": "system", "content": "system"}, {"role": "user", "content": "prompt"}], "max_tokens": 12, "stream": False}
    assert request["headers"]["Authorization"] == "Bearer fixture-proxy-key"


def test_cliproxy_without_a_credential_fails_closed(proxy_url):
    backend = CLIProxyBackend(base_url=proxy_url, api_key="")

    result = "".join(asyncio.run(_collect(backend.stream("reasoner", "prompt", "", 12))))

    assert "credential unavailable" in result
    assert backend.list_models() == []
    assert backend.health() is False
    assert _ProxyFixture.requests == []


def test_cliproxy_rejects_non_loopback_endpoint():
    with pytest.raises(ValueError, match="loopback"):
        CLIProxyBackend(base_url="https://proxy.example.test/v1")


def test_cliproxy_selector_is_opt_in_and_air_gapped_mode_blocks(proxy_url):
    engine = SovereignInferenceEngine()
    engine.register_backend("cliproxy", CLIProxyBackend(base_url=proxy_url))
    engine.set_air_gapped(True)
    result = "".join(asyncio.run(_collect(engine.generate_stream("cliproxy:reasoner", "prompt"))))
    assert "Air-gapped mode: request blocked" in result
    assert _ProxyFixture.requests == []


async def _collect(stream):
    return [chunk async for chunk in stream]


def test_cliproxy_default_is_registered_without_replacing_default_routes():
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / "03_VAULT/training/configs/sovereign_models.json").read_text(encoding="utf-8"))
    routing = json.loads((root / "01_KERNEL/EXCALIBUR/config/llm_routing.json").read_text(encoding="utf-8"))
    assert manifest["models"]["cliproxy:default"]["backend"] == "cliproxy"
    assert {
        "id": "cliproxy:default",
        "role": "high_reasoning_proxy",
        "max_ctx_tokens": 200000,
        "cost_weight": 0.2,
        "use_cases": ["high_reasoning", "swarm_coordination", "repo_analysis"],
    } in routing["model_profiles"]
    assert routing["routing_policy"]["swarm_coordination"] == "anthropic:claude-3.5-sonnet"
    assert routing["routing_policy"]["high_stakes_synthesis"] == "openai:gpt-4.5"
