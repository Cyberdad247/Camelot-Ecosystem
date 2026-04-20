# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Canonical Pattern: AtomicAgent → LangGraph Node → Camelot Tool Contract
Demonstrates the 3-layer integration architecture.

Uses Cyberdad247 forks:
- atomic-agents: Schema-first agent primitives
- langgraph: Stateful orchestration graphs
"""

from typing import TypedDict

from atomic_agents.lib.base.base_agent import BaseAgent, BaseAgentConfig
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from langgraph.graph import END, StateGraph
from pydantic import Field

# ============================================================================
# LAYER 1: Define the Atomic Agent (Schema-First)
# ============================================================================


class ResearchInput(BaseIOSchema):
    """Input schema for the research agent"""

    query: str = Field(..., description="The research query to investigate")
    max_results: int = Field(default=5, description="Maximum number of results")


class ResearchOutput(BaseIOSchema):
    """Output schema for the research agent"""

    findings: list[str] = Field(..., description="List of research findings")
    confidence: float = Field(..., description="Confidence score 0-1")


class ResearchAgentConfig(BaseAgentConfig):
    """Configuration for the research agent"""

    model: str = "gpt-4"
    temperature: float = 0.7


class ResearchAgent(BaseAgent):
    """
    Atomic Agent for deep research tasks.
    Provider-agnostic, schema-enforced, composable.
    """

    input_schema = ResearchInput
    output_schema = ResearchOutput

    def run(self, input_data: ResearchInput) -> ResearchOutput:
        """Execute the research task"""
        # Placeholder: Would call LLM via Instructor/Pydantic
        findings = [f"Finding 1 for: {input_data.query}", f"Finding 2 for: {input_data.query}"]
        return ResearchOutput(findings=findings, confidence=0.85)


# ============================================================================
# LAYER 2: Wrap as LangGraph Node
# ============================================================================


class CamelotState(TypedDict):
    """State for the Camelot orchestration graph"""

    query: str
    research_findings: list[str]
    confidence: float


def research_node(state: CamelotState) -> CamelotState:
    """
    LangGraph node that wraps the ResearchAgent.
    This is the bridge between Atomic Agents and Camelot orchestration.
    """
    agent = ResearchAgent(ResearchAgentConfig())

    # Convert LangGraph state to Atomic Agent input
    agent_input = ResearchInput(query=state["query"], max_results=5)

    # Execute the atomic agent
    result = agent.run(agent_input)

    # Convert Atomic Agent output back to LangGraph state
    state["research_findings"] = result.findings
    state["confidence"] = result.confidence

    return state


# ============================================================================
# LAYER 3: Integrate into Camelot OS Graph
# ============================================================================


def build_research_workflow() -> StateGraph:
    """
    Build a Camelot OS workflow using the canonical pattern.
    AtomicAgent → LangGraph Node → Camelot Tool Contract
    """
    workflow = StateGraph(CamelotState)

    # Add the atomic agent as a node
    workflow.add_node("research", research_node)

    # Define the graph structure
    workflow.set_entry_point("research")
    workflow.add_edge("research", END)

    return workflow.compile()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Build the workflow
    graph = build_research_workflow()

    # Execute with initial state
    result = graph.invoke(
        {"query": "What are the latest trends in AI agent frameworks?", "research_findings": [], "confidence": 0.0}
    )

    print("=" * 60)
    print("CAMELOT OS - ATOMIC AGENT INTEGRATION")
    print("=" * 60)
    print(f"Query: {result['query']}")
    print(f"Findings: {result['research_findings']}")
    print(f"Confidence: {result['confidence']}")