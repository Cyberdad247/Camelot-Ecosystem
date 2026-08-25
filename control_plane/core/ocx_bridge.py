# SPDX-License-Identifier: MIT

"""OpenCodex Bridge — Universal Provider Proxy for CAMELOT-OS.

Wraps the ``@bitkyc08/opencodex`` management API to provide:

- **Knight-tier model resolution** — maps SoulRouter knight IDs to
  opencodex provider/model combos with failover chains.
- **Health probes** — liveness (``/healthz``) and readiness (``/readyz``).
- **Process lifecycle** — start/stop/status for the opencodex sidecar.
- **Provider registry** — lists active providers and their models.

The bridge is **optional** — if opencodex is not running, callers fall
back to the existing ``llm_router`` / ``cliproxy`` resolution path.

Usage::

    from control_plane.core.ocx_bridge import OCXBridge

    bridge = OCXBridge()
    if bridge.is_ready():
        model, url, key = bridge.resolve("sir_boris")
    else:
        # fall back to cliproxy
        ...
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("camelot.ocx_bridge")

# ── Configuration ────────────────────────────────────────────────────────────

OCX_HOST = os.getenv("OCX_HOST", "127.0.0.1")
OCX_PORT = int(os.getenv("OCX_PORT", "10100"))
OCX_BASE = f"http://{OCX_HOST}:{OCX_PORT}"
OCX_API_KEY = os.getenv("OPENCODEX_API_AUTH_TOKEN", "")

# Fallback to cliproxy when opencodex is not available
CLIPROXY_URL = os.getenv("CLIPROXY_URL", "http://127.0.0.1:8080/v1")
CLIPROXY_KEY = os.getenv("CLIPROXY_KEY", "proxy-admin-key")
OLLAMA_URL = "http://127.0.0.1:11434/v1"

# ── Knight Tier → Provider/Model Mapping ─────────────────────────────────────
# Each tier defines a primary model and a failover chain.
# OpenCodex combos handle failover; we define the combo config here.

@dataclass(frozen=True)
class ProviderModel:
    """A provider/model pair for a knight tier."""
    provider: str
    model: str
    base_url: str = ""
    api_key: str = ""

    @property
    def wire_id(self) -> str:
        """OpenCodex slug codec wire ID (provider/model)."""
        return f"{self.provider}/{self.model}"


@dataclass(frozen=True)
class KnightTierConfig:
    """Configuration for a knight tier's model resolution."""
    tier: str
    primary: ProviderModel
    fallbacks: tuple[ProviderModel, ...] = ()
    combo_strategy: str = "failover"  # failover | round-robin
    local_only: bool = False


# Tier definitions — maps knight engine strings to provider configs.
# Source of truth: SoulRouter FOUNDRY_COUNCIL engine assignments + omniroute.json.
KNIGHT_TIER_MAP: dict[str, KnightTierConfig] = {
    # ── G3: Apex frontier (Google priority) ──────────────────────────────
    "claude_code": KnightTierConfig(
        tier="G3",
        primary=ProviderModel("anthropic", "claude-opus-5"),
        fallbacks=(
            ProviderModel("google", "gemini-3.1-pro-preview"),
            ProviderModel("openai", "gpt-5.5"),
        ),
    ),
    "gemini_flash": KnightTierConfig(
        tier="G3",
        primary=ProviderModel("google", "gemini-3-pro-preview"),
        fallbacks=(
            ProviderModel("anthropic", "claude-sonnet-4"),
            ProviderModel("openai", "gpt-5.4"),
        ),
    ),
    # ── G2: Pro context/research (Google priority) ──────────────────────
    "antigravity.cli": KnightTierConfig(
        tier="G2",
        primary=ProviderModel("google", "gemini-3.1-pro-preview"),
        fallbacks=(
            ProviderModel("openai", "gpt-5.4"),
        ),
    ),
    "integration_brain": KnightTierConfig(
        tier="G2",
        primary=ProviderModel("google", "gemini-3.1-pro-preview"),
        fallbacks=(
            ProviderModel("anthropic", "claude-sonnet-4"),
        ),
    ),
    # ── G1: Flash bridge ────────────────────────────────────────────────
    "open_source": KnightTierConfig(
        tier="G1",
        primary=ProviderModel("google", "gemini-3-flash-preview"),
        fallbacks=(
            ProviderModel("openai", "gpt-4.1-mini"),
        ),
    ),
    # ── X1: Codex velocity ──────────────────────────────────────────────
    "openai_codex": KnightTierConfig(
        tier="X1",
        primary=ProviderModel("openai", "gpt-5.5-codex"),
        fallbacks=(),
    ),
    # ── L0: Local harness-locked ────────────────────────────────────────
    "local_qwen": KnightTierConfig(
        tier="L0",
        primary=ProviderModel("ollama", "qwen3:8b", base_url=OLLAMA_URL),
        fallbacks=(),
        local_only=True,
    ),
    "open_coder": KnightTierConfig(
        tier="L0",
        primary=ProviderModel("ollama", "qwen3:1.7b", base_url=OLLAMA_URL),
        fallbacks=(),
        local_only=True,
    ),
    "agents_a1": KnightTierConfig(
        tier="L0",
        primary=ProviderModel("ollama", "agents-a1", base_url=OLLAMA_URL),
        fallbacks=(),
        local_only=True,
    ),
    # ── Catch-all for unmapped engines ───────────────────────────────────
    "default": KnightTierConfig(
        tier="G2",
        primary=ProviderModel("google", "gemini-3-pro-preview"),
        fallbacks=(
            ProviderModel("anthropic", "claude-sonnet-4"),
            ProviderModel("openai", "gpt-5.4"),
        ),
    ),
}


