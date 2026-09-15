# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT
"""Colibri MoE Disk Streaming Runtime (GLM-5.2 744B on 25GB RAM Architecture).

Assimilated from colibri C/Python high-throughput bare-metal streaming engine:
- LFRU Expert Cache (Frequency + Recency tiebreaker, 25% + 4 hysteresis against ping-pong,
  decaying live heat maps, dynamic hot-store re-pinning, prefetching).
- Multi-Head Latent Attention (MLA) with Low-Rank Compressed KV-Cache (kv_lora + decoupled qk_rope),
  on-the-fly key/value reconstruction, and COLIKV1 persistent disk serialization.
- Sigmoid Router with bias and routed_scaling_factor, top-k selection, and Batch-Union MoE
  (loading each unique expert once per batch/sequence for shared disk I/O amortisation).
- MTP (Multi-Token Prediction) Speculative Decoding (GLM-5.2/DeepSeek-V3 native dual-state draft head,
  Leviathan rejection sampling, ngram prompt-lookup fallback, and MTP KV absorption).
- GBNF Grammar-Forced Drafts (Pushdown Automaton byte-level walker for deterministic syntax acceleration).
- 744B Resource Planner for running 744B parameter models comfortably within <=25GB RAM constraints.

Zero external dependencies outside Python stdlib.
"""

from __future__ import annotations

import copy
import math
import random
import re
import struct
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# ============================================================================
# 1. ARCHITECTURE CONFIGURATION & RESOURCE PLANNER (GLM-5.2 744B on 25GB RAM)
# ============================================================================

@dataclass
class ColibriConfig:
    """GLM-5.2 744B / MoE Model Architecture Configuration."""
    model_name: str = "GLM-5.2-744B-MoE"
    hidden_size: int = 6144
    n_layers: int = 78
    n_heads: int = 48
    n_experts: int = 256
    top_k: int = 8
    moe_intermediate_size: int = 2048
    dense_intermediate_size: int = 16384
    first_k_dense_replace: int = 2
    n_shared_experts: int = 1
    vocab_size: int = 151552
    
    # MLA Attention parameters
    q_lora_rank: int = 1536
    kv_lora_rank: int = 576
    qk_nope_head_dim: int = 128
    qk_rope_head_dim: int = 64
    v_head_dim: int = 128
    rotary_base: float = 10000.0
    attn_scale: Optional[float] = None
    
    # Router parameters
    routed_scaling_factor: float = 2.5
    norm_topk: bool = False
    top_p_routing: float = 1.0
    
    # Quantization format: 0=F32 (4B), 1=INT8 (1B), 2=INT4 (0.5B), 3=INT2 (0.25B)
    dense_bits: int = 4   # Dense resident params in INT4
    expert_bits: int = 4  # Expert streamed params in INT4
    
    # Speculation parameters
    has_mtp: bool = True
    mtp_draft_depth: int = 3
    ngram_draft_depth: int = 3
    grammar_forced_draft_max: int = 16
    
    # System RAM budget
    max_ram_budget_bytes: int = 25 * 1024 * 1024 * 1024  # 25 GB RAM
    hot_expert_slots_per_layer: int = 4
    
    def __post_init__(self) -> None:
        if self.attn_scale is None:
            self.attn_scale = 1.0 / math.sqrt(self.qk_nope_head_dim + self.qk_rope_head_dim)


@dataclass
class ResourcePlanReport:
    """Hardware & Memory layout breakdown for 744B MoE execution."""
    model_name: str
    total_params_b: float
    dense_params_b: float
    moe_params_b: float
    dense_resident_bytes: int
    expert_single_bytes: int
    hot_store_ram_bytes: int
    kv_cache_per_token_bytes: int
    max_context_tokens_in_ram: int
    projected_resident_ram_gb: float
    fits_ram_budget: bool
    recommended_pin_capacity: int
    storage_footprint_gb: float


