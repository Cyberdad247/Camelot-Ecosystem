"""Local LT Memory server for Camelot boot.

This is the localhost companion expected by control_plane.boot_sequence.
It mirrors the Modal LT-memory HTTP contract closely enough for local boot,
store, and synthesize flows without requiring a remote Modal deployment.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "memory" / "lt_local"
MEMORY_LOG = DATA_DIR / "memories.jsonl"

app = FastAPI(title="Camelot Local LT Memory", version="1.0")


class StoreRequest(BaseModel):
    title: str
    content: str


class SynthesizeRequest(BaseModel):
    query: str
    limit: int = 5


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_LOG.touch(exist_ok=True)


def _iter_memories() -> list[dict]:
    _ensure_store()
    records: list[dict] = []
    for line in MEMORY_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _score(query: str, record: dict) -> int:
    haystack = f"{record.get('title', '')} {record.get('content', '')}".lower()
    terms = [term for term in query.lower().split() if term]
    return sum(1 for term in terms if term in haystack)


@app.get("/health")
async def health() -> dict:
    records = _iter_memories()
    return {
        "status": "online",
        "service": "camelot-local-lt-memory",
        "backend": "jsonl",
        "records": len(records),
        "path": str(MEMORY_LOG),
    }


@app.post("/store")
async def store(payload: StoreRequest) -> dict:
    _ensure_store()
    t0 = time.perf_counter()
    doc = {
        "id": str(uuid.uuid4()),
        "title": payload.title,
        "content": payload.content,
        "chars": len(payload.content),
        "ts": _utc_now(),
    }
    with MEMORY_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(doc, ensure_ascii=True) + "\n")
    return {
        "status": "stored",
        "document_id": doc["id"],
        "chars": doc["chars"],
        "ms": round((time.perf_counter() - t0) * 1000),
    }


@app.post("/synthesize")
async def synthesize(payload: SynthesizeRequest) -> dict:
    t0 = time.perf_counter()
    records = _iter_memories()
    ranked = sorted(records, key=lambda record: _score(payload.query, record), reverse=True)
    matches = [record for record in ranked if _score(payload.query, record) > 0][: payload.limit]
    if not matches:
        matches = ranked[-payload.limit :]
    snippets = [
        f"{record.get('title', 'Untitled')}: {record.get('content', '')[:240]}"
        for record in matches
    ]
    return {
        "result": "\n\n".join(snippets) if snippets else "[LT: no memories stored yet]",
        "sources": len(matches),
        "query": payload.query,
        "ms": round((time.perf_counter() - t0) * 1000),
    }
