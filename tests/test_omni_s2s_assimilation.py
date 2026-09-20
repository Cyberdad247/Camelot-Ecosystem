# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit Test Suite for Omni Speech-to-Speech (S2S) Assimilation Protocol
=====================================================================
Verifies:
1. νKG crystal integrity for OMEGA_OMNI_S2S_NEXUS (4-repo assimilation).
2. RadixAudioCache prefix matching, edge splitting, and LRU eviction.
3. AgoraRTCBridge SD-RTN connection lifecycle, PLC concealment, and SHM piping.
4. OmniS2SEngine multi-turn KV cache hit rate acceleration and sub-100ms TTFA.
5. Runic router dispatch for //OMNI_S2S and its aliases (//sglang_omni, //agora_rtc, //s2s_stream).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import struct
import sys
import pytest

from control_plane.runes.runic_router import route_rune

CAMELOT_HOME = Path(__file__).resolve().parent.parent

# Import omni_s2s modules
s2s_dir = CAMELOT_HOME / "02_FORGE" / "assimilation" / "omni_s2s"
if str(s2s_dir) not in sys.path:
    sys.path.insert(0, str(s2s_dir))

import radix_audio_cache
import agora_rtc_bridge
import omni_s2s_engine

RadixAudioCache = radix_audio_cache.RadixAudioCache
RadixNode = radix_audio_cache.RadixNode
AgoraRTCBridge = agora_rtc_bridge.AgoraRTCBridge
AgoraRTCConfig = agora_rtc_bridge.AgoraRTCConfig
OmniS2SEngine = omni_s2s_engine.OmniS2SEngine


# ── 1. νKG Crystal Integrity Test ─────────────────────────────────────────────

def test_vkg_crystal_presence_and_structure():
    """Verify vkg_omni_s2s_nexus.json exists, lists 4 repos, and defines latency budget."""
    crystal_path = (
        CAMELOT_HOME
        / "03_VAULT"
        / "runtime_state"
        / "open_notebook"
        / "vkg_crystals"
        / "vkg_omni_s2s_nexus.json"
    )
    assert crystal_path.exists(), "vkg_omni_s2s_nexus.json must exist"

    data = json.loads(crystal_path.read_text(encoding="utf-8"))
    assert data["system_identity"] == "OMEGA_OMNI_S2S_NEXUS"
    assert len(data["assimilated_repositories"]) == 4

    repo_urls = [r["repo"] for r in data["assimilated_repositories"]]
    assert "https://github.com/sgl-project/mini-sglang.git" in repo_urls
    assert "https://github.com/sgl-project/sglang-omni" in repo_urls
    assert "https://github.com/Yudhyy/AgoraAI_ChatBotApp" in repo_urls
    assert "https://github.com/tanveer-Ai-verse/AgoraAi.git" in repo_urls

    assert data["latency_budget_ms"]["total_target_ttfa_ms"] <= 160


# ── 2. RadixAudioCache Prefix Matching & Edge Splitting Tests ─────────────────

def test_radix_audio_cache_prefix_matching():
    """Verify Radix tree accurately matches shared prefixes across conversation turns."""
    cache = RadixAudioCache(max_cached_tokens=1024)

    # Insert base prompt prefix
    base_prefix = [1, 2, 3, 4, 5, 6, 7, 8]
    cache.insert_sequence(base_prefix, kv_data={"ptr": "0xBASE"})

    # Query with exact prefix + delta tokens
    turn_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    matched_node, matched_count = cache.match_prefix(turn_1)

    assert matched_count == 8
    assert matched_node is not None
    assert matched_node.kv_cache_ref == {"ptr": "0xBASE"}


def test_radix_audio_cache_edge_splitting():
    """Verify inserting divergent branches splits edges cleanly."""
    cache = RadixAudioCache(max_cached_tokens=1024)

    # Branch A: [10, 20, 30, 40]
    cache.insert_sequence([10, 20, 30, 40], kv_data={"branch": "A"})

    # Branch B: [10, 20, 35, 45] -> should split at [10, 20]
    cache.insert_sequence([10, 20, 35, 45], kv_data={"branch": "B"})

    # Query common prefix
    node, matched = cache.match_prefix([10, 20, 99])
    assert matched == 2  # [10, 20] matched

    # Query Branch A
    node_a, matched_a = cache.match_prefix([10, 20, 30, 40])
    assert matched_a == 4
    assert node_a.kv_cache_ref == {"branch": "A"}

    # Query Branch B
    node_b, matched_b = cache.match_prefix([10, 20, 35, 45])
    assert matched_b == 4
    assert node_b.kv_cache_ref == {"branch": "B"}


