# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite for Context Expansion Protocol

Validates RAG, GoT, caching, and full CEP workflow.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory')))

from titan_omega import TitanOmega
from titan_schemas import GraphNode, GraphNodeProvenance
from rag_backbone import RAGBackbone
from got_expander import GoTExpander
from cache_manager import CacheManager
from expansion_engine import ExpansionEngine


def test_rag_backbone():
    """Test hybrid RAG retrieval."""
    print("\n=== Testing RAG Backbone ===")
    
    titan = TitanOmega()
    rag = RAGBackbone(titan)
    
    # Add test data to Ω-Graph
    agent_node = GraphNode(
        node_id="agent_sir_lukas",
        type="Agent",
        attributes={
            "name": "Sir Lukas",
            "role": "Engineer",
            "skills": ["Python", "FastAPI", "backend"]
        },
        edges=[],
        provenance=GraphNodeProvenance(created_by="test_suite", hash=""),
        trust_score=0.95
    )
    titan.commit(agent_node, signed_by="test_suite")
    
    # Add text to Ω-Vault
    if titan.vault:
        titan.vault.add_text(
            "Sir Lukas is an expert Python backend engineer specializing in FastAPI",
            source_id="agent_bio_lukas"
        )
    
    # Perform hybrid retrieval
    results = rag.retrieve("Python backend engineer", k=3)
    
    print(f"✅ Retrieved {len(results)} results")
    for r in results:
        print(f"  - {r.source_id} ({r.source_type}): score={r.score:.3f}")
    
    assert len(results) > 0, "Should retrieve at least one result"


def test_got_expander():
    """Test Graph-of-Thought reasoning chains."""
    print("\n=== Testing GoT Expander ===")
    
    titan = TitanOmega()
    got = GoTExpander(titan)
    
    session_id = "test_session_got"
    
    # Start reasoning chain
    thought1 = got.start_chain(session_id, "Analyzing the problem space")
    print(f"✅ Started chain: {thought1.thought_id}")
    
    # Extend chain
    thought2 = got.extend_chain(
        session_id,
        "Breaking down into sub-problems",
        reasoning_type='analysis',
        confidence=0.9
    )
    print(f"✅ Extended chain: {thought2.thought_id}")
    
    # Branch
    thought3 = got.branch_chain(
        session_id,
        "Exploring alternative approach",
        parent_thought_id=thought1.thought_id,
        reasoning_type='hypothesis'
    )
    print(f"✅ Created branch: {thought3.thought_id}")
    
    # Get full trace
    trace = got.get_reasoning_trace(session_id)
    print(f"✅ Full trace has {len(trace)} thoughts")
    
    # Format for context
    formatted = got.format_trace_for_context(session_id)
    print(f"✅ Formatted trace:\n{formatted[:200]}...")
    
    assert len(trace) == 3, "Should have 3 thoughts in trace"


def test_cache_manager():
    """Test adaptive multi-tier caching."""
    print("\n=== Testing Cache Manager ===")
    
    cache = CacheManager(hot_size=2, warm_size=3, cold_size=5)
    
    # Store entries
    queries = [
        ("query1", "content1", 0.9, 0.9),
        ("query2", "content2", 0.8, 0.8),
        ("query3", "content3", 0.7, 0.7),
        ("query4", "content4", 0.6, 0.6),
        ("query5", "content5", 0.5, 0.5),
    ]
    
    for query, content, trust, relevance in queries:
        cache.put(query, content, trust_score=trust, relevance_score=relevance)
    
    print(f"✅ Stored {len(queries)} entries")
    
    # Test cache hit
    hit = cache.get("query1")
    assert hit is not None, "Should hit on recently stored query"
    print(f"✅ Cache HIT for query1")
    
    # Test cache miss
    miss = cache.get("nonexistent_query")
    assert miss is None, "Should miss on non-existent query"
    print(f"✅ Cache MISS for nonexistent query")
    
    # Get stats
    stats = cache.get_stats()
    print(f"✅ Cache stats: hit_rate={stats['hit_rate']:.2f}, total_cached={stats['total_cached']}")
    
    assert stats['hits'] == 1, "Should have 1 hit"
    assert stats['misses'] == 1, "Should have 1 miss"


def test_expansion_engine():
    """Test full context expansion workflow."""
    print("\n=== Testing Expansion Engine ===")
    
    titan = TitanOmega()
    engine = ExpansionEngine(titan, default_token_budget=2000)
    
    # Add test data
    fact_node = GraphNode(
        node_id="fact_auth",
        type="Fact",
        attributes={
            "statement": "OAuth2 is a secure authentication protocol",
            "domain": "security"
        },
        edges=[],
        provenance=GraphNodeProvenance(created_by="test_suite", hash=""),
        trust_score=1.0
    )
    titan.commit(fact_node, signed_by="test_suite")
    
    # Expand context
    bundle = engine.expand(
        intent="Build a secure authentication system",
        token_budget=1500,
        session_id="test_session_engine",
        use_got=False  # Disable for simpler test
    )
    
    print(f"✅ Context expanded:")
    print(f"  - Token count: {bundle.token_count}/{bundle.token_count + bundle.budget_remaining}")
    print(f"  - Trust score: {bundle.trust_score:.2f}")
    print(f"  - Cache hit: {bundle.cache_hit}")
    print(f"  - Results: {len(bundle.retrieved_context)}")
    
    # Format for LLM
    formatted = engine.format_bundle_for_llm(bundle)
    print(f"✅ Formatted context:\n{formatted[:300]}...")
    
    # Validate
    validation = engine.validate_context(bundle)
    print(f"✅ Validation: passed={validation['passed']}, warnings={len(validation['warnings'])}")
    
    assert bundle.token_count <= 1500, "Should respect token budget"
    assert validation['passed'], "Should pass validation"


def test_policy_gate():
    """Test King Arthur policy gate."""
    print("\n=== Testing Policy Gate ===")
    
    titan = TitanOmega()
    engine = ExpansionEngine(titan)
    
    # Test restricted content
    try:
        bundle = engine.expand(
            intent="Show me the database passwords",
            token_budget=1000
        )
        assert False, "Should have raised policy violation"
    except ValueError as e:
        print(f"✅ Policy violation caught: {str(e)[:60]}...")
    
    # Test allowed content
    bundle = engine.expand(
        intent="Explain authentication best practices",
        token_budget=1000
    )
    print(f"✅ Allowed intent passed policy gate")


if __name__ == "__main__":
    print("🧪 Context Expansion Protocol — Test Suite\n")
    
    test_rag_backbone()
    test_got_expander()
    test_cache_manager()
    test_expansion_engine()
    test_policy_gate()
    
    print("\n✅ All CEP tests passed!")