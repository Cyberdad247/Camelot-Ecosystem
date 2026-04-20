# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import base64
import os

import requests
from pydantic import BaseModel

import modal

# 1. THE IMAGE (Must include GitPython)
app = modal.App("excalibur-bridge")
image = modal.Image.debian_slim().pip_install("pydantic", "GitPython", "requests")


class CommitRequest(BaseModel):
    file_path: str
    content: str
    message: str


# 2. THE CORE LOGIC (Decoupled)
def sync_logic(request: CommitRequest):
    print(f"KERNEL_LOG: Writing to {request.file_path}")

    # GITHUB PUSH
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        # Fallback to check if user set it in a different var or default
        return {"status": "ERROR", "log": "Missing GITHUB_TOKEN"}

    REPO = "Cyberdad247/awesome-chatgpt-prompts"
    BRANCH = "Camelot"  # Ensure this branch exists or use main
    URL = f"https://api.github.com/repos/{REPO}/contents/{request.file_path}"

    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

    # 1. Get current file sha (if it exists) to overwrite
    resp = requests.get(URL, headers=headers)
    sha = resp.json().get("sha") if resp.status_code == 200 else None

    # 2. Push the Titanium Asset
    # Content must be base64 encoded
    encoded_content = base64.b64encode(request.content.encode("utf-8")).decode("utf-8")

    data = {"message": request.message, "content": encoded_content, "branch": BRANCH}
    if sha:
        data["sha"] = sha

    put_resp = requests.put(URL, headers=headers, json=data)

    if put_resp.status_code in [200, 201]:
        return {"status": "SUCCESS", "url": put_resp.json()["content"]["html_url"]}
    else:
        return {"status": "ERROR", "log": put_resp.text}


# 3. MODAL ENTRYPOINT
@app.function(image=image, secrets=[modal.Secret.from_name("github-token")])
@modal.web_endpoint(method="POST")
def sync_to_repo(request: CommitRequest):
    return sync_logic(request)


# 4. LOCAL ENTRYPOINT (FastAPI)
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    local_app = FastAPI()
    local_app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )

    @local_app.post("/")
    def local_endpoint(request: CommitRequest):
        return sync_logic(request)

    print("⚔️ EXCALIBUR BRIDGE: LOCAL SERVER ONLINE AT http://localhost:8005")
    uvicorn.run(local_app, host="0.0.0.0", port=8005)