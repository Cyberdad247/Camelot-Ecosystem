# -*- coding: utf-8 -*-
"""
modal_lt_server.py — CAMELOT Long-Term Memory (Modal Deployment)
=================================================================
P2-A. Deploys open-notebooklm + Appwrite vector store on Modal GPU.

Deploy: modal deploy 03_VAULT/training/configs/modal_lt_server.py
Test:   modal run   03_VAULT/training/configs/modal_lt_server.py::health

After deploy, set ENV on the harness host:
  LONG_TERM_BACKEND=modal
  MODAL_ENDPOINT=https://<your-app>--camelot-lt-api-fastapi-app.modal.run
  APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1   (or self-hosted)
  APPWRITE_PROJECT=<project-id>
  APPWRITE_API_KEY=<api-key>

Architecture:
  integration_brain._lt_*() → HTTP → Modal FastAPI → Appwrite (Documents + Vector)
  Appwrite collections:
    - "lt_memory": title, content, tags, ts, embedding[]
    - "lt_index":  vector embeddings for semantic search
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any

import modal

# ── Modal App definition ─────────────────────────────────────────────────────

app = modal.App("camelot-lt-memory")

# Shared image — sentence-transformers for embeddings, httpx for Appwrite calls
lt_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi>=0.111",
        "uvicorn>=0.29",
        "httpx>=0.27",
        "sentence-transformers>=2.7",
        "numpy>=1.26",
    )
)

# GPU T4 for embedding generation (Modal free tier available)
lt_gpu = "T4"

# ── Appwrite client helper ────────────────────────────────────────────────────

APPWRITE_ENDPOINT = os.environ.get("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT  = os.environ.get("APPWRITE_PROJECT", "")
APPWRITE_API_KEY  = os.environ.get("APPWRITE_API_KEY", "")
COLLECTION_ID     = "lt_memory"
DATABASE_ID       = "camelot_lt"


async def _appwrite_headers() -> dict:
    return {
        "X-Appwrite-Project": APPWRITE_PROJECT,
        "X-Appwrite-Key":     APPWRITE_API_KEY,
        "Content-Type":       "application/json",
    }


async def _aw_create_document(title: str, content: str, embedding: list[float]) -> dict:
    import httpx
    doc = {
        "documentId": "unique()",
        "data": {
            "title": title,
            "content": content[:65_000],  # Appwrite 64KB doc limit
            "embedding": json.dumps(embedding[:128]),  # store first 128 dims
            "ts": datetime.now(timezone.utc).isoformat(),
            "chars": len(content),
        },
    }
    url = f"{APPWRITE_ENDPOINT}/databases/{DATABASE_ID}/collections/{COLLECTION_ID}/documents"
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(url, headers=await _appwrite_headers(), json=doc)
        r.raise_for_status()
        return r.json()


async def _aw_search(query_embedding: list[float], limit: int = 5) -> list[dict]:
    """Naive cosine search over stored embeddings — production: use Appwrite Vector Search."""
    import httpx
    import numpy as np
    url = f"{APPWRITE_ENDPOINT}/databases/{DATABASE_ID}/collections/{COLLECTION_ID}/documents"
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url, headers=await _appwrite_headers(),
                             params={"limit": 100})
        if r.status_code != 200:
            return []
    docs = r.json().get("documents", [])
    q = np.array(query_embedding[:128], dtype=float)
    scored: list[tuple[float, dict]] = []
    for doc in docs:
        try:
            emb = np.array(json.loads(doc["embedding"])[:128], dtype=float)
            score = float(np.dot(q, emb) / (np.linalg.norm(q) * np.linalg.norm(emb) + 1e-9))
            scored.append((score, doc))
        except Exception:
            continue
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:limit]]


# ── Embedding model (singleton on GPU container) ─────────────────────────────

@app.cls(image=lt_image, gpu=lt_gpu, secrets=[modal.Secret.from_name("camelot-lt-secrets")])
class EmbeddingService:
    def __enter__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        return self

    @modal.method()
    def embed(self, texts: list[str]) -> list[list[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vecs]


# ── FastAPI endpoints ─────────────────────────────────────────────────────────

@app.function(image=lt_image, secrets=[modal.Secret.from_name("camelot-lt-secrets")])
@modal.fastapi_endpoint(method="GET")
async def health() -> dict:
    return {
        "status": "online",
        "service": "camelot-lt-memory",
        "backend": "Modal + Appwrite",
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@app.function(
    image=lt_image,
    gpu=lt_gpu,
    secrets=[modal.Secret.from_name("camelot-lt-secrets")],
)
@modal.fastapi_endpoint(method="POST")
async def store(title: str, content: str) -> dict:
    """Store content in Appwrite with vector embedding."""
    t0 = time.perf_counter()
    svc = EmbeddingService()
    embedding = (await svc.embed.remote.aio([content[:512]]))[0]
    doc = await _aw_create_document(title, content, embedding)
    ms = (time.perf_counter() - t0) * 1000
    return {
        "status": "stored",
        "document_id": doc.get("$id", "unknown"),
        "chars": len(content),
        "embedding_dims": len(embedding),
        "ms": round(ms),
    }


@app.function(
    image=lt_image,
    gpu=lt_gpu,
    secrets=[modal.Secret.from_name("camelot-lt-secrets")],
)
@modal.fastapi_endpoint(method="POST")
async def synthesize(query: str) -> dict:
    """Semantic search + synthesis over LT memory."""
    t0 = time.perf_counter()
    svc = EmbeddingService()
    q_emb = (await svc.embed.remote.aio([query[:512]]))[0]
    docs = await _aw_search(q_emb, limit=5)
    # Concatenate top results for synthesis
    synthesis = "\n\n---\n\n".join(
        f"## {d.get('title','(untitled)')}\n{d.get('content','')[:800]}"
        for d in docs
    )
    ms = (time.perf_counter() - t0) * 1000
    return {
        "result": synthesis or "[LT: no matching memory]",
        "sources": len(docs),
        "query": query,
        "ms": round(ms),
    }


# ── Local test entry ──────────────────────────────────────────────────────────

@app.local_entrypoint()
def main():
    import asyncio
    async def _test():
        h = await health.remote.aio()
        print("Health:", h)
    asyncio.run(_test())
