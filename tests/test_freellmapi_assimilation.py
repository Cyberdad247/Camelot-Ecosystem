# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Tests for FreeLLMAPI Assimilation Bridge, Skill, Tools & Runic Router

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load freellmapi_bridge dynamically
_bridge_path = REPO_ROOT / "02_FORGE" / "assimilation" / "freellmapi" / "freellmapi_bridge.py"
assert _bridge_path.exists(), f"Missing bridge at {_bridge_path}"
_spec = importlib.util.spec_from_file_location("freellmapi_bridge", str(_bridge_path))
assert _spec and _spec.loader
freellmapi_mod = importlib.util.module_from_spec(_spec)
sys.modules["freellmapi_bridge"] = freellmapi_mod
_spec.loader.exec_module(freellmapi_mod)

FreeLLMAPIBridge = freellmapi_mod.FreeLLMAPIBridge
SecretSanitizationViolation = freellmapi_mod.SecretSanitizationViolation
FREE_MODEL_CATALOG = freellmapi_mod.FREE_MODEL_CATALOG
get_freellmapi_bridge = freellmapi_mod.get_freellmapi_bridge

from control_plane.runes.runic_router import route_rune


class TestFreeLLMAPIAssimilation:
    """Test suite for FreeLLMAPI zero-cost gateway bridge and tools."""

    def test_bridge_singleton_and_defaults(self):
        bridge = get_freellmapi_bridge()
        assert bridge is not None
        assert "http" in bridge.base_url
        assert bridge.timeout_seconds == 30.0

    def test_model_catalog(self):
        bridge = FreeLLMAPIBridge()
        catalog = bridge.list_models()
        assert len(catalog) >= 8
        model_ids = [m["id"] for m in catalog]
        assert "auto" in model_ids
        assert "deepseek-chat" in model_ids
        assert "qwen-2.5-72b" in model_ids
        assert "llama-3.3-70b" in model_ids

    def test_secret_sanitization_blocks_api_keys(self):
        bridge = FreeLLMAPIBridge()

        # Test various secret leaks
        with pytest.raises(SecretSanitizationViolation):
            bridge.chat_completion(prompt="Here is my API_KEY=sk-12345678901234567890123456789012 please analyze")

        with pytest.raises(SecretSanitizationViolation):
            bridge.chat_completion(prompt="Use Bearer a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 for auth")

        with pytest.raises(SecretSanitizationViolation):
            bridge.chat_completion(prompt="Admin password is SuperSecretPassword123")

        with pytest.raises(SecretSanitizationViolation):
            bridge.chat_completion(prompt="My github token is ghp_123456789012345678901234567890123456")

    def test_clean_prompt_passes_sanitizer(self):
        bridge = FreeLLMAPIBridge(enable_observatory_tap=False)
        # Should not raise SecretSanitizationViolation
        resp = bridge.chat_completion(
            prompt="Explain the difference between synchronous and asynchronous execution in Python.",
            model="auto",
        )
        assert resp is not None
        assert resp.total_tokens > 0
        assert resp.model_used is not None

    def test_standby_fallback_mode_when_offline(self):
        bridge = FreeLLMAPIBridge(base_url="http://127.0.0.1:9999/v1", enable_observatory_tap=False)
        alive, msg = bridge.is_alive()
        assert not alive
        assert "UNREACHABLE" in msg or "ERROR" in msg

        resp = bridge.chat_completion(
            prompt="Calculate the fibonacci sequence up to 10.",
            model="deepseek-chat",
            calling_knight="SIR_CODEX",
        )
        assert resp.is_fallback is True
        assert resp.provider == "freellmapi_standby"
        assert "deepseek-chat" in resp.model_used
        assert resp.duration_ms >= 0.0

    def test_mock_live_upstream_response(self):
        bridge = FreeLLMAPIBridge(enable_observatory_tap=False)

        mock_payload = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "A Multi-Armed Bandit balances exploration and exploitation.",
                    }
                }
            ],
            "model": "deepseek-chat",
            "provider": "modelscope",
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 10,
                "total_tokens": 22,
            },
        }

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            resp = bridge.chat_completion(
                prompt="Explain Multi-Armed Bandits",
                model="deepseek-chat",
                calling_knight="SIR_HELIOS",
            )
            assert resp.content == "A Multi-Armed Bandit balances exploration and exploitation."
            assert resp.model_used == "deepseek-chat"
            assert resp.is_fallback is False
            assert resp.total_tokens == 22

    def test_runic_router_freellmapi_and_zero_cost(self):
        res1 = route_rune("//FREELLMAPI", param="Write a rust macro for logging")
        assert res1.rune == "//FREELLMAPI"
        assert res1.knight == "sir_helios"
        assert res1.metadata.get("action") == "freellmapi_chat"
        assert res1.metadata.get("status") == "SUCCESS"

        res2 = route_rune("//ZERO_COST", param="Generate a quick regex pattern for email")
        assert res2.rune == "//ZERO_COST"
        assert res2.metadata.get("action") == "freellmapi_chat"
        assert res2.metadata.get("status") == "SUCCESS"

    def test_fastmcp_tools(self):
        from control_plane.mcp.cloudbrain_mcp_server import (
            freellmapi_chat,
            freellmapi_status,
            freellmapi_list_models,
        )

        # Status tool
        st = freellmapi_status()
        assert "status" in st
        assert "curated_model_count" in st
        assert st["curated_model_count"] >= 8

        # Models tool
        models = freellmapi_list_models()
        assert len(models) >= 8

        # Chat tool (clean prompt)
        chat_res = freellmapi_chat(
            prompt="What is the speed of light in vacuum?",
            model="auto",
            calling_knight="SIR_HELIOS",
        )
        assert "content" in chat_res or "status" in chat_res

        # Chat tool (secret prompt must be rejected)
        secret_res = freellmapi_chat(
            prompt="My secret API_KEY=sk-test123456789012345678901234567890",
            model="auto",
        )
        assert secret_res.get("status") == "SECRET_FENCE_TRIGGERED"
        assert "error" in secret_res