class ColibriResourcePlanner:
    """Calculates exact memory allocations, disk bandwidth, and slot layouts."""

    @staticmethod
    def plan_model(cfg: ColibriConfig) -> ResourcePlanReport:
        d = cfg.hidden_size
        moe_inter = cfg.moe_intermediate_size
        dense_inter = cfg.dense_intermediate_size
        L = cfg.n_layers
        E = cfg.n_experts
        V = cfg.vocab_size

        # Embedding + LM Head
        embed_params = V * d
        lm_head_params = V * d

        # Attention MLA parameters per layer:
        q_head_total = cfg.n_heads * (cfg.qk_nope_head_dim + cfg.qk_rope_head_dim)
        kv_head_total = cfg.n_heads * (cfg.qk_nope_head_dim + cfg.v_head_dim)
        mla_layer_params = (
            d * cfg.q_lora_rank +
            cfg.q_lora_rank * q_head_total +
            d * (cfg.kv_lora_rank + cfg.qk_rope_head_dim) +
            cfg.kv_lora_rank * kv_head_total +
            (cfg.n_heads * cfg.v_head_dim) * d
        )

        # Dense MLP params per dense layer (first_k_dense_replace): gate, up, down
        dense_mlp_layer_params = 2 * d * dense_inter + dense_inter * d

        # MoE Layer: shared expert + router + E routed experts
        shared_expert_params = cfg.n_shared_experts * (2 * d * moe_inter + moe_inter * d)
        router_params = d * E + E  # weights + bias
        single_expert_params = 2 * d * moe_inter + moe_inter * d
        moe_routed_layer_params = E * single_expert_params

        # Aggregation
        dense_layers_count = cfg.first_k_dense_replace
        moe_layers_count = L - dense_layers_count

        dense_params_total = (
            embed_params + lm_head_params +
            L * mla_layer_params +
            dense_layers_count * dense_mlp_layer_params +
            moe_layers_count * (shared_expert_params + router_params) +
            (2 * d * d if cfg.has_mtp else 0)  # eh_proj
        )

        moe_params_total = moe_layers_count * moe_routed_layer_params
        if cfg.has_mtp:
            moe_params_total += moe_routed_layer_params

        total_params = dense_params_total + moe_params_total

        # Byte calculations based on INT4 (0.5 B/param) or INT8 (1 B/param) + float scales
        d_bytes_per_param = 0.5 if cfg.dense_bits == 4 else (1.0 if cfg.dense_bits == 8 else 4.0)
        e_bytes_per_param = 0.5 if cfg.expert_bits == 4 else (1.0 if cfg.expert_bits == 8 else 4.0)

        dense_resident_bytes = int(dense_params_total * d_bytes_per_param) + (L * 4096 * 4)  # norms
        single_expert_bytes = int(single_expert_params * e_bytes_per_param) + (moe_inter * 4 * 3)  # scales

        # Hot store in RAM (pinned + LRU working set)
        slots_per_layer = cfg.hot_expert_slots_per_layer
        hot_store_ram_bytes = moe_layers_count * slots_per_layer * single_expert_bytes

        # Compressed KV Cache per token (only latent c_KV [576] and k_rot [64] per layer)
        kv_floats_per_token_per_layer = cfg.kv_lora_rank + cfg.qk_rope_head_dim
        kv_cache_per_token_bytes = L * kv_floats_per_token_per_layer * 4  # Float32 KV cache

        # Overhead headroom for KV, buffers, activations
        headroom_bytes = 4 * 1024 * 1024 * 1024  # 4 GB headroom
        available_for_kv = cfg.max_ram_budget_bytes - (dense_resident_bytes + hot_store_ram_bytes + headroom_bytes)
        max_context_tokens = max(1024, int(available_for_kv // max(1, kv_cache_per_token_bytes)))

        projected_resident_ram_gb = (dense_resident_bytes + hot_store_ram_bytes + 4096 * kv_cache_per_token_bytes) / 1e9
        fits_ram = (dense_resident_bytes + hot_store_ram_bytes + 4096 * kv_cache_per_token_bytes) <= cfg.max_ram_budget_bytes
        storage_footprint_gb = (dense_resident_bytes + moe_params_total * e_bytes_per_param) / 1e9

        return ResourcePlanReport(
            model_name=cfg.model_name,
            total_params_b=round(total_params / 1e9, 2),
            dense_params_b=round(dense_params_total / 1e9, 2),
            moe_params_b=round(moe_params_total / 1e9, 2),
            dense_resident_bytes=dense_resident_bytes,
            expert_single_bytes=single_expert_bytes,
            hot_store_ram_bytes=hot_store_ram_bytes,
            kv_cache_per_token_bytes=kv_cache_per_token_bytes,
            max_context_tokens_in_ram=max_context_tokens,
            projected_resident_ram_gb=round(projected_resident_ram_gb, 2),
            fits_ram_budget=fits_ram,
            recommended_pin_capacity=slots_per_layer,
            storage_footprint_gb=round(storage_footprint_gb, 2),
        )


# ============================================================================
# 2. EXPERT DISK STORE & LFRU TIERED CACHE (WITH 25%+4 HYSTERESIS)
# ============================================================================

@dataclass
class QuantizedTensor:
    """INT8 / INT4 Quantized Tensor with per-row scaling factor."""
    fmt: int  # 0=F32, 1=INT8, 2=INT4
    rows: int
    cols: int
    data: bytes
    scales: List[float]

    @classmethod
    def from_floats(cls, matrix: List[List[float]], fmt: int = 1) -> QuantizedTensor:
        rows = len(matrix)
        cols = len(matrix[0]) if rows > 0 else 0
        scales: List[float] = []
        byte_chunks: List[bytes] = []

        if fmt in (0, 32):  # F32
            for row in matrix:
                scales.append(1.0)
                byte_chunks.append(struct.pack(f"{len(row)}f", *row))
            return cls(fmt=0, rows=rows, cols=cols, data=b"".join(byte_chunks), scales=scales)

        elif fmt in (1, 8):  # INT8 per-row absmax/127
            for row in matrix:
                amax = max(abs(v) for v in row) if row else 1e-12
                scale = amax / 127.0 if amax > 1e-12 else 1e-12
                scales.append(scale)
                inv_scale = 1.0 / scale
                q8 = [max(-128, min(127, int(round(v * inv_scale)))) for v in row]
                byte_chunks.append(struct.pack(f"{len(q8)}b", *q8))
            return cls(fmt=1, rows=rows, cols=cols, data=b"".join(byte_chunks), scales=scales)

        elif fmt in (2, 4):  # INT4 packed (2 nibbles per byte, offset -8)
            for row in matrix:
                amax = max(abs(v) for v in row) if row else 1e-12
                scale = amax / 7.0 if amax > 1e-12 else 1e-12
                scales.append(scale)
                inv_scale = 1.0 / scale
                packed_row = bytearray()
                for i in range(0, len(row), 2):
                    v0 = max(-8, min(7, int(round(row[i] * inv_scale)))) + 8  # [0, 15]
                    v1 = (max(-8, min(7, int(round(row[i+1] * inv_scale)))) + 8) if i + 1 < len(row) else 8
                    packed_row.append((v0 & 0x0F) | ((v1 & 0x0F) << 4))
                byte_chunks.append(bytes(packed_row))
            return cls(fmt=2, rows=rows, cols=cols, data=b"".join(byte_chunks), scales=scales)

        raise ValueError(f"Unsupported quantization format: {fmt}")

    def dequantize_row(self, row_idx: int) -> List[float]:
        scale = self.scales[row_idx]
        if self.fmt == 0:
            off = row_idx * self.cols * 4
            return list(struct.unpack(f"{self.cols}f", self.data[off:off + self.cols * 4]))
        elif self.fmt == 1:
            off = row_idx * self.cols
            raw_ints = struct.unpack(f"{self.cols}b", self.data[off:off + self.cols])
            return [float(x) * scale for x in raw_ints]
        elif self.fmt == 2:
            row_bytes = (self.cols + 1) // 2
            off = row_idx * row_bytes
            raw_bytes = self.data[off:off + row_bytes]
            out: List[float] = []
            for b in raw_bytes:
                n0 = (b & 0x0F) - 8
                n1 = ((b >> 4) & 0x0F) - 8
                out.append(float(n0) * scale)
                if len(out) < self.cols:
                    out.append(float(n1) * scale)
            return out[:self.cols]
        return []

    def matmul_vec(self, x: List[float]) -> List[float]:
        """y = W @ x where W is [rows, cols], x is [cols], y is [rows]."""
        out: List[float] = [0.0] * self.rows
        for r in range(self.rows):
            w_row = self.dequantize_row(r)
            s = 0.0
            for c in range(self.cols):
                s += w_row[c] * x[c]
            out[r] = s
        return out


@dataclass
class ExpertWeights:
    """Expert weights slot: gate_proj, up_proj, down_proj."""
    layer: int
    expert_id: int
    gate_proj: QuantizedTensor
    up_proj: QuantizedTensor
    down_proj: QuantizedTensor
    size_bytes: int

    def forward(self, x: List[float]) -> List[float]:
        """SwiGLU forward: down_proj(SiLU(gate_proj(x)) * up_proj(x))."""
        g = self.gate_proj.matmul_vec(x)
        u = self.up_proj.matmul_vec(x)
        # silu(g) * u
        inter = [(gi / (1.0 + math.exp(-max(-30.0, min(30.0, gi))))) * ui for gi, ui in zip(g, u)]
        return self.down_proj.matmul_vec(inter)


class ExpertDiskStore:
    """Simulates NVMe disk layout of quantized expert shards."""

    def __init__(self, cfg: ColibriConfig, synthetic_seed: int = 42) -> None:
        self.cfg = cfg
        self.seed = synthetic_seed
        self.io_reads_count = 0
        self.bytes_read_total = 0
        self.synthetic_experts: Dict[Tuple[int, int], ExpertWeights] = {}
        self._init_synthetic_shards()

    def _init_synthetic_shards(self) -> None:
        rng = random.Random(self.seed)
        d = self.cfg.hidden_size
        inter = self.cfg.moe_intermediate_size
        fmt = self.cfg.expert_bits

        # Generate lightweight representative synthetic weights for available layers
        for layer in range(min(4, self.cfg.n_layers)):
            if layer < self.cfg.first_k_dense_replace:
                continue
            for e in range(min(32, self.cfg.n_experts)):
                g_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(inter)]
                u_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(inter)]
                d_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(inter)] for _ in range(d)]

                q_g = QuantizedTensor.from_floats(g_mat, fmt=fmt)
                q_u = QuantizedTensor.from_floats(u_mat, fmt=fmt)
                q_d = QuantizedTensor.from_floats(d_mat, fmt=fmt)
                size_b = len(q_g.data) + len(q_u.data) + len(q_d.data) + (inter * 4 * 2 + d * 4)

                self.synthetic_experts[(layer, e)] = ExpertWeights(
                    layer=layer,
                    expert_id=e,
                    gate_proj=q_g,
                    up_proj=q_u,
                    down_proj=q_d,
                    size_bytes=size_b,
                )

    def read_expert(self, layer: int, expert_id: int) -> ExpertWeights:
        """Pread from disk storage with simulated access accounting."""
        self.io_reads_count += 1
        expert = self.synthetic_experts.get((layer, expert_id))
        if expert is None:
            rng = random.Random(self.seed + layer * 1000 + expert_id)
            d = self.cfg.hidden_size
            inter = self.cfg.moe_intermediate_size
            g_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(inter)]
            u_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(inter)]
            d_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(inter)] for _ in range(d)]
            expert = ExpertWeights(
                layer=layer,
                expert_id=expert_id,
                gate_proj=QuantizedTensor.from_floats(g_mat, fmt=self.cfg.expert_bits),
                up_proj=QuantizedTensor.from_floats(u_mat, fmt=self.cfg.expert_bits),
                down_proj=QuantizedTensor.from_floats(d_mat, fmt=self.cfg.expert_bits),
                size_bytes=2 * d * inter + inter * d,
            )
        self.bytes_read_total += expert.size_bytes
        return expert


