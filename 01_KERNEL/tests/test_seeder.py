# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite for Titan Omega Seeder Pipelines
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'memory')))

from memory.seeder import TitanSeeder
from memory.titan_omega import TitanOmega


def test_seeder_logic():
    print("\n[TEST] Initializing Titan Omega and Seeder...")
    titan = TitanOmega()
    seeder = TitanSeeder(titan)
    
    print("\n[TEST] Seeding a multi-paragraph document...")
    doc_content = """
    Camelot OS uses a Tri-Realm architecture:
    1. 01_KERNEL: Core logic, memory stacks, and governance.
    2. 02_FORGE: Application development, tools, and agent cartridges.
    3. 03_VAULT: Persistent knowledge, archives, and asset storage.
    
    The Titan Omega memory stack is the backbone of the Kernel's cognitive capacity.
    It integrates Graph, Vault, and Flux for a holistic memory experience.
    
    Project Chimera represents the next evolution of this stack, 
    introducing Graph-of-Thought (GoT) reasoning and self-optimization loops.
    """
    
    seeder.seed_text_document(
        content=doc_content, 
        source_id="Camelot_Architecture_v24.md", 
        metadata={"domain": "system_design", "version": "v24.0"}
    )
    
    print("\n[TEST] Verifying Vector Search Recall...")
    # Search for something specific in the first paragraph
    results = titan.vault.vector_search("What are the three realms of Camelot?", k=2)
    assert len(results) > 0, "Vector search should return results"
    print(f"✅ Found {len(results)} vector matches")
    
    print("\n[TEST] Verifying Graph Anchor...")
    # The fact id is computed from hash, but we can query by type
    facts = titan.graph.query({"type": "Fact"})
    matching_facts = [f for f in facts if "Camelot_Architecture_v24.md" in str(f.attributes.get("title"))]
    assert len(matching_facts) > 0, "Graph fact node should exist"
    print(f"✅ Found graph fact: {matching_facts[0].node_id}")

    print("\n[TEST] Seeding Agent Manifest...")
    manifest = {
        "cartridge_id": "TEST_CORE",
        "description": "A temporary test cartridge",
        "version": "0.1.0",
        "capabilities": ["testing", "mock_logic"],
        "agents": ["Sir_Tester", "Dame_Debugger"]
    }
    seeder.seed_agent_cartridge(manifest)
    
    # Verify agents in graph
    agents = titan.graph.query({"type": "Agent"})
    test_agents = [a for a in agents if a.node_id in ["Sir_Tester", "Dame_Debugger"]]
    assert len(test_agents) == 2, "Both agents should be in the graph"
    print("✅ Verified agents Sir_Tester and Dame_Debugger in graph")

    print("\n[TEST] Hybrid Search Validation...")
    results = titan.hybrid_search("Chimera stack evolution")
    assert len(results["vector_results"]) > 0 or len(results["graph_results"]) > 0
    print("✅ Hybrid search merged results successfully")

if __name__ == "__main__":
    print("🧪 Starting Seeder Test Suite...")
    try:
        test_seeder_logic()
        print("\n🏆 ALL SEEDER TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()