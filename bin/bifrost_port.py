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
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

app = FastAPI(title="Bifrost Port", description="24/7 Mesh Communication and File Transfer")

# The Secure Vault Drop Zone
BIFROST_DIR = Path(os.path.expanduser("~/CAMELOT_OS/03_VAULT/bifrost_drop")).resolve()
BIFROST_DIR.mkdir(parents=True, exist_ok=True)
MESSAGES_FILE = BIFROST_DIR / "comms_log.json"

if not MESSAGES_FILE.exists():
    MESSAGES_FILE.write_text("[]", encoding="utf-8")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Anya's Kinetic Drop - Securely receive files into the Vault."""
    file_path = BIFROST_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)
    print(f"📥 [ANYA]: Kinetic Drop Secured -> {file.filename} ({len(content)} bytes)")
    return {"status": "success", "filename": file.filename, "size": len(content)}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Merlin's Retrieval - Securely fetch files from the Vault."""
    file_path = BIFROST_DIR / filename
    if not file_path.exists():
        print(f"❌ [MERLIN]: File '{filename}' lost in the void.")
        raise HTTPException(status_code=404, detail="File lost in the void.")
    print(f"📤 [MERLIN]: Retrieval Authorized -> {filename}")
    return FileResponse(path=file_path, filename=filename)

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
