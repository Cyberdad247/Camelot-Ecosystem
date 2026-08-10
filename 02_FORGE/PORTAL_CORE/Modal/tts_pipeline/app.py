"""Camelot TTS pipeline.

Canonical repo-owned replacement for the deployed Modal app
`camelot-tts-pipeline`.
"""

from __future__ import annotations

import base64
import os
from typing import Any

import modal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

APP_NAME = "camelot-tts-pipeline"
web_app = FastAPI(title=APP_NAME)
app = modal.App(APP_NAME)

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "pydantic",
    "httpx",
)


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice: str = Field(default="nova")
    model: str = Field(default="gpt-4o-mini-tts")
    response_format: str = Field(default="mp3")


class TTSResponse(BaseModel):
    status: str
    audio_base64: str | None = None
    mime_type: str | None = None
    provider: str | None = None
    service_role: str = "text_to_speech"
    memory_owner: str = "none"
    notes: list[str] = Field(default_factory=list)


async def _synthesize_via_openai(request: TTSRequest) -> TTSResponse:
    import httpx

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return TTSResponse(
            status="NOT_CONFIGURED",
            provider="openai",
            notes=[
                "OPENAI_API_KEY is missing.",
                "This canonical replacement preserves the endpoint contract but needs provider credentials.",
            ],
        )

    payload = {
        "model": request.model,
        "voice": request.voice,
        "input": request.text,
        "format": request.response_format,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
        response.raise_for_status()
        audio_bytes = response.content

    if not audio_bytes:
        raise HTTPException(status_code=502, detail="Provider returned an empty audio payload.")

    return TTSResponse(
        status="SUCCESS",
        audio_base64=base64.b64encode(audio_bytes).decode("ascii"),
        mime_type=f"audio/{request.response_format}",
        provider="openai",
        notes=[
            "Canonical repo-owned replacement implementation.",
            "This service is peripheral and does not own long-term or short-term memory.",
        ],
    )


@app.function(image=image, timeout=300, memory=1024, secrets=[modal.Secret.from_name("my-sovereign-secrets")])
@modal.asgi_app()
def fastapi_app():
    return web_app


@web_app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "alive",
        "service": APP_NAME,
        "service_role": "text_to_speech",
        "memory_owner": "none",
    }


@web_app.post("/synthesize_speech", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest) -> TTSResponse:
    return await _synthesize_via_openai(request)