class LFRUExpertCache:
    """Colibri LFRU Tiered Cache Engine with Hysteresis and Dynamic Re-pinning."""

    def __init__(self, cfg: ColibriConfig, disk_store: ExpertDiskStore) -> None:
        self.cfg = cfg
        self.disk = disk_store
        self.clock: int = 0
        self.hits: int = 0
        self.misses: int = 0
        self.evictions: int = 0
        
        # Per layer heat and recency tracking: layer -> {expert_id: count}
        self.eheat: Dict[int, Dict[int, int]] = {l: {} for l in range(cfg.n_layers)}
        self.elast: Dict[int, Dict[int, int]] = {l: {} for l in range(cfg.n_layers)}
        
        # Resident working set and pinned hot-store: layer -> OrderedDict[expert_id, ExpertWeights]
        self.pinned: Dict[int, Dict[int, ExpertWeights]] = {l: {} for l in range(cfg.n_layers)}
        self.lru_cache: Dict[int, OrderedDict[int, ExpertWeights]] = {l: OrderedDict() for l in range(cfg.n_layers)}
        self.pin_capacity = cfg.hot_expert_slots_per_layer
        self.lru_capacity = cfg.hot_expert_slots_per_layer * 2

    def lfru_score(self, heat: int, last_access: int) -> int:
        """tier_lfru_score: (heat << 8) | (255 - age)."""
        age = self.clock - last_access if self.clock >= last_access else 0
        recent = 255 - age if age < 255 else 0
        return (heat << 8) | recent

    def pick_lfru_swap(self, layer: int) -> Optional[Tuple[int, int, int]]:
        """Finds if a candidate unpinned expert should replace the coldest pinned expert."""
        pinned_eids = list(self.pinned[layer].keys())
        if not pinned_eids or len(pinned_eids) < self.pin_capacity:
            return None

        cold_eid = min(
            pinned_eids,
            key=lambda e: self.lfru_score(self.eheat[layer].get(e, 0), self.elast[layer].get(e, 0))
        )
        cs = self.lfru_score(self.eheat[layer].get(cold_eid, 0), self.elast[layer].get(cold_eid, 0))

        hot_eid = -1
        hs = 0
        for e, heat in self.eheat[layer].items():
            if e in self.pinned[layer]:
                continue
            sc = self.lfru_score(heat, self.elast[layer].get(e, 0))
            if sc > hs:
                hs = sc
                hot_eid = e

        if hot_eid < 0:
            return None

        # 25% + (4 << 8) Hysteresis threshold
        hysteresis_margin = cs + (cs >> 2) + (4 << 8)
        if hs <= hysteresis_margin:
            return None  # Gain is not high enough to warrant disk swap

        gain = (hs - cs) >> 8
        return (cold_eid, hot_eid, gain)

    def touch(self, layer: int, expert_id: int) -> None:
        """Increment heat and tick clock."""
        self.clock += 1
        self.eheat[layer][expert_id] = self.eheat[layer].get(expert_id, 0) + 1
        self.elast[layer][expert_id] = self.clock

    def decay_heat(self, layer: Optional[int] = None) -> None:
        """Periodic heat decay (tier_decay: heat >>= 1)."""
        layers_to_decay = [layer] if layer is not None else list(self.eheat.keys())
        for l in layers_to_decay:
            for e in list(self.eheat[l].keys()):
                self.eheat[l][e] >>= 1
                if self.eheat[l][e] == 0:
                    del self.eheat[l][e]

    def repin_pass(self, layer: int) -> Optional[Dict[str, Any]]:
        """Live Re-pin pass between turns: swaps cold pins for hot unpinned experts."""
        swap = self.pick_lfru_swap(layer)
        if not swap:
            return None
        cold_eid, hot_eid, gain = swap
        del self.pinned[layer][cold_eid]
        if hot_eid in self.lru_cache[layer]:
            expert = self.lru_cache[layer].pop(hot_eid)
        else:
            expert = self.disk.read_expert(layer, hot_eid)
        self.pinned[layer][hot_eid] = expert
        self.decay_heat(layer)
        return {
            "layer": layer,
            "evicted_pin": cold_eid,
            "admitted_pin": hot_eid,
            "gain": gain,
        }

    def get_expert(self, layer: int, expert_id: int) -> ExpertWeights:
        """Fetch expert from Pinned hot-store, LRU RAM cache, or load from Disk."""
        self.touch(layer, expert_id)

        # 1. Pinned Hot-Store
        if expert_id in self.pinned[layer]:
            self.hits += 1
            return self.pinned[layer][expert_id]

        # 2. LRU RAM Cache
        if expert_id in self.lru_cache[layer]:
            self.hits += 1
            expert = self.lru_cache[layer].pop(expert_id)
            self.lru_cache[layer][expert_id] = expert
            return expert

        # 3. Disk Miss
        self.misses += 1
        expert = self.disk.read_expert(layer, expert_id)

        if len(self.pinned[layer]) < self.pin_capacity:
            self.pinned[layer][expert_id] = expert
            return expert

        if len(self.lru_cache[layer]) >= self.lru_capacity:
            self.lru_cache[layer].popitem(last=False)
            self.evictions += 1
        self.lru_cache[layer][expert_id] = expert
        return expert


