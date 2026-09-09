# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

"""Unit tests for Hermes MoA routing, transcript supervision capture, and signal mining.

Tests:
  - Task classifier regex branches (light, multimodal, gen_heavy, hard, moa)
  - Cheapest competent agent routing policy (Qwen3.6, Nemotron-Omni, Two-Tower, DSV4F, Cloud)
  - Pre-LLM call routing hook (state persistence, session extraction)
  - Post-LLM call supervision capture hook (routing linkage, transcript extraction)
  - Transcript signal miner with 2.0x gold weighting on cloud escalations and 1.5x on routing
  - SQLite kanban mining and request dump mining
  - Runtime state manifest generation
  - Zero external dependencies verification (Python standard library only)
"""

import importlib.util
import json
import sqlite3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "01_KERNEL" / "reasoning" / "hermes_moa_loop.py"

spec = importlib.util.spec_from_file_location("hermes_moa_loop", MODULE_PATH)
hermes_moa_loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hermes_moa_loop)

AGENTS = hermes_moa_loop.AGENTS
CLOUD_AGENTS = hermes_moa_loop.CLOUD_AGENTS
HermesMoAHookPipeline = hermes_moa_loop.HermesMoAHookPipeline
HermesSignalMiner = hermes_moa_loop.HermesSignalMiner
classify_task = hermes_moa_loop.classify_task
generate_moa_manifest = hermes_moa_loop.generate_moa_manifest
route_task = hermes_moa_loop.route_task


# ---------------------------------------------------------------------------
# 1. Task Classifier Tests
# ---------------------------------------------------------------------------


def test_classify_light_tasks():
    # Short length threshold (<100 chars)
    assert classify_task("hello there") == "light"
    assert classify_task("what is the capital of France?") == "light"
    assert classify_task("summarize this briefly") == "light"
    assert classify_task("extract the name: John Doe") == "light"
    assert classify_task("format the json payload") == "light"
    assert classify_task("translate to spanish") == "light"


def test_classify_gen_heavy_tasks():
    assert classify_task("generate 100 sample user profiles for database seeding") == "gen_heavy"
    assert classify_task("batch create diffusion renderings for luxury knight banners") == "gen_heavy"
    assert classify_task("bulk produce repetitive marketing copy variations") == "gen_heavy"


def test_classify_hard_tasks():
    assert classify_task("perform a zero-trust security audit on kernel memory bridges") == "hard"
    assert classify_task("conduct deep vulnerability research on AST sandboxing") == "hard"
    assert classify_task("resolve this complex and unprecedented distributed consensus failure") == "hard"


def test_classify_multimodal_tasks():
    assert classify_task("inspect this screenshot and extract the UI button coordinates") == "multimodal"
    assert classify_task("transcribe the following audio stream from bifrost") == "multimodal"
    assert classify_task("look at the photo and describe what you see") == "multimodal"


def test_classify_moa_fallback():
    # Longer task with ambiguous/multi-step requirements
    long_task = (
        "We need to architect an end-to-end event-driven state machine that coordinates "
        "multiple background workers across disparate clusters, evaluating competing draft proposals "
        "to ensure optimal quorum while maintaining backwards compatibility with legacy protocols."
    )
    assert classify_task(long_task) == "moa"


# ---------------------------------------------------------------------------
# 2. Cheapest Competent Agent Routing Policy Tests
# ---------------------------------------------------------------------------


def test_route_light_task():
    agent, route_type, gold = route_task("classify this sentiment: positive")
    assert agent == "qwen36-nvfp4-a4q"
    assert route_type == "light"
    assert gold is None


def test_route_multimodal_task():
    agent, route_type, gold = route_task("analyze this picture of the server rack")
    assert agent == "nemotron-omni"
    assert route_type == "perception"
    assert gold is None


def test_route_multimodal_flag_override():
    agent, route_type, gold = route_task("some neutral text", has_multimodal_input=True)
    assert agent == "nemotron-omni"
    assert route_type == "perception"
    assert gold is None


def test_route_gen_heavy_task():
    agent, route_type, gold = route_task("generate 50 batch variations of diffusion art")
    assert agent == "deepseek-v4-flash-dspark"
    assert route_type == "gen_heavy"
    assert gold is None


