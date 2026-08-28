# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
OMX Swarm Primitives & State Machines (L5 Agentic)
==================================================
Assimilates oh-my-codex (OMX) multi-agent workflow state machines and schemas
into Camelot-OS 01_KERNEL/swarm/.

Primitives:
  1. $plan ($ralplan): Socratic interview vs direct planning state machine
  2. $ultragoal: Durable multi-goal execution, steering invariants & completion gates
  3. $team: N coordinated agents on shared task list, mailbox coordination, role routing
  4. $code-review: Independent 2-lane review (code-reviewer + architect) with strict synthesis
  5. $ultraqa: Adversarial dynamic e2e QA state machine (up to 5 cycles) with hostile scenarios
  6. $autopilot: Master supervisor FSM orchestrating deep-interview -> plan -> ultragoal -> review/qa
  7. Capability Lock Schema: Cryptographic digests & tool/skill/agent contract verification
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================================
# 1. Capability Lock Schemas & Verification
# ============================================================================

class CapabilityFailureCode(str, Enum):
    LOCKFILE_MISSING = "lockfile_missing"
    LOCKFILE_INVALID_JSON = "lockfile_invalid_json"
    LOCKFILE_UNSUPPORTED_VERSION = "lockfile_unsupported_version"
    CONFIGURED_TOOL_SURFACE_MISMATCH = "configured_tool_surface_mismatch"
    SKILL_SURFACE_MISMATCH = "skill_surface_mismatch"
    AGENT_SURFACE_MISMATCH = "agent_surface_mismatch"
    FIXTURE_CONTRACT_MISMATCH = "fixture_contract_mismatch"
    EXTERNAL_SCHEMA_UNAVAILABLE = "external_schema_unavailable"
    OBSERVATIONS_MISSING = "observations_missing"
    OBSERVATIONS_INVALID_JSON = "observations_invalid_json"
    REQUIRED_OBSERVATION_MISSING = "required_observation_missing"
    UNKNOWN_FIXTURE = "unknown_fixture"
    DUPLICATE_OBSERVATION = "duplicate_observation"
    HALLUCINATED_TOOL = "hallucinated_tool"
    UNAVAILABLE_TOOL = "unavailable_tool"
    WRONG_TOOL_SELECTED = "wrong_tool_selected"
    MISSING_REQUIRED_ARG = "missing_required_arg"
    ARG_SCHEMA_INVALID = "arg_schema_invalid"
    UNEXPECTED_TOOL_CALL = "unexpected_tool_call"
    STRUCTURED_OUTPUT_INVALID = "structured_output_invalid"


@dataclass
class ToolContract:
    name: str
    server: str
    enabled: bool = True
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None


@dataclass
class DigestEntry:
    path: str
    digest: str


@dataclass
class FixtureContract:
    id: str
    prompt_id: str
    required: bool = True
    allowed_tools: List[str] = field(default_factory=list)
    expected_tool: Optional[str] = None
    no_tool_calls: bool = False


