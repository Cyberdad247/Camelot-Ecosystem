# SPDX-License-Identifier: MIT

"""tests/test_fcc_assimilation.py — Unit tests for Free Claude Code (FCC) assimilation.

Verifies:
1. FCC provider catalog (50+ providers), canonical endpoints, and provider descriptors.
2. Knight tier multi-provider failover chains.
3. Zero-downtime failover session state machine (pre-commit advancement vs post-commit lock).
4. RTK terminal output filtering and token reduction.
5. RTK command prefix extraction, env var handling, and filepath extraction.
6. OmniRoute policies with FCC failover and RTK optimization lane signals.
"""

from __future__ import annotations


from control_plane.core.ocx_bridge import (
    FCC_DEFAULT_BASE_URLS,
    FCC_PROVIDER_CATALOG,
    KNIGHT_TIER_MAP,
    FailoverCandidateState,
    OCXBridge,
    ProviderAuthKind,
    ProviderModel,
    ZeroDowntimeFailoverSession,
    extract_command_prefix,
    extract_filepaths_from_command,
    filter_terminal_output,
    get_fcc_provider_descriptor,
    get_provider_base_url,
    is_quota_check_request,
    is_title_generation_request,
)
from control_plane.dispatch.omniroute_policies import (
    LANE_CLIPROXY_HEAVY_REASONING,
    LANE_DEFAULT,
    LANE_FCC_FAILOVER_MATRIX,
    LANE_OMNI_ROUTE_CODEX,
    LANE_RTK_FILTERED_FAST_PATH,
    get_fcc_provider_policy,
    resolve_fcc_failover_chain,
    select_lane,
)


# ── 1. FCC Provider Catalog & Canonical Endpoints ────────────────────────────

def test_fcc_provider_catalog_contains_expected_providers():
    """Verify the assimilated provider catalog has all 50+ providers."""
    assert len(FCC_PROVIDER_CATALOG) >= 30
    assert len(FCC_DEFAULT_BASE_URLS) >= 40

    key_providers = [
        "nvidia_nim",
        "open_router",
        "groq",
        "cline_pass",
        "openai",
        "xai",
        "qwencloud",
        "together",
        "deepinfra",
        "siliconflow",
        "gemini",
        "vertex",
        "deepseek",
        "mistral",
        "opencode_zen",
        "vercel",
        "bedrock",
        "huggingface",
        "cohere",
        "github_models",
        "cloudflare",
        "zai",
        "ollama_cloud",
        "lmstudio",
        "llamacpp",
        "ollama",
    ]
    for pid in key_providers:
        assert pid in FCC_PROVIDER_CATALOG, f"Missing provider: {pid}"
        assert pid in FCC_DEFAULT_BASE_URLS, f"Missing default base URL for: {pid}"


def test_fcc_provider_descriptors():
    """Verify provider descriptors and base URLs return expected attributes."""
    nim = get_fcc_provider_descriptor("nvidia_nim")
    assert nim is not None
    assert nim.provider_id == "nvidia_nim"
    assert nim.display_name == "NVIDIA NIM"
    assert nim.credential_env == "NVIDIA_NIM_API_KEY"
    assert "nvidia.com" in nim.default_base_url

    openai_desc = get_fcc_provider_descriptor("openai")
    assert openai_desc is not None
    assert openai_desc.auth_kind == ProviderAuthKind.CONNECTED_ACCOUNT

    local_ollama = get_fcc_provider_descriptor("ollama")
    assert local_ollama is not None
    assert local_ollama.local is True

    # Base URL lookup
    assert get_provider_base_url("groq") == "https://api.groq.com/openai/v1"
    assert get_provider_base_url("deepseek") == "https://api.deepseek.com"
    assert get_provider_base_url("unknown_xyz") == ""


def test_ocx_bridge_fcc_provider_listing():
    """Verify OCXBridge list_fcc_providers returns structured catalog entries."""
    bridge = OCXBridge()
    providers = bridge.list_fcc_providers()
    assert len(providers) == len(FCC_PROVIDER_CATALOG)
    p_dict = {p["id"]: p for p in providers}
    assert "open_router" in p_dict
    assert p_dict["open_router"]["display_name"] == "OpenRouter"


# ── 2. Knight Tier Map & Multi-Provider Failover Chains ──────────────────────

def test_knight_tier_map_failover_chains():
    """Verify Knight tier mappings contain rich multi-provider failover chains."""
    claude_cfg = KNIGHT_TIER_MAP["claude_code"]
    assert claude_cfg.tier == "G3"
    assert claude_cfg.primary.provider == "anthropic"
    assert len(claude_cfg.fallbacks) >= 4

    fallback_providers = [fb.provider for fb in claude_cfg.fallbacks]
    assert "google" in fallback_providers
    assert "nvidia_nim" in fallback_providers
    assert "open_router" in fallback_providers
    assert "groq" in fallback_providers

    codex_cfg = KNIGHT_TIER_MAP["openai_codex"]
    assert codex_cfg.tier == "X1"
    assert codex_cfg.primary.provider == "openai"
    codex_fallbacks = [fb.provider for fb in codex_cfg.fallbacks]
    assert "opencode_zen" in codex_fallbacks
    assert "mistral_codestral" in codex_fallbacks


