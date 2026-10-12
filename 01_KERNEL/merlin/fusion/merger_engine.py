# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Agentic Merger Engine (Node 5.3)

The high-level orchestrator for Project Chimera's fusion protocol.
Links Capability Graph, Fusion Strategies, and LLM-as-a-Judge.
"""

import json
import os
import sys
import time
import uuid
from typing import Any, Dict, List

# Add parent directory (01_KERNEL) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from iron_gate.judge.llm_judge import JudgeRequest, LLMJudge

from fusion.capability_graph import CapabilityGraph
from fusion.strategies import EnsembleStrategy, FusionType, HybridStrategy, SerialStrategy


class MergerEngine:
    """
    Core engine for merging multiple agents into a single cognitive unit.
    Orchestrates discovery, selection, execution, and fusion.
    """
    
    def __init__(self, packages_dir: str):
        self.cap_graph = CapabilityGraph(packages_dir)
        self.cap_graph.refresh()
        
        self.strategies = {
            FusionType.SERIAL: SerialStrategy(),
            FusionType.ENSEMBLE: EnsembleStrategy(),
            FusionType.HYBRID: HybridStrategy()
        }
        
        # Initialize Quality Adjudicator
        self.judge = LLMJudge()
        
    def execute_fusion(self, goal: str, required_capabilities: List[str], type: FusionType = FusionType.SERIAL) -> Dict[str, Any]:
        """
        Orchestrate a complete agent fusion cycle.
        1. Discover relevant agents.
        2. Execute individual outputs (mocked).
        3. Merge via chosen strategy.
        4. Return unified Chimera result.
        """
        print(f"[Merger] Starting Fusion cycle for: {goal}")
        
        # 1. Discovery
        potential_agents = self.cap_graph.find_agents_for_goal(required_capabilities)
        if not potential_agents:
            return {"status": "error", "error": f"No agents found for capabilities: {required_capabilities}"}
            
        print(f"[Merger] Selected agents for fusion: {potential_agents}")
        
        # 2. Mock Agent Execution 
        # (In production, this triggers the Agentic Swarm / Cartridge Sandbox)
        agent_outputs = []
        for agent_id in potential_agents:
            agent_outputs.append({
                "agent_id": agent_id,
                "content": f"Output from {agent_id} targeting goal '{goal}'",
                "timestamp": time.time()
            })
            
        # 3. Apply Fusion Strategy
        strategy = self.strategies.get(type, self.strategies[FusionType.SERIAL])
        fusion_result = strategy.fuse(goal, agent_outputs, context={})
        
        # 4. Wrap with metadata
        chimera_id = f"chimera_{uuid.uuid4().hex[:8]}"
        
        # 5. Quality Adjudication (Node 1.3 integration)
        judge_req = JudgeRequest(
            artifact_id=chimera_id,
            artifact_type="fusion_result",
            content=fusion_result["fused_content"],
            context={
                "goal": goal,
                "strategy": type,
                "agents": potential_agents
            }
        )
        judge_output = self.judge.evaluate(judge_req)
        
        return {
            "chimera_id": chimera_id,
            "status": "success",
            "goal": goal,
            "fused_by": type,
            "agents_involved": potential_agents,
            "result": fusion_result["fused_content"],
            "rationale": fusion_result["rationale"],
            "judge_score": judge_output.judge_score,
            "verdict": judge_output.verdict.name,
            "evaluation": judge_output.rationale,
            "trace_link": f"01_KERNEL/diagnostics/traces/{chimera_id}.json"
        }

if __name__ == "__main__":
    # Test Merger
    import os
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "02_FORGE", "cartridge", "packages")
    merger = MergerEngine(base_path)
    
    # Run a Strategy + Engineering fusion
    result = merger.execute_fusion(
        goal="Architecture for a secure Kubernetes mesh",
        required_capabilities=["architecture", "backend", "security"],
        type=FusionType.SERIAL
    )
    
    print("\n--- FUSION RESULT ---")
    print(json.dumps(result, indent=2))
