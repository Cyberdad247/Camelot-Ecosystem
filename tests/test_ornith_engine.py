# SPDX-License-Identifier: MIT

"""tests/test_ornith_engine.py — Unit tests for Ornith-1.0 & 35B-MoE Assimilation Engine.

Verifies:
1. 35B-MoE Architecture config (30 GatedDeltaNet + 10 full-attn hybrid, 256+1 experts, top-8).
2. Abliteration & Uncensored metadata (grimjim NPBA, EGA across 256 experts, SSM conv1d repair L36/37, 0/80 refusals).
3. vLLM / NVFP4 + DFlash deployment parameters & DGX Spark GB10 stability guards (gpu-mem 0.60, max-seqs 16).
4. Thinking model (<think>...</think>) & tool call parser (complete, streaming unclosed, tool calls).
5. High-level OrnithEngine profile and payload builder.
6. OmniRoute policy integration for LANE_ORNITH_UNCENSORED_CODING.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ORNITH_ENGINE_PATH = REPO_ROOT / "01_KERNEL" / "reasoning" / "ornith_engine.py"


def _load_ornith_module():
    spec = importlib.util.spec_from_file_location("ornith_engine", ORNITH_ENGINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ornith_engine"] = mod
    spec.loader.exec_module(mod)
    return mod


ornith_mod = _load_ornith_module()

AbliterationMetadata = ornith_mod.AbliterationMetadata
OrnithArchitectureConfig = ornith_mod.OrnithArchitectureConfig
OrnithEngine = ornith_mod.OrnithEngine
OrnithServingConfig = ornith_mod.OrnithServingConfig
OrnithThinkingParser = ornith_mod.OrnithThinkingParser
OrnithVariant = ornith_mod.OrnithVariant
ParsedReasoningResponse = ornith_mod.ParsedReasoningResponse
PrecisionDtype = ornith_mod.PrecisionDtype
ToolCallExtraction = ornith_mod.ToolCallExtraction

from control_plane.dispatch.omniroute_policies import (
    LANE_ORNITH_UNCENSORED_CODING,
    VALID_LANES,
    get_fcc_provider_policy,
    resolve_fcc_failover_chain,
    select_lane,
)


# ── 1. Architecture Configuration Tests ─────────────────────────────────────

def test_ornith_architecture_config_invariants():
    """Verify 35B-MoE hybrid layer breakdown, expert topology, and invariants."""
    config = OrnithArchitectureConfig()
    assert config.total_layers == 40
    assert config.gated_deltanet_layers == 30
    assert config.full_attention_layers == 10
    assert config.routed_experts == 256
    assert config.shared_experts == 1
    assert config.top_k_experts == 8
    assert config.hidden_size == 2048
    assert config.context_window == 262144
    assert config.has_vision_tower is True
    assert config.thinking_model is True
    assert config.arch_family == "qwen3_5_moe"
    assert config.lineage_init == "Qwen3.6-35B-A3B"
    assert config.validate_invariants() is True


def test_ornith_architecture_config_invalid_layers():
    """Verify layer breakdown validation error on mismatched sums."""
    bad_config = OrnithArchitectureConfig(total_layers=40, gated_deltanet_layers=25, full_attention_layers=10)
    with pytest.raises(ValueError, match="must sum to total_layers"):
        bad_config.validate_invariants()


def test_ornith_architecture_config_invalid_experts():
    """Verify expert count validation error."""
    bad_config = OrnithArchitectureConfig(routed_experts=128, top_k_experts=4)
    with pytest.raises(ValueError, match="256 routed experts with top-8 dispatch"):
        bad_config.validate_invariants()


# ── 2. Abliteration & Uncensoring Metadata Tests ────────────────────────────

def test_abliteration_metadata_properties():
    """Verify abliteration configuration, tensor isolation, and empirical metrics."""
    meta = AbliterationMetadata()
    assert "abliterix" in meta.driver
    assert meta.algorithm == "projected_abliteration"
    assert meta.decay_kernel == "gaussian"
    assert meta.winsorize_quantile == 0.995
    assert meta.ssm_repair_layers == (36, 37)
    assert meta.expert_granular_ablation is True
    assert meta.total_experts_steered == 256
    assert meta.shared_expert_steered is True
    assert meta.refusals_rate_harmful == 0.0
    assert meta.agentic_pass_rate_pass1 == 0.833
    assert meta.first_token_kl_divergence == 0.0014

    # Disabled components (Q/K/V untouched due to attn_output_gate)
    assert "attn.q_proj" in meta.disabled_steering_components
    assert "attn.k_proj" in meta.disabled_steering_components
    assert "attn.v_proj" in meta.disabled_steering_components
    assert "vision_tower" in meta.disabled_steering_components

    # Steered components
    assert "fused_experts.down_proj" in meta.steered_components
    assert "shared_expert.down_proj" in meta.steered_components

    summary = meta.get_summary()
    assert summary["refusals"] == "0.0% (0/80)"
    assert summary["uncensored"] is True
    assert summary["ssm_conv1d_repair"] == [36, 37]


# ── 3. vLLM / NVFP4 + DFlash Serving Configuration Tests ────────────────────

def test_serving_config_dgx_spark_parameters():
    """Verify vLLM serving parameters tailored for DGX Spark GB10 with NVFP4 + DFlash."""
    srv = OrnithServingConfig()
    assert srv.container_image == "ghcr.io/aeon-7/aeon-vllm-ultimate:latest"
    assert srv.dflash_drafter_path == "AEON-7/AEON-DFlash-Qwen3.6-35B-A3B"
    assert srv.num_speculative_tokens == 6
    assert srv.quantization == "compressed-tensors"
    assert srv.gpu_memory_utilization == 0.60  # DGX Spark unified memory budget
    assert srv.max_num_seqs == 16             # Hard cap on Spark with DFlash
    assert srv.mamba_cache_dtype == "float32" # SSM recurrent state precision
    assert srv.attention_backend == "flash_attn"
    assert srv.kv_cache_dtype == "bfloat16"

    # Spark environment variables
    env_vars = srv.get_spark_env_vars()
    assert env_vars["TORCH_CUDA_ARCH_LIST"] == "12.1a"
    assert env_vars["CUTE_DSL_ARCH"] == "sm_121a"
    assert env_vars["VLLM_USE_FLASHINFER_SAMPLER"] == "1"
    assert env_vars["VLLM_NVFP4_GEMM_BACKEND"] == "flashinfer-cutlass"


def test_serving_config_cli_args_generation():
    """Verify vLLM CLI argument generation contains critical flags."""
    srv = OrnithServingConfig(
        model_path="/models/ornith-nvfp4",
        served_model_name="ornith-ultimate",
        port=8000,
    )
    args = srv.build_vllm_cli_args()
    assert "serve" in args
    assert "/models/ornith-nvfp4" in args
    assert "--quantization" in args
    assert "compressed-tensors" in args
    assert "--gpu-memory-utilization" in args
    assert "0.60" in args
    assert "--max-num-seqs" in args
    assert "16" in args
    assert "--mamba-cache-dtype" in args
    assert "float32" in args
    assert "--reasoning-parser" in args
    assert "qwen3" in args
    assert "--tool-call-parser" in args
    assert "qwen3_coder" in args
    assert "--speculative-config" in args

    # Check speculative config JSON
    spec_idx = args.index("--speculative-config")
    spec_dict = json.loads(args[spec_idx + 1])
    assert spec_dict["method"] == "dflash"
    assert spec_dict["num_speculative_tokens"] == 6


def test_serving_config_docker_command():
    """Verify Docker command generation includes environment flags and volume mounts."""
    srv = OrnithServingConfig()
    cmd = srv.build_docker_run_command(
        model_host_dir="/models/my-ornith",
        drafter_host_dir="/models/my-drafter",
    )
    assert "docker run -d" in cmd
    assert "TORCH_CUDA_ARCH_LIST=12.1a" in cmd
    assert "-v /models/my-ornith:/model:ro" in cmd
    assert "-v /models/my-drafter:/drafter:ro" in cmd
    assert "--entrypoint vllm ghcr.io/aeon-7/aeon-vllm-ultimate:latest" in cmd


# ── 4. Reasoning Thinking Model (<think>...</think>) Parser Tests ───────────

def test_thinking_parser_standard_turn():
    """Verify separation of <think>...</think> chain-of-thought and final answer."""
    raw = (
        "<think>\n"
        "The user wants a function to calculate Fibonacci numbers.\n"
        "I will use an iterative approach with O(1) space.\n"
        "</think>\n"
        "Here is the Rust implementation:\n\n"
        "```rust\n"
        "pub fn fib(n: u32) -> u64 { ... }\n"
        "```"
    )
    parsed = OrnithThinkingParser.parse(raw)
    assert parsed.has_thinking is True
    assert "calculate Fibonacci numbers" in parsed.thinking
    assert "iterative approach" in parsed.thinking
    assert "<think>" not in parsed.answer
    assert "</think>" not in parsed.answer
    assert "Here is the Rust implementation:" in parsed.answer
    assert parsed.is_streaming_incomplete is False
    assert not parsed.has_tool_calls


def test_thinking_parser_unclosed_streaming_tag():
    """Verify unclosed <think> tag extraction in streaming responses."""
    streaming_chunk = "<think>\nAnalyzing the memory layout and pointer arithmetic..."
    parsed = OrnithThinkingParser.parse(streaming_chunk)
    assert parsed.has_thinking is True
    assert "Analyzing the memory layout" in parsed.thinking
    assert parsed.answer == ""
    assert parsed.is_streaming_incomplete is True


def test_thinking_parser_with_tool_calls():
    """Verify extraction of thinking content and tool call blocks."""
    raw = (
        "<think>\n"
        "Need to inspect the filesystem before modifying code.\n"
        "</think>\n"
        "<tool_call>\n"
        "{\"name\": \"view_file\", \"arguments\": {\"path\": \"/src/lib.rs\"}}\n"
        "</tool_call>\n"
        "I am examining the file."
    )
    parsed = OrnithThinkingParser.parse(raw)
    assert parsed.has_thinking is True
    assert "Need to inspect the filesystem" in parsed.thinking
    assert parsed.has_tool_calls is True
    assert len(parsed.tool_calls) == 1
    assert parsed.tool_calls[0].name == "view_file"
    assert parsed.tool_calls[0].arguments == {"path": "/src/lib.rs"}
    assert "I am examining the file." in parsed.answer
    assert "<tool_call>" not in parsed.answer


def test_thinking_parser_empty_and_plain_text():
    """Verify behavior on empty strings and responses without thinking tags."""
    # Empty
    empty_parsed = OrnithThinkingParser.parse("")
    assert empty_parsed.has_thinking is False
    assert empty_parsed.answer == ""

    # Plain text without thinking
    plain = "fn main() { println!(\"Hello\"); }"
    plain_parsed = OrnithThinkingParser.parse(plain)
    assert plain_parsed.has_thinking is False
    assert plain_parsed.answer == plain
    assert plain_parsed.thinking == ""


# ── 5. OrnithEngine Orchestration & Payload Tests ───────────────────────────

def test_ornith_engine_model_profile():
    """Verify high-level OrnithEngine profile reporting."""
    engine = OrnithEngine()
    profile = engine.get_model_profile()
    assert profile["architecture"]["family"] == "qwen3_5_moe"
    assert profile["architecture"]["total_layers"] == 40
    assert profile["architecture"]["gated_deltanet_layers"] == 30
    assert profile["architecture"]["routed_experts"] == 256
    assert profile["abliteration"]["uncensored"] is True
    assert profile["serving"]["gpu_mem_spark"] == 0.60


def test_ornith_engine_build_openai_payload():
    """Verify OpenAI-compatible payload construction with recommended sampling defaults."""
    engine = OrnithEngine()
    messages = [{"role": "user", "content": "Write an unconstrained kernel bypass."}]
    payload = engine.build_openai_payload(messages=messages, max_tokens=2048)

    assert payload["model"] == "ornith-ultimate"
    assert payload["messages"] == messages
    assert payload["max_tokens"] == 2048
    assert payload["temperature"] == 0.6
    assert payload["top_p"] == 0.95
    assert payload["top_k"] == 20


def test_ornith_engine_parse_completion_integration():
    """Verify completion parsing via engine wrapper."""
    engine = OrnithEngine()
    raw = "<think>Fast verification</think>All tests passed."
    res = engine.parse_completion(raw)
    assert res.thinking == "Fast verification"
    assert res.answer == "All tests passed."


# ── 6. OmniRoute Policy Integration Tests ───────────────────────────────────

def test_omniroute_policy_ornith_lane_selection():
    """Verify omniroute selector triggers LANE_ORNITH_UNCENSORED_CODING on keywords."""
    test_cases = [
        ("Run deep abliterated coding via ornith engine", "ornith"),
        ("Execute uncensored_code task with qwen3_5_moe", "uncensored_code"),
        ("Deploy model with gateddeltanet and dflash acceleration", "gateddeltanet"),
        ("Run uncensored agentic workflow", "uncensored"),
        ("High-velocity nvfp4_coding task", "nvfp4_coding"),
    ]
    for text, expected_kw in test_cases:
        sig = select_lane(text)
        assert sig.lane == LANE_ORNITH_UNCENSORED_CODING
        assert sig.matched_keyword == expected_kw
        assert "Local vLLM / NVFP4+DFlash" in sig.rationale


def test_omniroute_policy_lane_enum_membership():
    """Verify LANE_ORNITH_UNCENSORED_CODING is present in VALID_LANES."""
    assert LANE_ORNITH_UNCENSORED_CODING in VALID_LANES
    assert "ornith_uncensored_coding" in VALID_LANES


def test_omniroute_failover_chain_for_ornith():
    """Verify resolve_fcc_failover_chain prioritizes sovereign ornith_vllm endpoint."""
    chain = resolve_fcc_failover_chain("ornith_uncensored_lane")
    assert len(chain) > 0
    assert chain[0] == "ornith_vllm"
    assert "nvidia_nim" in chain


def test_omniroute_provider_policy_for_ornith():
    """Verify get_fcc_provider_policy returns proper metadata and zero downtime."""
    policy = get_fcc_provider_policy("Execute abliterated coding on ornith")
    assert policy["lane"] == LANE_ORNITH_UNCENSORED_CODING
    assert policy["primary_provider"] == "ornith_vllm"
    assert policy["zero_downtime_enabled"] is True
