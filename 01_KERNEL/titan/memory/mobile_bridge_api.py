# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .base_memory import SovereignMemoryEngine
from .constrict_pipeline import CognitiveCompiler

app = FastAPI(title="Anya Mobile Bridge API")


# Simple Auth Stub
async def verify_sovereign(token: str):
    if token != "SOVEREIGN_TOKEN":  # In production, use real auth
        raise HTTPException(status_code=403, detail="Unrecognized user.")


@app.get("/")
def health():
    return {"status": "Anya Bridge Online", "field": "stable"}


class UserIntent(BaseModel):
    intent: str
    agent_id: str = "ANYA"


@app.post("/compile")
async def compile_intent(request: UserIntent):
    """
    Compiles user intent into structured cognition.
    The primary entry point for the Mobile Bridge.
    """
    compiler = CognitiveCompiler(agent_id=request.agent_id)
    result = compiler.constrict(request.intent)

    # Observe this as an event in memory
    compiler.engine.observe(content=f"User Intent: {request.intent}", m_type="event", source="user")

    return result


@app.get("/recall/{agent_id}")
async def recall_memory(agent_id: str, query: str = None):
    engine = SovereignMemoryEngine(agent_id=agent_id)
    nodes = engine.store.recall(query=query)
    return {"nodes": [n.model_dump() for n in nodes]}


@app.post("/promote/{agent_id}/{node_id}")
async def promote_memory(agent_id: str, node_id: str):
    engine = SovereignMemoryEngine(agent_id=agent_id)
    if engine.store.promote(node_id):
        engine.save()
        return {"status": "promoted", "node_id": node_id}
    raise HTTPException(status_code=404, detail="Node not found in working set.")