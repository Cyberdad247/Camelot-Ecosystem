# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
LIGHTRAG_RETRIEVE RUNE PHASE
Camelot OS v33.0 - Knowledge Retrieval Phase
==============================================================================
Position: AFTER Anya_Translate, BEFORE Knight_Execution
Symbol: {📚}
==============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    pass


# ==============================================================================
# CONFIGURATION
# ==============================================================================

PHASE_NAME = "LightRAG_Retrieve"
PHASE_SYMBOL = "📚"
PHASE_POSITION = "AFTER_Anya_Translate"


# ==============================================================================
# RESULT TYPE
# ==============================================================================


@dataclass
class RetrievalResult:
    """Result of the LightRAG_Retrieve phase."""

    query: str
    context_found: bool
    context_text: str
    sources: list[dict]
    latency_ms: float
    total_results: int


# ==============================================================================
# MAIN PHASE IMPLEMENTATION
# ==============================================================================


async def lightrag_retrieve(
    query: str,
    top_k: int = 5,
    persona_id: Optional[str] = None,
) -> RetrievalResult:
    """
    Execute the LightRAG_Retrieve rune phase.

    WORKFLOW:
    1. Send query to LightRAG engine
    2. Retrieve top-k relevant documents
    3. Format results as context for Knight_Execution

    Args:
        query: User's query or translated prompt
        top_k: Number of results to retrieve
        persona_id: Optional persona filter

    Returns:
        RetrievalResult with context and sources
    """
    try:
        from kernel.rag.lightrag_engine import get_lightrag_engine
    except ImportError:
        # LightRAG not available, return empty result
        return RetrievalResult(
            query=query,
            context_found=False,
            context_text="",
            sources=[],
            latency_ms=0,
            total_results=0,
        )

    engine = get_lightrag_engine()

    # Build filter if persona_id provided
    filter_metadata = None
    if persona_id:
        filter_metadata = {"persona_id": persona_id}

    # Query LightRAG
    try:
        response = engine.query(query, top_k=top_k, filter_metadata=filter_metadata)
    except Exception as e:
        print(f"[LIGHTRAG] Query error: {e}")
        return RetrievalResult(
            query=query,
            context_found=False,
            context_text=f"Error: {e}",
            sources=[],
            latency_ms=0,
            total_results=0,
        )

    if not response.results:
        return RetrievalResult(
            query=query,
            context_found=False,
            context_text="",
            sources=[],
            latency_ms=response.latency_ms,
            total_results=0,
        )

    # Format context from results
    context_parts = ["## Relevant Knowledge from EXP Ledger:\n"]
    sources = []

    for i, result in enumerate(response.results, 1):
        context_parts.append(f"### Source {i} (Score: {result.score:.2f})")
        context_parts.append(f"{result.content}\n")

        sources.append(
            {
                "id": result.doc_id,
                "score": result.score,
                "type": result.metadata.get("complication_type", "unknown"),
                "preview": result.content[:100] + "..." if len(result.content) > 100 else result.content,
            }
        )

    context_text = "\n".join(context_parts)

    return RetrievalResult(
        query=query,
        context_found=True,
        context_text=context_text,
        sources=sources,
        latency_ms=response.latency_ms,
        total_results=len(response.results),
    )


def lightrag_retrieve_sync(
    query: str,
    top_k: int = 5,
    persona_id: Optional[str] = None,
) -> RetrievalResult:
    """Synchronous version of lightrag_retrieve."""
    import asyncio

    return asyncio.get_event_loop().run_until_complete(lightrag_retrieve(query, top_k, persona_id))


# ==============================================================================
# CONTEXT FUSION
# ==============================================================================


def fuse_context_with_prompt(
    original_prompt: str,
    retrieval_result: RetrievalResult,
) -> str:
    """
    Fuse retrieved context with the original prompt.

    Args:
        original_prompt: The user's prompt
        retrieval_result: Result from lightrag_retrieve

    Returns:
        Augmented prompt with context
    """
    if not retrieval_result.context_found:
        return original_prompt

    augmented = f"""
## Relevant Context:
{retrieval_result.context_text}

## User Query:
{original_prompt}

## Instructions:
Use the relevant context above to inform your response. If the context contains
a solution to a similar problem, adapt and apply it. Always cite which source
you used if applicable.
"""
    return augmented.strip()


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    import asyncio

    async def test():
        print("[TEST] LightRAG_Retrieve Phase")
        print("=" * 60)

        # Test retrieval
        result = await lightrag_retrieve(
            query="How to fix Python import error?",
            top_k=3,
        )

        print(f"[1] Query: {result.query}")
        print(f"    Context found: {result.context_found}")
        print(f"    Results: {result.total_results}")
        print(f"    Latency: {result.latency_ms}ms")

        if result.sources:
            print(f"    Top source: {result.sources[0]}")

        # Test context fusion
        augmented = fuse_context_with_prompt("Fix my Python code", result)
        print(f"\n[2] Augmented prompt length: {len(augmented)} chars")

        print("=" * 60)
        print("[DONE] LightRAG_Retrieve phase test complete.")

    asyncio.run(test())