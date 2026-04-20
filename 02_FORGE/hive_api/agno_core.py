# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import uuid
import sys
import os
from pathlib import Path
import importlib.util

app = FastAPI(title="Agno Cognitive Orchestrator v2", version="2.0.0")

# --- KERNEL INTEGRATION ---
KERNEL_DIR = Path("C:/Users/vizio/CAMELOT_OS/01_KERNEL")

def get_kernel_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ukg_module = get_kernel_module("ukg_runtime", KERNEL_DIR / "Engines/ukg_runtime.py")
tt_module = get_kernel_module("think_tank", KERNEL_DIR / "orchestration/think_tank.py")
merlin_module = get_kernel_module("merlin_llm", KERNEL_DIR / "Engines/merlin_llm.py")
mcp_module = get_kernel_module("mcp_adapter", KERNEL_DIR / "Engines/mcp_adapter.py")

UKGRuntime = ukg_module.UKGRuntime
ThinkTankOrchestrator = tt_module.ThinkTankOrchestrator
MerlinLLM = merlin_module.MerlinLLM
MCPAdapter = mcp_module.MCPAdapter

# Initialize Runtime Components
ukg = UKGRuntime()
tt = ThinkTankOrchestrator()
llm_manager = MerlinLLM()
mcp_gateway = MCPAdapter()

# --- MODELS ---
class TaskRequest(BaseModel):
    objective: str
    repo_path: str = "C:/Users/vizio/CAMELOT_OS"
    priority: str = "medium"

class PersonaTAL(BaseModel):
    root: Dict[str, str]
    branch: Dict[str, str]
    leaf: List[str]

class FeedbackRequest(BaseModel):
    persona_id: str
    success: bool
    notes: str
    traces: List[Dict[str, Any]]
    trigger_lora_retrain: bool = False

class AdapterRegistration(BaseModel):
    name: str
    description: str
    endpoint: str
    capability: str
    params_schema: Optional[Dict] = None

# --- ENDPOINTS ---

@app.get("/llm/registry")
async def get_llm_registry():
    """Lists available local and cloud LLMs and their specializations."""
    return {
        "registry": llm_manager.registry,
        "profiles": llm_manager.profiles
    }

@app.post("/llm/assign")
async def assign_llm(task: str, priority: str = "low"):
    """[DYNAMIC_ASSIGNMENT] Dynamically selects an LLM for a given task."""
    model = llm_manager.select_model(task, priority)
    return {"assigned_model": model, "task": task, "priority": priority}

@app.get("/mcp/tools")
async def list_mcp_tools():
    """[DYNAMIC_DISCOVERY] Lists all registered API Adapters and Tools."""
    return {
        "tools": mcp_gateway.list_tools(),
        "gateway_status": "ONLINE",
        "governance": "[👤✅] HITL GATE ACTIVE"
    }

@app.post("/mcp/register")
async def register_tool(adapter: AdapterRegistration):
    """Registers a new external API or internal service as an MCP tool."""
    mcp_gateway.register_adapter(
        adapter.name, 
        adapter.description, 
        adapter.endpoint, 
        adapter.capability, 
        adapter.params_schema
    )
    return {"status": "REGISTERED", "name": adapter.name}

@app.post("/session/start")
async def start_session(request: TaskRequest):
    """Initiates a Versatile v3.0 Agno-led 5-Panel Debate."""
    try:
        session_results = await tt.execute_session(
            request.objective, 
            request.repo_path, 
            request.priority
        )
        return {
            "status": "success",
            "session_id": session_results["session_id"],
            "orchestrator": session_results["orchestrator_config"],
            "debate_summary": session_results["debate_summary"],
            "experts": session_results["experts"],
            "external_data": session_results.get("external_data"),
            "kinetic_result": session_results["kinetic_result"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/merlin/v2/feedback")
async def merlin_feedback(request: FeedbackRequest):
    """Lukas Müller's Evaluation Gate for Merlin's Personas."""
    try:
        # 1. Log to Persona Evolution Protocol
        ukg.execute(f"LOG_FEEDBACK: {request.persona_id} | Success: {request.success}")
        
        retrain_status = "SKIPPED"
        if request.trigger_lora_retrain:
            retrain_status = "QUEUED_FOR_MORGAN_METAL"
            
        return {
            "status": "ACCEPTED",
            "log_id": str(uuid.uuid4()),
            "retrain_status": retrain_status,
            "governance": "[⚖️] EVALUATION_COMPLETE"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/merlin/forge/{role}")
async def merlin_forge(role: str):
    """Refined Merlin v2 Persona Creation Endpoint using TAL Synthesis."""
    try:
        payload = ukg.execute(role, mode="LOWER")
        return {
            "persona_id": payload["root_id"],
            "tal_manifest": payload["tal_manifest"],
            "glyphs": payload["glyphs"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vault/personas")
async def list_vault_personas():
    """Lists forged expert personas in the persistent library."""
    experts = ukg.list_persona_library()
    return {"library_experts": experts}

@app.post("/vault/persona/save")
async def save_persona(persona: PersonaTAL):
    """Saves or updates a persona TAL manifest in the vault."""
    try:
        expert_id = persona.root.get("id", "").strip("#").lower()
        if not expert_id:
            raise HTTPException(status_code=400, detail="Invalid Persona ID")
            
        file_path = KERNEL_DIR / f"../03_VAULT/knowledge/persona_library/{expert_id}.jsonld"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(persona.dict(), f, indent=2)
            
        return {"status": "SAVED", "path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vault/persona/{name}")
async def get_persona(name: str):
    """Retrieves a specific persona TAL manifest."""
    persona = ukg.load_persona(name)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18788)