def test_radix_audio_cache_lru_eviction():
    """Verify exceeding max_cached_tokens triggers LRU leaf eviction."""
    cache = RadixAudioCache(max_cached_tokens=30)

    # Insert sequence of 20 tokens
    cache.insert_sequence(list(range(20)))
    assert cache.total_tokens_cached == 20

    # Insert another sequence of 20 tokens (total 40 > 30) -> triggers eviction
    cache.insert_sequence(list(range(100, 120)))
    assert cache.total_tokens_cached <= 30


# ── 3. AgoraRTCBridge Tests ───────────────────────────────────────────────────

def test_agora_rtc_bridge_lifecycle_and_plc():
    """Verify Agora RTC bridge joins channel, pipes frames to SHM, and applies PLC."""
    bridge = AgoraRTCBridge(AgoraRTCConfig(channel_name="camelot_test_rtc"))
    
    # 1. Join channel
    join_res = bridge.join_channel()
    assert join_res["status"] == "AGORA_CHANNEL_JOINED"
    assert join_res["transport"] == "AGORA_SD_RTN_GLOBAL_MESH"

    # 2. Ingest normal frame
    pcm_frame = b"\x10\x00" * 160  # 160 samples (20ms)
    ingest_res = bridge.push_audio_frame(pcm_frame)
    assert ingest_res["frame_index"] == 1
    assert ingest_res["bytes_ingested"] == 320
    assert ingest_res["plc_applied"] is False

    # 3. Simulate lost/corrupted frame (0 bytes) -> Packet Loss Concealment (PLC)
    plc_res = bridge.push_audio_frame(b"")
    assert plc_res["frame_index"] == 2
    assert plc_res["plc_applied"] is True
    assert plc_res["bytes_ingested"] == 320  # Concealed synthesized frame

    # 4. Pull egress frame back to Agora
    egress_res = bridge.pull_egress_frame(pcm_frame)
    assert egress_res["status"] == "STREAMED_TO_AGORA_SD_RTN"
    assert egress_res["latency_ms"] < 20.0

    # 5. Stats
    stats = bridge.get_stats()
    assert stats["connected"] is True
    assert stats["ingress_frames"] == 2
    assert stats["egress_frames"] == 1


# ── 4. OmniS2SEngine Multi-Turn Acceleration Tests ────────────────────────────

def test_omni_s2s_engine_multi_turn_acceleration():
    """Verify multi-turn speech turns progressively benefit from RadixAttention KV reuse."""
    engine = OmniS2SEngine(channel_name="test_omni_s2s")

    samples = [int(1200 * math.sin(2 * math.pi * 220 * i / 16000)) for i in range(4000)]
    pcm = struct.pack(f"<{len(samples)}h", *samples)

    # Turn 1
    t1 = engine.process_speech_turn(pcm, "Initialize diagnostic sweep", "sir_codex")
    assert t1.turn_index == 1
    assert t1.radix_cache_hit_rate > 70.0
    assert t1.estimated_ttfa_ms < 100.0

    # Turn 2
    t2 = engine.process_speech_turn(pcm, "Examine memory slab", "sir_codex")
    assert t2.turn_index == 2
    assert t2.radix_cache_hit_rate >= t1.radix_cache_hit_rate
    assert t2.estimated_ttfa_ms <= t1.estimated_ttfa_ms

    # Turn 3
    t3 = engine.process_speech_turn(pcm, "All clear, proceed", "sir_codex")
    assert t3.turn_index == 3
    assert t3.radix_cache_hit_rate >= t2.radix_cache_hit_rate
    assert t3.estimated_ttfa_ms < 85.0


# ── 5. Runic Router Dispatch Tests ────────────────────────────────────────────

def test_runic_dispatch_omni_s2s():
    """Verify //OMNI_S2S dispatches correctly to OmniS2SEngine."""
    res = route_rune("//OMNI_S2S Stream test over Agora RTC", {})
    assert res.rune == "//OMNI_S2S"
    assert res.metadata["status"] == "OMNI_S2S_STREAM_ACTIVE"
    assert res.metadata["turn_result"]["status"] == "S2S_TURN_COMPLETED"
    assert res.metadata["turn_result"]["estimated_ttfa_ms"] < 100.0


def test_runic_dispatch_omni_s2s_aliases():
    """Verify //sglang_omni, //agora_rtc, and //s2s_stream aliases work."""
    # 1. //sglang_omni
    res1 = route_rune("//sglang_omni Test Radix caching", {})
    assert res1.rune == "//sglang_omni"
    assert res1.metadata["status"] == "OMNI_S2S_STREAM_ACTIVE"

    # 2. //agora_rtc
    res2 = route_rune("//agora_rtc Check SD-RTN carrier channel", {})
    assert res2.rune == "//agora_rtc"
    assert res2.metadata["status"] == "OMNI_S2S_STREAM_ACTIVE"

    # 3. //s2s_stream
    res3 = route_rune("//s2s_stream Full duplex stream check", {})
    assert res3.rune == "//s2s_stream"
    assert res3.metadata["status"] == "OMNI_S2S_STREAM_ACTIVE"