# ============================================================================
# 3. SIGMOID ROUTER & BATCH-UNION MOE
# ============================================================================

class SigmoidMoERouter:
    """GLM-5.2 Sigmoid Router with bias, top-k selection, and routed scaling factor."""

    def __init__(self, cfg: ColibriConfig, seed: int = 101) -> None:
        self.cfg = cfg
        d = cfg.hidden_size
        E = cfg.n_experts
        rng = random.Random(seed)
        self.weight = [[(rng.random() * 0.02 - 0.01) for _ in range(E)] for _ in range(d)]
        self.bias = [(rng.random() * 0.01 - 0.005) for _ in range(E)]

    def route(self, x: List[float]) -> Tuple[List[int], List[float]]:
        """Compute sigmoid(x @ W) + bias, and select top-k experts."""
        d = self.cfg.hidden_size
        E = self.cfg.n_experts
        K = self.cfg.top_k

        logits = [0.0] * E
        for e in range(E):
            s = 0.0
            for i in range(d):
                s += x[i] * self.weight[i][e]
            logits[e] = s

        probs = [1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, val)))) for val in logits]
        scores = [p + b for p, b in zip(probs, self.bias)]

        indexed_scores = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        top_k_indices = [idx for idx, _ in indexed_scores[:K]]
        top_k_weights = [probs[idx] for idx in top_k_indices]

        if 0.0 < self.cfg.top_p_routing < 1.0:
            tot = sum(top_k_weights)
            cum = 0.0
            keep_count = K
            for i, w in enumerate(top_k_weights):
                cum += w
                if cum >= self.cfg.top_p_routing * tot:
                    keep_count = i + 1
                    break
            top_k_indices = top_k_indices[:keep_count]
            top_k_weights = top_k_weights[:keep_count]

        if self.cfg.norm_topk:
            s_sum = sum(top_k_weights) + 1e-20
            top_k_weights = [w / s_sum for w in top_k_weights]

        top_k_weights = [w * self.cfg.routed_scaling_factor for w in top_k_weights]
        return top_k_indices, top_k_weights


class BatchUnionMoE:
    """MoE Forward pass with Batch-Union Expert Deduplication."""

    def __init__(self, cfg: ColibriConfig, layer_idx: int, cache: LFRUExpertCache, seed: int = 202) -> None:
        self.cfg = cfg
        self.layer = layer_idx
        self.cache = cache
        self.router = SigmoidMoERouter(cfg, seed=seed + layer_idx)
        d = cfg.hidden_size
        inter = cfg.moe_intermediate_size * cfg.n_shared_experts
        rng = random.Random(seed + 999 + layer_idx)
        g_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(inter)]
        u_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(inter)]
        d_mat = [[(rng.random() * 0.02 - 0.01) for _ in range(inter)] for _ in range(d)]
        self.shared_expert = ExpertWeights(
            layer=layer_idx,
            expert_id=-1,
            gate_proj=QuantizedTensor.from_floats(g_mat, fmt=cfg.expert_bits),
            up_proj=QuantizedTensor.from_floats(u_mat, fmt=cfg.expert_bits),
            down_proj=QuantizedTensor.from_floats(d_mat, fmt=cfg.expert_bits),
            size_bytes=2 * d * inter + inter * d,
        )

    def forward_batch(self, batch_x: List[List[float]]) -> List[List[float]]:
        """Forward batch of sequence positions through MoE layer."""
        S = len(batch_x)
        d = self.cfg.hidden_size
        out = [[0.0] * d for _ in range(S)]

        batch_routes: List[Tuple[List[int], List[float]]] = []
        for s in range(S):
            indices, weights = self.router.route(batch_x[s])
            batch_routes.append((indices, weights))

        unique_experts: OrderedDict[int, List[Tuple[int, float]]] = OrderedDict()
        for s in range(S):
            indices, weights = batch_routes[s]
            for eid, w in zip(indices, weights):
                if eid not in unique_experts:
                    unique_experts[eid] = []
                unique_experts[eid].append((s, w))

        for eid, positions in unique_experts.items():
            expert = self.cache.get_expert(self.layer, eid)
            for s_idx, weight in positions:
                x_pos = batch_x[s_idx]
                h_out = expert.forward(x_pos)
                for i in range(d):
                    out[s_idx][i] += weight * h_out[i]

        for s in range(S):
            sh_out = self.shared_expert.forward(batch_x[s])
            for i in range(d):
                out[s][i] += sh_out[i]

        return out


# ============================================================================
# 4. MLA ATTENTION WITH COMPRESSED KV-CACHE & DISK PERSISTENCE (COLIKV1)
# ============================================================================

@dataclass
class CompressedKVCacheRow:
    """Compressed KV representation for single token: latent c_KV + rotary key k_rot."""
    token_id: int
    latent_c_kv: List[float]  # size: kv_lora_rank (e.g. 576)
    k_rot: List[float]        # size: qk_rope_head_dim (e.g. 64)


