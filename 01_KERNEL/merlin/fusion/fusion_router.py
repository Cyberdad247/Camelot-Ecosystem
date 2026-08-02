# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Fusion API Router (Node 5.5)

Exposes the Agentic Merger and Fusion Protocol via FastAPI.
Integrates Capability Discovery, Multi-Strategy Fusion, and LLM-as-a-Judge adjudication.
"""

import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Ensure internal modules are reachable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fusion.merger_engine import FusionType, MergerEngine

router = APIRouter(prefix="/v2/fusion", tags=["fusion"])

# Initialize Engine (In production, this might be a singleton or dependency injected)
PACKAGES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "02_FORGE", "cartridge", "packages")
)
merger = MergerEngine(PACKAGES_DIR)

class FusionRequest(BaseModel):
    goal: str = Field(..., description="The objective for the agent fusion")
    required_capabilities: List[str] = Field(..., description="Agent traits needed for this goal")
    fusion_type: FusionType = Field(default=FusionType.SERIAL, description="Logic for merging outputs")
    context_bundle: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context/metadata")

class FusionResponse(BaseModel):
    chimera_id: str
    status: str
    goal: str
    fused_by: str
    agents_involved: List[str]
    result: str
    rationale: str
    judge_score: float
    verdict: str
    evaluation: List[str]
    trace_link: str

@router.post("/merge", response_model=FusionResponse)
async def merge_agents(request: FusionRequest):
    """
    Execute a synchronous agent fusion cycle.
    Discover, Merge, and Adjudicate.
    """
    print(f"[API] >>> Incoming Fusion Request: Goal='{request.goal[:50]}'")
    
    try:
        # Refresh capability graph to pick up new cartridges
        print("[API] Refreshing Capability Graph...")
        merger.cap_graph.refresh()
        
        print(f"[API] Executing Fusion with Strategy: {request.fusion_type}")
        result = merger.execute_fusion(
            goal=request.goal,
            required_capabilities=request.required_capabilities,
            type=request.fusion_type
        )
        
        if result.get("status") == "error":
            print(f"[API] Fusion Error handled: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error"))
            
        print(f"[API] <<< Fusion Success: ChimeraID={result.get('chimera_id')}")
        return result

    except Exception as e:
        print(f"[API] Fusion Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fusion Engine Failure: {str(e)}")

@router.get("/capabilities")
async def list_capabilities():
    """List all available agent capabilities across the CMX."""
    merger.cap_graph.refresh()
    return {
        "capabilities": list(merger.cap_graph.capability_map.keys()),
        "agent_count": len(merger.cap_graph.agent_map)
    }

@router.get("/agents")
async def list_agents():
    """List all agents currently indexed in the fusion lattice."""
    merger.cap_graph.refresh()
    return {
        "agents": [a.agent_id for a in merger.cap_graph.agent_map.values()],
        "active_cartridges": list(set(a.cartridge_id for a in merger.cap_graph.agent_map.values()))
    }