@dataclass
class CapabilityLockfile:
    version: int = 1
    kind: str = "omx_capabilities_lock"
    tools: List[ToolContract] = field(default_factory=list)
    skills: List[DigestEntry] = field(default_factory=list)
    agents: List[DigestEntry] = field(default_factory=list)
    fixtures: List[FixtureContract] = field(default_factory=list)

    def compute_surface_digest(self) -> str:
        payload = json.dumps(
            {
                "tools": [asdict(t) for t in self.tools],
                "skills": [asdict(s) for s in self.skills],
                "agents": [asdict(a) for a in self.agents],
                "fixtures": [asdict(f) for f in self.fixtures],
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def validate_observation(
        self, fixture_id: str, tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        failures = []
        fixture = next((f for f in self.fixtures if f.id == fixture_id), None)
        if not fixture:
            failures.append({
                "code": CapabilityFailureCode.UNKNOWN_FIXTURE.value,
                "message": f"Fixture {fixture_id} not registered in lockfile",
                "fixture_id": fixture_id,
            })
            return failures

        calls = tool_calls or []
        if fixture.no_tool_calls and calls:
            failures.append({
                "code": CapabilityFailureCode.UNEXPECTED_TOOL_CALL.value,
                "message": f"Fixture {fixture_id} expected no tool calls but received {len(calls)}",
                "fixture_id": fixture_id,
            })
            return failures

        allowed_set = set(fixture.allowed_tools)
        registered_tools = {t.name: t for t in self.tools if t.enabled}

        for call in calls:
            tname = call.get("name")
            if not tname:
                failures.append({
                    "code": CapabilityFailureCode.ARG_SCHEMA_INVALID.value,
                    "message": "Tool call missing tool name",
                    "fixture_id": fixture_id,
                })
                continue
            if tname not in registered_tools:
                failures.append({
                    "code": CapabilityFailureCode.HALLUCINATED_TOOL.value,
                    "message": f"Tool '{tname}' is not in configured tool registry",
                    "fixture_id": fixture_id,
                    "tool": tname,
                })
            elif allowed_set and tname not in allowed_set:
                failures.append({
                    "code": CapabilityFailureCode.WRONG_TOOL_SELECTED.value,
                    "message": f"Tool '{tname}' is not allowed for fixture {fixture_id}",
                    "fixture_id": fixture_id,
                    "tool": tname,
                })

        if fixture.expected_tool and not any(c.get("name") == fixture.expected_tool for c in calls):
            failures.append({
                "code": CapabilityFailureCode.WRONG_TOOL_SELECTED.value,
                "message": f"Fixture {fixture_id} expected tool '{fixture.expected_tool}'",
                "fixture_id": fixture_id,
                "tool": fixture.expected_tool,
            })

        return failures


# ============================================================================
# 2. Plan State Machine ($plan / $ralplan)
# ============================================================================

class PlanMode(str, Enum):
    INTERVIEW = "interview"
    DIRECT = "direct"
    REVIEW = "review"


class PlanPhase(str, Enum):
    INIT = "init"
    EXPLORING = "exploring"
    INTERVIEWING = "interviewing"
    ANALYSIS = "analysis"
    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REVISE = "revise"
    REJECTED = "rejected"


@dataclass
class PlanStateMachine:
    directive: str
    mode: PlanMode = PlanMode.DIRECT
    current_phase: PlanPhase = PlanPhase.INIT
    clarification_questions: List[str] = field(default_factory=list)
    answers: Dict[str, str] = field(default_factory=dict)
    codebase_facts: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    implementation_steps: List[Dict[str, Any]] = field(default_factory=list)
    review_verdict: Optional[str] = None
    iteration: int = 1

    def advance(self, action: str = "next", payload: Optional[Dict[str, Any]] = None) -> PlanPhase:
        p = payload or {}
        if self.current_phase == PlanPhase.INIT:
            if self.mode == PlanMode.INTERVIEW:
                self.current_phase = PlanPhase.EXPLORING
            elif self.mode == PlanMode.REVIEW:
                self.current_phase = PlanPhase.REVIEWING
            else:
                self.current_phase = PlanPhase.ANALYSIS

        elif self.current_phase == PlanPhase.EXPLORING:
            if "facts" in p:
                self.codebase_facts.extend(p["facts"])
            self.current_phase = PlanPhase.INTERVIEWING

        elif self.current_phase == PlanPhase.INTERVIEWING:
            if "questions" in p:
                self.clarification_questions.extend(p["questions"])
            if "answers" in p:
                self.answers.update(p["answers"])
            if "criteria" in p:
                self.acceptance_criteria = p["criteria"]
            if "steps" in p:
                self.implementation_steps = p["steps"]
            if p.get("ready_for_draft"):
                self.current_phase = PlanPhase.DRAFTING

        elif self.current_phase == PlanPhase.ANALYSIS:
            if "facts" in p:
                self.codebase_facts.extend(p["facts"])
            if "criteria" in p:
                self.acceptance_criteria = p["criteria"]
            if "steps" in p:
                self.implementation_steps = p["steps"]
            self.current_phase = PlanPhase.DRAFTING

        elif self.current_phase == PlanPhase.DRAFTING:
            if "criteria" in p:
                self.acceptance_criteria = p["criteria"]
            if "steps" in p:
                self.implementation_steps = p["steps"]
            if p.get("request_review"):
                self.current_phase = PlanPhase.REVIEWING
            else:
                self.current_phase = PlanPhase.APPROVED

        elif self.current_phase == PlanPhase.REVIEWING:
            verdict = p.get("verdict", "APPROVED").upper()
            self.review_verdict = verdict
            if verdict == "APPROVED":
                self.current_phase = PlanPhase.APPROVED
            elif verdict == "REVISE":
                self.current_phase = PlanPhase.REVISE
                self.iteration += 1
            else:
                self.current_phase = PlanPhase.REJECTED

        elif self.current_phase == PlanPhase.REVISE:
            self.current_phase = PlanPhase.DRAFTING

        return self.current_phase

    def validate_plan_quality(self) -> Dict[str, Any]:
        """Check 80%+ file citations and 90%+ concrete testable criteria."""
        has_file_ref = 0
        for step in self.implementation_steps:
            text = json.dumps(step)
            if any(ext in text for ext in [".py", ".ts", ".rs", ".json", ".md", "/"]):
                has_file_ref += 1

        citation_ratio = (has_file_ref / len(self.implementation_steps)) if self.implementation_steps else 0.0
        concrete_criteria = sum(1 for c in self.acceptance_criteria if len(c.strip()) > 10)
        criteria_ratio = (concrete_criteria / len(self.acceptance_criteria)) if self.acceptance_criteria else 0.0

        return {
            "citation_ratio": citation_ratio,
            "citations_passed": citation_ratio >= 0.8 or not self.implementation_steps,
            "criteria_ratio": criteria_ratio,
            "criteria_passed": criteria_ratio >= 0.9 or not self.acceptance_criteria,
            "valid": (citation_ratio >= 0.8 or not self.implementation_steps) and (criteria_ratio >= 0.9 or not self.acceptance_criteria),
        }


# ============================================================================
# 3. Ultragoal State Machine & Steering Invariants ($ultragoal)
# ============================================================================

class UltragoalStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"
    REVIEW_BLOCKED = "review_blocked"
    NEEDS_USER_DECISION = "needs_user_decision"


class UltragoalSteeringMutationKind(str, Enum):
    ADD_SUBGOAL = "add_subgoal"
    SPLIT_SUBGOAL = "split_subgoal"
    REORDER_PENDING = "reorder_pending"
    REVISE_PENDING_WORDING = "revise_pending_wording"
    ANNOTATE_LEDGER = "annotate_ledger"
    MARK_BLOCKED_SUPERSEDED = "mark_blocked_superseded"


@dataclass
class GoalStory:
    id: str
    title: str
    objective: str
    status: UltragoalStatus = UltragoalStatus.PENDING
    evidence: List[str] = field(default_factory=list)
    token_budget: Optional[int] = None
    blockers: List[str] = field(default_factory=list)


@dataclass
class UltragoalStateMachine:
    brief: str
    goals: List[GoalStory] = field(default_factory=list)
    status: UltragoalStatus = UltragoalStatus.PENDING
    codex_goal_mode: str = "aggregate"  # aggregate | per_story
    active_goal_id: Optional[str] = None
    ledger_entries: List[Dict[str, Any]] = field(default_factory=list)

    def add_goal(self, title: str, objective: str, goal_id: Optional[str] = None) -> GoalStory:
        gid = goal_id or f"goal-{len(self.goals) + 1:03d}"
        story = GoalStory(id=gid, title=title, objective=objective)
        self.goals.append(story)
        self.ledger_entries.append({
            "timestamp": _utc_now_str(),
            "event": "goal_created",
            "goal_id": gid,
            "title": title,
        })
        return story

    def start_next_goal(self) -> Optional[GoalStory]:
        for g in self.goals:
            if g.status == UltragoalStatus.PENDING:
                g.status = UltragoalStatus.IN_PROGRESS
                self.active_goal_id = g.id
                self.status = UltragoalStatus.IN_PROGRESS
                self.ledger_entries.append({
                    "timestamp": _utc_now_str(),
                    "event": "goal_started",
                    "goal_id": g.id,
                })
                return g
        return None

    def checkpoint_goal(
        self, goal_id: str, status: UltragoalStatus, evidence: str, quality_gate: Optional[Dict[str, Any]] = None
    ) -> bool:
        story = next((g for g in self.goals if g.id == goal_id), None)
        if not story:
            return False

        story.status = status
        story.evidence.append(evidence)
        self.ledger_entries.append({
            "timestamp": _utc_now_str(),
            "event": "goal_checkpoint",
            "goal_id": goal_id,
            "status": status.value,
            "evidence": evidence,
            "quality_gate": quality_gate or {},
        })

        if all(g.status == UltragoalStatus.COMPLETE for g in self.goals):
            self.status = UltragoalStatus.COMPLETE
            self.active_goal_id = None
        elif any(g.status == UltragoalStatus.FAILED for g in self.goals):
            self.status = UltragoalStatus.FAILED
        elif any(g.status == UltragoalStatus.REVIEW_BLOCKED for g in self.goals):
            self.status = UltragoalStatus.REVIEW_BLOCKED

        return True

    def steer(
        self,
        kind: UltragoalSteeringMutationKind,
        evidence: str,
        rationale: str,
        target_goal_id: Optional[str] = None,
        title: Optional[str] = None,
        objective: Optional[str] = None,
        child_goals: Optional[List[Dict[str, str]]] = None,
        new_order: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Evidence-backed mutation of durable plan invariants."""
        if not evidence.strip() or not rationale.strip():
            return {
                "accepted": False,
                "rejected_reasons": ["Steering mutation requires non-empty evidence and rationale"],
            }

        if kind == UltragoalSteeringMutationKind.ADD_SUBGOAL:
            if not title or not objective:
                return {"accepted": False, "rejected_reasons": ["Missing title or objective for add_subgoal"]}
            story = self.add_goal(title, objective)
            return {"accepted": True, "goal_id": story.id}

        elif kind == UltragoalSteeringMutationKind.SPLIT_SUBGOAL:
            if not target_goal_id or not child_goals:
                return {"accepted": False, "rejected_reasons": ["target_goal_id and child_goals required"]}
            target = next((g for g in self.goals if g.id == target_goal_id), None)
            if not target or target.status != UltragoalStatus.PENDING:
                return {"accepted": False, "rejected_reasons": ["Only pending goals can be split"]}
            idx = self.goals.index(target)
            self.goals.pop(idx)
            new_stories = []
            for i, cg in enumerate(child_goals):
                nid = f"{target_goal_id}.{i + 1}"
                ns = GoalStory(id=nid, title=cg["title"], objective=cg["objective"])
                self.goals.insert(idx + i, ns)
                new_stories.append(ns)
            return {"accepted": True, "split_into": [s.id for s in new_stories]}

        elif kind == UltragoalSteeringMutationKind.REORDER_PENDING:
            if not new_order:
                return {"accepted": False, "rejected_reasons": ["new_order list required"]}
            pending_ids = {g.id for g in self.goals if g.status == UltragoalStatus.PENDING}
            if set(new_order) != pending_ids:
                return {"accepted": False, "rejected_reasons": ["new_order must match exact pending goal set"]}
            sorted_pending = sorted([g for g in self.goals if g.status == UltragoalStatus.PENDING], key=lambda g: new_order.index(g.id))
            non_pending = [g for g in self.goals if g.status != UltragoalStatus.PENDING]
            self.goals = non_pending + sorted_pending
            return {"accepted": True, "new_order": new_order}

        elif kind == UltragoalSteeringMutationKind.MARK_BLOCKED_SUPERSEDED:
            if not target_goal_id:
                return {"accepted": False, "rejected_reasons": ["target_goal_id required"]}
            target = next((g for g in self.goals if g.id == target_goal_id), None)
            if not target:
                return {"accepted": False, "rejected_reasons": ["Goal not found"]}
            target.status = UltragoalStatus.COMPLETE
            target.blockers.append(f"Superseded: {rationale}")
            return {"accepted": True, "goal_id": target_goal_id, "status": "superseded"}

        elif kind == UltragoalSteeringMutationKind.ANNOTATE_LEDGER:
            self.ledger_entries.append({
                "timestamp": _utc_now_str(),
                "event": "steering_annotation",
                "evidence": evidence,
                "rationale": rationale,
            })
            return {"accepted": True}

        return {"accepted": False, "rejected_reasons": [f"Unsupported mutation kind: {kind}"]}


# ============================================================================
# 4. Team Coordination State Machine ($team)
# ============================================================================

class TeamTaskStatus(str, Enum):
    PENDING = "pending"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TeamWorker:
    name: str
    role: str
    model_class: str = "standard"
    status: str = "idle"
    claimed_task_id: Optional[str] = None


@dataclass
class TeamTask:
    id: str
    title: str
    assigned_worker: Optional[str] = None
    status: TeamTaskStatus = TeamTaskStatus.PENDING
    claim_token: Optional[str] = None
    result_evidence: Optional[str] = None


@dataclass
class TeamMessage:
    from_worker: str
    to_worker: str
    body: str
    timestamp: str = field(default_factory=_utc_now_str)


@dataclass
class TeamStateMachine:
    name: str
    leader_role: str = "sir_boris"
    workers: Dict[str, TeamWorker] = field(default_factory=dict)
    tasks: Dict[str, TeamTask] = field(default_factory=dict)
    mailboxes: Dict[str, List[TeamMessage]] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    active: bool = True

    def register_worker(self, name: str, role: str, model_class: str = "standard") -> TeamWorker:
        w = TeamWorker(name=name, role=role, model_class=model_class)
        self.workers[name] = w
        self.mailboxes[name] = []
        return w

    def add_task(self, task_id: str, title: str, assigned_worker: Optional[str] = None) -> TeamTask:
        t = TeamTask(id=task_id, title=title, assigned_worker=assigned_worker)
        self.tasks[task_id] = t
        return t

    def send_message(self, from_worker: str, to_worker: str, body: str) -> TeamMessage:
        msg = TeamMessage(from_worker=from_worker, to_worker=to_worker, body=body)
        if to_worker not in self.mailboxes:
            self.mailboxes[to_worker] = []
        self.mailboxes[to_worker].append(msg)
        self.events.append({
            "timestamp": _utc_now_str(),
            "event": "message_delivered",
            "from": from_worker,
            "to": to_worker,
        })
        return msg

    def claim_task(self, worker_name: str, task_id: str) -> Tuple[bool, Optional[str]]:
        if worker_name not in self.workers or task_id not in self.tasks:
            return False, "Invalid worker or task"
        task = self.tasks[task_id]
        if task.status != TeamTaskStatus.PENDING:
            return False, f"Task {task_id} is not pending (current: {task.status.value})"
        
        worker = self.workers[worker_name]
        token = hashlib.sha256(f"{worker_name}:{task_id}:{_utc_now_str()}".encode("utf-8")).hexdigest()[:16]
        task.status = TeamTaskStatus.IN_PROGRESS
        task.assigned_worker = worker_name
        task.claim_token = token
        worker.status = "working"
        worker.claimed_task_id = task_id
        return True, token

    def complete_task(self, task_id: str, claim_token: str, evidence: str) -> Tuple[bool, str]:
        if task_id not in self.tasks:
            return False, "Task not found"
        task = self.tasks[task_id]
        if task.claim_token != claim_token:
            return False, "Invalid claim token"
        task.status = TeamTaskStatus.COMPLETED
        task.result_evidence = evidence
        if task.assigned_worker and task.assigned_worker in self.workers:
            w = self.workers[task.assigned_worker]
            w.status = "idle"
            w.claimed_task_id = None
        self.events.append({
            "timestamp": _utc_now_str(),
            "event": "task_completed",
            "task_id": task_id,
            "evidence": evidence,
        })
        return True, "Task marked completed"

    def shutdown(self) -> Dict[str, Any]:
        self.active = False
        completed = sum(1 for t in self.tasks.values() if t.status == TeamTaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TeamTaskStatus.FAILED)
        pending = sum(1 for t in self.tasks.values() if t.status == TeamTaskStatus.PENDING)
        return {
            "active": False,
            "tasks_completed": completed,
            "tasks_failed": failed,
            "tasks_pending": pending,
            "clean": pending == 0 and failed == 0,
        }


# ============================================================================
# 5. Code Review State Machine ($code-review)
# ============================================================================

class ReviewVerdict(str, Enum):
    APPROVE = "APPROVE"
    COMMENT = "COMMENT"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class ArchitectStatus(str, Enum):
    CLEAR = "CLEAR"
    WATCH = "WATCH"
    BLOCK = "BLOCK"


@dataclass
class CodeReviewLaneResult:
    lane: str  # code-reviewer | architect
    status: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    evidence: str = ""
    available: bool = True


@dataclass
class CodeReviewSynthesis:
    reviewer_result: Optional[CodeReviewLaneResult] = None
    architect_result: Optional[CodeReviewLaneResult] = None
    final_verdict: ReviewVerdict = ReviewVerdict.REQUEST_CHANGES
    rationale: str = ""
    is_merge_ready: bool = False

    @classmethod
    def synthesize(
        cls,
        reviewer_result: Optional[CodeReviewLaneResult],
        architect_result: Optional[CodeReviewLaneResult],
    ) -> CodeReviewSynthesis:
        if not reviewer_result or not reviewer_result.available or not architect_result or not architect_result.available:
            return cls(
                reviewer_result=reviewer_result,
                architect_result=architect_result,
                final_verdict=ReviewVerdict.REQUEST_CHANGES,
                rationale="Independent review unavailable: both code-reviewer and architect lanes must return evidence.",
                is_merge_ready=False,
            )

        arch_status = architect_result.status.upper()
        rev_verdict = reviewer_result.status.upper()

        if arch_status == ArchitectStatus.BLOCK.value:
            return cls(
                reviewer_result=reviewer_result,
                architect_result=architect_result,
                final_verdict=ReviewVerdict.REQUEST_CHANGES,
                rationale=f"Architect lane status is BLOCK: {architect_result.evidence}",
                is_merge_ready=False,
            )

        if rev_verdict == ReviewVerdict.REQUEST_CHANGES.value:
            return cls(
                reviewer_result=reviewer_result,
                architect_result=architect_result,
                final_verdict=ReviewVerdict.REQUEST_CHANGES,
                rationale=f"Code-reviewer lane requested changes: {reviewer_result.evidence}",
                is_merge_ready=False,
            )

        if arch_status == ArchitectStatus.WATCH.value:
            return cls(
                reviewer_result=reviewer_result,
                architect_result=architect_result,
                final_verdict=ReviewVerdict.COMMENT,
                rationale=f"Architect lane flagged WATCH notes: {architect_result.evidence}",
                is_merge_ready=False,
            )

        if rev_verdict == ReviewVerdict.APPROVE.value and arch_status == ArchitectStatus.CLEAR.value:
            return cls(
                reviewer_result=reviewer_result,
                architect_result=architect_result,
                final_verdict=ReviewVerdict.APPROVE,
                rationale="Both independent lanes verified: code-reviewer approved and architect status is CLEAR.",
                is_merge_ready=True,
            )

        return cls(
            reviewer_result=reviewer_result,
            architect_result=architect_result,
            final_verdict=ReviewVerdict.COMMENT,
            rationale=f"Review completed with notes (reviewer: {rev_verdict}, architect: {arch_status})",
            is_merge_ready=False,
        )


# ============================================================================
# 6. UltraQA State Machine ($ultraqa)
# ============================================================================

class UltraQAPhase(str, Enum):
    PLANNING = "planning"
    BASELINE = "baseline"
    ADVERSARIAL_E2E = "adversarial-e2e"
    DIAGNOSE = "diagnose"
    FIX = "fix"
    CLEANUP = "cleanup"
    COMPLETE = "complete"
    STOPPED = "stopped"
    BLOCKED = "blocked"


@dataclass
class QAScenario:
    id: str
    scenario_class: str  # malformed_input | repeated_interruptions | prompt_injection | stale_state | dirty_worktree | hung_command | flaky_tests | misleading_output
    intent: str
    command: str
    expected_signal: str
    actual_result: Optional[str] = None
    passed: bool = False
    evidence: str = ""


@dataclass
class UltraQAStateMachine:
    goal: str
    current_phase: UltraQAPhase = UltraQAPhase.PLANNING
    iteration: int = 1
    max_iterations: int = 5
    scenarios: List[QAScenario] = field(default_factory=list)
    failure_history: List[str] = field(default_factory=list)
    residual_risks: List[str] = field(default_factory=list)
    active: bool = True

    def add_scenario(self, scenario_id: str, scenario_class: str, intent: str, command: str, expected_signal: str) -> QAScenario:
        sc = QAScenario(id=scenario_id, scenario_class=scenario_class, intent=intent, command=command, expected_signal=expected_signal)
        self.scenarios.append(sc)
        return sc

    def record_scenario_result(self, scenario_id: str, passed: bool, actual_result: str, evidence: str) -> bool:
        sc = next((s for s in self.scenarios if s.id == scenario_id), None)
        if not sc:
            return False
        sc.passed = passed
        sc.actual_result = actual_result
        sc.evidence = evidence
        if not passed:
            self.failure_history.append(f"[{sc.scenario_class}] {actual_result}")
        return True

    def evaluate_cycle(self) -> UltraQAPhase:
        if all(s.passed for s in self.scenarios) and self.scenarios:
            self.current_phase = UltraQAPhase.CLEANUP
            return self.current_phase

        # Check repeated failure stopping condition
        if len(self.failure_history) >= 3:
            recent_3 = self.failure_history[-3:]
            if recent_3[0] == recent_3[1] == recent_3[2]:
                self.current_phase = UltraQAPhase.STOPPED
                self.active = False
                return self.current_phase

        if self.iteration >= self.max_iterations:
            self.current_phase = UltraQAPhase.STOPPED
            self.residual_risks.append("Reached maximum QA cycle iterations (5) with unresolved failures")
            self.active = False
            return self.current_phase

        self.current_phase = UltraQAPhase.DIAGNOSE
        return self.current_phase

    def apply_fix_and_next_cycle(self) -> UltraQAPhase:
        self.iteration += 1
        self.current_phase = UltraQAPhase.BASELINE
        return self.current_phase

    def complete_and_cleanup(self) -> Dict[str, Any]:
        self.current_phase = UltraQAPhase.COMPLETE
        self.active = False
        return {
            "status": "ULTRAQA COMPLETE",
            "iterations": self.iteration,
            "scenarios_passed": sum(1 for s in self.scenarios if s.passed),
            "total_scenarios": len(self.scenarios),
            "residual_risks": self.residual_risks,
        }


# ============================================================================
# 7. Autopilot Master Supervisor FSM ($autopilot)
# ============================================================================

class AutopilotPhase(str, Enum):
    DEEP_INTERVIEW = "deep-interview"
    RALPLAN = "ralplan"
    ULTRAGOAL = "ultragoal"
    REWORK = "rework"
    TEAM = "team"
    RALPH = "ralph"
    CODE_REVIEW = "code-review"
    ULTRAQA = "ultraqa"
    WAITING_FOR_USER = "waiting-for-user"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class AutopilotStateMachine:
    directive: str
    current_phase: AutopilotPhase = AutopilotPhase.DEEP_INTERVIEW
    previous_phase: Optional[AutopilotPhase] = None
    handoff_artifacts: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

    def transition(self, to_phase: AutopilotPhase, artifacts: Optional[Dict[str, Any]] = None) -> AutopilotPhase:
        if artifacts:
            self.handoff_artifacts.update(artifacts)
        self.previous_phase = self.current_phase
        self.current_phase = to_phase
        if to_phase in (AutopilotPhase.COMPLETE, AutopilotPhase.FAILED):
            self.active = False
        return self.current_phase

    def pause_for_user(self, question: str) -> AutopilotPhase:
        self.handoff_artifacts["pending_user_question"] = question
        self.previous_phase = self.current_phase
        self.current_phase = AutopilotPhase.WAITING_FOR_USER
        return self.current_phase

    def resume_from_user(self, answer: str) -> AutopilotPhase:
        self.handoff_artifacts["last_user_answer"] = answer
        next_phase = self.previous_phase or AutopilotPhase.RALPLAN
        self.current_phase = next_phase
        return self.current_phase
