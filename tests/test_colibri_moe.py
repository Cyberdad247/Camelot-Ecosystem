# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT
"""Unit tests for Colibri MoE Disk Streaming Runtime and Control Plane Bridge."""

import importlib
import os
import tempfile
import unittest

_streamer = importlib.import_module("01_KERNEL.reasoning.colibri_moe_streamer")
BatchUnionMoE = _streamer.BatchUnionMoE
ColibriConfig = _streamer.ColibriConfig
ColibriMoEStreamerRuntime = _streamer.ColibriMoEStreamerRuntime
ColibriResourcePlanner = _streamer.ColibriResourcePlanner
CompressedKVCache = _streamer.CompressedKVCache
CompressedKVCacheRow = _streamer.CompressedKVCacheRow
ExpertDiskStore = _streamer.ExpertDiskStore
ExpertWeights = _streamer.ExpertWeights
GBNFAlternate = _streamer.GBNFAlternate
GBNFAutomaton = _streamer.GBNFAutomaton
GBNFParser = _streamer.GBNFParser
GBNFRule = _streamer.GBNFRule
GBNFSymbol = _streamer.GBNFSymbol
LFRUExpertCache = _streamer.LFRUExpertCache
MLAAttention = _streamer.MLAAttention
MTPSpeculativeEngine = _streamer.MTPSpeculativeEngine
QuantizedTensor = _streamer.QuantizedTensor
ResourcePlanReport = _streamer.ResourcePlanReport
SigmoidMoERouter = _streamer.SigmoidMoERouter

from control_plane.infra.colibri_bridge import (
    ColibriBridgeService,
    ColibriInferenceRequest,
    ColibriInferenceResponse,
)


