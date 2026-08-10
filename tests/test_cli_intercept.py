"""tests/test_cli_intercept.py — engine dispatch regression for Agents-A1.

The cli_intercept._resolve_engine() function maps a RouteDecision.engine
to (cmd, model, url). When the new ``agents_a1`` engine (the Agents-A1
35B MoE agentic LLM, served locally via vLLM/SGLang with an
OpenAI-compatible API) is selected, dispatch must route to:

  1. ``AGENTS_A1_BASE_URL`` env var (if set — operator's public tunnel),
  2. ``engines["agents_a1"].execution_path`` from omniroute.json,
  3. ``http://127.0.0.1:8000/v1`` (local vLLM default).

The ``cmd`` is always ``"openai_compat"`` so the downstream execution
layer knows the endpoint speaks OpenAI's chat-completions API (not
Ollama's). This file also verifies that ``sir_agentis`` is registered
in ``FOUNDRY_COUNCIL`` (else the route can never reach the engine).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make the project root importable when pytest is invoked from anywhere.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from control_plane.soul_router import (  # noqa: E402
    IntentTensor,
    RouteDecision,
    SoulRouter,
)

from control_plane import cli_intercept  # noqa: E402

# ── Helpers ────────────────────────────────────────────────────────────────


def _decision(engine: str, knight_id: str = "sir_agentis") -> RouteDecision:
    """Build a minimal RouteDecision that _resolve_engine() can read."""
    tensor = IntentTensor(velocity=0.5, magnitude=0.5, privacy=0.0, environment=0.0)
    return RouteDecision(
        knight_id=knight_id,
        engine=engine,
        weight=0.87,
        score=0.5,
        tensor=tensor,
        reason="KEYWORD_MATCH: sir_agentis",
    )


def _write_omniroute(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agents_a1_cfg: dict,
) -> None:
    """Write a minimal omniroute.json to a temp path and patch the module
    constant so CLIIntercept._load_omniroute() picks it up."""
    cfg = tmp_path / "omniroute.json"
    cfg.write_text(json.dumps({"engines": {"agents_a1": agents_a1_cfg}}))
    monkeypatch.setattr(cli_intercept, "OMNIROUTE_CONFIG", cfg)


# ── agents_a1 dispatch (env override) ──────────────────────────────────────


def test_agents_a1_uses_env_base_url(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """AGENTS_A1_BASE_URL beats omniroute.json execution_path."""
    _write_omniroute(
        monkeypatch,
        tmp_path,
        {
            "provider": "local",
            "execution_path": "127.0.0.1:8000",
            "model": "InternScience/Agents-A1",
        },
    )
    monkeypatch.setenv("AGENTS_A1_BASE_URL", "https://tunnel.example.com/v1")

    intercept = cli_intercept.CLIIntercept()
    cmd, model, url = intercept._resolve_engine(_decision("agents_a1"))

    assert cmd == "openai_compat"
    assert model == "InternScience/Agents-A1"
    assert url == "https://tunnel.example.com/v1"


# ── agents_a1 dispatch (omniroute.json execution_path) ─────────────────────


def test_agents_a1_falls_back_to_execution_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When AGENTS_A1_BASE_URL is unset, dispatch uses omniroute.json
    execution_path, prepending ``http://`` if no scheme is present."""
    _write_omniroute(
        monkeypatch,
        tmp_path,
        {
            "provider": "local",
            "execution_path": "127.0.0.1:8000",
            "model": "InternScience/Agents-A1",
        },
    )
    monkeypatch.delenv("AGENTS_A1_BASE_URL", raising=False)

    intercept = cli_intercept.CLIIntercept()
    cmd, model, url = intercept._resolve_engine(_decision("agents_a1"))

    assert cmd == "openai_compat"
    assert model == "InternScience/Agents-A1"
    # The openai SDK appends /chat/completions to baseURL, so we don't
    # add a trailing /v1 here — the path is just the host:port.
    assert url == "http://127.0.0.1:8000"


def test_agents_a1_full_url_in_execution_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """If execution_path is already a full URL (http://...), use it verbatim
    — the dispatcher must not double-prepend ``http://``."""
    _write_omniroute(
        monkeypatch,
        tmp_path,
        {
            "provider": "local",
            "execution_path": "http://127.0.0.1:8000/v1",
            "model": "InternScience/Agents-A1",
        },
    )
    monkeypatch.delenv("AGENTS_A1_BASE_URL", raising=False)

    intercept = cli_intercept.CLIIntercept()
    _cmd, _model, url = intercept._resolve_engine(_decision("agents_a1"))

    assert url == "http://127.0.0.1:8000/v1"


