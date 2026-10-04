# SPDX-License-Identifier: MIT
"""
tests/test_frontier_compressor.py — Unit tests for Frontier Edge Compression & Quantization.
Verifies BitNet b1.58, SpinQuant, KIVI 2-bit KV Cache, SnapKV Governor, and Speculative Cascade.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from control_plane.quantization.frontier_compressor import (
    AttentionEvictionState,
    CompressedKIVICache,
    KIVICacheCompressor,
    PackedTernaryWeights,
    SnapKVAttentionGovernor,
    SpeculativeDraftCascade,
    SpinQuantRotator,
    Ternary158Compressor,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "03_VAULT" / "training" / "configs" / "config" / "frontier_quantization_spec.json"


def test_frontier_spec_validity():
    """Verify that frontier_quantization_spec.json exists and conforms to schema requirements."""
    assert SPEC_PATH.exists(), f"Spec missing at {SPEC_PATH}"
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    assert spec["version"] == "v10001.00-CYBERTRONIA"
    assert spec["global_law_compliance"]["node_ceiling_mb"] == 4096
    assert "tier_0_extreme_edge_ternary" in spec["quantization_profiles"]
    assert "tier_1_ultra_low_bit_gguf" in spec["quantization_profiles"]
    assert "kv_cache_compression" in spec
    assert spec["kv_cache_compression"]["engine"] == "KIVI_POLARQUANT_ASYMMETRIC"


def test_ternary_158_quantization_and_packing():
    """Verify BitNet b1.58 ternary quantization and 2-bit packing/unpacking."""
    rng = np.random.default_rng(42)
    weights = rng.normal(0.0, 1.0, size=(128, 256)).astype(np.float32)

    ternary, gamma = Ternary158Compressor.quantize(weights)
    assert set(np.unique(ternary)).issubset({-1, 0, 1})
    assert gamma > 0.0

    packed = Ternary158Compressor.pack(ternary, gamma)
    assert isinstance(packed, PackedTernaryWeights)
    assert packed.shape == (128, 256)
    assert packed.packed_data.dtype == np.uint8

    reconstructed = Ternary158Compressor.unpack(packed)
    assert reconstructed.shape == weights.shape

    ratio = Ternary158Compressor.compression_ratio(weights, packed)
    # Original is 128*256*4 = 131,072 bytes. Packed is ~8,192 bytes. Ratio > 15x.
    assert ratio >= 14.0

    # Ensure nonzero correlation between original and reconstructed
    corr = np.corrcoef(weights.ravel(), reconstructed.ravel())[0, 1]
    assert corr > 0.65


def test_spinquant_hadamard_orthogonality_and_kurtosis():
    """Verify SpinQuant normalized Hadamard matrix orthogonality and outlier dispersion."""
    for dim in [8, 16, 64]:
        h = SpinQuantRotator.generate_hadamard_matrix(dim)
        is_ortho, max_err = SpinQuantRotator.verify_orthogonality(h)
        assert is_ortho, f"Hadamard matrix {dim}x{dim} not orthogonal (error: {max_err})"
        assert max_err < 1e-12

    # Test randomized rotation with random diagonal sign flips
    rot64 = SpinQuantRotator.create_randomized_rotation(64, seed=123)
    is_ortho, max_err = SpinQuantRotator.verify_orthogonality(rot64)
    assert is_ortho, f"Randomized Hadamard rotation not orthogonal: {max_err}"

    # Verify outlier suppression
    rng = np.random.default_rng(999)
    activations = rng.normal(0, 0.1, size=(50, 64))
    # Inject heavy outlier in channel 5
    activations[:, 5] += 12.0

    kurt_before = SpinQuantRotator.compute_kurtosis(activations)
    rotated = SpinQuantRotator.rotate_activations(activations, rot64)
    kurt_after = SpinQuantRotator.compute_kurtosis(rotated)

    assert kurt_before > 10.0
    assert kurt_after < kurt_before
    # Inner product isometry check: ||X||_F == ||X R||_F
    norm_orig = np.linalg.norm(activations)
    norm_rot = np.linalg.norm(rotated)
    np.testing.assert_allclose(norm_orig, norm_rot, rtol=1e-5)


def test_kivi_asymmetric_kv_cache_compression():
    """Verify KIVI asymmetric 2-bit Key (per-channel) and Value (per-token) compression."""
    rng = np.random.default_rng(2026)
    seq_len, num_heads, head_dim = 64, 4, 32
    keys = rng.normal(0, 1, size=(seq_len, num_heads, head_dim)).astype(np.float32)
    values = rng.normal(0, 1, size=(seq_len, num_heads, head_dim)).astype(np.float32)

    compressed = KIVICacheCompressor.compress_kv(keys, values)
    assert isinstance(compressed, CompressedKIVICache)
    assert compressed.compression_ratio >= 7.0

    recon_k = KIVICacheCompressor.dequantize_keys(
        compressed.k_packed, compressed.k_scales, compressed.k_zeros, keys.shape
    )
    recon_v = KIVICacheCompressor.dequantize_values(
        compressed.v_packed, compressed.v_scales, compressed.v_zeros, values.shape
    )

    assert recon_k.shape == keys.shape
    assert recon_v.shape == values.shape

    # Mean squared error of 2-bit quantization on standard normal should be bounded
    k_mse = float(np.mean((keys - recon_k) ** 2))
    v_mse = float(np.mean((values - recon_v) ** 2))
    assert k_mse < 0.50
    assert v_mse < 0.50


def test_snapkv_streaming_attention_governor():
    """Verify SnapKV dynamic eviction and memory budget compliance."""
    gov = SnapKVAttentionGovernor(
        preserved_sink_tokens=16,
        preserved_local_tokens=32,
        max_budget_mb=0.05,  # 0.05 MB budget (~200 tokens ceiling)
        num_layers=4,
        num_heads=4,
        head_dim=32,
        bytes_per_elem=0.25,
    )

    seq_len = 500
    scores = np.linspace(0.1, 1.0, seq_len)
    preserved, state = gov.select_eviction_indices(scores)

    assert isinstance(state, AttentionEvictionState)
    assert state.total_tokens_seen == 500
    assert state.evicted_tokens > 0
    assert state.current_cache_mb <= state.max_budget_mb

    # Sinks (0..15) must be preserved
    for i in range(16):
        assert i in preserved

    # Local window (468..499) must be preserved
    for i in range(468, 500):
        assert i in preserved


def test_speculative_draft_cascade_verification():
    """Verify speculative decoding rejection sampling and speedup calculations."""
    draft = [10, 20, 30, 40]
    draft_p = np.array([0.9, 0.9, 0.8, 0.8])
    target_p = np.array([0.95, 0.95, 0.85, 0.85])

    res = SpeculativeDraftCascade.verify_tokens(draft, draft_p, target_p, seed=42)
    assert res.draft_tokens_proposed == 4
    assert res.num_accepted == 4
    assert res.acceptance_rate == 1.0
    assert res.speedup_multiplier > 2.0

    # With mismatched logits, cascade stops at rejection point
    target_p_low = np.array([0.95, 0.001, 0.85, 0.85])
    res_mismatch = SpeculativeDraftCascade.verify_tokens(draft, draft_p, target_p_low, seed=42)
    assert res_mismatch.num_accepted == 1  # only first accepted