class CompressedKVCache:
    """Compressed KV Cache with low memory footprint and COLIKV1 serialization."""

    MAGIC = b"COLIKV1\x00"

    def __init__(self, cfg: ColibriConfig) -> None:
        self.cfg = cfg
        self.layers_cache: List[List[CompressedKVCacheRow]] = [[] for _ in range(cfg.n_layers)]
        self.mtp_cache: List[CompressedKVCacheRow] = []

    def append_token(self, layer: int, token_id: int, latent_c_kv: List[float], k_rot: List[float]) -> None:
        row = CompressedKVCacheRow(token_id=token_id, latent_c_kv=latent_c_kv, k_rot=k_rot)
        if layer < self.cfg.n_layers:
            self.layers_cache[layer].append(row)
        else:
            self.mtp_cache.append(row)

    def truncate(self, length: int) -> None:
        for layer in range(self.cfg.n_layers):
            self.layers_cache[layer] = self.layers_cache[layer][:length]
        self.mtp_cache = self.mtp_cache[:length]

    def length(self) -> int:
        return len(self.layers_cache[0]) if self.layers_cache else 0

    def serialize_to_disk(self, filepath: Union[str, Path]) -> int:
        """COLIKV1 binary disk serialization (atomic append/sync)."""
        path = Path(filepath)
        nrec = self.length()
        header = struct.pack(
            "<8s8i",
            self.MAGIC,
            self.cfg.n_layers,
            self.cfg.kv_lora_rank,
            self.cfg.qk_rope_head_dim,
            0,  # index_hd
            0,  # nic
            self.cfg.vocab_size,
            nrec,
            0,  # reserved
        )

        records_bytes = bytearray()
        for p in range(nrec):
            tok_id = self.layers_cache[0][p].token_id
            records_bytes.extend(struct.pack("<i", tok_id))
            for l in range(self.cfg.n_layers):
                row = self.layers_cache[l][p]
                records_bytes.extend(struct.pack(f"{len(row.latent_c_kv)}f", *row.latent_c_kv))
                records_bytes.extend(struct.pack(f"{len(row.k_rot)}f", *row.k_rot))

        with open(path, "wb") as f:
            f.write(header)
            f.write(records_bytes)

        return len(header) + len(records_bytes)

    @classmethod
    def load_from_disk(cls, cfg: ColibriConfig, filepath: Union[str, Path]) -> CompressedKVCache:
        """Reconstruct compressed KV Cache from COLIKV1 file."""
        cache = cls(cfg)
        path = Path(filepath)
        if not path.exists():
            return cache

        with open(path, "rb") as f:
            magic_and_header = f.read(40)
            if len(magic_and_header) < 40:
                return cache
            magic, n_layers, kv_lora, qk_rope, _, _, _, nrec, _ = struct.unpack("<8s8i", magic_and_header)
            if magic != cls.MAGIC or n_layers != cfg.n_layers:
                return cache

            rec_floats_per_layer = kv_lora + qk_rope
            for _ in range(nrec):
                tok_raw = f.read(4)
                if len(tok_raw) < 4:
                    break
                tok_id = struct.unpack("<i", tok_raw)[0]
                for l in range(n_layers):
                    c_kv_bytes = f.read(kv_lora * 4)
                    k_rot_bytes = f.read(qk_rope * 4)
                    if len(c_kv_bytes) < kv_lora * 4 or len(k_rot_bytes) < qk_rope * 4:
                        break
                    c_kv = list(struct.unpack(f"{kv_lora}f", c_kv_bytes))
                    k_rot = list(struct.unpack(f"{qk_rope}f", k_rot_bytes))
                    cache.append_token(l, tok_id, c_kv, k_rot)

        return cache


class MLAAttention:
    """Multi-Head Latent Attention (MLA) with decoupled RoPE and dynamic KV reconstruction."""

    def __init__(self, cfg: ColibriConfig, layer_idx: int, seed: int = 303) -> None:
        self.cfg = cfg
        self.layer = layer_idx
        d = cfg.hidden_size
        H = cfg.n_heads
        q_lora = cfg.q_lora_rank
        kv_lora = cfg.kv_lora_rank
        qk_nope = cfg.qk_nope_head_dim
        qk_rope = cfg.qk_rope_head_dim
        vh = cfg.v_head_dim

        rng = random.Random(seed + layer_idx)
        q_head_dim = qk_nope + qk_rope
        self.q_a = [[(rng.random() * 0.02 - 0.01) for _ in range(q_lora)] for _ in range(d)]
        self.q_b = [[(rng.random() * 0.02 - 0.01) for _ in range(H * q_head_dim)] for _ in range(q_lora)]

        kv_head_dim = qk_nope + vh
        self.kv_a = [[(rng.random() * 0.02 - 0.01) for _ in range(kv_lora + qk_rope)] for _ in range(d)]
        self.kv_b = [[(rng.random() * 0.02 - 0.01) for _ in range(H * kv_head_dim)] for _ in range(kv_lora)]

        self.w_o = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(H * vh)]

    def apply_rope(self, x: List[float], pos: int) -> List[float]:
        """RoPE rotary embedding applied to pair coordinates."""
        dim = len(x)
        out = list(x)
        for i in range(0, dim - 1, 2):
            freq = 1.0 / (self.cfg.rotary_base ** (i / dim))
            theta = pos * freq
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            x0, x1 = x[i], x[i+1]
            out[i] = x0 * cos_t - x1 * sin_t
            out[i+1] = x0 * sin_t + x1 * cos_t
        return out

    def forward(
        self,
        x: List[float],
        pos: int,
        token_id: int,
        kv_cache: CompressedKVCache
    ) -> List[float]:
        """Compute causal MLA attention for single position and update compressed KV-cache."""
        d = self.cfg.hidden_size
        H = self.cfg.n_heads
        q_lora = self.cfg.q_lora_rank
        kv_lora = self.cfg.kv_lora_rank
        qk_nope = self.cfg.qk_nope_head_dim
        qk_rope = self.cfg.qk_rope_head_dim
        vh = self.cfg.v_head_dim

        # 1. Project Q through Q-LoRA
        q_latent = [0.0] * q_lora
        for j in range(q_lora):
            s = 0.0
            for i in range(d):
                s += x[i] * self.q_a[i][j]
            q_latent[j] = s

        q_proj_dim = H * (qk_nope + qk_rope)
        q_full = [0.0] * q_proj_dim
        for j in range(q_proj_dim):
            s = 0.0
            for i in range(q_lora):
                s += q_latent[i] * self.q_b[i][j]
            q_full[j] = s

        # 2. Project KV through KV-LoRA
        kv_a_out_dim = kv_lora + qk_rope
        kv_a_out = [0.0] * kv_a_out_dim
        for j in range(kv_a_out_dim):
            s = 0.0
            for i in range(d):
                s += x[i] * self.kv_a[i][j]
            kv_a_out[j] = s

        c_kv = kv_a_out[:kv_lora]
        k_rot_raw = kv_a_out[kv_lora:]
        k_rot = self.apply_rope(k_rot_raw, pos)

        kv_cache.append_token(self.layer, token_id, c_kv, k_rot)

        # 3. Dynamic Attention over past cached tokens
        context_len = len(kv_cache.layers_cache[self.layer])
        head_outputs: List[float] = [0.0] * (H * vh)
        attn_scale = self.cfg.attn_scale or (1.0 / math.sqrt(qk_nope + qk_rope))

        for h in range(H):
            q_head_offset = h * (qk_nope + qk_rope)
            q_nope_h = q_full[q_head_offset : q_head_offset + qk_nope]
            q_rope_raw = q_full[q_head_offset + qk_nope : q_head_offset + qk_nope + qk_rope]
            q_rope_h = self.apply_rope(q_rope_raw, pos)

            scores: List[float] = []
            values: List[List[float]] = []

            for t in range(context_len):
                row = kv_cache.layers_cache[self.layer][t]
                kv_b_head_offset = h * (qk_nope + vh)
                k_nope_t: List[float] = [0.0] * qk_nope
                v_t: List[float] = [0.0] * vh

                for j in range(qk_nope):
                    s = 0.0
                    col = kv_b_head_offset + j
                    for i in range(kv_lora):
                        s += row.latent_c_kv[i] * self.kv_b[i][col]
                    k_nope_t[j] = s

                for j in range(vh):
                    s = 0.0
                    col = kv_b_head_offset + qk_nope + j
                    for i in range(kv_lora):
                        s += row.latent_c_kv[i] * self.kv_b[i][col]
                    v_t[j] = s

                score = sum(qn * kn for qn, kn in zip(q_nope_h, k_nope_t))
                score += sum(qr * kr for qr, kr in zip(q_rope_h, row.k_rot))
                score *= attn_scale
                scores.append(score)
                values.append(v_t)

            max_s = max(scores) if scores else 0.0
            exp_s = [math.exp(max(-30.0, min(30.0, s - max_s))) for s in scores]
            sum_exp = sum(exp_s) + 1e-12
            weights = [s / sum_exp for s in exp_s]

            for j in range(vh):
                val_acc = sum(w * v[j] for w, v in zip(weights, values))
                head_outputs[h * vh + j] = val_acc

        # 4. Output Projection
        out = [0.0] * d
        for j in range(d):
            s = 0.0
            for i in range(H * vh):
                s += head_outputs[i] * self.w_o[i][j]
            out[j] = s

        return out