class TestColibriMoEStreamer(unittest.TestCase):
    """Test suite verifying all Colibri MoE subsystems in pure Python stdlib."""

    def setUp(self) -> None:
        self.tiny_cfg = ColibriConfig(
            model_name="GLM-5.2-744B-TestMini",
            hidden_size=64,
            n_layers=4,
            n_heads=4,
            n_experts=16,
            top_k=4,
            moe_intermediate_size=32,
            dense_intermediate_size=64,
            first_k_dense_replace=1,
            n_shared_experts=1,
            vocab_size=256,
            q_lora_rank=32,
            kv_lora_rank=16,
            qk_nope_head_dim=16,
            qk_rope_head_dim=8,
            v_head_dim=16,
            dense_bits=4,
            expert_bits=4,
            max_ram_budget_bytes=25 * 1024 * 1024 * 1024,
            hot_expert_slots_per_layer=2,
        )

    def test_colibri_config_and_resource_planner_744b(self) -> None:
        """Verify 744B memory planning and RAM budget calculations."""
        full_cfg = ColibriConfig()
        report = ColibriResourcePlanner.plan_model(full_cfg)

        self.assertGreater(report.total_params_b, 600.0)
        self.assertLess(report.total_params_b, 900.0)
        self.assertGreater(report.moe_params_b, 500.0)
        self.assertTrue(report.fits_ram_budget)
        self.assertLess(report.projected_resident_ram_gb, 25.0)
        self.assertGreater(report.max_context_tokens_in_ram, 1024)
        self.assertGreater(report.storage_footprint_gb, 100.0)

    def test_quantized_tensors_int8_int4_f32(self) -> None:
        """Verify quantization formats F32, INT8, and INT4 packing/dequantization."""
        sample_mat = [
            [0.5, -0.25, 0.75, -1.0],
            [1.5, -0.5, 0.0, 0.25],
        ]

        # F32
        q_f32 = QuantizedTensor.from_floats(sample_mat, fmt=0)
        row0_f32 = q_f32.dequantize_row(0)
        self.assertEqual(len(row0_f32), 4)
        self.assertAlmostEqual(row0_f32[0], 0.5, places=5)

        # INT8
        q_i8 = QuantizedTensor.from_floats(sample_mat, fmt=1)
        row0_i8 = q_i8.dequantize_row(0)
        self.assertEqual(len(row0_i8), 4)
        self.assertAlmostEqual(row0_i8[0], 0.5, delta=0.05)

        # INT4
        q_i4 = QuantizedTensor.from_floats(sample_mat, fmt=2)
        row0_i4 = q_i4.dequantize_row(0)
        self.assertEqual(len(row0_i4), 4)
        self.assertAlmostEqual(row0_i4[0], 0.5, delta=0.2)

        # Matmul Vec
        x = [1.0, 2.0, 3.0, 4.0]
        y_i8 = q_i8.matmul_vec(x)
        self.assertEqual(len(y_i8), 2)

    def test_lfru_cache_and_hysteresis(self) -> None:
        """Verify LFRU tiered cache, heat decay, and 25%+4 hysteresis margin."""
        disk = ExpertDiskStore(self.tiny_cfg, synthetic_seed=77)
        cache = LFRUExpertCache(self.tiny_cfg, disk)

        # Access expert 0 and 1 on layer 1
        e0 = cache.get_expert(1, 0)
        e1 = cache.get_expert(1, 1)
        self.assertEqual(cache.hits, 0)
        self.assertEqual(cache.misses, 2)
        self.assertIn(0, cache.pinned[1])
        self.assertIn(1, cache.pinned[1])

        # Second access should hit pinned cache
        _ = cache.get_expert(1, 0)
        self.assertEqual(cache.hits, 1)

        # Access unpinned expert 2 multiple times to build heat
        for _ in range(10):
            cache.touch(1, 2)

        # Check LFRU swap detection
        swap = cache.pick_lfru_swap(1)
        self.assertIsNotNone(swap)
        cold_eid, hot_eid, gain = swap
        self.assertEqual(hot_eid, 2)
        self.assertGreater(gain, 0)

        # Test live repin pass
        repin_result = cache.repin_pass(1)
        self.assertIsNotNone(repin_result)
        self.assertIn(2, cache.pinned[1])
        self.assertNotIn(cold_eid, cache.pinned[1])

        # Test heat decay (halving)
        heat_before = cache.eheat[1].get(2, 0)
        cache.decay_heat(1)
        heat_after = cache.eheat[1].get(2, 0)
        self.assertLessEqual(heat_after, heat_before)

    def test_sigmoid_moe_router(self) -> None:
        """Verify Sigmoid Router top-k selection and routed scaling factor."""
        router = SigmoidMoERouter(self.tiny_cfg, seed=12)
        x = [0.1] * self.tiny_cfg.hidden_size
        indices, weights = router.route(x)

        self.assertEqual(len(indices), self.tiny_cfg.top_k)
        self.assertEqual(len(weights), self.tiny_cfg.top_k)
        self.assertTrue(all(0 <= idx < self.tiny_cfg.n_experts for idx in indices))
        self.assertTrue(all(w > 0 for w in weights))

    def test_batch_union_moe(self) -> None:
        """Verify BatchUnionMoE forward pass across multiple batch positions."""
        disk = ExpertDiskStore(self.tiny_cfg, synthetic_seed=88)
        cache = LFRUExpertCache(self.tiny_cfg, disk)
        moe = BatchUnionMoE(self.tiny_cfg, layer_idx=1, cache=cache, seed=99)

        batch_x = [
            [0.05 * (i + 1) for i in range(self.tiny_cfg.hidden_size)],
            [-0.03 * (i + 1) for i in range(self.tiny_cfg.hidden_size)],
        ]
        out = moe.forward_batch(batch_x)
        self.assertEqual(len(out), 2)
        self.assertEqual(len(out[0]), self.tiny_cfg.hidden_size)
        self.assertEqual(len(out[1]), self.tiny_cfg.hidden_size)

    def test_mla_attention_compressed_kv(self) -> None:
        """Verify MLA attention forward pass and low-rank KV cache update."""
        attn = MLAAttention(self.tiny_cfg, layer_idx=0, seed=45)
        kv_cache = CompressedKVCache(self.tiny_cfg)

        x0 = [0.02] * self.tiny_cfg.hidden_size
        out0 = attn.forward(x0, pos=0, token_id=10, kv_cache=kv_cache)
        self.assertEqual(len(out0), self.tiny_cfg.hidden_size)
        self.assertEqual(len(kv_cache.layers_cache[0]), 1)

        x1 = [0.03] * self.tiny_cfg.hidden_size
        out1 = attn.forward(x1, pos=1, token_id=11, kv_cache=kv_cache)
        self.assertEqual(len(out1), self.tiny_cfg.hidden_size)
        self.assertEqual(len(kv_cache.layers_cache[0]), 2)

    def test_kv_cache_disk_persistence_colikv1(self) -> None:
        """Verify COLIKV1 binary serialization and reconstruction from disk."""
        kv_cache = CompressedKVCache(self.tiny_cfg)
        for p in range(5):
            for l in range(self.tiny_cfg.n_layers):
                c_kv = [float(p + l * 0.1)] * self.tiny_cfg.kv_lora_rank
                k_rot = [float(p * 0.05)] * self.tiny_cfg.qk_rope_head_dim
                kv_cache.append_token(l, token_id=100 + p, latent_c_kv=c_kv, k_rot=k_rot)

        with tempfile.NamedTemporaryFile(suffix=".coli_kv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            bytes_written = kv_cache.serialize_to_disk(tmp_path)
            self.assertGreater(bytes_written, 40)

            loaded_cache = CompressedKVCache.load_from_disk(self.tiny_cfg, tmp_path)
            self.assertEqual(loaded_cache.length(), 5)
            self.assertEqual(len(loaded_cache.layers_cache), self.tiny_cfg.n_layers)
            self.assertEqual(loaded_cache.layers_cache[0][0].token_id, 100)
            self.assertAlmostEqual(loaded_cache.layers_cache[0][0].latent_c_kv[0], 0.0)
            self.assertAlmostEqual(loaded_cache.layers_cache[1][2].latent_c_kv[0], 2.1, places=4)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_gbnf_grammar_and_forced_drafts(self) -> None:
        """Verify GBNF parser, Pushdown Automaton walker, and deterministic draft forcing."""
        schema = r'''
        root ::= "{" pair "}"
        pair ::= "\"status\":" "\"ok\""
        '''
        automaton = GBNFAutomaton(schema, root_rule="root")
        self.assertTrue(automaton.alive)

        # Forced span should begin with '{' and '\"status\":'
        forced = automaton.extract_forced_span(max_bytes=10)
        self.assertEqual(forced, b'{"status":')

        # Feed the forced bytes into the automaton
        for b in forced:
            ok = automaton.accept_byte(b)
            self.assertTrue(ok)

        # Next forced span should be '"ok"'
        next_forced = automaton.extract_forced_span(max_bytes=5)
        self.assertEqual(next_forced, b'"ok"')

    def test_mtp_speculation_and_leviathan_verification(self) -> None:
        """Verify MTP multi-token draft rollout and Leviathan rejection sampling."""
        mtp = MTPSpeculativeEngine(self.tiny_cfg, seed=55)
        hidden = [0.05] * self.tiny_cfg.hidden_size
        drafts = mtp.generate_drafts(token_id=42, hidden_state=hidden, depth=3)

        self.assertEqual(len(drafts), 3)

        # N-Gram prompt lookup test
        history = [10, 20, 30, 40, 10, 20]
        ngram_draft = mtp.ngram_draft(history, depth=2)
        self.assertEqual(ngram_draft, [30, 40])

        # Verification tests
        oracle_logits = [
            [1.0 if i == drafts[0] else 0.0 for i in range(256)],
            [1.0 if i == drafts[1] else 0.0 for i in range(256)],
            [1.0 if i == 999 else 0.0 for i in range(256)],  # mismatch on 3rd
        ]
        acc_count, verified = mtp.verify_drafts_greedy(oracle_logits, drafts)
        self.assertEqual(acc_count, 2)
        self.assertEqual(verified, drafts[:2])

        # Stochastic verification
        stoch_acc, stoch_v = mtp.verify_drafts_stochastic(oracle_logits, drafts, temperature=0.7)
        self.assertGreaterEqual(stoch_acc, 0)

    def test_colibri_moe_streamer_runtime_generation(self) -> None:
        """Verify end-to-end ColibriMoEStreamerRuntime generation loop."""
        runtime = ColibriMoEStreamerRuntime(self.tiny_cfg, seed=66)
        schema = r'''
        root ::= "{\"response\":\"" [a-z]+ "\"}"
        '''
        runtime.set_grammar(schema)

        prompt = [1, 2, 3]
        emitted = runtime.generate(prompt_tokens=prompt, max_new_tokens=8, temperature=0.0)

        self.assertEqual(len(emitted), 8)
        telemetry = runtime.get_telemetry()
        self.assertGreaterEqual(telemetry["total_generated_tokens"], 8)
        self.assertGreater(telemetry["forward_passes"], 0)
        self.assertIn("cache_hit_rate_pct", telemetry)
        self.assertIn("disk_reads_count", telemetry)

    def test_colibri_control_plane_bridge(self) -> None:
        """Verify ColibriBridgeService integration with Camelot-OS control plane."""
        bridge = ColibriBridgeService(config_overrides={
            "hidden_size": 64,
            "n_layers": 4,
            "n_heads": 4,
            "n_experts": 16,
            "top_k": 4,
            "moe_intermediate_size": 32,
            "dense_intermediate_size": 64,
            "first_k_dense_replace": 1,
            "vocab_size": 256,
            "q_lora_rank": 32,
            "kv_lora_rank": 16,
            "qk_nope_head_dim": 16,
            "qk_rope_head_dim": 8,
            "v_head_dim": 16,
            "hot_expert_slots_per_layer": 2,
        })

        plan = bridge.get_hardware_plan()
        self.assertTrue(plan["fits_ram_budget"])
        self.assertIn("total_params_b", plan)

        req = ColibriInferenceRequest(
            prompt_tokens=[5, 6, 7],
            max_tokens=6,
            temperature=0.0,
            gbnf_grammar='root ::= "{\"id\":1}"',
        )
        resp = bridge.execute_reasoning(req)
        self.assertIsInstance(resp, ColibriInferenceResponse)
        self.assertEqual(resp.tokens_count, 6)
        self.assertIn("cache_hit_rate_pct", resp.telemetry)


if __name__ == "__main__":
    unittest.main()
