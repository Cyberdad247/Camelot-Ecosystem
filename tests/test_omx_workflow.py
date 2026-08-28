# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for OMX Multi-Agent Workflow Primitives
===================================================================
Validates:
  1. $plan ($ralplan) state machine & quality criteria
  2. $ultragoal durable multi-goal planning, checkpoints & steering mutations
  3. $team worker coordination, mailboxes, task claiming & shutdown
  4. $code-review 2-lane independent synthesis & devil's-advocate gates
  5. $ultraqa adversarial dynamic QA cycles & stopping conditions
  6. $autopilot supervisor FSM transitions & user pause/resume
  7. Capability lock surface digest & observation validation
  8. Runic router integration for //OMX_* and $-aliases
"""

import pytest

from control_plane.runes.omx_workflow_adapter import (
    AutopilotPhase,
    AutopilotStateMachine,
    CapabilityFailureCode,
    CapabilityLockfile,
    CodeReviewLaneResult,
    CodeReviewSynthesis,
    FixtureContract,
    PlanMode,
    PlanPhase,
    PlanStateMachine,
    ReviewVerdict,
    TeamStateMachine,
    TeamTaskStatus,
    ToolContract,
    UltragoalStateMachine,
    UltragoalStatus,
    UltragoalSteeringMutationKind,
    UltraQAPhase,
    UltraQAStateMachine,
    normalize_omx_rune,
)
from control_plane import runic_router


# ============================================================================
# 1. Plan State Machine Tests
# ============================================================================

def test_plan_state_machine_direct_flow():
    sm = PlanStateMachine(directive="Build auth service", mode=PlanMode.DIRECT)
    assert sm.current_phase == PlanPhase.INIT
    
    sm.advance()
    assert sm.current_phase == PlanPhase.ANALYSIS
    
    sm.advance("draft", {
        "criteria": [
            "Acceptance Criteria 1: JWT token signature validated",
            "Acceptance Criteria 2: Expired tokens rejected with 401",
        ],
        "steps": [
            {"step": 1, "desc": "Edit auth.py", "path": "services/auth.py"},
            {"step": 2, "desc": "Add tests", "path": "tests/test_auth.py"},
        ],
    })
    assert sm.current_phase == PlanPhase.DRAFTING
    sm.advance("finalize")
    assert sm.current_phase == PlanPhase.APPROVED
    
    quality = sm.validate_plan_quality()
    assert quality["valid"] is True
    assert quality["citation_ratio"] == 1.0
    assert quality["criteria_ratio"] == 1.0


def test_plan_state_machine_interview_flow():
    sm = PlanStateMachine(directive="Refactor database", mode=PlanMode.INTERVIEW)
    sm.advance()
    assert sm.current_phase == PlanPhase.EXPLORING
    
    sm.advance("facts", {"facts": ["Database uses PostgreSQL", "ORM is SQLAlchemy"]})
    assert sm.current_phase == PlanPhase.INTERVIEWING
    assert len(sm.codebase_facts) == 2
    
    sm.advance("interview", {
        "questions": ["Should we support migrations?"],
        "answers": {"Should we support migrations?": "Yes, using Alembic"},
        "ready_for_draft": True,
    })
    assert sm.current_phase == PlanPhase.DRAFTING


# ============================================================================
# 2. Ultragoal State Machine Tests
# ============================================================================

def test_ultragoal_lifecycle_and_checkpoints():
    sm = UltragoalStateMachine(brief="Deploy Payment Gateway")
    g1 = sm.add_goal("Stripe Integration", "Connect Stripe API")
    g2 = sm.add_goal("Webhook Handler", "Process invoice payments")
    
    assert sm.status == UltragoalStatus.PENDING
    assert len(sm.goals) == 2
    
    started = sm.start_next_goal()
    assert started.id == g1.id
    assert sm.status == UltragoalStatus.IN_PROGRESS
    
    # Checkpoint goal 1
    sm.checkpoint_goal(g1.id, UltragoalStatus.COMPLETE, "Tests passed: 10/10")
    assert sm.status == UltragoalStatus.IN_PROGRESS
    
    # Start and checkpoint goal 2
    started2 = sm.start_next_goal()
    assert started2.id == g2.id
    sm.checkpoint_goal(g2.id, UltragoalStatus.COMPLETE, "Webhooks verified with live replay")
    
    # All complete
    assert sm.status == UltragoalStatus.COMPLETE
    assert len(sm.ledger_entries) >= 4


def test_ultragoal_steering_mutations():
    sm = UltragoalStateMachine(brief="Cloud migration")
    g1 = sm.add_goal("Storage Migration", "Move S3 buckets")
    g2 = sm.add_goal("Compute Migration", "Deploy EKS clusters")
    
    # Steering: Split subgoal
    split_res = sm.steer(
        kind=UltragoalSteeringMutationKind.SPLIT_SUBGOAL,
        evidence="Compute migration too large for single batch",
        rationale="Decompose into staging and production EKS",
        target_goal_id=g2.id,
        child_goals=[
            {"title": "Staging EKS", "objective": "Setup staging cluster"},
            {"title": "Prod EKS", "objective": "Setup production cluster"},
        ],
    )
    assert split_res["accepted"] is True
    assert len(sm.goals) == 3
    assert sm.goals[1].id == f"{g2.id}.1"
    assert sm.goals[2].id == f"{g2.id}.2"


# ============================================================================
# 3. Team Coordination State Machine Tests
# ============================================================================

def test_team_coordination_and_mailboxes():
    sm = TeamStateMachine(name="alpha-squad")
    w1 = sm.register_worker("worker-1", "sir_codex")
    w2 = sm.register_worker("worker-2", "sir_forge")
    
    t1 = sm.add_task("task-100", "Implement Redis cache")
    
    # Claim task
    claimed, token = sm.claim_task("worker-1", "task-100")
    assert claimed is True
    assert token is not None
    assert w1.status == "working"
    
    # Mailbox messaging
    msg = sm.send_message("worker-1", "worker-2", "Need Redis connection parameters")
    assert len(sm.mailboxes["worker-2"]) == 1
    assert sm.mailboxes["worker-2"][0].body == msg.body
    
    # Complete task
    completed, msg = sm.complete_task("task-100", token, "Cache tests green")
    assert completed is True
    assert t1.status == TeamTaskStatus.COMPLETED
    assert w1.status == "idle"
    
    # Shutdown
    shutdown_res = sm.shutdown()
    assert shutdown_res["clean"] is True
    assert shutdown_res["tasks_completed"] == 1


# ============================================================================
# 4. Code Review Independent 2-Lane Synthesis Tests
# ============================================================================

def test_code_review_synthesis_scenarios():
    # Scenario A: Both lanes pass
    rev_ok = CodeReviewLaneResult(lane="code-reviewer", status="APPROVE", evidence="All lints/tests clean")
    arch_ok = CodeReviewLaneResult(lane="architect", status="CLEAR", evidence="Boundary invariants respected")
    res_a = CodeReviewSynthesis.synthesize(rev_ok, arch_ok)
    assert res_a.final_verdict == ReviewVerdict.APPROVE
    assert res_a.is_merge_ready is True

    # Scenario B: Architect blocks
    arch_block = CodeReviewLaneResult(lane="architect", status="BLOCK", evidence="Cyclic dependency introduced")
    res_b = CodeReviewSynthesis.synthesize(rev_ok, arch_block)
    assert res_b.final_verdict == ReviewVerdict.REQUEST_CHANGES
    assert res_b.is_merge_ready is False

    # Scenario C: Architect watch
    arch_watch = CodeReviewLaneResult(lane="architect", status="WATCH", evidence="Check memory profile under load")
    res_c = CodeReviewSynthesis.synthesize(rev_ok, arch_watch)
    assert res_c.final_verdict == ReviewVerdict.COMMENT
    assert res_c.is_merge_ready is False

    # Scenario D: Missing lane (unavailable)
    res_d = CodeReviewSynthesis.synthesize(rev_ok, None)
    assert res_d.final_verdict == ReviewVerdict.REQUEST_CHANGES
    assert "Independent review unavailable" in res_d.rationale


# ============================================================================
# 5. UltraQA State Machine Tests
# ============================================================================

def test_ultraqa_lifecycle_and_stopping_conditions():
    sm = UltraQAStateMachine(goal="Adversarial Audit of Runic Router")
    sc1 = sm.add_scenario("S1", "malformed_input", "Pass null byte", "router --detect '\\0'", "graceful")
    sc2 = sm.add_scenario("S2", "prompt_injection", "Extract key", "router --detect '//FORGE api_key'", "ghost")
    
    sm.record_scenario_result("S1", True, "graceful", "log")
    sm.record_scenario_result("S2", True, "ghost", "log")
    
    cycle_phase = sm.evaluate_cycle()
    assert cycle_phase == UltraQAPhase.CLEANUP
    
    report = sm.complete_and_cleanup()
    assert report["status"] == "ULTRAQA COMPLETE"
    assert report["scenarios_passed"] == 2


def test_ultraqa_repeated_failure_stops():
    sm = UltraQAStateMachine(goal="Flaky Service Audit")
    sm.add_scenario("S1", "flaky_tests", "Stress test", "run_tests", "pass")
    
    # 3 consecutive identical failures
    sm.record_scenario_result("S1", False, "Connection reset", "fail")
    sm.record_scenario_result("S1", False, "Connection reset", "fail")
    sm.record_scenario_result("S1", False, "Connection reset", "fail")
    
    phase = sm.evaluate_cycle()
    assert phase == UltraQAPhase.STOPPED
    assert sm.active is False


# ============================================================================
# 6. Autopilot Master Supervisor Tests
# ============================================================================

def test_autopilot_supervisor_flow():
    sm = AutopilotStateMachine(directive="Full Feature Autopilot Build")
    assert sm.current_phase == AutopilotPhase.DEEP_INTERVIEW
    
    sm.transition(AutopilotPhase.RALPLAN, {"plan_id": "plan-123"})
    assert sm.current_phase == AutopilotPhase.RALPLAN
    
    # User clarification pause
    sm.pause_for_user("Choose database backend")
    assert sm.current_phase == AutopilotPhase.WAITING_FOR_USER
    
    # Resume
    sm.resume_from_user("PostgreSQL")
    assert sm.current_phase == AutopilotPhase.RALPLAN
    
    sm.transition(AutopilotPhase.ULTRAGOAL)
    sm.transition(AutopilotPhase.CODE_REVIEW)
    sm.transition(AutopilotPhase.ULTRAQA)
    sm.transition(AutopilotPhase.COMPLETE)
    assert sm.active is False


# ============================================================================
# 7. Capability Lock Schema Tests
# ============================================================================

def test_capability_lock_digest_and_observations():
    lock = CapabilityLockfile(
        version=1,
        tools=[
            ToolContract(name="view_file", server="default_api", enabled=True),
            ToolContract(name="run_command", server="default_api", enabled=True),
        ],
        fixtures=[
            FixtureContract(id="f-01", prompt_id="p-01", allowed_tools=["view_file"], expected_tool="view_file"),
            FixtureContract(id="f-02", prompt_id="p-02", no_tool_calls=True),
        ],
    )
    
    digest = lock.compute_surface_digest()
    assert isinstance(digest, str)
    assert len(digest) == 64
    
    # Valid call
    val_ok = lock.validate_observation("f-01", [{"name": "view_file", "arguments": {}}])
    assert len(val_ok) == 0
    
    # Unexpected tool call for f-02
    val_err = lock.validate_observation("f-02", [{"name": "run_command", "arguments": {}}])
    assert len(val_err) == 1
    assert val_err[0]["code"] == CapabilityFailureCode.UNEXPECTED_TOOL_CALL.value

    # Hallucinated tool
    val_hallucinated = lock.validate_observation("f-01", [{"name": "non_existent_tool"}])
    assert any(f["code"] == CapabilityFailureCode.HALLUCINATED_TOOL.value for f in val_hallucinated)


# ============================================================================
# 8. Runic Router Integration Tests
# ============================================================================

@pytest.fixture
def router(monkeypatch, tmp_path):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    return runic_router


def test_omx_rune_aliases_normalization():
    assert normalize_omx_rune("$plan") == "//OMX_PLAN"
    assert normalize_omx_rune("$ralplan") == "//OMX_PLAN"
    assert normalize_omx_rune("$ultragoal") == "//OMX_ULTRAGOAL"
    assert normalize_omx_rune("$team") == "//OMX_TEAM"
    assert normalize_omx_rune("$code-review") == "//OMX_CODE_REVIEW"
    assert normalize_omx_rune("$ultraqa") == "//OMX_ULTRAQA"
    assert normalize_omx_rune("$autopilot") == "//OMX_AUTOPILOT"


def test_omx_runes_dispatch_via_router(router):
    # Test //OMX_PLAN
    res_plan = router.route_rune("//OMX_PLAN", "Build new caching engine")
    assert res_plan.knight == "merlin_omega"
    assert res_plan.metadata["action"] == "omx_plan_direct"

    # Test $ultragoal alias dispatch
    res_ultra = router.route_rune("$ultragoal", "Ship release v1.0")
    assert res_ultra.knight == "sir_codex"
    assert res_ultra.metadata["action"] == "omx_ultragoal_init"

    # Test $team alias dispatch
    res_team = router.route_rune("$team", "Implement feature X across 3 lanes")
    assert res_team.knight == "sir_boris"
    assert res_team.metadata["action"] == "omx_team_init"

    # Test $code-review alias dispatch
    res_review = router.route_rune("$code-review", "Audit pull request diff")
    assert res_review.knight == "sir_sentinel"
    assert res_review.metadata["action"] == "omx_code_review_synthesize"

    # Test $ultraqa alias dispatch
    res_qa = router.route_rune("$ultraqa", "Full e2e regression check")
    assert res_qa.knight == "sir_sentinel"
    assert res_qa.metadata["action"] == "omx_ultraqa_cycle"

    # Test $autopilot alias dispatch
    res_auto = router.route_rune("$autopilot", "Autonomous project delivery")
    assert res_auto.knight == "sir_boris"
    assert res_auto.metadata["action"] == "omx_autopilot_conduct"


def test_omx_privacy_shield_redirection(router):
    # Privacy keyword in param redirects to sir_ghost
    res = router.route_rune("//OMX_PLAN", "plan database with secret api_key password")
    assert res.knight == "sir_ghost"
    assert res.metadata["privacy_override"] is True