def test_agents_a1_empty_env_string_falls_back(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An env var explicitly set to ``""`` is treated as unset (the
    ``or`` short-circuits because empty string is falsy). Guards against
    a future refactor that swaps ``or`` for an explicit truthiness check
    that would break this behavior."""
    _write_omniroute(
        monkeypatch,
        tmp_path,
        {
            "provider": "local",
            "execution_path": "127.0.0.1:8000",
            "model": "InternScience/Agents-A1",
        },
    )
    monkeypatch.setenv("AGENTS_A1_BASE_URL", "")

    intercept = cli_intercept.CLIIntercept()
    _cmd, _model, url = intercept._resolve_engine(_decision("agents_a1"))

    assert url == "http://127.0.0.1:8000"


def test_agents_a1_whitespace_env_stripped(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An env var with surrounding whitespace is stripped before the
    ``startswith`` check, so a value like ``'  https://tunnel/v1  '``
    resolves to a valid URL instead of failing the scheme check."""
    _write_omniroute(monkeypatch, tmp_path, {})
    monkeypatch.setenv("AGENTS_A1_BASE_URL", "  https://tunnel.example.com/v1  ")

    intercept = cli_intercept.CLIIntercept()
    _cmd, _model, url = intercept._resolve_engine(_decision("agents_a1"))

    assert url == "https://tunnel.example.com/v1"


def test_agents_a1_hardcoded_default_when_no_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When both env and execution_path are missing, dispatch uses the
    hardcoded ``http://127.0.0.1:8000/v1`` fallback so the test
    environment is always runnable."""
    _write_omniroute(monkeypatch, tmp_path, {})  # no agents_a1 entry
    monkeypatch.delenv("AGENTS_A1_BASE_URL", raising=False)

    intercept = cli_intercept.CLIIntercept()
    cmd, model, url = intercept._resolve_engine(_decision("agents_a1"))

    assert cmd == "openai_compat"
    assert model == "InternScience/Agents-A1"
    assert url == "http://127.0.0.1:8000/v1"


# ── Foundry Council registration (regression guard) ───────────────────────


def test_sir_agentis_is_registered_in_foundry_council() -> None:
    """The soul_router must register ``sir_agentis`` so the engine is
    reachable at all. This guards against a future refactor that
    accidentally drops the KnightEngine from FOUNDRY_COUNCIL."""
    engine = SoulRouter().get_engine("sir_agentis")
    assert engine is not None, "sir_agentis must be in FOUNDRY_COUNCIL"
    assert engine.engine == "agents_a1"
    assert engine.privacy_level == 0.9, (
        "agents-a1 is local-first; privacy_level should be 0.9 so the "
        "PRIVACY_OVERRIDE branch in SoulRouter.route() leaves it eligible"
    )


# ── Cross-surface consistency (regression guards) ─────────────────────────
#
# These tests verify that the four OmniRoute surfaces stay in sync:
#   - omniroute.json (config)
#   - soul_router.FOUNDRY_COUNCIL (knight registry)
#   - cli_intercept._resolve_engine (Python dispatch)
#   - bifrost._ENGINE_DISPATCH (real LLM dispatcher)
#   - switchboard.TERMINAL_REGISTRY (health probe)
#
# Each new engine should appear in all five. A test that catches a
# missing surface prevents the classic "engine is routable from CLI
# but not from the Bifrost dispatcher" footgun.


def test_agents_a1_in_bifrost_engine_dispatch() -> None:
    """bifrost._ENGINE_DISPATCH must route agents_a1 via the cliproxy
    strategy with AGENTS_A1_BASE as the base URL. Without this, the
    Bifrost dispatcher (the actual LLM call path) silently falls through
    to the default claude-sonnet-4-6 dispatch."""
    from control_plane import bifrost
    assert "agents_a1" in bifrost._ENGINE_DISPATCH, (
        "agents_a1 missing from bifrost._ENGINE_DISPATCH; the real "
        "dispatcher would fall through to claude-sonnet-4-6 by default"
    )
    strategy, base, model = bifrost._ENGINE_DISPATCH["agents_a1"]
    assert strategy == "cliproxy", (
        f"agents_a1 should reuse the cliproxy (OpenAI-compat) strategy; "
        f"got {strategy!r}"
    )
    assert base == bifrost.AGENTS_A1_BASE, (
        f"agents_a1 base should equal AGENTS_A1_BASE env var; got {base!r}"
    )
    assert model == "InternScience/Agents-A1"


def test_sir_agentis_in_switchboard_terminal_registry() -> None:
    """switchboard.TERMINAL_REGISTRY must register sir_agentis so the
    cockpit's HUD (and any operator console) can probe its health."""
    from control_plane import switchboard
    terminal = switchboard.TERMINAL_REGISTRY.get("sir_agentis")
    assert terminal is not None, (
        "sir_agentis missing from switchboard.TERMINAL_REGISTRY; the "
        "cockpit's HUD would never show its health"
    )
    assert terminal.engine == "agents_a1"
    assert terminal.cost_tier == "free", (
        "agents-a1 is local-first; cost_tier should be 'free'"
    )
    assert "agentic" in terminal.capability
    assert terminal.probe_url, (
        "sir_agentis must have a probe_url (vLLM /health) for the "
        "switchboard to probe its live status"
    )
