# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Tests for Assimilated Local LLM Adapter & Daemon (bitgpu + LiteRT-LM).
=====================================================================
Validates 1-bit quantized GPU execution, low-memory edge runner patterns,
attention sinks, speculative prompt lookup decoding (PLD), and the zero-cost
local LLM routing lane.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "03_VAULT" / "training" / "configs"))

from control_plane.infra.local_llm_daemon import (
    CATALOG_MODELS,
    AttentionSinkKVCache,
    BitGpuQuantizer,
    LocalInferenceEngine,
    PromptLookupEngine,
)


def test_bitgpu_sign_pack_and_unpack():
    """Verify 1-bit binary-weight packing into uint32 words and scale expansion."""
    # 32 weights with alternating signs
    weights = [1.0 if i % 2 == 0 else -1.0 for i in range(32)]
    packed = BitGpuQuantizer.pack_sign_words(weights)
    assert len(packed) == 1, "32 weights should pack into exactly 1 uint32 word"
    
    # 0b1010... binary pattern: even bits (0, 2, 4...) set to 1
    unpacked = BitGpuQuantizer.unpack_sign_word(packed[0], scale=2.5)
    assert len(unpacked) == 32
    for i in range(32):
        expected = 2.5 if i % 2 == 0 else -2.5
        assert unpacked[i] == expected


def test_bitgpu_binary_gemv():
    """Verify vectorized 1-bit GEMV calculation with block scaling."""
    # Rows=2, Cols=128 (1 block of 128 per row)
    rows = 2
    cols = 128
    block_size = 128
    
    x = [1.0] * cols
    
    # Row 0: all positive signs (0xFFFFFFFF for each 32-bit word) -> sum = 128 * 1.0 * scale
    # Row 1: all negative signs (0x00000000) -> sum = 128 * -1.0 * scale
    words_per_row = cols // 32
    sign_bits = [0xFFFFFFFF] * words_per_row + [0x00000000] * words_per_row
    scales = [0.5, 0.25]  # Row 0 scale=0.5, Row 1 scale=0.25
    
    y = BitGpuQuantizer.binary_gemv(x, sign_bits, scales, rows, cols, block_size)
    assert len(y) == 2
    assert y[0] == 128 * 1.0 * 0.5   # 64.0
    assert y[1] == 128 * -1.0 * 0.25  # -32.0


def test_speculative_prompt_lookup_decoding():
    """Verify Prompt Lookup Decoding (PLD) n-gram pattern matching."""
    # History containing recurring pattern: [10, 20, 30, 40, 50, ...] then ending in [10, 20]
    history = [10, 20, 30, 40, 50, 99, 10, 20]
    drafts = PromptLookupEngine.lookup_candidate_tokens(history, ngram_size=2, max_draft=3)
    assert drafts == [30, 40, 50], f"Expected candidate draft [30, 40, 50], got {drafts}"

    # Short history returns empty draft
    short_history = [10]
    assert PromptLookupEngine.lookup_candidate_tokens(short_history, ngram_size=2) == []


def test_attention_sink_kv_cache_eviction():
    """Verify bounded memory retention with attention sinks (StreamingLLM pattern)."""
    kv = AttentionSinkKVCache(max_seq_len=64, sink_tokens=4, precision="q8")
    assert kv.current_len == 0

    # Fill up to max sequence length
    for _ in range(64):
        kv.step()
    assert kv.current_len == 64
    assert kv.eviction_count == 0

    # Overflow should trigger compaction while preserving sink tokens
    kv.step()
    assert kv.eviction_count == 1
    assert kv.current_len >= kv.sink_tokens
    assert kv.current_len < 64


def test_local_model_catalog_and_vram_budget():
    """Verify registered local model manifests and memory budget estimation."""
    assert "bonsai-1.7b-1bit" in CATALOG_MODELS
    assert "qwen3-4b-1bit" in CATALOG_MODELS
    assert "litert-gemma-2b" in CATALOG_MODELS

    engine = LocalInferenceEngine("bonsai-1.7b-1bit")
    vram_mb = engine.get_vram_budget_mb()
    # 1.7B 1-bit should fit comfortably under 2000 MB VRAM
    assert vram_mb > 0
    assert vram_mb < 2000, f"Expected low memory footprint, got {vram_mb} MB"


def test_local_inference_chat_completion():
    """Verify local inference chat generation response structure and metrics."""
    engine = LocalInferenceEngine("bonsai-1.7b-1bit")
    messages = [
        {"role": "system", "content": "You are Sir Codex kinetic builder."},
        {"role": "user", "content": "Run 1-bit WebGPU matrix execution."},
    ]
    resp = engine.chat_completion(messages, temperature=0.5, max_tokens=32)

    assert resp["object"] == "chat.completion"
    assert resp["model"] == "bonsai-1.7b-1bit"
    assert resp["provider"] == "local_llm_daemon"
    assert "Zero-Cost Local Inference" in resp["content"]
    assert resp["usage"]["prompt_tokens"] > 0
    assert resp["usage"]["completion_tokens"] > 0
    assert "tokens_per_second" in resp["metrics"]


def test_llm_router_zero_cost_lane_integration():
    """Verify llm_router.py connects to local_daemon in the zero-cost local LLM routing lane."""
    from llm_router import PROVIDERS, chat

    assert "local_daemon" in PROVIDERS
    assert "bitgpu" in PROVIDERS
    assert PROVIDERS["local_daemon"].available is True
    assert PROVIDERS["bitgpu"].available is True

    # Test direct dispatch to local_daemon provider
    res = chat(
        messages=[{"role": "user", "content": "Execute zero-cost kinetic audit"}],
        provider="local_daemon",
    )
    assert res["provider"] == "local_daemon"
    assert "Zero-Cost Local Inference" in res["content"]


def test_typescript_adapter_artifacts_exist():
    """Verify 02_FORGE/kinetic/local_llm_adapter.ts is generated and contains core exports."""
    ts_path = PROJECT_ROOT / "02_FORGE" / "kinetic" / "local_llm_adapter.ts"
    assert ts_path.exists(), "local_llm_adapter.ts must exist in 02_FORGE/kinetic/"

    content = ts_path.read_text(encoding="utf-8")
    assert "export class LocalLlmAdapter" in content
    assert "export class BinaryWeightMath" in content
    assert "export class PromptLookupDecoder" in content
    assert "export class EdgeKVCacheManager" in content
    assert "WGSL_SHADERS" in content
