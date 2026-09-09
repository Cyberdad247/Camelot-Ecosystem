# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

"""Unit tests for assimilated Deer-Flow v2.0 Deep Exploration Research Flow,
Hierarchical Memory Trees, InfoQuest Web Crawler, and Secure Sandbox."""

import importlib.util
from pathlib import Path
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEER_MODULE_PATH = REPO_ROOT / "01_KERNEL" / "reasoning" / "deer_research_flow.py"


def _load_deer_module():
    spec = importlib.util.spec_from_file_location("deer_research_flow", DEER_MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["deer_research_flow"] = mod
    spec.loader.exec_module(mod)
    return mod


deer_mod = _load_deer_module()

CommandResult = deer_mod.CommandResult
CrawledPage = deer_mod.CrawledPage
DeerResearchFlow = deer_mod.DeerResearchFlow
HierarchicalMemoryTree = deer_mod.HierarchicalMemoryTree
InfoQuestCrawler = deer_mod.InfoQuestCrawler
MemoryConflictError = deer_mod.MemoryConflictError
MemoryCorruptionError = deer_mod.MemoryCorruptionError
MemoryFact = deer_mod.MemoryFact
MemoryTreeNode = deer_mod.MemoryTreeNode
MockWebClient = deer_mod.MockWebClient
MultiAgentResearchCoordinator = deer_mod.MultiAgentResearchCoordinator
ResearchPhase = deer_mod.ResearchPhase
SandboxPathMapping = deer_mod.SandboxPathMapping
SandboxSecurityViolation = deer_mod.SandboxSecurityViolation
SecureSandbox = deer_mod.SecureSandbox
WebSearchResult = deer_mod.WebSearchResult


# ---------------------------------------------------------------------------
# Test Hierarchical Memory Trees
# ---------------------------------------------------------------------------

def test_memory_tree_lifecycle(tmp_path: Path):
    storage_file = tmp_path / "memory_tree.json"
    tree = HierarchicalMemoryTree(storage_file, agent_name="sir_boris", user_id="vashawn_head")

    # 1. Add Dimension Node
    dim_node = tree.add_node(
        name="Zero-Trust Architecture",
        node_type="dimension",
        content="Zero-trust isolation boundaries and mTLS verification.",
    )
    assert dim_node.name == "Zero-Trust Architecture"
    assert dim_node.node_type == "dimension"
    assert dim_node.parent_id == "root"

    # 2. Add Child Node
    child_node = tree.add_node(
        name="Key Management",
        node_type="theme",
        content="Sub-theme for ephemeral secret key handling.",
        parent_id=dim_node.id,
    )
    assert child_node.parent_id == dim_node.id
    assert child_node.id in dim_node.children_ids

    # 3. Add Facts
    fact1 = tree.add_fact(
        node_id=child_node.id,
        category="constraint",
        content="Never persist raw API secrets into config files.",
        confidence=0.99,
        tags=["security", "secrets"],
    )
    assert fact1.category == "constraint"
    assert fact1.revision == 1

    # 4. Update Fact with Revision Concurrency Check
    updated_fact = tree.update_fact(
        node_id=child_node.id,
        fact_id=fact1.id,
        content="Never persist raw API secrets into config files; use presence flags only.",
        expected_revision=1,
    )
    assert updated_fact.revision == 2
    assert "presence flags" in updated_fact.content

    # 5. Revision Conflict Test
    with pytest.raises(MemoryConflictError):
        tree.update_fact(
            node_id=child_node.id,
            fact_id=fact1.id,
            content="Conflicting write",
            expected_revision=1,  # Stale revision
        )

    # 6. Signal Detection
    signals = tree.detect_signals("We decided that zero external deps is strictly required for our goal.")
    detected_cats = {s["category"] for s in signals}
    assert "decision" in detected_cats
    assert "constraint" in detected_cats
    assert "goal" in detected_cats

    # 7. Search Memory Tree
    results = tree.search("secrets security")
    assert len(results) >= 1
    score, node, fact = results[0]
    assert score > 0.0
    assert fact is not None
    assert "presence flags" in fact.content

    # 8. Export Injection Text
    injection = tree.export_context_for_injection(max_chars=2000)
    assert "<hierarchical_memory>" in injection
    assert "Key Management" in injection
    assert "</hierarchical_memory>" in injection

    # 9. Persistence Reload Check
    reloaded_tree = HierarchicalMemoryTree(storage_file, agent_name="sir_boris", user_id="vashawn_head")
    assert len(reloaded_tree.list_nodes()) == len(tree.list_nodes())
    fetched = reloaded_tree.get_node(child_node.id)
    assert fetched is not None
    assert len(fetched.facts) == 1
    assert fetched.facts[0].content == updated_fact.content

    # 10. Remove Fact
    removed = tree.remove_fact(child_node.id, fact1.id)
    assert removed is True
    assert len(tree.get_node(child_node.id).facts) == 0


# ---------------------------------------------------------------------------
# Test InfoQuest Web Crawler
# ---------------------------------------------------------------------------

def test_infoquest_query_generation_and_crawling():
    mock_client = MockWebClient()
    mock_client.add_search_mock("quantum", [
        WebSearchResult(
            title="Quantum Annealing Metrics",
            url="https://camelot.os/papers/quantum-metrics",
            snippet="Detailed benchmarks on 128-qubit coherent annealing.",
            source_engine="arxiv",
        )
    ])
    mock_client.add_page_mock(
        "https://camelot.os/papers/quantum-metrics",
        "# Quantum Annealing Paper\nEmpirical latency benchmarks indicate 10x speedup.",
    )

    crawler = InfoQuestCrawler(web_client=mock_client)
    queries = crawler.generate_multi_angle_queries("Quantum Computing", temporal_qualifier="2026")
    assert "facts_and_data" in queries
    assert "challenges_and_limitations" in queries
    assert any("2026" in q for q in queries["facts_and_data"])

    crawled = crawler.execute_osint_crawl("Quantum Computing", temporal_anchor="2026", max_pages=3)
    assert len(crawled) >= 1
    assert crawled[0].url.startswith("https://")
    assert crawled[0].content_hash != ""


# ---------------------------------------------------------------------------
# Test Secure Local Sandbox
# ---------------------------------------------------------------------------

def test_secure_sandbox_execution_and_containment(tmp_path: Path):
    workspace = tmp_path / "sandbox_ws"
    sandbox = SecureSandbox("sbx_test_01", workspace)

    # 1. Virtual Path Resolution & Write
    v_file = "/mnt/user-data/workspace/src/test.txt"
    sandbox.write_file(v_file, "Line 1: Hello Sandbox\nLine 2: Contained Data\nLine 3: Camelot OS\n")

    # 2. Read File with Line Bounds
    full_text = sandbox.read_file(v_file)
    assert "Line 1: Hello Sandbox" in full_text
    slice_text = sandbox.read_file(v_file, start_line=2, end_line=3)
    assert "Line 2: Contained Data" in slice_text
    assert "Line 1" not in slice_text

    # 3. Directory Listing
    entries = sandbox.list_dir("/mnt/user-data/workspace/src")
    assert len(entries) == 1
    assert entries[0]["name"] == "test.txt"

    # 4. Grep Search
    grep_res = sandbox.grep_search("Contained", "/mnt/user-data/workspace")
    assert len(grep_res) == 1
    assert grep_res[0]["line_number"] == 2
    assert "Contained Data" in grep_res[0]["line_content"]

    # 5. Path Escape Prevention
    with pytest.raises(SandboxSecurityViolation):
        sandbox.resolve_path("/mnt/user-data/workspace/../../etc/passwd")

    # 6. Read-Only Mount Enforcement
    ro_dir = tmp_path / "ro_mount"
    ro_dir.mkdir(parents=True, exist_ok=True)
    custom_sbx = SecureSandbox(
        "sbx_ro",
        workspace,
        virtual_mappings=[SandboxPathMapping("/mnt/readonly", ro_dir, read_only=True)],
    )
    with pytest.raises(SandboxSecurityViolation):
        custom_sbx.write_file("/mnt/readonly/forbidden.txt", "data")

    # 7. Command Execution with Env Validation
    cmd_res = sandbox.execute_command("echo SandboxActive", env={"TEST_FLAG": "ENABLED"})
    assert cmd_res.exit_code == 0
    assert "SandboxActive" in cmd_res.stdout
    assert cmd_res.timed_out is False

    # 8. Invalid Env Key Rejected
    with pytest.raises(ValueError):
        sandbox.execute_command("echo test", env={"INVALID-KEY!": "VAL"})


# ---------------------------------------------------------------------------
# Test DeerResearchFlow Orchestration & Subagents
# ---------------------------------------------------------------------------

def test_deer_research_flow_full_cycle(tmp_path: Path):
    storage_file = tmp_path / "research_mem.json"
    memory_tree = HierarchicalMemoryTree(storage_file)
    mock_client = MockWebClient()
    crawler = InfoQuestCrawler(mock_client)
    workspace = tmp_path / "flow_ws"
    sandbox = SecureSandbox("sbx_flow", workspace)

    flow = DeerResearchFlow(memory_tree=memory_tree, crawler=crawler, sandbox=sandbox)
    trajectory = flow.run_research_loop("Asynchronous Message Bus in Distributed OS", temporal_anchor="2026")

    assert trajectory.phase == ResearchPhase.COMPLETE
    assert len(trajectory.dimensions) == 3
    assert len(trajectory.crawled_pages) >= 3
    assert len(trajectory.extracted_facts) >= 3
    assert trajectory.final_report is not None
    assert "Deep Exploration Report" in trajectory.final_report
    assert "Synthesis Gate Verification" in trajectory.final_report

    # Verify report written to sandbox outputs
    out_report = sandbox.read_file(f"/mnt/user-data/outputs/{trajectory.session_id}_report.md")
    assert out_report == trajectory.final_report

    # Subagent Coordinator Test
    coordinator = MultiAgentResearchCoordinator(flow)
    task = coordinator.spawn_research_subagent(
        name="Distributed Ledger Researcher",
        role="Research Specialist",
        prompt="State Machine Replication and RAFT Consensus",
    )
    assert task.status == "pending"

    executed_task = coordinator.execute_subagent_task(task.task_id)
    assert executed_task.status == "completed"
    assert executed_task.result is not None
    assert "Deep Exploration Report" in executed_task.result
