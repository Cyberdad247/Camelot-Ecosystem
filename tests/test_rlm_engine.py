# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

"""Unit tests for the assimilated RLM engine and continual /refine loop."""

import importlib.util
from pathlib import Path
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RLM_ENGINE_PATH = REPO_ROOT / "01_KERNEL" / "reasoning" / "rlm_engine.py"


def _load_rlm_module():
    spec = importlib.util.spec_from_file_location("rlm_engine", RLM_ENGINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rlm_engine"] = mod
    spec.loader.exec_module(mod)
    return mod


rlm_mod = _load_rlm_module()

AppliedRefinementEdit = rlm_mod.AppliedRefinementEdit
HarnessEntry = rlm_mod.HarnessEntry
HarnessState = rlm_mod.HarnessState
RefinementAction = rlm_mod.RefinementAction
RefinementEdit = rlm_mod.RefinementEdit
RefinementProposal = rlm_mod.RefinementProposal
RefinementResult = rlm_mod.RefinementResult
RLMEngine = rlm_mod.RLMEngine
RLMModel = rlm_mod.RLMModel
RLMSpawnHandle = rlm_mod.RLMSpawnHandle
RLMSubagent = rlm_mod.RLMSubagent
TokenUsage = rlm_mod.TokenUsage
apply_refinement_proposal = rlm_mod.apply_refinement_proposal
create_rollback_proposal = rlm_mod.create_rollback_proposal


# ---------------------------------------------------------------------------
# Test HarnessState CRUD & Persistence
# ---------------------------------------------------------------------------

def test_harness_state_crud(tmp_path: Path):
    state_file = tmp_path / "harness_state.json"
    state = HarnessState(state_file, scope="local")

    # 1. Create Memory
    mem = state.create("memory", "Arch Decision", "Use ZeroMQ and RLM recursion", id="arch_dec_1")
    assert mem.id == "arch_dec_1"
    assert mem.kind == "memory"
    assert mem.title == "Arch Decision"
    assert mem.content == "Use ZeroMQ and RLM recursion"
    assert mem.version == 1

    # 2. Get Memory
    fetched = state.get("memory", "arch_dec_1")
    assert fetched is not None
    assert fetched.content == "Use ZeroMQ and RLM recursion"

    # 3. Update Memory
    updated = state.update("memory", "arch_dec_1", "Arch Decision", "Use ZeroMQ, asyncio, and RLM recursion")
    assert updated.version == 2
    assert updated.content == "Use ZeroMQ, asyncio, and RLM recursion"

    # 4. Duplicate create error
    with pytest.raises(ValueError, match="already exists"):
        state.create("memory", "Arch Decision", "duplicate content", id="arch_dec_1")

    # 5. Disk persistence verification
    state2 = HarnessState(state_file, scope="local")
    reloaded = state2.get("memory", "arch_dec_1")
    assert reloaded is not None
    assert reloaded.version == 2
    assert reloaded.content == "Use ZeroMQ, asyncio, and RLM recursion"

    # 6. Delete
    assert state.delete("memory", "arch_dec_1") is True
    assert state.get("memory", "arch_dec_1") is None
    assert state.delete("memory", "arch_dec_1") is False


def test_harness_state_skill_validation(tmp_path: Path):
    state_file = tmp_path / "harness_state.json"
    state = HarnessState(state_file, scope="local")

    # Valid Python skill
    skill = state.create(
        "skill",
        "Test Scanner",
        "Runs AST scan",
        id="ast_scanner",
        reference={"type": "python", "import": "tools.scanner", "callable": "run_scan"},
        arguments={"target": {"type": "str", "required": True}},
    )
    assert skill.id == "ast_scanner"
    assert skill.reference["callable"] == "run_scan"

    # Invalid Python skill reference
    with pytest.raises(ValueError, match="skill reference"):
        state.create("skill", "Bad Skill", "Invalid", id="bad_skill", reference={})


def test_harness_state_refinement_recording_and_overview(tmp_path: Path):
    state_file = tmp_path / "harness_state.json"
    state = HarnessState(state_file, scope="local")
    state.create("prompt", "Safety Guard", "Never bypass HITL gates", id="hitl_rule")

    ev = state.record_refinement("Audit trigger", ["create prompt:hitl_rule"], evidence="HITL compliance pass")
    assert ev.id.startswith("refine_")
    assert "create prompt:hitl_rule" in ev.changes

    overview = state.overview()
    assert "prompt: 1" in overview
    assert "Safety Guard" in overview
    assert "refinements: 1" in overview


# ---------------------------------------------------------------------------
# Test Continual /refine Proposal & Rollback Loop
# ---------------------------------------------------------------------------

def test_continual_refine_apply_proposal(tmp_path: Path):
    state_file = tmp_path / "harness_state.json"
    state = HarnessState(state_file, scope="local")

    proposal = RefinementProposal(
        summary="Add subagent spec and prompt policy",
        rationale="Multi-agent orchestration requires specialized coder subagent",
        expected_outcome="Coder subagent is available in harness",
        edits=[
            RefinementEdit(
                action="create",
                kind="subagent",
                id="coder_subagent",
                title="Coder Subagent",
                content="Implements algorithmic Python routines without external dependencies",
                path="development",
            ),
            RefinementEdit(
                action="create",
                kind="prompt",
                id="strict_typing_policy",
                title="Strict Typing",
                content="Always write strict Python type annotations",
                path="policy",
            ),
        ],
    )

    result = apply_refinement_proposal(state, proposal)
    assert result.summary == proposal.summary
    assert len(result.applied_edits) == 2
    assert all(e.applied for e in result.applied_edits)

    assert state.get("subagent", "coder_subagent") is not None
    assert state.get("prompt", "strict_typing_policy") is not None

    # Base system prompt protection
    bad_proposal = RefinementProposal(
        summary="Try to edit immutable prompt",
        rationale="Invalid attempt",
        expected_outcome="Fail edit",
        edits=[
            RefinementEdit(
                action="create",
                kind="prompt",
                id="base_system_prompt",
                title="Hacked Prompt",
                content="New Base Prompt",
            )
        ],
    )
    bad_res = apply_refinement_proposal(state, bad_proposal)
    assert not bad_res.applied_edits[0].applied
    assert "not editable" in bad_res.applied_edits[0].error


def test_continual_refine_rollback(tmp_path: Path):
    state_file = tmp_path / "harness_state.json"
    state = HarnessState(state_file, scope="local")

    # Initial state
    state.create("prompt", "Original Policy", "Initial content", id="policy_1")

    # Apply refinement with update and create
    proposal = RefinementProposal(
        summary="Refinement 1",
        rationale="Update policy_1 and add memory_1",
        expected_outcome="Updated",
        edits=[
            RefinementEdit(
                action="update",
                kind="prompt",
                id="policy_1",
                title="Updated Policy",
                content="Updated content",
            ),
            RefinementEdit(
                action="create",
                kind="memory",
                id="mem_temp",
                title="Temporary Fact",
                content="Temp fact",
            ),
        ],
    )
    res = apply_refinement_proposal(state, proposal)
    assert state.get("prompt", "policy_1").content == "Updated content"
    assert state.get("memory", "mem_temp") is not None

    # Invert and rollback
    rollback_prop = create_rollback_proposal(res)
    rollback_res = apply_refinement_proposal(state, rollback_prop)
    assert len(rollback_res.applied_edits) == 2
    assert all(e.applied for e in rollback_res.applied_edits)

    # Verify original state restored
    assert state.get("prompt", "policy_1").content == "Initial content"
    assert state.get("memory", "mem_temp") is None


# ---------------------------------------------------------------------------
# Test RLMEngine Execution & Subagent Lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_rlm_engine_subagent_spawning(tmp_path: Path):
    engine = RLMEngine(max_depth=2, base_dir=tmp_path)

    # Spawn child agent
    handle = await engine.run("Review PR #42", name="pr-reviewer", model="gemini-2.5-flash")
    assert isinstance(handle, RLMSpawnHandle)
    assert handle.name == "pr-reviewer"
    assert handle.model == "gemini-2.5-flash"
    assert handle.depth == 1

    # Verify registry
    subagents = engine.list_subagents()
    assert len(subagents) == 1
    assert subagents[0].rlm_child_id == handle.rlm_child_id
    assert subagents[0].session_name == "pr-reviewer"

    # Spawn second child with callable syntax
    handle2 = await engine("Verify coverage", name="coverage-auditor")
    assert handle2.name == "coverage-auditor"
    assert len(engine.list_subagents()) == 2

    # Usage attribution
    engine.attribute_usage(handle.rlm_child_id, TokenUsage(100, 50, 150, 0.002))
    engine.attribute_usage(handle2.rlm_child_id, TokenUsage(200, 100, 300, 0.004))
    total = engine.total_usage()
    assert total.total_tokens == 450
    assert total.cost_usd == pytest.approx(0.006)

    # Delete subagent
    deleted = engine.delete_subagent(handle.rlm_child_id)
    assert deleted.status == "cancelled"
    assert len(engine.list_subagents()) == 1


@pytest.mark.anyio
async def test_rlm_engine_depth_bounding(tmp_path: Path):
    engine = RLMEngine(max_depth=2, base_dir=tmp_path)

    # Depth 1: allowed
    h1 = await engine.run("Task 1", current_depth=0)
    assert h1.depth == 1

    # Depth 2: allowed
    h2 = await engine.run("Task 2", current_depth=1)
    assert h2.depth == 2

    # Depth 3: raises RuntimeError (exceeds max_depth 2)
    with pytest.raises(RuntimeError, match="RLM recursion depth exceeded"):
        await engine.run("Task 3", current_depth=2)


@pytest.mark.anyio
async def test_rlm_engine_refine_loop_integration(tmp_path: Path):
    engine = RLMEngine(base_dir=tmp_path)

    dict_proposal = {
        "summary": "Integration refine test",
        "rationale": "Testing engine refine API",
        "expected_outcome": "New memory stored",
        "edits": [
            {
                "action": "create",
                "kind": "memory",
                "id": "int_mem_1",
                "title": "Kernel Memory",
                "content": "RLM assimilation into Camelot-OS is complete",
            }
        ],
    }

    result = await engine.refine(dict_proposal)
    assert result.summary == "Integration refine test"
    assert engine.harness.get("memory", "int_mem_1") is not None
    assert engine.harness.get("memory", "int_mem_1").content == "RLM assimilation into Camelot-OS is complete"
