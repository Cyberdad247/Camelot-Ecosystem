# -*- coding: utf-8 -*-
"""
modal_lt_server.py — CAMELOT Long-Term Memory (Modal Volume backend)
=====================================================================
Replaces Appwrite with a Modal Volume — zero external accounts required.
All memory is persisted on a Modal NFS volume (camelot-lt-vol) and survives
container restarts / scale-to-zero cycles.

Deploy: modal deploy 03_VAULT/training/configs/modal_lt_server.py
Test:   curl https://cyberdad247--camelot-lt-memory-health.modal.run

Architecture:
  integration_brain._lt_*() → HTTP → Modal FastAPI → Volume JSON store
  Volume layout:
    /data/memories.jsonl   — append-only record log
    /data/index.json       — {id: {title, chars, ts, embedding[128]}} lookup
"""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import modal

# ── Modal primitives ──────────────────────────────────────────────────────────

app = modal.App("camelot-lt-memory")

lt_vol = modal.Volume.from_name("camelot-lt-vol", create_if_missing=True)
VOL_PATH = Path("/data")

lt_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi>=0.111",
        "uvicorn>=0.29",
        "numpy>=1.26",
        "sentence-transformers>=2.7",
    )
)

lt_gpu = "T4"

# ── Volume helpers ────────────────────────────────────────────────────────────

def _memories_path() -> Path:
    return VOL_PATH / "memories.jsonl"

def _index_path() -> Path:
    return VOL_PATH / "index.json"

def _load_index() -> dict:
    p = _index_path()
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return {}
    return {}

def _save_index(idx: dict) -> None:
    _index_path().write_text(json.dumps(idx))

def _append_memory(doc: dict) -> None:
    with _memories_path().open("a") as f:
        f.write(json.dumps(doc) + "\n")

def _cosine_search(query_emb: list[float], limit: int = 5) -> list[dict]:
    import numpy as np
    idx = _load_index()
    if not idx:
        return []
    q = np.array(query_emb[:128], dtype=float)
    scored: list[tuple[float, dict]] = []
    mem_path = _memories_path()
    if not mem_path.exists():
        return []
    # Build id→full_doc map from JSONL
    docs_by_id: dict[str, dict] = {}
    for line in mem_path.read_text().splitlines():
        try:
            d = json.loads(line)
            docs_by_id[d["id"]] = d
        except Exception:
            continue
    for doc_id, meta in idx.items():
        try:
            emb = np.array(meta["embedding"][:128], dtype=float)
            score = float(np.dot(q, emb) / (np.linalg.norm(q) * np.linalg.norm(emb) + 1e-9))
            scored.append((score, docs_by_id.get(doc_id, meta)))
        except Exception:
            continue
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:limit]]


# ── Embedding service (GPU singleton) ────────────────────────────────────────

@app.cls(image=lt_image, gpu=lt_gpu, volumes={str(VOL_PATH): lt_vol})
class EmbeddingService:
    @modal.enter()
    def load(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    @modal.method()
    def embed(self, texts: list[str]) -> list[list[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vecs]


# ── FastAPI endpoints ─────────────────────────────────────────────────────────

@app.function(image=lt_image, volumes={str(VOL_PATH): lt_vol})
@modal.fastapi_endpoint(method="GET")
async def health() -> dict:
    idx = _load_index()
    return {
        "status": "online",
        "service": "camelot-lt-memory",
        "backend": "Modal Volume (camelot-lt-vol)",
        "memories": len(idx),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@app.function(image=lt_image, gpu=lt_gpu, volumes={str(VOL_PATH): lt_vol})
@modal.fastapi_endpoint(method="POST")
async def store(title: str, content: str) -> dict:
    """Embed and persist content to Modal Volume."""
    t0 = time.perf_counter()
    VOL_PATH.mkdir(parents=True, exist_ok=True)
    svc = EmbeddingService()
    embedding = (await svc.embed.remote.aio([content[:512]]))[0]
    doc_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": doc_id, "title": title,
        "content": content, "ts": ts,
        "chars": len(content), "embedding": embedding[:128],
    }
    _append_memory(doc)
    idx = _load_index()
    idx[doc_id] = {"title": title, "ts": ts, "chars": len(content), "embedding": embedding[:128]}
    _save_index(idx)
    lt_vol.commit()
    ms = (time.perf_counter() - t0) * 1000
    return {
        "status": "stored", "document_id": doc_id,
        "chars": len(content), "embedding_dims": len(embedding), "ms": round(ms),
    }


@app.function(image=lt_image, gpu=lt_gpu, volumes={str(VOL_PATH): lt_vol})
@modal.fastapi_endpoint(method="POST")
async def synthesize(query: str) -> dict:
    """Semantic search over Volume memory."""
    t0 = time.perf_counter()
    svc = EmbeddingService()
    q_emb = (await svc.embed.remote.aio([query[:512]]))[0]
    docs = _cosine_search(q_emb, limit=5)
    synthesis = "\n\n---\n\n".join(
        f"## {d.get('title','(untitled)')}\n{d.get('content','')[:800]}"
        for d in docs
    )
    ms = (time.perf_counter() - t0) * 1000
    return {
        "result": synthesis or "[LT: no memories stored yet]",
        "sources": len(docs), "query": query, "ms": round(ms),
    }


# ── Local test ────────────────────────────────────────────────────────────────

@app.local_entrypoint()
def main():
    import asyncio
    async def _test():
        h = await health.remote.aio()
        print("Health:", h)
    asyncio.run(_test())
