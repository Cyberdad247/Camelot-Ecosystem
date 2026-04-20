# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite for Agentic Merger Engine
"""

import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fusion.merger_engine import MergerEngine, FusionType

def test_capability_discovery():
    print("\n=== Testing Capability Discovery ===")
    base_path = os.path.join(os.path.dirname(__file__), "..", "02_FORGE", "cartridge", "packages")
    merger = MergerEngine(base_path)
    
    # Sir Lukas should be found for 'backend'
    agents = merger.cap_graph.find_agents_for_goal(["backend"])
    print(f"✅ Found {len(agents)} agents for 'backend': {agents}")
    assert "Sir_Lukas" in agents or "Sir Lukas" in agents
    
    # Lord Nexus should be found for 'architecture'
    agents = merger.cap_graph.find_agents_for_goal(["architecture"])
    print(f"✅ Found {len(agents)} agents for 'architecture': {agents}")
    assert "Lord_Nexus" in agents or "Lord Nexus" in agents

def test_serial_fusion():
    print("\n=== Testing Serial Fusion ===")
    base_path = os.path.join(os.path.dirname(__file__), "..", "02_FORGE", "cartridge", "packages")
    merger = MergerEngine(base_path)
    
    result = merger.execute_fusion(
        goal="Build a secure KV store",
        required_capabilities=["backend", "security"],
        type=FusionType.SERIAL
    )
    
    print(f"✅ Fusion Status: {result['status']}")
    print(f"✅ Agents Involved: {result['agents_involved']}")
    print(f"✅ Final Rationale: {result['rationale']}")
    
    assert result['status'] == "success"
    assert len(result['agents_involved']) >= 1
    assert "Step 1" in result['result']
    assert "judge_score" in result, "Result should include judge_score"
    assert "verdict" in result, "Result should include verdict"

def test_ensemble_fusion():
    print("\n=== Testing Ensemble Fusion ===")
    base_path = os.path.join(os.path.dirname(__file__), "..", "02_FORGE", "cartridge", "packages")
    merger = MergerEngine(base_path)
    
    result = merger.execute_fusion(
        goal="Determine best cache TTL",
        required_capabilities=["planning", "backend"],
        type=FusionType.ENSEMBLE
    )
    
    print(f"✅ Fusion Status: {result['status']}")
    print(f"✅ Result Synthesis Snippet: {result['result'][:100]}...")
    
    assert result['status'] == "success"
    assert "Ensemble Synthesis" in result['result']
    assert result['judge_score'] > 0, "Judge score should be positive"
    print(f"✅ Judge Adjudication: score={result['judge_score']:.2f}, verdict={result['verdict']}")

if __name__ == "__main__":
    print("🧪 Starting Merger Engine Test Suite...")
    try:
        test_capability_discovery()
        test_serial_fusion()
        test_ensemble_fusion()
        print("\n🏆 ALL MERGER TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()