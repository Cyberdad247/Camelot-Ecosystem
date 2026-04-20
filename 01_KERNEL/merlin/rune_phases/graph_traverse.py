# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
GRAPH_TRAVERSE RUNE PHASE
Camelot OS v33.0 - The Graph Sovereign
==============================================================================
Position: AFTER Extract, BEFORE Merlin
Symbol: {🕸️}

The Graph Walk:
1. Find the nodes (entities)
2. Find the edges (relations)
3. Feed the Sub-Graph to Merlin
==============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# ==============================================================================
# CONFIGURATION
# ==============================================================================

PHASE_NAME = "GRAPH_TRAVERSE"
PHASE_SYMBOL = "🕸️"
PHASE_POSITION = "AFTER_Extract"


# ==============================================================================
# RESULT TYPES
# ==============================================================================


@dataclass
class GraphTraverseResult:
    """Result of the GRAPH_TRAVERSE phase."""

    query: str
    context_found: bool
    context_text: str
    triplets: list[str]  # Human-readable triplets
    entities_count: int
    relations_count: int
    latency_ms: float
    mode: str


# ==============================================================================
# MAIN PHASE IMPLEMENTATION
# ==============================================================================


async def graph_traverse(
    query: str,
    mode: str = "hybrid",
    hops: int = 2,
) -> GraphTraverseResult:
    """
    Execute the GRAPH_TRAVERSE rune phase.

    THE GRAPH WALK:
    1. Send query to Knowledge Graph Engine
    2. Find matching entities (nodes)
    3. Get neighboring entities via relations (edges)
    4. Build a SubGraph for context
    5. Format as chain-of-thought context for Merlin

    Args:
        query: User's query or extracted intent
        mode: Query mode ("local", "global", "hybrid", "naive")
        hops: Number of hops for neighborhood traversal

    Returns:
        GraphTraverseResult with context and triplets
    """
    try:
        from kernel.graph.knowledge_graph import get_graph_engine
    except ImportError:
        return GraphTraverseResult(
            query=query,
            context_found=False,
            context_text="",
            triplets=[],
            entities_count=0,
            relations_count=0,
            latency_ms=0,
            mode=mode,
        )

    engine = get_graph_engine()

    # Execute graph query
    result = engine.query(query, mode=mode, hops=hops)

    if not result.subgraph.entities:
        return GraphTraverseResult(
            query=query,
            context_found=False,
            context_text="",
            triplets=[],
            entities_count=0,
            relations_count=0,
            latency_ms=result.latency_ms,
            mode=mode,
        )

    # Build context from subgraph
    context_text = result.subgraph.to_context()
    triplets = [str(t) for t in result.subgraph.to_triplets()]

    return GraphTraverseResult(
        query=query,
        context_found=True,
        context_text=context_text,
        triplets=triplets,
        entities_count=len(result.subgraph.entities),
        relations_count=len(result.subgraph.relations),
        latency_ms=result.latency_ms,
        mode=mode,
    )


def graph_traverse_sync(
    query: str,
    mode: str = "hybrid",
    hops: int = 2,
) -> GraphTraverseResult:
    """Synchronous version of graph_traverse."""
    import asyncio

    return asyncio.get_event_loop().run_until_complete(graph_traverse(query, mode, hops))


# ==============================================================================
# CONTEXT FUSION FOR MERLIN
# ==============================================================================


def fuse_graph_context_with_prompt(
    original_prompt: str,
    traverse_result: GraphTraverseResult,
) -> str:
    """
    Fuse graph context with the original prompt for Merlin.

    Merlin doesn't read text anymore. He reads relationships.

    Args:
        original_prompt: The user's prompt
        traverse_result: Result from graph_traverse

    Returns:
        Augmented prompt with graph context
    """
    if not traverse_result.context_found:
        return original_prompt

    # Build triplet chain
    triplet_chain = "\n".join(f"  • {t}" for t in traverse_result.triplets[:10])

    augmented = f"""
## 🕸️ KNOWLEDGE GRAPH CONTEXT

### Chain of Thought (Triplets):
{triplet_chain}

### Full Context:
{traverse_result.context_text}

---

## 👤 USER QUERY:
{original_prompt}

---

## 🧠 MERLIN INSTRUCTIONS:
You have been provided with a knowledge graph subgraph.
Use the triplets above to trace the chain of causality.
Your answer should:
1. Reference specific entities from the graph
2. Explain relationships between entities
3. Ground your reasoning in the graph structure

**Never hallucinate. If it's not in the graph, say "unknown".**
"""
    return augmented.strip()


# ==============================================================================
# CYPHER-LIKE QUERY BUILDER
# ==============================================================================


def build_cypher_query(query: str) -> str:
    """
    Translate natural language to Cypher-like query (for logging/debugging).

    Example:
        "Why did Auth fail?" -> "MATCH (n:Error {type:'Auth'}) RETURN n, [n]-[r]->(m)"
    """
    # This is simplified - a real implementation would use NLP
    words = query.lower().split()

    # Detect patterns
    if any(w in words for w in ["why", "how", "what caused"]):
        # Causality query
        return f"MATCH (n)-[:caused_by|:linked_to*1..3]->(m) WHERE n.name CONTAINS '{words[-1]}' RETURN n, m"

    if any(w in words for w in ["connected", "related", "linked"]):
        # Relationship query
        return f"MATCH (n)-[r]-(m) WHERE n.name CONTAINS '{words[-1]}' RETURN n, r, m"

    # Default: entity search
    return f"MATCH (n) WHERE n.name CONTAINS '{words[-1]}' RETURN n"


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    import asyncio

    async def test():
        print("[TEST] GRAPH_TRAVERSE Phase")
        print("=" * 60)

        # Test graph traverse
        result = await graph_traverse(
            query="How to fix import error?",
            mode="hybrid",
            hops=2,
        )

        print(f"[1] Query: {result.query}")
        print(f"    Context found: {result.context_found}")
        print(f"    Entities: {result.entities_count}")
        print(f"    Relations: {result.relations_count}")
        print(f"    Latency: {result.latency_ms}ms")

        if result.triplets:
            print(f"    Sample triplet: {result.triplets[0]}")

        # Test Cypher builder
        cypher = build_cypher_query("Why did Auth fail?")
        print(f"\n[2] Cypher: {cypher}")

        # Test context fusion
        augmented = fuse_graph_context_with_prompt("Fix my authentication", result)
        print(f"\n[3] Augmented prompt length: {len(augmented)} chars")

        print("=" * 60)
        print("[DONE] GRAPH_TRAVERSE phase test complete.")

    asyncio.run(test())