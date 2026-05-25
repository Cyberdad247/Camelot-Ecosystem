#!/usr/bin/env python3
"""
🌈 BIFROST PORT — 24/7 Sovereign Communication & Transfer Node
Forged by the Triumvirate: Merlin_Ω (Logic), Anya_Ω (Kinetic), Sir Alex (Cognitive)
Under the watchful gaze of Sir Heimdall 🛡️

Usage:
    uv run --with fastapi --with uvicorn --with python-multipart python bifrost_port.py
"""

import os
import time
import json
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

app = FastAPI(title="Bifrost Port", description="24/7 Mesh Communication and File Transfer")

# The Secure Vault Drop Zone
BIFROST_DIR = Path(os.path.expanduser("~/CAMELOT_OS/03_VAULT/bifrost_drop")).resolve()
BIFROST_DIR.mkdir(parents=True, exist_ok=True)
MESSAGES_FILE = BIFROST_DIR / "comms_log.json"

if not MESSAGES_FILE.exists():
    MESSAGES_FILE.write_text("[]", encoding="utf-8")

@app.middleware("http")
async def bifrost_security_gate(request: Request, call_next):
    """🛡️ Sir Heimdall's Middleware: Mandatory Sovereign Identity Check."""
    # Allow local loopback without tokens for simplicity, 
    # but still enforce owner check via bifrost.enforce
    
    # Extract token from various possible locations
    token = request.headers.get("x-bifrost-token") or request.headers.get("x-camelot-token")
    auth_header = request.headers.get("Authorization")
    if not token and auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    try:
        # bifrost.enforce handles loopback (owner only) and tailnet (peer + token)
        bifrost.enforce(remote_addr=request.client.host, presented_token=token)
    except bifrost.AccessDenied as e:
        return JSONResponse(
            status_code=403, 
            content={"error": "Access Denied", "detail": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"error": "Bifrost Gate Failure", "detail": str(e)}
        )
    
    return await call_next(request)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Anya's Kinetic Drop - Securely receive files into the Vault."""
    # Sanitize filename to prevent directory traversal on upload
    safe_name = os.path.basename(file.filename)
    file_path = BIFROST_DIR / safe_name
    content = await file.read()
    file_path.write_bytes(content)
    print(f"📥 [ANYA]: Kinetic Drop Secured -> {safe_name} ({len(content)} bytes)")
    return {"status": "success", "filename": safe_name, "size": len(content)}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Merlin's Retrieval - Securely fetch files from the Vault."""
    # CRITICAL FIX: Sanitize filename to prevent path traversal
    safe_name = os.path.basename(filename)
    file_path = BIFROST_DIR / safe_name
    
    if not file_path.exists():
        print(f"❌ [MERLIN]: File '{safe_name}' lost in the void.")
        raise HTTPException(status_code=404, detail="File lost in the void.")
    
    print(f"📤 [MERLIN]: Retrieval Authorized -> {safe_name}")
    return FileResponse(path=file_path, filename=safe_name)

@app.post("/message")
async def send_message(sender: str = Form(...), content: str = Form(...)):
    """Alex's Cognitive Link - Send a message across the mesh."""
    try:
        messages = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
    except:
        messages = []
    
    msg = {
        "timestamp": time.time(),
        "sender": sender,
        "content": content
    }
    messages.append(msg)
    MESSAGES_FILE.write_text(json.dumps(messages, indent=2), encoding="utf-8")
    print(f"💬 [ALEX]: Cognitive Link from {sender} -> {content[:50]}...")
    return {"status": "Message anchored to the UKG."}

@app.get("/messages")
async def get_messages(limit: int = 50):
    """Read the latest messages traversing the Bifrost."""
    try:
        messages = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
        return JSONResponse(content=messages[-limit:])
    except:
        return JSONResponse(content=[])

if __name__ == "__main__":
    print("========================================================")
    print("🛡️ SIR HEIMDALL: The Bifrost Port is Opening...")
    print(f"📂 Vault Drop Zone: {BIFROST_DIR}")
    print("========================================================")
    # Binding to 0.0.0.0 exposes it to the Tailscale Mesh
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="warning")
