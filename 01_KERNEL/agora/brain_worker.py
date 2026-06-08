# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys
from fastapi import FastAPI, Request, HTTPException
import uvicorn

# PATH CONFIGURATION
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from merlin_omega import Merlin_Omega
from kernel.rag.lightrag_engine import get_lightrag_engine

app = FastAPI(title="Camelot Internal Brain")

# Initialize Merlin
kernel = Merlin_Omega()

@app.get("/health")
async def health():
    return {"status": "BRAIN_ACTIVE", "version": kernel.version}

@app.post("/process")
async def process_intent(request: Request):
    try:
        data = await request.json()
        intent = data.get("intent")
        if not intent:
            raise HTTPException(status_code=400, detail="Missing intent")
        
        print(f"🧠 [BRAIN_WORKER] Processing: {intent}")
        response = await kernel.process_request(intent)
        return {"status": "SUCCESS", "response": response}
    except Exception as e:
        print(f"❌ BRAIN ERROR: {e}")
        return {"status": "ERROR", "response": str(e)}

@app.get("/memory/query")
async def query_memory(q: str, top_k: int = 5):
    try:
        engine = get_lightrag_engine()
        results = engine.query(q, top_k=top_k)
        
        formatted_results = []
        if results and hasattr(results, "results"):
            for res in results.results:
                formatted_results.append({
                    "content": res.content[:200] + "...",
                    "score": getattr(res, "score", 0.0),
                    "source": getattr(res, "metadata", {}).get("source", "unknown"),
                })
        return {"query": q, "count": len(formatted_results), "results": formatted_results}
    except Exception as e:
        return {"query": q, "results": [], "status": "RAG_ERROR", "debug": str(e)}

if __name__ == "__main__":
    print("🧠 BRAIN_WORKER: Starting internal service on port 8005...")
    uvicorn.run(app, host="127.0.0.1", port=8005)