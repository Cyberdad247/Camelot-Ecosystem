"""Camelot voice pipeline.

Canonical repo-owned replacement for the deployed Modal app
`camelot-voice-pipeline`.

Primary role:
- speech-to-text entrypoint for uploaded audio

Explicit non-role:
- not a long-term memory owner
- does not replace excalibur-brain or NotebookLM
"""

from __future__ import annotations

import base64
import os
from typing import Any

import modal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


APP_NAME = "camelot-voice-pipeline"
web_app = FastAPI(title=APP_NAME)
app = modal.App(APP_NAME)

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "pydantic",
    "httpx",
)


class TranscriptionRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded audio payload.")
    mime_type: str = Field(default="audio/wav")
    filename: str = Field(default="input.wav")
    model: str = Field(default="gpt-4o-mini-transcribe")
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranscriptionResponse(BaseModel):
    status: str
    transcript: str | None = None
    provider: str | None = None
    service_role: str = "speech_to_text"
    memory_owner: str = "none"
    notes: list[str] = Field(default_factory=list)


def _decode_audio(audio_base64: str) -> bytes:
    try:
        return base64.b64decode(audio_base64)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=f"Invalid audio_base64 payload: {exc}") from exc


async def _transcribe_via_openai(request: TranscriptionRequest) -> TranscriptionResponse:
    import httpx

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return TranscriptionResponse(
            status="NOT_CONFIGURED",
            provider="openai",
            notes=[
                "OPENAI_API_KEY is missing.",
                "This canonical replacement preserves the endpoint contract but needs provider credentials.",
            ],
        )

    audio_bytes = _decode_audio(request.audio_base64)
    files = {
        "file": (request.filename, audio_bytes, request.mime_type),
    }
    data = {
        "model": request.model,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            data=data,
            files=files,
        )
        response.raise_for_status()
        payload = response.json()

    transcript = str(payload.get("text") or "").strip()
    return TranscriptionResponse(
        status="SUCCESS",
        transcript=transcript,
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
        "service_role": "speech_to_text",
        "memory_owner": "none",
    }


@web_app.post("/transcribe_audio", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest) -> TranscriptionResponse:
    return await _transcribe_via_openai(request)
