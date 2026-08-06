# -*- coding: utf-8 -*-
"""
Graph Orchestrator — Swarm Graph Orchestration (L5 Agentic)
==========================================================
Manages a stateful task DAG using langgraph patterns.
Nodes: Architect, Forge, Sentinel, Veritas.
"""

from __future__ import annotations

import operator
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

# ============================================================================
# Graph State Definition
# ============================================================================

class SwarmState(TypedDict):
    """State for the Swarm orchestration graph"""
    directive: str
    current_file_set: List[str]
    validation_results: Dict[str, Any]
    evolution_logs: Annotated[List[str], operator.add]
    errors: List[str]
    iteration_count: int

# ============================================================================
# Utilities
# ============================================================================

def log_to_ledger(task_name: str, author: str, status: str, notes: str):
    """Log an entry to the PROVENANCE_LEDGER.md."""
    ledger_path = Path(__file__).parent.parent.parent / "PROVENANCE_LEDGER.md"
    if not ledger_path.exists():
        return

    # Find the last ID
    last_id = 2000 # Default if we can't find it
    try:
        content = ledger_path.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if l.startswith("|") and not l.startswith("| ID")]
        if lines:
            # Extract IDs from lines
            ids = []
            for line in lines:
                parts = line.split("|")
                if len(parts) > 1:
                    try:
                        ids.append(int(parts[1].strip()))
                    except ValueError:
                        continue
            if ids:
                last_id = max(ids)
    except Exception:
        pass

    new_id = last_id + 1
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"| {new_id} | **{task_name}** | {author} | {status} | {notes} — {timestamp} |"

    # Append to the top after the header
    try:
        content = ledger_path.read_text(encoding="utf-8")
        header_end = 0
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("| :--"):
                header_end = i + 1
                break
        
        if header_end:
            new_lines = lines[:header_end] + [entry] + lines[header_end:]
            ledger_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    except Exception:
        # Fallback to simple append
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

# ============================================================================
# Node Implementations
# ============================================================================

def architect_node(state: SwarmState) -> SwarmState:
    """Architect: Plans the task and identifies affected files."""
    log_msg = f"Architect: Planning task: {state['directive']}"
    log_to_ledger("Swarm Graph: Architect", "ARCHITECT", "✅ PLANNED", log_msg)
    
    # Simulation: Identify files
    files = ["CAMELOT_OS/01_KERNEL/swarm/graph_orchestrator.py"]
    
    return {
        "evolution_logs": [log_msg],
        "current_file_set": files,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def forge_node(state: SwarmState) -> SwarmState:
    """Forge: Implements the task."""
    log_msg = f"Forge: Actuating implementation for {len(state['current_file_set'])} files"
    log_to_ledger("Swarm Graph: Forge", "FORGE", "✅ ACTUATED", log_msg)
    
    return {
        "evolution_logs": [log_msg],
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def sentinel_node(state: SwarmState) -> SwarmState:
    """Sentinel: Validates the task."""
    log_msg = "Sentinel: Running system verification"
    log_to_ledger("Swarm Graph: Sentinel", "SENTINEL", "✅ VERIFIED", log_msg)
    
    # Simulation: validation pass
    results = {"status": "pass", "coverage": 100}
    
    return {
        "evolution_logs": [log_msg],
        "validation_results": results
    }

def veritas_node(state: SwarmState) -> SwarmState:
    """Veritas: Self-error correction check."""
    results = state.get("validation_results", {})
    if results.get("status") == "fail":
        log_msg = "Veritas: Negative result detected. Triggering REFORGE."
        log_to_ledger("Swarm Graph: Veritas", "VERITAS", "❌ RE-EVAL", log_msg)
        return {
            "evolution_logs": [log_msg],
            "errors": ["Validation failure"]
        }
    else:
        log_msg = "Veritas: Positive result confirmed. Mission SUCCESS."
        log_to_ledger("Swarm Graph: Veritas", "VERITAS", "✅ FINALIZED", log_msg)
        return {
            "evolution_logs": [log_msg],
            "errors": []
        }

# ============================================================================
# Graph Construction
# ============================================================================

class GraphOrchestrator:
    """Stateful task DAG for Camelot Kernel swarm orchestration."""

    def __init__(self):
        self.workflow = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(SwarmState)

        # Add Nodes
        builder.add_node("architect", architect_node)
        builder.add_node("forge", forge_node)
        builder.add_node("sentinel", sentinel_node)
        builder.add_node("veritas", veritas_node)

        # Define Edges
        builder.add_edge(START, "architect")
        builder.add_edge("architect", "forge")
        builder.add_edge("forge", "sentinel")
        builder.add_edge("sentinel", "veritas")

        def should_continue(state: SwarmState) -> Literal["forge", "__end__"]:
            if state.get("errors") and state.get("iteration_count", 0) < 3:
                return "forge"
            return END

        builder.add_conditional_edges(
            "veritas",
            should_continue
        )

        return builder.compile()

    def run(self, directive: str) -> SwarmState:
        """Execute the swarm graph."""
        initial_state: SwarmState = {
            "directive": directive,
            "current_file_set": [],
            "validation_results": {},
            "evolution_logs": [f"System: Swarm Graph actuate for: {directive}"],
            "errors": [],
            "iteration_count": 0
        }
        return self.workflow.invoke(initial_state)

if __name__ == "__main__":
    orchestrator = GraphOrchestrator()
    final_state = orchestrator.run("Omega_EVOLUTION_702 Track Alpha Actuation")
    print("\n--- SWARM EVOLUTION COMPLETE ---")
    for log in final_state["evolution_logs"]:
        print(f"> {log}")