# ── HTTP helpers (httpx preferred, stdlib fallback) ──────────────────────────

def _http_get(url: str, timeout: float = 5.0) -> Optional[dict[str, Any]]:
    """GET a JSON endpoint. Returns None on any failure."""
    try:
        import httpx
        headers = {}
        if OCX_API_KEY:
            headers["x-opencodex-api-key"] = OCX_API_KEY
        resp = httpx.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass

    # Stdlib fallback
    try:
        import urllib.request
        req = urllib.request.Request(url)
        if OCX_API_KEY:
            req.add_header("x-opencodex-api-key", OCX_API_KEY)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        pass

    return None


def _http_post(url: str, data: dict, timeout: float = 10.0) -> Optional[dict[str, Any]]:
    """POST JSON to an endpoint. Returns None on any failure."""
    try:
        import httpx
        headers = {"Content-Type": "application/json"}
        if OCX_API_KEY:
            headers["x-opencodex-api-key"] = OCX_API_KEY
        resp = httpx.post(url, json=data, headers=headers, timeout=timeout)
        if resp.status_code in (200, 201):
            return resp.json()
    except Exception:
        pass

    try:
        import urllib.request
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        if OCX_API_KEY:
            req.add_header("x-opencodex-api-key", OCX_API_KEY)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        pass

    return None


# ── Bridge Class ─────────────────────────────────────────────────────────────

