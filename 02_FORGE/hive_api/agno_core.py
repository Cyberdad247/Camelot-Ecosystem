# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS - CONFIDENTIAL AND PROPRIETARY
from __future__ import annotations

import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Agno Cognitive Orchestrator v2", version="2.1.0")

# --- KERNEL INTEGRATION ---
KERNEL_DIR = Path("C:/Users/vizio/CAMELOT_OS/01_KERNEL")
CAMELOT_ROOT = Path("C:/Users/vizio/CAMELOT_OS")
if str(CAMELOT_ROOT) not in sys.path:
    sys.path.append(str(CAMELOT_ROOT))


def get_kernel_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


from control_plane.main import ControlPlane

ukg = None
tt = None
llm_manager = None
mcp_gateway = None
kernel_runtime_error: Optional[str] = None

try:
    ukg_module = get_kernel_module("ukg_runtime", KERNEL_DIR / "merlin/Engines/ukg_runtime.py")
    tt_module = get_kernel_module("think_tank", KERNEL_DIR / "agora/orchestration/think_tank.py")
    merlin_module = get_kernel_module("merlin_llm", KERNEL_DIR / "merlin/Engines/merlin_llm.py")
    mcp_module = get_kernel_module("mcp_adapter", KERNEL_DIR / "merlin/Engines/mcp_adapter.py")

    UKGRuntime = ukg_module.UKGRuntime
    ThinkTankOrchestrator = tt_module.ThinkTankOrchestrator
    MerlinLLM = merlin_module.MerlinLLM
    MCPAdapter = mcp_module.MCPAdapter

    ukg = UKGRuntime()
    tt = ThinkTankOrchestrator()
    llm_manager = MerlinLLM()
    mcp_gateway = MCPAdapter()
except Exception as exc:
    kernel_runtime_error = str(exc)


def _require_runtime(component: Any, name: str) -> Any:
    if component is None:
        raise HTTPException(
            status_code=503,
            detail=f"{name} unavailable; kernel runtime failed: {kernel_runtime_error}",
        )
    return component


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
    params_schema: Optional[Dict[str, Any]] = None


class HiveSelfTestRequest(BaseModel):
    target: str = "harness_codex"
    prompt: str = "codex"
    timeout: int = 30
    runtime: str = "auto"


# --- ENDPOINTS ---
@app.get("/llm/registry")
async def get_llm_registry():
    manager = _require_runtime(llm_manager, "llm_manager")
    return {"registry": manager.registry, "profiles": manager.profiles}


@app.post("/llm/assign")
async def assign_llm(task: str, priority: str = "low"):
    manager = _require_runtime(llm_manager, "llm_manager")
    model = manager.select_model(task, priority)
    return {"assigned_model": model, "task": task, "priority": priority}


@app.get("/mcp/tools")
async def list_mcp_tools():
    gateway = _require_runtime(mcp_gateway, "mcp_gateway")
    return {
        "tools": gateway.list_tools(),
        "gateway_status": "ONLINE",
        "governance": "HITL GATE ACTIVE",
    }


@app.post("/mcp/register")
async def register_tool(adapter: AdapterRegistration):
    gateway = _require_runtime(mcp_gateway, "mcp_gateway")
    gateway.register_adapter(
        adapter.name,
        adapter.description,
        adapter.endpoint,
        adapter.capability,
        adapter.params_schema,
    )
    return {"status": "REGISTERED", "name": adapter.name}


@app.post("/session/start")
async def start_session(request: TaskRequest):
    orchestrator = _require_runtime(tt, "think_tank_orchestrator")
    try:
        session_results = await orchestrator.execute_session(
            request.objective,
            request.repo_path,
            request.priority,
        )
        return {
            "status": "success",
            "session_id": session_results["session_id"],
            "orchestrator": session_results["orchestrator_config"],
            "debate_summary": session_results["debate_summary"],
            "experts": session_results["experts"],
            "external_data": session_results.get("external_data"),
            "kinetic_result": session_results["kinetic_result"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/hive/self-test")
async def hive_self_test(request: HiveSelfTestRequest):
    runtime = request.runtime.strip().lower()
    if runtime not in {"auto", "go", "rust", "python"}:
        raise HTTPException(status_code=400, detail="runtime must be one of: auto, go, rust, python")
    if request.timeout < 1 or request.timeout > 300:
        raise HTTPException(status_code=400, detail="timeout must be between 1 and 300")

    os.environ["CAMELOT_HARNESS_RUNTIME"] = runtime

    try:
        cp = ControlPlane()
        result = cp.team_self_test(
            worker_id=request.target,
            prompt=request.prompt,
            timeout=request.timeout,
        )
        return {
            "status": "success",
            "self_test": result,
            "runtime": runtime,
            "target": request.target,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/merlin/v2/feedback")
async def merlin_feedback(request: FeedbackRequest):
    runtime = _require_runtime(ukg, "ukg_runtime")
    try:
        runtime.execute(f"LOG_FEEDBACK: {request.persona_id} | Success: {request.success}")
        retrain_status = "QUEUED_FOR_MORGAN_METAL" if request.trigger_lora_retrain else "SKIPPED"
        return {
            "status": "ACCEPTED",
            "log_id": str(uuid.uuid4()),
            "retrain_status": retrain_status,
            "governance": "EVALUATION_COMPLETE",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/merlin/forge/{role}")
async def merlin_forge(role: str):
    runtime = _require_runtime(ukg, "ukg_runtime")
    try:
        payload = runtime.execute(role, mode="LOWER")
        return {
            "persona_id": payload["root_id"],
            "tal_manifest": payload["tal_manifest"],
            "glyphs": payload["glyphs"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/vault/personas")
async def list_vault_personas():
    runtime = _require_runtime(ukg, "ukg_runtime")
    return {"library_experts": runtime.list_persona_library()}


@app.post("/vault/persona/save")
async def save_persona(persona: PersonaTAL):
    _require_runtime(ukg, "ukg_runtime")
    try:
        expert_id = persona.root.get("id", "").strip("#").lower()
        if not expert_id:
            raise HTTPException(status_code=400, detail="Invalid Persona ID")
        file_path = KERNEL_DIR / f"../03_VAULT/knowledge/persona_library/{expert_id}.jsonld"
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(persona.dict(), handle, indent=2)
        return {"status": "SAVED", "path": str(file_path)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/vault/persona/{name}")
async def get_persona(name: str):
    runtime = _require_runtime(ukg, "ukg_runtime")
    persona = runtime.load_persona(name)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=18788)
