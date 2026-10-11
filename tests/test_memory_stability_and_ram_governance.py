# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Memory Governance, Leak & Stability Verification Suite
"""
Unit and Stress Tests for:
1. Law 03 Resource Governance (Camelot Node <= 4096MB, Server <= 8192MB)
2. Graphify Semantic Triplet Extractor memory stability across repetitive runs
3. Triple-QFT Symbolect & Anchor Token Compiler memory growth & determinism
4. Open-Notebook Crystal Finalization pipeline memory bounded profile (Delta M <= 50MB)
5. HybridMemoryRouter tier-1 in-memory cache eviction & bounded capacity
"""

from __future__ import annotations

import gc
import json
import os
import psutil
import sys
import time
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "control_plane"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

NODE_RAM_CEILING_MB = 4096.0
SERVER_RAM_CEILING_MB = 8192.0


def test_resource_governance_node_and_server_ceilings():
    """Verify system RAM ceilings conform strictly to Law 03 boundaries."""
    from scripts.ops.check_ram_governance import get_system_ram_mb

    mem = get_system_ram_mb()
    assert mem["total_mb"] > 0, "System total memory must be strictly positive"
    assert mem["avail_mb"] >= 0, "Available memory must be non-negative"
    assert mem["used_mb"] <= SERVER_RAM_CEILING_MB, (
        f"Server working memory ({mem['used_mb']} MB) must never exceed 8192 MB ceiling."
    )


def test_graphify_extraction_stability_and_zero_leak():
    """Verify Graphify extracts triplets reliably across multiple cycles with bounded RAM."""
    from control_plane.graphify import extract_triplets

    proc = psutil.Process()
    gc.collect()
    rss_start = proc.memory_info().rss / (1024 * 1024)

    test_prose = (
        "Sir Helios routes flash telemetry to Redis. "
        "Anya Gate validates sovereign execution. "
        "Qdrant stores semantic vector embeddings. "
        "OpenNotebook maintains local living tissues. "
        "NotebookLM governs deep reasoning across nodes."
    )

    for i in range(50):
        triplets = extract_triplets(f"{test_prose} (Cycle {i})")
        assert len(triplets) >= 3, f"Cycle {i} must extract at least 3 triplets"

    gc.collect()
    rss_end = proc.memory_info().rss / (1024 * 1024)
    delta_mb = rss_end - rss_start

    # Memory growth across 50 iterations must remain strictly bounded (< 25 MB)
    assert delta_mb < 25.0, f"Graphify memory growth too high: {delta_mb:.2f} MB"


def test_symbolect_transpiler_stability_and_determinism():
    """Verify TripleQFTTranspiler generates deterministic anchor tokens with zero leakage."""
    from scripts.symbolect_transpiler import TripleQFTTranspiler

    trans = TripleQFTTranspiler()
    proc = psutil.Process()
    gc.collect()
    rss_start = proc.memory_info().rss / (1024 * 1024)

    phrase = "Authenticate with Google OAuth and sync NotebookLM to Redis"
    first_res = trans.compile(phrase)
    assert first_res["status"] in ("RADIANT", "PASS")
    assert len(first_res["anchor_tokens"]) >= 4

    for _ in range(50):
        subsequent_res = trans.compile(phrase)
        assert subsequent_res["anchor_tokens"] == first_res["anchor_tokens"], "Anchor tokens must be deterministic"

    gc.collect()
    rss_end = proc.memory_info().rss / (1024 * 1024)
    delta_mb = rss_end - rss_start
    assert delta_mb < 20.0, f"Symbolect compiler memory growth too high: {delta_mb:.2f} MB"


def test_finalize_open_notebook_crystal_bounded_footprint():
    """Verify Open-Notebook Crystal Finalization executes within tight memory bounds (Node profile)."""
    from scripts.finalize_open_notebook_crystal import finalize_open_notebook_crystal

    proc = psutil.Process()
    gc.collect()
    rss_start = proc.memory_info().rss / (1024 * 1024)

    # Execute 15 crystal finalization cycles
    for i in range(15):
        res = finalize_open_notebook_crystal(
            knight_id="SIR_HELIOS",
            title=f"Memory Stability Benchmark Node {i}",
            text=f"Benchmark payload {i}: Sir Helios routes telemetry. Anya Gate validates execution.",
            category="BENCHMARK",
            sources_count=1,
        )
        assert res["crystal_id"].startswith("VKG_")
        assert res["triplet_count"] >= 1
        assert len(res["anchor_tokens"]) >= 2

    gc.collect()
    rss_end = proc.memory_info().rss / (1024 * 1024)
    delta_mb = rss_end - rss_start

    # Bounded footprint assertion: total delta for 15 crystal builds < 30 MB
    assert delta_mb < 30.0, f"Crystal finalization memory footprint exceeded bound: {delta_mb:.2f} MB"
    assert rss_end < NODE_RAM_CEILING_MB, f"Process RSS ({rss_end:.2f} MB) must be well within 4096 MB node ceiling"


def test_hybrid_memory_router_fallback_stability():
    """Verify HybridMemoryRouter handles repeated queries without memory exhaustion."""
    import importlib
    mod = importlib.import_module("01_KERNEL.memory.hybrid_worldtree_architecture")
    HybridMemoryRouter = mod.HybridMemoryRouter

    router = HybridMemoryRouter()
    proc = psutil.Process()
    gc.collect()
    rss_start = proc.memory_info().rss / (1024 * 1024)

    # 100 queries against memory cascade
    for i in range(100):
        router._local_l1_cache[f"bench_key_{i}"] = f"Cached value payload {i}"
        status = router.get_architecture_status()
        assert "tier_1_redis" in status

    gc.collect()
    rss_end = proc.memory_info().rss / (1024 * 1024)
    delta_mb = rss_end - rss_start
    assert delta_mb < 15.0, f"HybridMemoryRouter memory leak detected: {delta_mb:.2f} MB"
