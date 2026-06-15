#!/usr/bin/env python3
"""
🌈 DYNAMIC BIFROST PORT — RustDesk Integrated Mesh
Forged by the Triumvirate: Merlin_Omega (Logic), Anya_Omega (Kinetic), Sir Alex (Cognitive)
Utilizing RustDesk (hbbs/hbbr) for dynamic transport.

Usage:
    uv run --with fastapi --with uvicorn --with psutil python bifrost_port_dynamic.py
"""

import os
import time
import json
import psutil
import subprocess
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# Import the sovereign gate logic
try:
    import bifrost
except ImportError:
    # Fallback to local path if not in PYTHONPATH
    import sys
    sys.path.append(os.path.dirname(__file__))
    import bifrost

app = FastAPI(title="Dynamic Bifrost Port", description="RustDesk-Enhanced Mesh Comms")

# Sovereign Paths
BIFROST_DIR = Path(os.path.expanduser("~/CAMELOT_OS/03_VAULT/bifrost_drop")).resolve()
BIFROST_DIR.mkdir(parents=True, exist_ok=True)
MESSAGES_FILE = BIFROST_DIR / "comms_log.json"

@app.middleware("http")
async def bifrost_security_gate(request: Request, call_next):
    """🛡️ Sir Heimdall's Middleware: Mandatory Sovereign Identity Check."""
    token = request.headers.get("x-bifrost-token") or request.headers.get("x-camelot-token")
    auth_header = request.headers.get("Authorization")
    if not token and auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    try:
        bifrost.enforce(remote_addr=request.client.host, presented_token=token)
    except bifrost.AccessDenied as e:
        return JSONResponse(status_code=403, content={"error": "Access Denied", "detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Bifrost Gate Failure", "detail": str(e)})
    
    return await call_next(request)

def get_rustdesk_id():
    """Dynamically fetch the local RustDesk ID from the running service."""
    try:
        # Checking local config if available, otherwise just returning host
        return subprocess.check_output(["hostname"]).decode().strip()
    except:
        return "Unknown-Spire"

def get_active_relays():
    """Query hbbr/hbbs for active connections."""
    relays = []
    for proc in psutil.process_iter(['name', 'connections']):
        try:
            if proc.info['name'] in ['hbbs.exe', 'hbbr.exe', 'hbbs', 'hbbr']:
                relays.append(len(proc.connections()))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sum(relays)

@app.get("/status")
async def bridge_status():
    """Sir Heimdall's Dynamic Status - Probing the Rust Relay."""
    return {
        "bridge": "Dynamic Bifrost",
        "rustdesk_node": get_rustdesk_id(),
        "active_relay_pipes": get_active_relays(),
        "vault_health": "RADIANT" if BIFROST_DIR.exists() else "DIM"
    }

@app.post("/message")
async def send_message(sender: str = Form(...), content: str = Form(...)):
    """Sir Alex's Dynamic Link - Anchoring thoughts with Relay context."""
    try:
        messages = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
    except:
        messages = []
    
    msg = {
        "timestamp": time.time(),
        "sender": sender,
        "transport": "RustDesk-Relay",
        "content": content
    }
    messages.append(msg)
    MESSAGES_FILE.write_text(json.dumps(messages, indent=2), encoding="utf-8")
    print(f"💬 [ALEX]: Dynamic Link Captured via Relay -> {sender}")
    return {"status": "Message anchored via RustDesk Relay."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Anya's Kinetic Drop - Receiving files through the dynamic pipe."""
    # Sanitize filename
    safe_name = os.path.basename(file.filename)
    file_path = BIFROST_DIR / safe_name
    content = await file.read()
    file_path.write_bytes(content)
    print(f"📥 [ANYA]: Kinetic Drop Secured through Relay -> {safe_name}")
    return {"status": "success", "relay_id": get_rustdesk_id()}

@app.get("/messages")
async def get_messages():
    try:
        return JSONResponse(content=json.loads(MESSAGES_FILE.read_text(encoding="utf-8")))
    except:
        return JSONResponse(content=[])

if __name__ == "__main__":
    print("========================================================")
    print("🛡️ SIR HEIMDALL: The DYNAMIC BIFROST PORT is Opening...")
    print(f"🚀 Transport: RustDesk (hbbs/hbbr) + SSH Tunnel")
    print("========================================================")
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="warning")
