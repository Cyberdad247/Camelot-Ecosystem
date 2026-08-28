# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
Unit Tests for LMCache Affinity Adapter, KV Cache Management, & TTFT Telemetry
==============================================================================
"""

import importlib.util
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control_plane.infra.lmcache_affinity_adapter import (
    CacheEngineKey,
    LayerCacheEngineKey,
    ChunkMemoryObj,
    LRUCachePolicy,
    LFUCachePolicy,
    FIFOCachePolicy,
    MRUCachePolicy,
    LocalMemoryBackend,
    RedisCacheConnector,
    P2PCacheConnector,
    TTFTTelemetryTracker,
    LMCacheAffinityAdapter,
    chunk_token_sequence,
)
from control_plane.multivoice_bridge import MultivoiceBridge, render_panel

# Dynamically load 01_KERNEL/memory/chunk_kv.py
_spec = importlib.util.spec_from_file_location(
    "chunk_kv",
    REPO_ROOT / "01_KERNEL" / "memory" / "chunk_kv.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["chunk_kv"] = _mod
_spec.loader.exec_module(_mod)
ChunkKVPolicy = _mod.ChunkKVPolicy
LMCacheChunkKVStore = _mod.LMCacheChunkKVStore
ChunkKVEntry = _mod.ChunkKVEntry


# =====================================================================
# 1. Key Hashing & Serialization Tests
# =====================================================================

def test_cache_engine_key_serialization():
    key = CacheEngineKey(
        model_name="qwen-2.5-72b",
        world_size=2,
        worker_id=0,
        chunk_hash=0x123456789ABCDEF0,
        dtype="bfloat16",
        request_configs={"lmcache.tag.session": "ses_001", "lmcache.tag.user": "vizion"},
    )
    s = key.to_string()
    assert "qwen-2.5-72b@2@0@123456789abcdef0@bfloat16" in s
    assert "session%ses_001" in s

    parsed = CacheEngineKey.from_string(s)
    assert parsed.model_name == key.model_name
    assert parsed.world_size == key.world_size
    assert parsed.worker_id == key.worker_id
    assert parsed.chunk_hash == key.chunk_hash
    assert parsed.dtype == key.dtype
    assert parsed.request_configs is not None
    assert parsed.request_configs.get("lmcache.tag.session") == "ses_001"

    d = key.to_dict()
    from_d = CacheEngineKey.from_dict(d)
    assert from_d.chunk_hash == key.chunk_hash
    assert from_d.model_name == key.model_name


def test_layer_cache_engine_key():
    layer_key = LayerCacheEngineKey(
        model_name="llama-3-70b",
        world_size=1,
        worker_id=1,
        chunk_hash=0xABCD,
        dtype="float16",
        layer_id=14,
    )
    s = layer_key.to_string()
    assert s.endswith("@14")
    parsed = LayerCacheEngineKey.from_string(s)
    assert parsed.layer_id == 14
    assert parsed.model_name == "llama-3-70b"


def test_token_chunking_and_hashing():
    tokens = ["Arthur", "is", "King", "of", "Camelot", "Merlin", "is", "wise", "counselor"]
    chunks = chunk_token_sequence(tokens, chunk_size=3)
    assert len(chunks) == 3
    # Chunks are hashed and prefix-chained
    h1, c1 = chunks[0]
    h2, c2 = chunks[1]
    assert h1 != h2
    assert len(c1) == 3
    assert len(c2) == 3


# =====================================================================
# 2. Eviction Policy Tests
# =====================================================================

def test_eviction_policies():
    # Test LRU
    lru = LRUCachePolicy()
    mapping = lru.init_mutable_mapping()
    k1 = CacheEngineKey("m", 1, 0, 1)
    k2 = CacheEngineKey("m", 1, 0, 2)
    k3 = CacheEngineKey("m", 1, 0, 3)

    obj1 = ChunkMemoryObj(b"chunk1")
    obj2 = ChunkMemoryObj(b"chunk2")
    obj3 = ChunkMemoryObj(b"chunk3")

    mapping[k1] = obj1
    lru.update_on_put(k1)
    mapping[k2] = obj2
    lru.update_on_put(k2)
    mapping[k3] = obj3
    lru.update_on_put(k3)

    # Access k1 to make it most recent
    lru.update_on_hit(k1, mapping)

    # Candidate should now be k2 (least recently used)
    cands = lru.get_evict_candidates(mapping, num_candidates=1)
    assert cands == [k2]

    # Pin k2 and verify it is skipped
    obj2.pin()
    assert not obj2.can_evict
    cands_after_pin = lru.get_evict_candidates(mapping, num_candidates=1)
    assert cands_after_pin == [k3]

    # Test LFU
    lfu = LFUCachePolicy()
    lfu_map = lfu.init_mutable_mapping()
    lfu_map[k1] = obj1; lfu.update_on_put(k1)
    lfu_map[k2] = obj2; lfu.update_on_put(k2)
    # Hit k1 twice
    lfu.update_on_hit(k1, lfu_map)
    lfu.update_on_hit(k1, lfu_map)
    # Evict candidate should be k2 (frequency 1 vs k1 frequency 3)
    obj2.unpin()  # unpin
    assert lfu.get_evict_candidates(lfu_map, 1) == [k2]

    # Test FIFO
    fifo = FIFOCachePolicy()
    fifo_map = fifo.init_mutable_mapping()
    fifo_map[k1] = obj1; fifo.update_on_put(k1)
    fifo_map[k2] = obj2; fifo.update_on_put(k2)
    assert fifo.get_evict_candidates(fifo_map, 1) == [k1]

    # Test MRU
    mru = MRUCachePolicy()
    mru_map = mru.init_mutable_mapping()
    mru_map[k1] = obj1; mru.update_on_put(k1)
    mru_map[k2] = obj2; mru.update_on_put(k2)
    mru.update_on_hit(k1, mru_map)  # k1 moved to MRU
    assert mru.get_evict_candidates(mru_map, 1) == [k1]


# =====================================================================
# 3. Local Memory Backend & Eviction Tests
# =====================================================================

def test_local_memory_backend():
    backend = LocalMemoryBackend(max_bytes=2048, max_chunks=2, policy=LRUCachePolicy())
    k1 = CacheEngineKey("m", 1, 0, 101)
    k2 = CacheEngineKey("m", 1, 0, 102)
    k3 = CacheEngineKey("m", 1, 0, 103)

    o1 = ChunkMemoryObj(b"x" * 500)
    o2 = ChunkMemoryObj(b"y" * 500)
    o3 = ChunkMemoryObj(b"z" * 500)

    assert backend.put(k1, o1)
    assert backend.put(k2, o2)
    assert backend.count() == 2

    # Put 3rd chunk triggers eviction of k1 (LRU)
    assert backend.put(k3, o3)
    assert backend.count() == 2
    assert not backend.exists(k1)
    assert backend.exists(k2)
    assert backend.exists(k3)
    assert backend.eviction_count == 1

    # Invalidate and get
    o2.invalidate()
    assert backend.get(k2) is None  # evicted because invalid


# =====================================================================
# 4. Redis and P2P Caching Hooks Tests
# =====================================================================

def test_redis_cache_connector():
    redis_hook = RedisCacheConnector(mock_backend=True)
    k = CacheEngineKey("model-x", 1, 0, 999)
    obj = ChunkMemoryObj(b"redis_serialized_kv_tensor")

    assert redis_hook.put(k, obj)
    assert redis_hook.exists(k)
    fetched = redis_hook.get(k)
    assert fetched is not None
    assert fetched.byte_array == b"redis_serialized_kv_tensor"
    assert redis_hook.hit_count == 1

    assert redis_hook.evict(k)
    assert not redis_hook.exists(k)


def test_p2p_cache_connector():
    b1 = LocalMemoryBackend()
    b2 = LocalMemoryBackend()
    p2p_node1 = P2PCacheConnector(node_id="sir_codex", local_backend=b1)
    p2p_node2 = P2PCacheConnector(node_id="sir_forge", local_backend=b2)

    p2p_node1.register_peer(p2p_node2)
    p2p_node2.register_peer(p2p_node1)

    k = CacheEngineKey("m", 1, 0, 777)
    obj = ChunkMemoryObj(b"p2p_fast_tensor", num_tokens=512)
    b2.put(k, obj)

    # Node 1 does not have k locally
    assert not b1.exists(k)

    # Pull from peer node 2
    transferred = p2p_node1.pull_from_peer(k)
    assert transferred is not None
    assert transferred.byte_array == b"p2p_fast_tensor"
    # Node 1 now has it cached locally
    assert b1.exists(k)
    assert p2p_node1.transfer_count == 1
    assert p2p_node1.transferred_tokens == 512
    assert p2p_node1.get_avg_transfer_speed() > 0.0


# =====================================================================
# 5. TTFT Telemetry Tracker Tests
# =====================================================================

def test_ttft_telemetry_tracker():
    tracker = TTFTTelemetryTracker(slo_ms=100.0)

    # Record cold request (no hit)
    tracker.record_request(
        engine="sir_codex",
        prompt_tokens=1000,
        hit_tokens=0,
        stored_tokens=1000,
        ttft_ms=150.0,  # exceeds SLO
        escaped=False,
    )

    # Record warm request (high hit)
    tracker.record_request(
        engine="sir_codex",
        prompt_tokens=1000,
        hit_tokens=800,
        stored_tokens=200,
        ttft_ms=25.0,  # fast hit
        escaped=False,
    )

    tracker.record_retrieve_op(tokens=800, duration_s=0.01)

    snap = tracker.get_snapshot()
    assert snap.total_requests == 2
    assert snap.cache_hits == 1
    assert snap.cache_hit_pct == 50.0
    assert snap.ttft_savings_pct == 40.0  # (800 hit / 2000 total) * 100
    assert snap.slo_escapes == 1  # 150ms > 100ms
    assert snap.avg_ttft_ms.get("sir_codex") == 87.5  # (150+25)/2


# =====================================================================
# 6. LMCache Affinity Adapter Full Flow Tests
# =====================================================================

def test_lmcache_affinity_adapter_routing():
    adapter = LMCacheAffinityAdapter(chunk_size=10, redis_mock=True)

    adapter.register_worker("sir_codex", worker_id=0, model_name="camelot-v1")
    adapter.register_worker("sir_forge", worker_id=1, model_name="camelot-v1")

    prompt = "Arthur and Merlin build Camelot with Excalibur and Round Table knights in sovereign realm"

    # Initially cold - should pick first available
    worker, score, hit_tokens = adapter.route_request(prompt)
    assert score == 0.0
    assert hit_tokens == 0

    # Store KV cache on sir_codex
    stored = adapter.store_prompt_kv("sir_codex", prompt)
    assert stored > 0

    # Next route of same prompt should route to sir_codex with 1.0 affinity score
    w_hit, s_hit, h_tokens = adapter.route_request(prompt)
    assert w_hit == "sir_codex"
    assert s_hit == 1.0
    assert h_tokens > 0

    # Test engine pin preference
    adapter.pin_worker("sir_forge", pinned=True)
    w_pref, _, _ = adapter.route_request(prompt, preferred_engine="sir_forge")
    assert w_pref == "sir_forge"

    # Export metrics
    metrics = adapter.export_metrics()
    assert metrics["affinity"] is True
    assert "cache_hit_pct" in metrics
    assert "ttft_savings_pct" in metrics


# =====================================================================
# 7. MultivoiceBridge Integration Tests
# =====================================================================

def test_multivoice_bridge_lmcache_integration():
    adapter = LMCacheAffinityAdapter()
    adapter.register_worker("merlin_omega", worker_id=0)

    # Record some requests in adapter
    adapter.telemetry.record_request("merlin_omega", 500, 400, 100, 35.0)

    bridge = MultivoiceBridge()
    bridge.attach_adapter(adapter)

    stats = bridge.fetch_affinity()
    assert stats.connected is True
    assert stats.tokens_hit == 400
    assert stats.ttft_savings_pct == 80.0

    html = render_panel(stats)
    assert "OMNIROUTE AFFINITY" in html
    assert "TTFT Saved: 80%" in html
    assert "400 hit tokens" in html


# =====================================================================
# 8. 01_KERNEL/memory/chunk_kv.py Integration & Backward Compatibility Tests
# =====================================================================

def test_kernel_chunk_kv_integration():
    # 1. Test backward-compatibility for ChunkKVPolicy
    policy = ChunkKVPolicy()
    text = "Arthur is king. Merlin is wise. Fragment"
    assert policy.prune(text) == "Arthur is king. Merlin is wise."

    # 2. Test LMCacheChunkKVStore
    store = LMCacheChunkKVStore(max_chunks=5, policy="lru", linguistic_pruning=True)
    doc = "The knight rode into battle. The realm was saved at dawn. Incomplete sentence"
    hashes = store.chunk_and_store(doc, chunk_size_words=5)
    assert len(hashes) > 0

    # Retrieve chunk
    entry = store.get_chunk(hashes[0])
    assert entry is not None
    assert entry.hit_count == 1

    # Pin chunk
    assert store.pin_chunk(hashes[0])
    assert entry.is_pinned

    # Check stats
    st = store.stats()
    assert st["chunks_cached"] == len(hashes)
    assert st["hits"] == 1
    assert st["hit_pct"] == 100.0
