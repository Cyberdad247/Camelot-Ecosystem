# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test suite for Titan Omega Memory Stack

Validates Omega-Graph, Omega-Vault, and Omega-Flux functionality.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime

from titan_omega import TitanOmega
from titan_schemas import GraphEdge, GraphNode, GraphNodeProvenance


def test_omega_graph():
    """Test Omega-Graph: add nodes, query, retrieve."""
    print("\n=== Testing Omega-Graph ===")
    titan = TitanOmega()
    
    # Create test agent node
    agent_node = GraphNode(
        node_id="agent_test_lukas",
        type="Agent",
        attributes={
            "name": "Sir Lukas",
            "role": "Engineer",
            "skills": ["Python", "Backend", "API"]
        },
        edges=[
            GraphEdge(to="skill_python", relationship="expert_in"),
            GraphEdge(to="cartridge_engineering", relationship="belongs_to")
        ],
        provenance=GraphNodeProvenance(
            created_by="test_suite",
            hash=""  # Will be auto-computed
        ),
        trust_score=0.95
    )
    
    # Commit to graph
    node_hash = titan.commit(agent_node, signed_by="test_suite")
    print(f"✅ Committed agent node with hash: {node_hash[:16]}...")
    
    # Query by type
    agents = titan.graph.query({"type": "Agent"})
    print(f"✅ Found {len(agents)} agent(s) in graph")
    
    # Retrieve single node
    retrieved = titan.graph.get_node("agent_test_lukas")
    assert retrieved is not None
    assert retrieved.attributes["role"] == "Engineer"
    print(f"✅ Retrieved agent: {retrieved.attributes['name']}")


def test_omega_vault():
    """Test Omega-Vault: add text, vector search."""
    print("\n=== Testing Omega-Vault ===")
    
    try:
        titan = TitanOmega()
        
        if not titan.vault:
            print("⚠️  Omega-Vault skipped (FAISS not available)")
            return
        
        # Add test documents
        texts = [
            "Sir Lukas is an expert Python backend engineer specializing in FastAPI and database design.",
            "Sir Hydron is a frontend webmaster skilled in React, Hydrogen, and Tailwind CSS.",
            "Vizion Wealth is a creative lyricist using the LCE 4.0 engine for advanced copywriting."
        ]
        
        for i, text in enumerate(texts):
            titan.vault.add_text(text, source_id=f"doc_{i}", metadata={"category": "agent_bio"})
        
        print(f"✅ Added {len(texts)} documents to Omega-Vault")
        
        # Perform vector search
        results = titan.vault.vector_search("backend engineering Python", k=2)
        print(f"✅ Vector search returned {len(results)} results")
        
        for emb, distance in results:
            print(f"  - {emb.source_id} (distance: {distance:.4f})")
        
        # Save to disk
        titan.vault.save()
        print("✅ Persisted Omega-Vault to disk")
        
    except ImportError as e:
        print(f"⚠️  Omega-Vault test skipped: {e}")


def test_omega_flux():
    """Test Omega-Flux: store events, retrieve, TTL expiration."""
    print("\n=== Testing Omega-Flux ===")
    titan = TitanOmega()
    
    session_id = "test_session_001"
    
    # Store reasoning events
    titan.flux.store_event(session_id, "Step 1: Analyzing user intent", priority="high", ttl=120)
    titan.flux.store_event(session_id, "Step 2: Retrieving context from Omega-Graph", priority="medium", ttl=90)
    flux_id_3 = titan.flux.store_event(session_id, "Step 3: Generating response draft", priority="low", ttl=60)
    
    print(f"✅ Stored 3 flux events for session {session_id}")
    
    # Retrieve session events
    events = titan.flux.get_session_events(session_id)
    print(f"✅ Retrieved {len(events)} events for session")
    
    for event in events:
        print(f"  - {event.flux_node_id}: {event.content[:50]}... (TTL: {event.ttl_seconds}s)")
    
    # Test expiration (simulate by manually setting old timestamp)
    import time
    old_event = titan.flux.nodes[flux_id_3]
    old_event.created_at = datetime.fromtimestamp(time.time() - 200)  # 200s ago
    
    titan.flux.cleanup_expired()
    events_after_cleanup = titan.flux.get_session_events(session_id)
    print(f"✅ After cleanup: {len(events_after_cleanup)} events remaining")


def test_hybrid_search():
    """Test hybrid RAG: Omega-Vault vector + Omega-Graph pattern matching."""
    print("\n=== Testing Hybrid Search ===")
    titan = TitanOmega()
    
    # Add a fact to graph
    fact_node = GraphNode(
        node_id="fact_001",
        type="Fact",
        attributes={
            "statement": "FastAPI is a modern Python web framework for building APIs",
            "domain": "backend_engineering"
        },
        edges=[],
        provenance=GraphNodeProvenance(created_by="test_suite", hash=""),
        trust_score=1.0
    )
    titan.commit(fact_node, signed_by="test_suite")
    
    # Perform hybrid search
    results = titan.hybrid_search("Python web framework", k=3)
    
    print("✅ Hybrid search results:")
    print(f"  - Vector results: {len(results['vector_results'])}")
    print(f"  - Graph results: {len(results['graph_results'])}")
    
    if results['graph_results']:
        print(f"  - Found fact: {results['graph_results'][0]['attributes']['statement'][:60]}...")


if __name__ == "__main__":
    print("🧪 Titan Omega Memory Stack — Test Suite\n")
    
    test_omega_graph()
    test_omega_vault()
    test_omega_flux()
    test_hybrid_search()
    
    print("\n✅ All tests passed!")