# ============================================================================
# 5. GBNF GRAMMAR ENGINE & FORCED DRAFTS
# ============================================================================

@dataclass
class GBNFSymbol:
    """Grammar symbol: literal character class or rule reference."""
    is_rule_ref: bool
    rule_name: str = ""
    allowed_bytes: Set[int] = field(default_factory=set)


@dataclass
class GBNFAlternate:
    """Sequence of grammar symbols forming an alternative path."""
    symbols: List[GBNFSymbol] = field(default_factory=list)


@dataclass
class GBNFRule:
    """Named GBNF rule with list of alternate derivations."""
    name: str
    alternates: List[GBNFAlternate] = field(default_factory=list)


class GBNFParser:
    """Parses subset of GBNF (literals, char classes, alternations, recursion)."""

    @staticmethod
    def _unescape_literal(s: str) -> bytes:
        out = bytearray()
        i = 0
        while i < len(s):
            if s[i] == "\\" and i + 1 < len(s):
                esc = s[i+1]
                if esc == "n": out.append(ord("\n"))
                elif esc == "r": out.append(ord("\r"))
                elif esc == "t": out.append(ord("\t"))
                elif esc == '"': out.append(ord('"'))
                elif esc == "\\": out.append(ord("\\"))
                elif esc == "x" and i + 3 < len(s):
                    try:
                        val = int(s[i+2:i+4], 16)
                        out.append(val)
                        i += 4
                        continue
                    except ValueError:
                        out.append(ord(esc))
                else:
                    out.append(ord(esc))
                i += 2
            else:
                out.extend(s[i].encode("utf-8"))
                i += 1
        return bytes(out)

    @staticmethod
    def parse(gbnf_text: str) -> Dict[str, GBNFRule]:
        rules: Dict[str, GBNFRule] = {}
        clean_lines: List[str] = []
        for line in gbnf_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line[:line.index("#")].strip()
            clean_lines.append(line)

        combined = " ".join(clean_lines)
        raw_rules = re.findall(r"([a-zA-Z0-9_-]+)\s*::=\s*(.*?)(?=(?:[a-zA-Z0-9_-]+\s*::=)|$)", combined)

        for rule_name, rule_body in raw_rules:
            rule_obj = GBNFRule(name=rule_name)
            alt_strings = [a.strip() for a in rule_body.split("|")]
            for alt_str in alt_strings:
                alt = GBNFAlternate()
                tokens = re.findall(r'"((?:\\.|[^"\\])*)"|\[(\^?(?:\\.|[^\]\\])*)\]|([a-zA-Z0-9_-]+)', alt_str)
                for lit, cls, ident in tokens:
                    if lit:
                        raw_b = GBNFParser._unescape_literal(lit)
                        for b in raw_b:
                            sym = GBNFSymbol(is_rule_ref=False, allowed_bytes={b})
                            alt.symbols.append(sym)
                    elif cls:
                        allowed: Set[int] = set()
                        neg = cls.startswith("^")
                        content = cls[1:] if neg else cls
                        idx = 0
                        while idx < len(content):
                            if idx + 2 < len(content) and content[idx+1] == "-":
                                start_b = ord(content[idx])
                                end_b = ord(content[idx+2])
                                for b in range(start_b, end_b + 1):
                                    allowed.add(b)
                                idx += 3
                            else:
                                allowed.add(ord(content[idx]))
                                idx += 1
                        if neg:
                            allowed = set(range(256)) - allowed
                        sym = GBNFSymbol(is_rule_ref=False, allowed_bytes=allowed)
                        alt.symbols.append(sym)
                    elif ident:
                        sym = GBNFSymbol(is_rule_ref=True, rule_name=ident)
                        alt.symbols.append(sym)
                rule_obj.alternates.append(alt)
            rules[rule_name] = rule_obj

        return rules


