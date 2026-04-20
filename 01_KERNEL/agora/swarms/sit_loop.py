# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
S.I.T. Loop: Sense-Integrate-Triage
The core LangGraph implementation of Anya's Triple-QFT Compiler.

Uses Cyberdad247/langgraph fork for enhanced durable execution and HITL support.
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph


class SITState(TypedDict):
    """State for the Sense-Integrate-Triage Loop"""

    raw_input: str
    renormalized_intent: str
    framework: str
    ambiguity_score: int
    compiled_prompt: str
    messages: Annotated[list, operator.add]


def sense_node(state: SITState) -> SITState:
    """SENSE: Renormalization (Physics Layer)"""
    import sys

    sys.path.append("../memory")
    from compiler import AnyaCompiler

    compiler = AnyaCompiler()
    state["renormalized_intent"] = compiler.renormalization_flow(state["raw_input"])
    state["messages"].append(f"[SENSE] Renormalized: {state['renormalized_intent']}")
    return state


def integrate_node(state: SITState) -> SITState:
    """INTEGRATE: Framework Matching (Engineering Layer)"""
    import sys

    sys.path.append("../memory")
    from compiler import AnyaCompiler

    compiler = AnyaCompiler()
    framework_data = compiler.framework_matching(state["renormalized_intent"])
    state["framework"] = framework_data["framework"]
    state["messages"].append(f"[INTEGRATE] Framework: {state['framework']}")
    return state


def triage_node(state: SITState) -> SITState:
    """TRIAGE: Pedagogy Check (Ambiguity Detection)"""
    import sys

    sys.path.append("../memory")
    from compiler import AnyaCompiler

    compiler = AnyaCompiler()
    qft = compiler.pedagogy_check(state["renormalized_intent"])
    state["ambiguity_score"] = qft.get("ambiguity_score", 0)
    state["messages"].append(f"[TRIAGE] Ambiguity: {state['ambiguity_score']}%")
    return state


def should_clarify(state: SITState) -> str:
    """Conditional edge: Loop back if ambiguous"""
    return "clarify" if state["ambiguity_score"] > 20 else "execute"


# Build the S.I.T. Loop graph
workflow = StateGraph(SITState)
workflow.add_node("sense", sense_node)
workflow.add_node("integrate", integrate_node)
workflow.add_node("triage", triage_node)

workflow.set_entry_point("sense")
workflow.add_edge("sense", "integrate")
workflow.add_edge("integrate", "triage")
workflow.add_conditional_edges("triage", should_clarify, {"clarify": "sense", "execute": END})  # Reflexion Loop

sit_loop = workflow.compile()

if __name__ == "__main__":
    # Test the loop
    result = sit_loop.invoke(
        {
            "raw_input": "help me fix it",
            "renormalized_intent": "",
            "framework": "",
            "ambiguity_score": 0,
            "compiled_prompt": "",
            "messages": [],
        }
    )
    print(result)