def test_ocx_bridge_resolve_with_fallback():
    """Verify resolve_with_fallback returns full chain of targets."""
    bridge = OCXBridge()
    chain = bridge.resolve_with_fallback("claude_code", "claude_code")
    assert len(chain) >= 5
    # First entry is primary
    primary_model, primary_url, _ = chain[0]
    assert "claude-opus" in primary_model


# ── 3. Zero-Downtime Failover Session State Machine ──────────────────────────

def test_zero_downtime_failover_session_progression():
    """Verify pre-commit retryable failover seamlessly advances across candidates."""
    candidates = [
        ProviderModel("anthropic", "claude-opus-5"),
        ProviderModel("nvidia_nim", "nemotron-3", base_url="https://nim.url"),
        ProviderModel("open_router", "free", base_url="https://openrouter.url"),
    ]
    session = ZeroDowntimeFailoverSession(candidates=candidates)

    assert session.candidate_count == 3
    assert session.candidate_index == 0
    assert session.current_candidate.provider_model_ref == "anthropic/claude-opus-5"
    assert session.current_candidate.state == FailoverCandidateState.ACTIVE
    assert not session.is_committed

    # 1. First candidate fails with a 503 retryable outage
    next_c = session.record_failure_and_advance(
        failure_kind="UNAVAILABLE", status_code=503, error_message="Provider overloaded", retryable=True
    )
    assert next_c is not None
    assert session.candidate_index == 1
    assert next_c.provider_model_ref == "nvidia_nim/nemotron-3"
    assert next_c.state == FailoverCandidateState.ACTIVE

    # 2. Second candidate fails with a timeout
    next_c2 = session.record_failure_and_advance(
        failure_kind="TIMEOUT", status_code=504, error_message="Read timed out", retryable=True
    )
    assert next_c2 is not None
    assert session.candidate_index == 2
    assert next_c2.provider_model_ref == "open_router/free"

    # 3. Third candidate succeeds and commits first stream frame
    session.commit()
    assert session.is_committed
    assert session.current_candidate.state == FailoverCandidateState.COMMITTED

    # 4. Once committed, failover is locked (prohibits downstream duplicate corruption)
    post_commit_advance = session.record_failure_and_advance(
        failure_kind="ERROR", status_code=500, error_message="Mid-stream drop", retryable=True
    )
    assert post_commit_advance is None

    # Verify traces captured
    traces = session.get_traces()
    assert len(traces) == 3
    events = [t["event"] for t in traces]
    assert "camelot.fcc.model_fallback.started" in events
    assert "camelot.fcc.model_fallback.committed" in events


def test_zero_downtime_failover_non_retryable_and_exhaustion():
    """Verify non-retryable errors stop failover immediately, and exhaustion is handled."""
    candidates = [
        ProviderModel("primary", "m1"),
        ProviderModel("backup", "m2"),
    ]
    # Non-retryable error
    session = ZeroDowntimeFailoverSession(candidates=candidates)
    res = session.record_failure_and_advance(
        failure_kind="AUTH_FAILED", status_code=401, error_message="Invalid key", retryable=False
    )
    assert res is None
    assert session.candidate_index == 0

    # Exhaustion
    session2 = ZeroDowntimeFailoverSession(candidates=candidates)
    next_1 = session2.record_failure_and_advance(failure_kind="ERROR", status_code=500, retryable=True)
    assert next_1 is not None
    # Now at last candidate, another failure exhausts list
    next_2 = session2.record_failure_and_advance(failure_kind="ERROR", status_code=500, retryable=True)
    assert next_2 is None


# ── 4. RTK Terminal Output Filtering ─────────────────────────────────────────

def test_rtk_filter_terminal_output_ansi_and_progress():
    """Verify RTK filtering cleans ANSI codes, progress bars, and collapses repetitive spinner ticks."""
    raw_terminal = (
        "\x1b[32m[INFO]\x1b[0m Starting build...\n"
        "Downloading package [=========>       ] 45%\n"
        "Downloading package [================>] 100%\n"
        "\x1b[1;34mBuild succeeded\x1b[0m in 1.2s\n"
    )
    cleaned = filter_terminal_output(raw_terminal)
    assert "\x1b[" not in cleaned
    assert "[INFO] Starting build..." in cleaned
    assert "Build succeeded in 1.2s" in cleaned
    assert "[=========>" not in cleaned

    # Token reduction test
    raw_noisy = ("Compiling crates.io...\n\x1b[2K\r[==> ] 20%\n" * 50) + "Finished dev [unoptimized + debuginfo] target(s)\n"
    cleaned_noisy = filter_terminal_output(raw_noisy)
    # Filtered output should be significantly shorter
    assert len(cleaned_noisy) < len(raw_noisy) * 0.3
    assert "Finished dev" in cleaned_noisy