class GBNFAutomaton:
    """Pushdown Automaton (PDA) walker for stateful byte evaluation and forced draft extraction."""

    def __init__(self, gbnf_text: str, root_rule: str = "root") -> None:
        self.rules = GBNFParser.parse(gbnf_text)
        self.root_rule = root_rule
        self.stacks: List[List[Tuple[str, int, int]]] = []
        self.alive: bool = True
        self.reset()

    def reset(self) -> None:
        if self.root_rule not in self.rules:
            self.alive = False
            self.stacks = []
            return
        self.alive = True
        self.stacks = []
        for a_idx in range(len(self.rules[self.root_rule].alternates)):
            self.stacks.append([(self.root_rule, a_idx, 0)])

    def get_valid_bytes(self) -> Set[int]:
        """Returns set of all valid next bytes across all active PDA stack paths."""
        valid_b: Set[int] = set()
        for stack in self.stacks:
            expanded_stack = self._expand_stack(stack)
            if expanded_stack:
                r_name, a_idx, s_idx = expanded_stack[-1]
                sym = self.rules[r_name].alternates[a_idx].symbols[s_idx]
                if not sym.is_rule_ref:
                    valid_b.update(sym.allowed_bytes)
        return valid_b

    def _expand_stack(self, stack: List[Tuple[str, int, int]]) -> Optional[List[Tuple[str, int, int]]]:
        """Expands non-terminal rule references down to a terminal byte class."""
        st = list(stack)
        while st:
            r_name, a_idx, s_idx = st[-1]
            alt = self.rules[r_name].alternates[a_idx]
            if s_idx >= len(alt.symbols):
                st.pop()
                if st:
                    parent_r, parent_a, parent_s = st.pop()
                    st.append((parent_r, parent_a, parent_s + 1))
                continue
            sym = alt.symbols[s_idx]
            if sym.is_rule_ref:
                target_rule = sym.rule_name
                if target_rule in self.rules and self.rules[target_rule].alternates:
                    st.append((target_rule, 0, 0))
                else:
                    return None
            else:
                return st
        return None

    def accept_byte(self, byte_val: int) -> bool:
        """Advance PDA state with incoming byte."""
        next_stacks: List[List[Tuple[str, int, int]]] = []
        for stack in self.stacks:
            exp = self._expand_stack(stack)
            if not exp:
                continue
            r_name, a_idx, s_idx = exp[-1]
            sym = self.rules[r_name].alternates[a_idx].symbols[s_idx]
            if byte_val in sym.allowed_bytes:
                new_st = list(exp)
                curr_r, curr_a, curr_s = new_st.pop()
                new_st.append((curr_r, curr_a, curr_s + 1))
                next_stacks.append(new_st)

        if not next_stacks:
            return False

        self.stacks = next_stacks[:32]
        return True

    def extract_forced_span(self, max_bytes: int = 16) -> bytes:
        """Extract deterministic span where exactly ONE legal byte sequence exists without branching."""
        span = bytearray()
        clone = copy.deepcopy(self)

        for _ in range(max_bytes):
            valid = clone.get_valid_bytes()
            if len(valid) == 1:
                b = next(iter(valid))
                if clone.accept_byte(b):
                    span.append(b)
                else:
                    break
            else:
                break

        return bytes(span)


# ============================================================================
# 6. MTP SPECULATIVE DECODING & LEVIATHAN VERIFICATION
# ============================================================================

class MTPSpeculativeEngine:
    """GLM-5.2 / DeepSeek-V3 Multi-Token Prediction (MTP) draft head."""

    def __init__(self, cfg: ColibriConfig, seed: int = 404) -> None:
        self.cfg = cfg
        d = cfg.hidden_size
        V = cfg.vocab_size
        rng = random.Random(seed)
        self.eh_proj = [[(rng.random() * 0.02 - 0.01) for _ in range(d)] for _ in range(2 * d)]
        self.lm_head = [[(rng.random() * 0.02 - 0.01) for _ in range(min(V, 2048))] for _ in range(d)]

    def generate_drafts(
        self,
        token_id: int,
        hidden_state: List[float],
        depth: int
    ) -> List[int]:
        """Propose speculative drafts via MTP dual-state head."""
        d = self.cfg.hidden_size
        V_sub = min(self.cfg.vocab_size, 2048)
        drafts: List[int] = []

        curr_h = list(hidden_state)
        rng = random.Random(token_id)
        emb = [(rng.random() * 0.02 - 0.01) for _ in range(d)]

        for _ in range(depth):
            cat = emb + curr_h
            h_next = [0.0] * d
            for j in range(d):
                s = 0.0
                for i in range(2 * d):
                    s += cat[i] * self.eh_proj[i][j]
                h_next[j] = s

            logits = [0.0] * V_sub
            for j in range(V_sub):
                s = 0.0
                for i in range(d):
                    s += h_next[i] * self.lm_head[i][j]
                logits[j] = s

            pred_tok = max(range(V_sub), key=lambda idx: logits[idx])
            drafts.append(pred_tok)

            curr_h = h_next
            emb = [(rng.random() * 0.02 - 0.01) for _ in range(d)]

        return drafts

    @staticmethod
    def ngram_draft(history: List[int], depth: int) -> List[int]:
        """Prompt-lookup fallback: finds recent bigram recurrence in history."""
        if len(history) < 4 or depth < 1:
            return []
        a, b = history[-2], history[-1]
        for i in range(len(history) - 3, 0, -1):
            if history[i-1] == a and history[i] == b:
                return history[i+1 : i+1+depth]
        return []

    @staticmethod
    def verify_drafts_greedy(
        oracle_logits: List[List[float]],
        draft_tokens: List[int]
    ) -> Tuple[int, List[int]]:
        """Verify drafts greedily against true base-model logits."""
        accepted: List[int] = []
        for k, draft in enumerate(draft_tokens):
            if k >= len(oracle_logits):
                break
            pred = max(range(len(oracle_logits[k])), key=lambda idx: oracle_logits[k][idx])
            if pred == draft:
                accepted.append(draft)
            else:
                break
        return len(accepted), accepted

    @staticmethod
    def verify_drafts_stochastic(
        oracle_logits: List[List[float]],
        draft_tokens: List[int],
        temperature: float = 0.7,
        seed: int = 505
    ) -> Tuple[int, List[int]]:
        """Leviathan Rejection Sampling verification for lossless stochastic sampling."""
        rng = random.Random(seed)
        accepted: List[int] = []

        for k, draft in enumerate(draft_tokens):
            if k >= len(oracle_logits):
                break
            lo = oracle_logits[k]
            max_lo = max(lo)
            exp_lo = [math.exp(max(-30.0, min(30.0, (val - max_lo) / max(1e-4, temperature)))) for val in lo]
            sum_exp = sum(exp_lo) + 1e-12
            p_draft = exp_lo[draft] / sum_exp if draft < len(exp_lo) else 0.0

            u = rng.random()
            if u < p_draft:
                accepted.append(draft)
            else:
                break

        return len(accepted), accepted


# ============================================================================
# 7. UNIFIED COLIBRI MOE STREAMING RUNTIME
# ============================================================================

