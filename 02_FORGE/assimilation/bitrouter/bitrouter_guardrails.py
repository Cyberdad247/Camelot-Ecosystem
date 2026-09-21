# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — BitRouter Anti-Tokenmaxxing Agent Guardrails
r"""
BitRouter Assimilation Bridge.
Assimilates Cyberdad247/bitrouter into Camelot-OS:
- Context-aware model routing that adapts to agent workflows
- Anti-tokenmaxxing guardrails (stops burning frontier tokens on repetitive loops)
- Dynamic model tightening across agent iterations
- Integration with ACP, MCP, and Knight loops
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("BitRouterGuardrails")

# Anti-Tokenmaxxing Thresholds
MAX_ALLOWED_RETRY_ITERATIONS = 25
MAX_TOKEN_BUDGET_PER_LOOP = 250_000
MAX_COST_BUDGET_USD_PER_LOOP = 1.50


@dataclass
class AgentLoopState:
    loop_id: str
    task_description: str
    calling_knight: str
    iteration: int = 0
    file_reads: int = 0
    tool_calls: int = 0
    subagent_hops: int = 0
    retries: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    recommended_model: str = "frontier"
    circuit_breaker_tripped: bool = False
    rationale: str = "Initial loop step"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "task_description": self.task_description,
            "calling_knight": self.calling_knight,
            "iteration": self.iteration,
            "metrics": {
                "file_reads": self.file_reads,
                "tool_calls": self.tool_calls,
                "subagent_hops": self.subagent_hops,
                "retries": self.retries,
                "total_tokens": self.total_tokens,
                "estimated_cost_usd": round(self.estimated_cost_usd, 4),
            },
            "routing": {
                "recommended_model": self.recommended_model,
                "circuit_breaker_tripped": self.circuit_breaker_tripped,
                "rationale": self.rationale,
            },
        }


class BitRouterEngine:
    """Anti-tokenmaxxing context-aware router engine (from bitrouter)."""

    def __init__(
        self,
        max_iterations: int = MAX_ALLOWED_RETRY_ITERATIONS,
        max_tokens: int = MAX_TOKEN_BUDGET_PER_LOOP,
        max_cost_usd: float = MAX_COST_BUDGET_USD_PER_LOOP,
    ):
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.max_cost_usd = max_cost_usd
        self._active_loops: Dict[str, AgentLoopState] = {}

    def start_or_update_loop(
        self,
        loop_id: str,
        task: str,
        knight_id: str = "SIR_CODEX",
        added_tokens: int = 0,
        added_cost: float = 0.0,
        step_type: str = "tool_call",  # 'file_read', 'tool_call', 'subagent_hop', 'retry'
    ) -> AgentLoopState:
        """Evaluate agent step and dynamically tighten model routing to prevent tokenmaxxing."""
        if loop_id not in self._active_loops:
            self._active_loops[loop_id] = AgentLoopState(
                loop_id=loop_id,
                task_description=task,
                calling_knight=knight_id,
            )

        state = self._active_loops[loop_id]
        state.iteration += 1
        state.total_tokens += added_tokens
        state.estimated_cost_usd += added_cost

        if step_type == "file_read":
            state.file_reads += 1
        elif step_type == "tool_call":
            state.tool_calls += 1
        elif step_type == "subagent_hop":
            state.subagent_hops += 1
        elif step_type == "retry":
            state.retries += 1

        # Evaluate Circuit Breaker
        if (
            state.iteration >= self.max_iterations
            or state.total_tokens >= self.max_tokens
            or state.estimated_cost_usd >= self.max_cost_usd
        ):
            state.circuit_breaker_tripped = True
            state.recommended_model = "circuit_breaker_halt"
            state.rationale = (
                f"BitRouter Circuit Tripped: Exceeded budget (Iterations: {state.iteration}/{self.max_iterations}, "
                f"Tokens: {state.total_tokens}/{self.max_tokens}, Cost: ${state.estimated_cost_usd:.2f}/${self.max_cost_usd:.2f})"
            )
            return state

        # Adaptive Tightening: Stepped Degradation based on loop depth
        if state.iteration <= 3:
            state.recommended_model = "frontier_primary"
            state.rationale = "Early exploration: Frontier accuracy priority"
        elif state.iteration <= 7:
            state.recommended_model = "reasoning_fast"
            state.rationale = "Mid-loop implementation: DeepSeek-R1 / Qwen-72B cost-optimal path"
        elif state.iteration <= 15:
            state.recommended_model = "zero_cost_fast"
            state.rationale = "Extended loop: Downshifted to Cerebras/Groq zero-cost pool (saving credits)"
        else:
            state.recommended_model = "local_air_gap"
            state.rationale = "High-iteration convergence: Anchored strictly to SIR_GHOST (Ollama local)"

        return state

    def evaluate_reflex_step(self, loop_id: str, proposed_action: str) -> Dict[str, Any]:
        """Use TypeSafe Jev System 1 model to reflexively validate action before token expenditure."""
        import importlib
        mod = importlib.import_module("02_FORGE.assimilation.omniroute.typesafe_jev_client")
        get_typesafe_jev_client = mod.get_typesafe_jev_client

        client = get_typesafe_jev_client()
        state = f"Loop: {loop_id} | Proposed Action: {proposed_action}"
        questions = {
            "can_execute_reflexively": {"type": "boolean"},
            "recommended_system": {"type": "choice", "options": ["system1_reflex", "system2_deliberative", "circuit_halt"]},
            "risk_score": {"type": "score", "min": 0, "max": 100},
        }
        res = client.decide(state, questions)
        return {
            "loop_id": loop_id,
            "proposed_action": proposed_action,
            "system1_model": res.model,
            "decisions": res.decisions,
            "latency_ms": res.latency_ms,
            "status": res.status,
        }

    def get_loop(self, loop_id: str) -> Optional[AgentLoopState]:
        return self._active_loops.get(loop_id)

    def list_active_loops(self) -> List[Dict[str, Any]]:
        return [l.to_dict() for l in self._active_loops.values()]


_bitrouter_instance: Optional[BitRouterEngine] = None


def get_bitrouter_engine() -> BitRouterEngine:
    global _bitrouter_instance
    if _bitrouter_instance is None:
        _bitrouter_instance = BitRouterEngine()
    return _bitrouter_instance
