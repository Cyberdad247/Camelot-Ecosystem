"""Camelot RustDesk server descriptor.

Canonical repo-owned replacement for the deployed Modal app
`camelot-rustdesk-server`.

This service documents and exposes the control surface only. It does not claim
to be a memory owner.
"""

from __future__ import annotations

import os
from typing import Any

import modal
from fastapi import FastAPI
from pydantic import BaseModel, Field

APP_NAME = "camelot-rustdesk-server"
web_app = FastAPI(title=APP_NAME)
app = modal.App(APP_NAME)

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "pydantic",
)


class RustDeskRequest(BaseModel):
    target_host: str = Field(default="127.0.0.1")
    relay_host: str | None = None
    api_port: int = Field(default=21117)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RustDeskResponse(BaseModel):
    status: str
    service_role: str = "remote_access"
    memory_owner: str = "none"
    endpoint: str | None = None
    notes: list[str] = Field(default_factory=list)


@app.function(image=image, timeout=300, memory=512)
@modal.asgi_app()
def fastapi_app():
    return web_app


@web_app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "alive",
        "service": APP_NAME,
        "service_role": "remote_access",
        "memory_owner": "none",
    }


@web_app.post("/run_rustdesk", response_model=RustDeskResponse)
async def run_rustdesk(request: RustDeskRequest) -> RustDeskResponse:
    endpoint = request.relay_host or os.environ.get("RUSTDESK_RELAY_HOST") or request.target_host
    return RustDeskResponse(
        status="READY",
        endpoint=endpoint,
        notes=[
            "Canonical repo-owned replacement descriptor for the Modal app surface.",
            "No long-term or short-term memory ownership is implied.",
        ],
    )