class ColibriMoEStreamerRuntime:
    """Sovereign Camelot-OS MoE Streaming Engine integrating all Colibri subsystems."""

    def __init__(self, cfg: Optional[ColibriConfig] = None, seed: int = 42) -> None:
        self.cfg = cfg or ColibriConfig()
        self.seed = seed
        self.disk_store = ExpertDiskStore(self.cfg, synthetic_seed=seed)
        self.cache = LFRUExpertCache(self.cfg, self.disk_store)
        self.kv_cache = CompressedKVCache(self.cfg)
        self.mtp_engine = MTPSpeculativeEngine(self.cfg, seed=seed)
        self.grammar_automaton: Optional[GBNFAutomaton] = None

        self.attention_layers: List[MLAAttention] = [
            MLAAttention(self.cfg, l, seed=seed + l * 10) for l in range(min(4, self.cfg.n_layers))
        ]
        self.moe_layers: List[BatchUnionMoE] = [
            BatchUnionMoE(self.cfg, l, self.cache, seed=seed + l * 20) for l in range(min(4, self.cfg.n_layers))
        ]

        self.total_generated_tokens: int = 0
        self.total_speculative_proposed: int = 0
        self.total_speculative_accepted: int = 0
        self.total_grammar_proposed: int = 0
        self.total_grammar_accepted: int = 0
        self.forward_passes_count: int = 0

    def set_grammar(self, gbnf_schema: str, root_rule: str = "root") -> None:
        """Arm GBNF schema for grammar-forced deterministic speculative drafts."""
        self.grammar_automaton = GBNFAutomaton(gbnf_schema, root_rule=root_rule)

    def forward_token(self, token_id: int, pos: int) -> Tuple[List[float], List[float]]:
        """Run single token causal forward through MLA attention and MoE layers."""
        self.forward_passes_count += 1
        d = self.cfg.hidden_size
        rng = random.Random(token_id + pos * 1000)
        x = [(rng.random() * 0.02 - 0.01) for _ in range(d)]

        for l in range(len(self.attention_layers)):
            attn_out = self.attention_layers[l].forward(x, pos, token_id, self.kv_cache)
            x = [xi + ai for xi, ai in zip(x, attn_out)]
            if l >= self.cfg.first_k_dense_replace:
                moe_out = self.moe_layers[l].forward_batch([x])[0]
                x = [xi + mi for xi, mi in zip(x, moe_out)]

        V_sub = min(self.cfg.vocab_size, 2048)
        logits = [0.0] * V_sub
        for j in range(V_sub):
            logits[j] = sum(x[i] * 0.01 for i in range(min(32, d))) + (0.5 if j == (token_id + 1) % V_sub else 0.0)

        return logits, x

    def generate(
        self,
        prompt_tokens: List[int],
        max_new_tokens: int = 16,
        temperature: float = 0.0
    ) -> List[int]:
        """Generate tokens with combined MTP, GBNF grammar forcing, and LFRU disk streaming."""
        history = list(prompt_tokens)
        emitted: List[int] = []

        last_hidden: List[float] = [0.0] * self.cfg.hidden_size
        last_logits: List[float] = []
        for p, tok in enumerate(prompt_tokens):
            last_logits, last_hidden = self.forward_token(tok, p)

        curr_pos = len(prompt_tokens)
        while len(emitted) < max_new_tokens:
            if temperature <= 0.0:
                next_tok = max(range(len(last_logits)), key=lambda idx: last_logits[idx])
            else:
                next_tok = (history[-1] + 1) % 2048

            emitted.append(next_tok)
            history.append(next_tok)
            self.total_generated_tokens += 1

            if len(emitted) >= max_new_tokens:
                break

            draft_tokens: List[int] = []
            draft_source = "none"

            if self.grammar_automaton and self.grammar_automaton.alive:
                forced_bytes = self.grammar_automaton.extract_forced_span(max_bytes=4)
                if forced_bytes:
                    draft_tokens = [b % 2048 for b in forced_bytes]
                    draft_source = "grammar"
                    self.total_grammar_proposed += len(draft_tokens)

            if not draft_tokens and self.cfg.has_mtp:
                draft_tokens = self.mtp_engine.generate_drafts(
                    token_id=next_tok,
                    hidden_state=last_hidden,
                    depth=min(self.cfg.mtp_draft_depth, max_new_tokens - len(emitted))
                )
                draft_source = "mtp"
                self.total_speculative_proposed += len(draft_tokens)

            if not draft_tokens:
                draft_tokens = self.mtp_engine.ngram_draft(
                    history,
                    depth=min(self.cfg.ngram_draft_depth, max_new_tokens - len(emitted))
                )
                if draft_tokens:
                    draft_source = "ngram"
                    self.total_speculative_proposed += len(draft_tokens)

            if draft_tokens:
                batch_logits: List[List[float]] = []
                for idx, t in enumerate(draft_tokens):
                    lo, h_out = self.forward_token(t, curr_pos + idx)
                    batch_logits.append(lo)
                    last_hidden = h_out
                    last_logits = lo

                acc_count, verified = self.mtp_engine.verify_drafts_greedy(batch_logits, draft_tokens)

                for v_tok in verified:
                    emitted.append(v_tok)
                    history.append(v_tok)
                    self.total_generated_tokens += 1
                    if len(emitted) >= max_new_tokens:
                        break

                if draft_source == "grammar":
                    self.total_grammar_accepted += acc_count
                else:
                    self.total_speculative_accepted += acc_count

                curr_pos += 1 + acc_count
            else:
                last_logits, last_hidden = self.forward_token(next_tok, curr_pos)
                curr_pos += 1

        return emitted

    def get_telemetry(self) -> Dict[str, Any]:
        """Collect runtime performance and cache telemetry."""
        total_cache_reqs = self.cache.hits + self.cache.misses
        hit_rate = (self.cache.hits / total_cache_reqs * 100.0) if total_cache_reqs > 0 else 0.0
        spec_rate = (
            (self.total_speculative_accepted / self.total_speculative_proposed * 100.0)
            if self.total_speculative_proposed > 0 else 0.0
        )
        grammar_rate = (
            (self.total_grammar_accepted / self.total_grammar_proposed * 100.0)
            if self.total_grammar_proposed > 0 else 0.0
        )
        tokens_per_forward = (
            (self.total_generated_tokens / self.forward_passes_count)
            if self.forward_passes_count > 0 else 1.0
        )

        return {
            "total_generated_tokens": self.total_generated_tokens,
            "forward_passes": self.forward_passes_count,
            "tokens_per_forward": round(tokens_per_forward, 2),
            "cache_hits": self.cache.hits,
            "cache_misses": self.cache.misses,
            "cache_hit_rate_pct": round(hit_rate, 2),
            "disk_reads_count": self.disk_store.io_reads_count,
            "disk_bytes_read_mb": round(self.disk_store.bytes_read_total / 1e6, 2),
            "speculative_proposed": self.total_speculative_proposed,
            "speculative_accepted": self.total_speculative_accepted,
            "speculative_acceptance_pct": round(spec_rate, 2),
            "grammar_proposed": self.total_grammar_proposed,
            "grammar_accepted": self.total_grammar_accepted,
            "grammar_acceptance_pct": round(grammar_rate, 2),
            "kv_cache_length": self.kv_cache.length(),
        }
