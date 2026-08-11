"""Camelot LLM Router -- Unified multi-provider LLM gateway.

Routes requests through a fallback chain of LLM providers:
  Tier 1: Cloud providers (Gemini, OpenAI, Claude, Grok, Mistral)
  Tier 2: OpenRouter (aggregated cloud fallback)
  Tier 3: Ollama (local inference)

Supports streaming, model selection, and automatic failover.
"""

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

__version__ = "1.0.0"

logger = logging.getLogger("camelot.llm_router")

# ── Provider Configuration ────────────────────────────────────────────

OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
CLIPROXY_BASE = os.environ.get("CLIPROXY_BASE", "http://127.0.0.1:8080/v1")
CLIPROXY_KEY = os.environ.get("CLIPROXY_KEY", "proxy-admin-key")

@dataclass
class ProviderConfig:
    name: str
    base_url: str
    api_key_env: str
    default_model: str
    models: list = field(default_factory=list)
    headers: dict = field(default_factory=dict)
    active: bool = True

    @property
    def api_key(self) -> Optional[str]:
        return os.environ.get(self.api_key_env)

    @property
    def available(self) -> bool:
        if self.name in ("ollama", "cliproxy"):
            return True  # Local services, always attempt
        return self.active and bool(self.api_key)


# Provider registry
PROVIDERS = {
    "cliproxy": ProviderConfig(
        name="cliproxy",
        base_url=CLIPROXY_BASE,
        api_key_env="CLIPROXY_KEY",
        default_model="gemini-2.5-flash",
        models=[],  # Populated dynamically from proxy /v1/models
        headers={"Authorization": f"Bearer {CLIPROXY_KEY}"},
    ),
    "gemini": ProviderConfig(
        name="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        api_key_env="GOOGLE_API_KEY",
        default_model="gemini-3-flash-preview",
        models=["gemini-3-flash-preview", "gemini-3-pro-preview", "gemini-2.5-flash", "gemini-2.5-pro"],
    ),
    "openai": ProviderConfig(
        name="openai",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        default_model="gpt-5.3",
        models=["gpt-5.3", "gpt-5.2", "gpt-5", "gpt-5.3-codex"],
    ),
    "claude": ProviderConfig(
        name="claude",
        base_url="https://api.anthropic.com/v1",
        api_key_env="ANTHROPIC_API_KEY",
        default_model="claude-sonnet-4-6",
        models=["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
    ),
    "grok": ProviderConfig(
        name="grok",
        base_url="https://api.x.ai/v1",
        api_key_env="XAI_API_KEY",
        default_model="grok-3",
        models=["grok-3", "grok-3-mini", "grok-2"],
    ),
    "mistral": ProviderConfig(
        name="mistral",
        base_url="https://api.mistral.ai/v1",
        api_key_env="MISTRAL_API_KEY",
        default_model="mistral-large-latest",
        models=["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest",
                "codestral-latest", "open-mistral-nemo"],
    ),
    "openrouter": ProviderConfig(
        name="openrouter",
        base_url=OPENROUTER_BASE,
        api_key_env="OPENROUTER_API_KEY",
        default_model="anthropic/claude-sonnet-4-6",
        models=["anthropic/claude-sonnet-4-6", "openai/gpt-4o", "google/gemini-2.0-flash",
                "mistralai/mistral-large", "x-ai/grok-3"],
        headers={"HTTP-Referer": "https://camelot-os.local", "X-Title": "Camelot OS"},
    ),
    "ollama": ProviderConfig(
        name="ollama",
        base_url=OLLAMA_BASE,
        api_key_env="",  # No key needed
        default_model="qwen3:0.6b",
        models=[],  # Populated dynamically from Ollama API
    ),
}

# Default fallback chain order
FALLBACK_CHAIN = ["cliproxy", "gemini", "openai", "claude", "grok", "mistral", "openrouter", "ollama"]


# ── Unified Chat Interface ────────────────────────────────────────────

def _get_cliproxy_models(provider: ProviderConfig) -> list:
    """Fetch available models from CLIProxyAPI."""
    try:
        headers = {**provider.headers}
        resp = httpx.get(f"{provider.base_url}/models", headers=headers, timeout=5)
        resp.raise_for_status()
        models = [m["id"] for m in resp.json().get("data", [])]
        if models:
            provider.models = models
        return models
    except Exception:
        return []


def _get_ollama_best_model(provider: ProviderConfig) -> str:
    """Auto-detect best available Ollama model."""
    try:
        resp = httpx.get(f"{provider.base_url}/api/tags", timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        if models:
            provider.models = models
            # Prefer larger models first
            for preferred in ["qwen3:8b", "llama3.2:3b", "mistral:7b", "qwen2.5:7b"]:
                if preferred in models:
                    return preferred
            return models[0]
    except Exception:
        pass
    return provider.default_model


def _openai_compatible_chat(provider: ProviderConfig, messages: list,
                            model: Optional[str] = None, stream: bool = False,
                            temperature: float = 0.7, max_tokens: int = 4096,
                            timeout: float = 30.0) -> dict:
    """Send a chat request using the OpenAI-compatible API format.

    Works with: OpenAI, Grok, Mistral, OpenRouter, Ollama.
    """
    selected_model = model or provider.default_model
    url = f"{provider.base_url}/chat/completions"

    headers = {"Content-Type": "application/json", **provider.headers}
    if provider.api_key:
        headers["Authorization"] = f"Bearer {provider.api_key}"

    # Ollama uses /api/chat with longer timeout for local inference
    if provider.name == "ollama":
        url = f"{provider.base_url}/api/chat"
        if model is None:
            selected_model = _get_ollama_best_model(provider)
        payload = {
            "model": selected_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        ollama_timeout = max(timeout, 120.0)  # Local models need more time
        resp = httpx.post(url, json=payload, timeout=ollama_timeout)
        resp.raise_for_status()
        data = resp.json()
        return {
            "provider": provider.name,
            "model": selected_model,
            "content": data.get("message", {}).get("content", ""),
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
            "duration_ms": int(data.get("total_duration", 0) / 1e6),
        }

    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    resp = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    choice = data.get("choices", [{}])[0]
    usage = data.get("usage", {})
    return {
        "provider": provider.name,
        "model": selected_model,
        "content": choice.get("message", {}).get("content", ""),
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
        },
        "duration_ms": 0,
    }


def _gemini_chat(provider: ProviderConfig, messages: list,
                 model: Optional[str] = None, temperature: float = 0.7,
                 max_tokens: int = 4096, timeout: float = 30.0) -> dict:
    """Send a chat request using the Gemini API format."""
    model = model or provider.default_model
    url = f"{provider.base_url}/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": provider.api_key}

    # Convert OpenAI message format to Gemini format
    contents = []
    system_instruction = None
    for msg in messages:
        role = msg["role"]
        if role == "system":
            system_instruction = msg["content"]
            continue
        gemini_role = "model" if role == "assistant" else "user"
        contents.append({"role": gemini_role, "parts": [{"text": msg["content"]}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    resp = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    candidates = data.get("candidates", [{}])
    content = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        content = "".join(p.get("text", "") for p in parts)

    usage_meta = data.get("usageMetadata", {})
    return {
        "provider": provider.name,
        "model": model,
        "content": content,
        "usage": {
            "prompt_tokens": usage_meta.get("promptTokenCount", 0),
            "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
        },
        "duration_ms": 0,
    }


def _claude_chat(provider: ProviderConfig, messages: list,
                 model: Optional[str] = None, temperature: float = 0.7,
                 max_tokens: int = 4096, timeout: float = 30.0) -> dict:
    """Send a chat request using the Anthropic Messages API."""
    model = model or provider.default_model
    url = f"{provider.base_url}/messages"

    # Extract system message
    system_text = ""
    api_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

    headers = {
        "Content-Type": "application/json",
        "x-api-key": provider.api_key,
        "anthropic-version": "2023-06-01",
    }

    payload = {
        "model": model,
        "messages": api_messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if system_text:
        payload["system"] = system_text

    resp = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    content_blocks = data.get("content", [])
    content = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
    usage = data.get("usage", {})
    return {
        "provider": provider.name,
        "model": model,
        "content": content,
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
        },
        "duration_ms": 0,
    }


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 2
RETRY_BACKOFF = 1.0  # seconds, doubles each retry


def _validate_response(result: dict) -> dict:
    """Validate LLM response has expected structure."""
    if not isinstance(result, dict):
        raise ValueError("Response is not a dict")
    if "content" not in result:
        raise ValueError("Response missing 'content' field")
    if not isinstance(result.get("content", ""), str):
        result["content"] = str(result.get("content", ""))
    # Truncate excessively long responses (safety)
    if len(result["content"]) > 100_000:
        result["content"] = result["content"][:100_000] + "\n[truncated]"
    return result


def _dispatch(provider: ProviderConfig, messages: list, **kwargs) -> dict:
    """Dispatch to the correct API format with retry on transient errors."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            if provider.name == "gemini":
                result = _gemini_chat(provider, messages, **kwargs)
            elif provider.name == "claude":
                result = _claude_chat(provider, messages, **kwargs)
            else:
                result = _openai_compatible_chat(provider, messages, **kwargs)
            return _validate_response(result)
        except httpx.HTTPStatusError as e:
            last_error = e
            if e.response.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF * (2 ** attempt)
                logger.info("Retrying %s after %ds (status %d)", provider.name, wait, e.response.status_code)
                time.sleep(wait)
                continue
            raise
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF * (2 ** attempt)
                logger.info("Retrying %s after %ds (%s)", provider.name, wait, type(e).__name__)
                time.sleep(wait)
                continue
            raise
    raise last_error


# ── Public API ────────────────────────────────────────────────────────

def _soul_route_provider(messages: list) -> Optional[tuple[str, str]]:
    """Consult the Soul Router if available. Returns (provider, model) or None.

    Checks user message content for privacy keywords and complexity signals,
    then routes through the MFOE matrix to select the optimal engine.
    """
    try:
        from control_plane.infra.cli_intercept import CLIIntercept
        intercept = CLIIntercept()

        # Extract the latest user message as the intent
        intent = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                intent = msg.get("content", "")
                break
        if not intent:
            return None

        result = intercept.intercept(intent)

        # Map engine_cmd back to provider name
        engine_to_provider = {
            "ollama": "ollama",
            "claude": "cliproxy",  # Claude goes through CLIProxyAPI
            "gemini": "cliproxy",
            "codex": "cliproxy",
        }
        provider = engine_to_provider.get(result.engine_cmd, "cliproxy")
        model = result.model

        logger.info(
            "[SOUL_ROUTER] %s -> %s/%s (score=%.4f, privacy=%s)",
            result.route.knight_id, provider, model,
            result.route.score, result.route.privacy_override,
        )
        return (provider, model)
    except Exception as e:
        logger.debug("Soul router unavailable: %s", e)
        return None


def chat(messages: list, provider: Optional[str] = None,
         model: Optional[str] = None, temperature: float = 0.7,
         max_tokens: int = 4096, timeout: float = 30.0,
         fallback: bool = True) -> dict:
    """Send a chat completion request with automatic fallback.

    Args:
        messages: List of {role, content} dicts.
        provider: Preferred provider name (e.g. "gemini", "ollama").
        model: Specific model override.
        temperature: Sampling temperature.
        max_tokens: Max response tokens.
        timeout: Request timeout in seconds.
        fallback: Whether to try next provider on failure.

    Returns:
        dict with keys: provider, model, content, usage, duration_ms, error (if any).
    """
    # Consult Soul Router for intelligent routing (unless provider is explicit)
    if not provider:
        soul_decision = _soul_route_provider(messages)
        if soul_decision:
            provider, model = soul_decision

    # Build provider chain
    if provider and provider in PROVIDERS:
        chain = [provider] + [p for p in FALLBACK_CHAIN if p != provider]
    else:
        chain = list(FALLBACK_CHAIN)

    explicit_model = model
    errors = []
    for pname in chain:
        prov = PROVIDERS.get(pname)
        if not prov or not prov.available:
            continue

        start = time.time()
        try:
            provider_model = explicit_model if pname == provider else None
            result = _dispatch(prov, messages, model=provider_model, temperature=temperature,
                               max_tokens=max_tokens, timeout=timeout)
            result["duration_ms"] = int((time.time() - start) * 1000)
            result["fallback_errors"] = errors
            return result
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            err = f"{pname}: {type(e).__name__}: {str(e)[:100]} ({elapsed}ms)"
            errors.append(err)
            logger.warning("Provider %s failed: %s", pname, e)
            if not fallback:
                break

    return {
        "provider": "none",
        "model": "none",
        "content": "",
        "usage": {},
        "duration_ms": 0,
        "error": f"All providers failed: {'; '.join(errors)}",
        "fallback_errors": errors,
    }


def list_available() -> list:
    """List all available providers and their status."""
    result = []
    for name, prov in PROVIDERS.items():
        has_key = bool(prov.api_key) if prov.api_key_env else True
        status = "ready" if prov.available else ("no_key" if not has_key else "disabled")

        # Check CLIProxyAPI connectivity
        if name == "cliproxy" and status == "ready":
            models = _get_cliproxy_models(prov)
            if models:
                status = f"ready ({len(models)} models)"
            else:
                status = "offline"

        # Check Ollama connectivity
        if name == "ollama" and status == "ready":
            try:
                resp = httpx.get(f"{prov.base_url}/api/tags", timeout=3)
                models = [m["name"] for m in resp.json().get("models", [])]
                status = f"ready ({len(models)} models)"
                prov.models = models or prov.models
            except Exception:
                status = "offline"

        result.append({
            "name": name,
            "status": status,
            "default_model": prov.default_model,
            "models": prov.models[:5],
        })
    return result


def quick_ask(prompt: str, system: str = "", provider: Optional[str] = None,
              model: Optional[str] = None) -> str:
    """Quick single-prompt helper. Returns just the response text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    result = chat(messages, provider=provider, model=model)
    if result.get("error"):
        return f"[ERROR] {result['error']}"
    return result["content"]