class OCXBridge:
    """Thin wrapper around the opencodex management API.

    Provides knight-tier model resolution, health probes, and process
    lifecycle management.  All methods are safe to call when opencodex
    is not running — they return sensible defaults or ``None``.
    """

    def __init__(self, base_url: str | None = None):
        self._base = (base_url or OCX_BASE).rstrip("/")
        self._tier_map = KNIGHT_TIER_MAP

    # ── Health probes ────────────────────────────────────────────────────

    def is_live(self) -> bool:
        """Check if the opencodex proxy is reachable (GET /healthz)."""
        result = _http_get(f"{self._base}/healthz", timeout=2.0)
        return result is not None

    def is_ready(self) -> bool:
        """Check if the proxy is fully ready (GET /readyz, status=ready)."""
        result = _http_get(f"{self._base}/readyz", timeout=3.0)
        if result is None:
            return False
        return result.get("status") == "ready"

    def health(self) -> dict[str, Any]:
        """Full health report from /readyz."""
        result = _http_get(f"{self._base}/readyz", timeout=3.0)
        return result or {"status": "unreachable", "service": "opencodex"}

    # ── Model resolution ─────────────────────────────────────────────────

    def resolve(
        self,
        knight_id: str,
        engine: str | None = None,
    ) -> tuple[str, str, str]:
        """Resolve a knight to (model, base_url, api_key).

        If opencodex is ready, uses its slug codec for provider/model
        resolution with failover.  Otherwise falls back to cliproxy.

        Returns:
            (model_id, base_url, api_key) tuple
        """
        tier_config = self._get_tier_config(engine)

        # If opencodex is ready, route through it
        if self.is_ready():
            if tier_config.local_only:
                # Local-only knights bypass opencodex (harness-locked)
                return tier_config.primary.model, tier_config.primary.base_url or OLLAMA_URL, ""
            wire_id = tier_config.primary.wire_id
            return wire_id, self._base, OCX_API_KEY or "proxy-admin-key"

        # Fallback: use cliproxy for cloud, Ollama for local
        if tier_config.local_only:
            return tier_config.primary.model, tier_config.primary.base_url or OLLAMA_URL, ""
        return tier_config.primary.model, CLIPROXY_URL, CLIPROXY_KEY

    def resolve_with_fallback(
        self,
        knight_id: str,
        engine: str | None = None,
    ) -> list[tuple[str, str, str]]:
        """Resolve with full failover chain.

        Returns a list of (model, base_url, api_key) tuples ordered by
        priority.  The first entry is the primary; the rest are fallbacks.
        """
        tier_config = self._get_tier_config(engine)
        result: list[tuple[str, str, str]] = []

        # Primary
        model, url, key = self.resolve(knight_id, engine)
        result.append((model, url, key))

        # Fallbacks (only if opencodex is handling them)
        if self.is_ready() and not tier_config.local_only:
            for fb in tier_config.fallbacks:
                wire_id = fb.wire_id
                result.append((wire_id, self._base, OCX_API_KEY or "proxy-admin-key"))

        return result

    # ── Provider registry ────────────────────────────────────────────────

    def list_providers(self) -> list[dict[str, Any]]:
        """List active providers from opencodex."""
        result = _http_get(f"{self._base}/api/providers", timeout=5.0)
        if result is None:
            return []
        # opencodex returns a dict of provider configs
        if isinstance(result, dict):
            return [{"id": k, **v} for k, v in result.items()]
        return result if isinstance(result, list) else []

    def list_models(self, provider: str | None = None) -> list[dict[str, Any]]:
        """List available models, optionally filtered by provider."""
        url = f"{self._base}/api/models"
        if provider:
            url += f"?provider={provider}"
        result = _http_get(url, timeout=5.0)
        if result is None:
            return []
        return result if isinstance(result, list) else []

    # ── Process lifecycle ────────────────────────────────────────────────

    def start(self, port: int | None = None) -> bool:
        """Start the opencodex proxy as a background process.

        Returns True if started successfully.
        """
        cmd = [sys.executable, "-m", "node_modules.@bitkyc08.opencodex.bin.ocx", "start"]
        if port:
            cmd.extend(["--port", str(port)])

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=os.getenv("CAMELOT_HOME", "."),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            logger.info("opencodex started (pid=%d)", proc.pid)
            return True
        except Exception as exc:
            logger.warning("failed to start opencodex: %s", exc)
            return False

    def stop(self) -> bool:
        """Stop the opencodex proxy."""
        try:
            result = _http_post(f"{self._base}/api/system/stop", {}, timeout=5.0)
            return result is not None
        except Exception:
            return False

    def status(self) -> dict[str, Any]:
        """Get proxy status."""
        result = _http_get(f"{self._base}/api/system/status", timeout=3.0)
        return result or {"status": "unreachable"}

    # ── Combo configuration ──────────────────────────────────────────────

    def get_combo_config(self, engine: str | None = None) -> dict[str, Any]:
        """Get the combo (failover/round-robin) config for a knight tier.

        Loads from omniroute.json ``combos`` section when available,
        falling back to the hardcoded ``KNIGHT_TIER_MAP``.
        """
        # Try to load from omniroute.json first
        omniroute_combos = self._load_omniroute_combos()
        if omniroute_combos and engine:
            tier_config = self._get_tier_config(engine)
            # Find a combo whose applicable_knights includes this engine's knights
            for combo_name, combo_cfg in omniroute_combos.items():
                if combo_cfg.get("local_only") != tier_config.local_only:
                    continue
                applicable = combo_cfg.get("applicable_knights", [])
                # Match by tier name prefix (G3, G2, G1, X1, L0)
                if combo_name.startswith(tier_config.tier):
                    return {
                        "strategy": combo_cfg.get("strategy", "failover"),
                        "targets": combo_cfg.get("targets", []),
                        "cooldown_seconds": combo_cfg.get("cooldown_seconds", 300),
                    }

        # Fallback: build from hardcoded tier map
        tier_config = self._get_tier_config(engine)
        targets = [{"provider": tier_config.primary.provider, "model": tier_config.primary.model}]
        for fb in tier_config.fallbacks:
            targets.append({"provider": fb.provider, "model": fb.model})
        return {
            "strategy": tier_config.combo_strategy,
            "targets": targets,
            "cooldown_seconds": 300,
        }

    def _load_omniroute_combos(self) -> dict[str, Any]:
        """Load combo definitions from omniroute.json."""
        candidates = [
            Path(os.getenv("CAMELOT_HOME", ".")) / "03_VAULT" / "training" / "configs" / "config" / "omniroute.json",
            Path(".") / "03_VAULT" / "training" / "configs" / "config" / "omniroute.json",
        ]
        for p in candidates:
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    combos = data.get("combos", {})
                    return {k: v for k, v in combos.items() if not k.startswith("_")}
                except Exception:
                    pass
        return {}

    # ── Internal helpers ─────────────────────────────────────────────────

    def _get_tier_config(self, engine: str | None) -> KnightTierConfig:
        """Look up tier config for an engine string."""
        if engine and engine in self._tier_map:
            return self._tier_map[engine]
        return self._tier_map["default"]


# ── Module-level singleton ───────────────────────────────────────────────────

_bridge: OCXBridge | None = None


def get_bridge() -> OCXBridge:
    """Get or create the module-level OCXBridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = OCXBridge()
    return _bridge


# ── Convenience functions (for SoulRouter / llm_router integration) ──────────

def resolve_knight_model(
    knight_id: str,
    engine: str | None = None,
) -> tuple[str, str, str]:
    """Resolve a knight to (model, base_url, api_key) via opencodex.

    This is the primary integration point for SoulRouter and llm_router.
    Falls back to cliproxy/Ollama if opencodex is not available.
    """
    return get_bridge().resolve(knight_id, engine)


def is_opencodex_available() -> bool:
    """Check if opencodex is running and ready."""
    return get_bridge().is_ready()
