# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
CAMELOT KERNEL [MERLIN_Omega]
The Central Nervous System of the Sovereign OS.
Integrates: TitanLink, RustDesk, Handoffs, and Iron Gate.
"""

import os
import sys
from datetime import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import BackgroundTasks, FastAPI

# Import Modules (Ensure paths are correct in Docker)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion.fusion_router import router as fusion_router

# Global State (Stubbed for Fusion Test)
titan_link = None
rustdesk = None
handoff_mgr = None
telemetry = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ignite Background Threads
    print("[🔥] MERLIN_Omega: Neural Link Ignited (Test Mode)")

    # def monitor_loop():
    #     while True:
    #         telemetry.poll_rotel()
    #         time.sleep(5)

    # t = threading.Thread(target=monitor_loop, daemon=True)
    # t.start()

    yield
    # Shutdown logic if needed
    print("[💀] MERLIN_Omega: Severing Link.")


app = FastAPI(title="Camelot Kernel", lifespan=lifespan)

# Include Fusion API (Project Chimera Node 5.5)
app.include_router(fusion_router)


@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ONLINE", "identity": "Merlin_Omega", "mode": os.getenv("MODE", "SIMULATION")}


@app.post("/agent/helio")
async def sir_helio_endpoint(query: str, session_id: str = "session_001"):
    """Dispatch a query to Sir Helio (pydantic-ai) via the control_plane knight."""
    _camelot_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if _camelot_root not in sys.path:
        sys.path.insert(0, _camelot_root)
    try:
        from control_plane.pydantic_ai_knight import run_sir_helio
        result = await run_sir_helio(query, session_id)
        return {"status": "SUCCESS", "result": result}
    except ImportError:
        return {"status": "UNAVAILABLE", "detail": "pydantic-ai not installed in this environment"}
    except Exception as exc:
        return {"status": "ERROR", "detail": str(exc)}


@app.post("/command")
def execute_command(intent: str, background_tasks: BackgroundTasks):
    print(f"[👂] KERNEL: Received Intent -> '{intent}'")

    # Process the intent
    decision = process_intent(intent)

    # Log to background tasks (Simulation of async processing)
    background_tasks.add_task(
        print, f"[⚡] BACKGROUND: Executing {decision['action']}..."
    )

    return {
        "status": "ACCEPTED",
        "decision": decision,
        "mode": os.getenv("MODE", "SIMULATION"),
    }

def process_intent(intent: str):
    """
    Parses and routes the raw intent to the appropriate sub-system.
    """
    intent_lower = intent.lower()
    timestamp = datetime.now().isoformat()

    # 1. System Health/Status
    if any(k in intent_lower for k in ["status", "health", "report"]):
        return {
            "action": "SYSTEM_HEALTH_CHECK",
            "priority": "LOW",
            "timestamp": timestamp,
            "target": "Merlin_Omega",
        }

    # 2. Research/Information
    if any(k in intent_lower for k in ["research", "search", "find", "who is"]):
        return {
            "action": "DISPATCH_RESEARCH_AGENT",
            "priority": "MEDIUM",
            "timestamp": timestamp,
            "target": "Morgana_Swarm",
        }

    # 3. Kinetic/Action
    if any(k in intent_lower for k in ["deploy", "build", "run", "execute"]):
        return {
            "action": "INITIATE_KINETIC_SEQUENCE",
            "priority": "HIGH",
            "timestamp": timestamp,
            "target": "Sir_Lukas",
        }

    # Default: Log & Archival
    print(f"[🧠] MERLIN: Routing generic intent -> {intent}")
    return {
        "action": "GENERIC_PROCESS",
        "payload": intent,
        "timestamp": timestamp,
        "target": "UKG_Vault",
    }


if __name__ == "__main__":
    # In Docker, this runs on 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=8000)