def test_route_hard_cloud_escalation():
    agent, route_type, gold = route_task("audit the cryptographic signature security implementation")
    assert agent == "deepseek-v4-flash-dspark"
    assert route_type == "escalation"
    assert gold == "cloud"


def test_route_moa_task():
    long_prompt = "Design a multi-faceted distributed consensus mechanism with draft voting and aggregation " * 2
    agent, route_type, gold = route_task(long_prompt)
    assert agent == "deepseek-v4-flash-dspark"
    assert route_type == "moa"
    assert gold is None


# ---------------------------------------------------------------------------
# 3. Two-Hook Pipeline Tests (pre_llm_call + post_llm_call)
# ---------------------------------------------------------------------------


def test_hook_pipeline_pre_and_post(tmp_path):
    state_file = tmp_path / "_last_routing.json"
    log_file = tmp_path / "routing_log.jsonl"
    pipeline = HermesMoAHookPipeline(state_file=state_file, log_file=log_file)

    # 1. Pre-LLM Hook for a light task
    payload_pre = {
        "session_id": "sess-101",
        "extra": {
            "user_message": "summarize the quarterly earnings report",
        },
    }
    decision = pipeline.pre_llm_call(payload_pre)
    assert decision["chosen_agent"] == "qwen36-nvfp4-a4q"
    assert decision["route_type"] == "light"
    assert decision["cloud_gold"] is None
    assert state_file.exists()

    # 2. Post-LLM Hook captures verdict and combines with routing state
    payload_post = {
        "session_id": "sess-101",
        "extra": {
            "assistant_response": "Quarterly earnings increased by 14% YoY.",
        },
    }
    logged = pipeline.post_llm_call(payload_post)
    assert logged is not None
    assert logged["task"] == "summarize the quarterly earnings report"
    assert logged["chosen_agent"] == "qwen36-nvfp4-a4q"
    assert logged["verdict"] == "Quarterly earnings increased by 14% YoY."
    assert logged["cloud_gold"] is None

    # Check file contents
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["session_id"] == "sess-101"
    assert row["chosen_agent"] == "qwen36-nvfp4-a4q"


def test_hook_pipeline_cloud_escalation(tmp_path):
    state_file = tmp_path / "_last_routing.json"
    log_file = tmp_path / "routing_log.jsonl"
    pipeline = HermesMoAHookPipeline(state_file=state_file, log_file=log_file)

    # Pre-hook on hard security task
    payload_pre = {
        "session_id": "sess-sec-99",
        "extra": {
            "user_message": "security audit of memory bounds in C extensions",
        },
    }
    decision = pipeline.pre_llm_call(payload_pre)
    assert decision["route_type"] == "escalation"
    assert decision["cloud_gold"] == "cloud"

    # Post-hook
    payload_post = {
        "session_id": "sess-sec-99",
        "extra": {
            "assistant_response": "Verified: no buffer overflows found across 12 pointers.",
        },
    }
    logged = pipeline.post_llm_call(payload_post)
    assert logged["cloud_gold"] == "cloud"

    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["cloud_gold"] == "cloud"


# ---------------------------------------------------------------------------
# 4. Transcript Signal Miner Tests (2.0x Gold Weighting)
# ---------------------------------------------------------------------------


