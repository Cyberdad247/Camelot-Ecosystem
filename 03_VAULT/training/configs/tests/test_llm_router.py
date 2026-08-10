"""Tests for the LLM router module."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from llm_router import (
    FALLBACK_CHAIN,
    PROVIDERS,
    ProviderConfig,
    __version__,
    _validate_response,
    chat,
    list_available,
)


def test_version_exists():
    assert __version__


def test_providers_configured():
    assert len(PROVIDERS) >= 7
    for name in ["gemini", "openai", "claude", "grok", "mistral", "openrouter", "ollama"]:
        assert name in PROVIDERS


def test_fallback_chain_order():
    assert FALLBACK_CHAIN[0] == "cliproxy"
    assert FALLBACK_CHAIN[-1] == "ollama"


def test_provider_config():
    p = ProviderConfig(name="test", base_url="http://localhost", api_key_env="",
                       default_model="test-model")
    assert p.name == "test"
    assert p.api_key is None
    assert p.available is False  # No key, not ollama


def test_ollama_always_available():
    assert PROVIDERS["ollama"].available is True


def test_validate_response_valid():
    r = _validate_response({"content": "hello", "provider": "test", "model": "m"})
    assert r["content"] == "hello"


def test_validate_response_missing_content():
    with pytest.raises(ValueError):
        _validate_response({"provider": "test"})


def test_validate_response_truncates():
    long = "x" * 200_000
    r = _validate_response({"content": long, "provider": "test", "model": "m"})
    assert len(r["content"]) <= 100_020  # 100k + "[truncated]"


def test_validate_response_coerces_type():
    r = _validate_response({"content": 42, "provider": "test", "model": "m"})
    assert r["content"] == "42"


def test_list_available_returns_list():
    result = list_available()
    assert isinstance(result, list)
    assert len(result) >= 7


def test_gemini_no_key_in_url():
    """HIGH: Verify Gemini API key is NOT passed as URL parameter."""
    import inspect

    import llm_router
    source = inspect.getsource(llm_router._gemini_chat)
    assert "?key=" not in source


def test_chat_all_fail_gracefully(monkeypatch):
    """Verify graceful failure when no providers work."""
    # Disable all cloud providers
    for name, prov in PROVIDERS.items():
        if name != "ollama":
            monkeypatch.setattr(prov, "active", False)
    # Point ollama to a dead port so it fails
    monkeypatch.setattr(PROVIDERS["ollama"], "base_url", "http://127.0.0.1:1")
    result = chat([{"role": "user", "content": "test"}], fallback=True, timeout=2)
    assert result.get("error") or result.get("provider") == "none"


def test_fallback_resets_model_for_next_provider(monkeypatch):
    """Fallback providers should use their own defaults unless explicitly pinned."""
    import llm_router

    monkeypatch.setenv("GOOGLE_API_KEY", "x")
    monkeypatch.setenv("OPENAI_API_KEY", "y")

    calls = []

    def fake_dispatch(prov, messages, **kwargs):
        calls.append((prov.name, kwargs.get("model")))
        if prov.name == "gemini":
            raise RuntimeError("boom")
        return {
            "provider": prov.name,
            "model": kwargs.get("model") or prov.default_model,
            "content": "ok",
            "usage": {},
            "duration_ms": 0,
        }

    monkeypatch.setattr(llm_router, "_dispatch", fake_dispatch)

    result = llm_router.chat(
        [{"role": "user", "content": "test"}],
        provider="gemini",
        model="gemini-2.5-pro",
    )

    assert calls[0] == ("gemini", "gemini-2.5-pro")
    assert calls[1][0] == "cliproxy"
    assert calls[1][1] is None
    assert result["provider"] == "cliproxy"


def test_ollama_autodetect_runs_when_model_not_supplied(monkeypatch):
    """Ollama should use autodetected model when no explicit model is given."""
    import llm_router

    payloads = []

    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "message": {"content": "ok"},
                "prompt_eval_count": 1,
                "eval_count": 2,
                "total_duration": 0,
            }

    def fake_post(url, json=None, timeout=None, headers=None):
        payloads.append((url, json, timeout))
        return Resp()

    monkeypatch.setattr(llm_router.httpx, "post", fake_post)
    monkeypatch.setattr(llm_router, "_get_ollama_best_model", lambda prov: "autodetected:model")

    result = llm_router._openai_compatible_chat(
        llm_router.PROVIDERS["ollama"],
        [{"role": "user", "content": "hi"}],
        model=None,
        timeout=0.01,
    )

    assert payloads[0][1]["model"] == "autodetected:model"
    assert result["model"] == "autodetected:model"
