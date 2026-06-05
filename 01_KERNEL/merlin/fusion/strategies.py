# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Fusion Strategies (Node 5.2)

Defines the logic for merging agent outputs.
1. Serial Pipeline: A -> B -> C refinement.
2. Ensemble Arbitration: A, B, C converge via voting.
3. Hybrid Merge: Parallel work followed by serial synthesis.
"""

from typing import List, Dict, Any
from enum import Enum

class FusionType(str, Enum):
    SERIAL = "serial"
    ENSEMBLE = "ensemble"
    HYBRID = "hybrid"

class FusionStrategy:
    """Base class for all agent fusion strategies."""
    
    def fuse(self, goal: str, agent_outputs: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Strategy must implement fuse()")

class SerialStrategy(FusionStrategy):
    """Refinement strategy: Output of Agent(N) is passed as context to Agent(N+1)."""
    
    def fuse(self, goal: str, agent_outputs: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        print("[Fusion] Executing Serial Pipeline Fusion...")
        # In a real system, the outputs are generated sequentially.
        # Here we 'merge' the existing outputs as a combined refined artifact.
        final_content = ""
        for i, out in enumerate(agent_outputs):
            final_content += f"\n--- Step {i+1} ({out.get('agent_id')}) ---\n"
            final_content += out.get("content", "")
            
        return {
            "fusion_type": FusionType.SERIAL,
            "fused_content": final_content.strip(),
            "rationale": "Sequential refinement pipeline completed."
        }

class EnsembleStrategy(FusionStrategy):
    """Consensus strategy: Multiple agents provide independent solutions; result is synthesized."""
    
    def fuse(self, goal: str, agent_outputs: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        print("[Fusion] Executing Ensemble Arbitration...")
        # Simple synthesis of perspectives
        synthesis = f"Ensemble Synthesis for Goal: {goal}\n\n"
        for out in agent_outputs:
            synthesis += f"Perspective from {out.get('agent_id')}:\n{out.get('content')}\n\n"
            
        return {
            "fusion_type": FusionType.ENSEMBLE,
            "fused_content": synthesis.strip(),
            "rationale": f"Arbitrated between {len(agent_outputs)} independent perspectives."
        }

class HybridStrategy(FusionStrategy):
    """Complex strategy: Parallel investigation + Combined Serial Synthesis."""
    
    def fuse(self, goal: str, agent_outputs: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        print("[Fusion] Executing Hybrid Merge...")
        # Combined logic
        return {
            "fusion_type": FusionType.HYBRID,
            "fused_content": "Hybrid result not yet fully implemented in mock.",
            "rationale": "Parallel investigation merged via serial refinement."
        }