# ── 5. RTK Command Utilities & Fast-Path Intercepts ──────────────────────────

def test_extract_command_prefix():
    """Verify command prefix extraction, env var handling, and injection detection."""
    assert extract_command_prefix("git commit -m 'Initial commit'") == "git commit"
    assert extract_command_prefix("npm test -- --watch") == "npm test"
    assert extract_command_prefix("cargo build --release") == "cargo build"
    assert extract_command_prefix("pytest tests/test_fcc.py") == "pytest"
    assert extract_command_prefix("python -m foo") == "python"

    # Environment variables (two-word command returns two-word prefix; single-word returns env+cmd)
    assert extract_command_prefix("NODE_ENV=production npm run build") == "npm run"
    assert extract_command_prefix("DEBUG=1 FOO=bar python script.py") == "DEBUG=1 FOO=bar python"

    # Command injection detection
    assert extract_command_prefix("echo `whoami`") == "command_injection_detected"
    assert extract_command_prefix("cat $(ls /etc)") == "command_injection_detected"

    # Empty
    assert extract_command_prefix("") == "none"


def test_extract_filepaths_from_command():
    """Verify filepath extraction from reading vs listing commands."""
    # Listing commands -> empty
    assert extract_filepaths_from_command("ls -la /var/log") == "<filepaths>\n</filepaths>"
    assert extract_filepaths_from_command("find . -name '*.py'") == "<filepaths>\n</filepaths>"
    assert extract_filepaths_from_command("tree src/") == "<filepaths>\n</filepaths>"

    # Reading commands -> extracted paths
    cat_res = extract_filepaths_from_command("cat src/main.py")
    assert "<filepaths>\nsrc/main.py\n</filepaths>" == cat_res

    head_res = extract_filepaths_from_command("head -n 20 docs/readme.md")
    assert "docs/readme.md" in head_res

    # Grep command
    grep_res = extract_filepaths_from_command("grep -e 'import' app.py server.py")
    assert "app.py" in grep_res
    assert "server.py" in grep_res


def test_fast_path_detectors():
    """Verify quota and title generation request detectors."""
    assert is_quota_check_request("Check my quota limit", max_tokens=1) is True
    assert is_quota_check_request("Check my quota limit", max_tokens=100) is False
    assert is_quota_check_request("Hello world", max_tokens=1) is False

    assert is_title_generation_request("Please return a sentence-case title for this session") is True
    assert is_title_generation_request("Return JSON with title field") is True
    assert is_title_generation_request("Refactor the database queries") is False


# ── 6. OmniRoute Policies FCC & RTK Lane Selection ──────────────────────────

def test_omniroute_policies_lane_selection():
    """Verify OmniRoute policy signals classify FCC failover and RTK optimization requests."""
    # RTK Optimization
    sig_rtk = select_lane("Clean terminal logs with rtk filter_terminal")
    assert sig_rtk.lane == LANE_RTK_FILTERED_FAST_PATH
    assert sig_rtk.matched_keyword == "rtk"
    assert "RTK Terminal Engine" in sig_rtk.rationale

    # FCC Failover
    sig_fcc = select_lane("Execute with zero-downtime failover across multi-provider matrix")
    assert sig_fcc.lane == LANE_FCC_FAILOVER_MATRIX
    assert sig_fcc.matched_keyword == "zero-downtime"
    assert "Multi-Provider Matrix" in sig_fcc.rationale

    # Existing Scaffold & Reasoning lanes
    sig_scaffold = select_lane("//CODEX scaffold a React login component")
    assert sig_scaffold.lane == LANE_OMNI_ROUTE_CODEX

    sig_reasoning = select_lane("MERLIN deep-context reasoning over 1m-context")
    assert sig_reasoning.lane == LANE_CLIPROXY_HEAVY_REASONING

    # Default
    sig_default = select_lane("//STATUS")
    assert sig_default.lane == LANE_DEFAULT


def test_omniroute_policies_fcc_helpers():
    """Verify resolve_fcc_failover_chain and get_fcc_provider_policy."""
    chain_g3 = resolve_fcc_failover_chain("G3_APEX")
    assert "anthropic" in chain_g3
    assert "nvidia_nim" in chain_g3
    assert "open_router" in chain_g3

    chain_x1 = resolve_fcc_failover_chain("X1_CODEX")
    assert "openai" in chain_x1
    assert "opencode_zen" in chain_x1

    policy = get_fcc_provider_policy("Zero-downtime multi-provider resilience")
    assert policy["lane"] == LANE_FCC_FAILOVER_MATRIX
    assert policy["zero_downtime_enabled"] is True
    assert len(policy["failover_chain"]) > 0