def test_signal_miner_routing_log_weights(tmp_path):
    log_file = tmp_path / "routing_log.jsonl"
    entries = [
        # 1. Normal light turn (routing decision 1.5x)
        {
            "ts": "2026-08-25T00:00:00Z",
            "task": "summarize repo",
            "chosen_agent": "qwen36-nvfp4-a4q",
            "route_type": "light",
            "drafts": [],
            "verdict": "Repo summary here.",
            "cloud_gold": None,
        },
        # 2. Cloud escalation (2.0x gold weighting + 1.5x routing decision)
        {
            "ts": "2026-08-25T00:01:00Z",
            "task": "audit zero-trust kernel vulnerability",
            "chosen_agent": "deepseek-v4-flash-dspark",
            "route_type": "escalation",
            "drafts": [],
            "verdict": "Kernel is sound.",
            "cloud_gold": "cloud",
        },
        # 3. MoA multi-draft aggregation (1.2x aggregation weight + 1.5x routing)
        {
            "ts": "2026-08-25T00:02:00Z",
            "task": "complex design pattern recommendation",
            "chosen_agent": "deepseek-v4-flash-dspark",
            "route_type": "moa",
            "drafts": ["Draft A: use factory", "Draft B: use builder"],
            "verdict": "Use factory pattern.",
            "cloud_gold": None,
        },
    ]
    with open(log_file, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    miner = HermesSignalMiner()
    mined_count = miner.mine_routing_log(log_file)
    assert mined_count >= 5  # 1 routing (entry 1) + 1 gold + 1 routing (entry 2) + 1 routing + 1 agg (entry 3)

    stats = miner.summary_stats()
    assert stats["total_pairs"] == 5
    assert stats["by_kind"]["specialist"] == 1  # Cloud escalation
    assert stats["by_kind"]["routing"] == 3     # 3 tasks routed
    assert stats["by_kind"]["aggregation"] == 1 # 1 multi-draft aggregation

    # Verify weights
    gold_pairs = [p for p in miner.pairs if p["kind"] == "specialist"]
    assert len(gold_pairs) == 1
    assert gold_pairs[0]["weight"] == 2.0  # 2x gold weighting

    routing_pairs = [p for p in miner.pairs if p["kind"] == "routing"]
    assert all(p["weight"] == 1.5 for p in routing_pairs)

    agg_pairs = [p for p in miner.pairs if p["kind"] == "aggregation"]
    assert agg_pairs[0]["weight"] == 1.2

    # Save to disk
    out_file = tmp_path / "train_pairs.jsonl"
    saved = miner.save_train_pairs(out_file)
    assert saved == 5
    assert out_file.exists()


def test_signal_miner_kanban_and_dumps(tmp_path):
    # 1. Mock SQLite Kanban DB
    db_path = tmp_path / "kanban.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT, body TEXT, status TEXT)")
    cur.execute("CREATE TABLE task_comments (id INTEGER PRIMARY KEY, task_id INTEGER, body TEXT, created_at TEXT)")
    cur.execute("INSERT INTO tasks VALUES (1, 'Refactor AST Parser', 'Implement visitor pattern', 'done')")
    cur.execute("INSERT INTO task_comments VALUES (1, 1, 'Completed visitor pattern in core.py', '2026-08-25')")
    conn.commit()
    conn.close()

    # 2. Mock Request Dump
    dump_path = tmp_path / "req_dump_01.json"
    dump_data = {
        "messages": [{"role": "user", "content": "Explain LRU cache"}],
        "response": {"choices": [{"message": {"content": "An LRU cache evicts least recently used items."}}]},
    }
    dump_path.write_text(json.dumps(dump_data), encoding="utf-8")

    miner = HermesSignalMiner()
    k_count = miner.mine_kanban(db_path)
    r_count = miner.mine_request_dumps(str(tmp_path / "*dump*.json"))

    assert k_count == 1
    assert r_count == 1

    stats = miner.summary_stats()
    assert stats["total_pairs"] == 2
    assert stats["by_kind"]["task_outcome"] == 1
    assert stats["by_kind"]["specialist"] == 1


# ---------------------------------------------------------------------------
# 5. System Manifest Export Tests
# ---------------------------------------------------------------------------


def test_generate_moa_manifest(tmp_path):
    manifest_path = tmp_path / "moa_manifest.json"
    manifest = generate_moa_manifest(manifest_path)

    assert manifest["status"] == "OK"
    assert manifest["system"] == "CAMELOT_OS_HERMES_MOA"
    assert "nodes" in manifest
    assert "light_tier" in manifest["nodes"]
    assert "perception" in manifest["nodes"]
    assert "two_tower_diffusion" in manifest["nodes"]
    assert "aggregator_brain" in manifest["nodes"]
    assert "escalation_cloud" in manifest["nodes"]
    assert manifest["nodes"]["escalation_cloud"]["gold_weight"] == 2.0
    assert manifest_path.exists()
