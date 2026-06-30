# -*- coding: utf-8 -*-
"""
[S8-03] QdrantStore — Semantic vector memory with graceful dark-mode fallback
=============================================================================
Wraps qdrant_client for upsert + search against a local Qdrant instance (:6333).
Falls back silently to an in-memory dict store when Qdrant is unreachable.

Usage:
    from qdrant_store import qdrant_store

    qdrant_store.upsert("knight_memory", id="t1", vector=[0.1, ...], payload={"text": "..."})
    hits = qdrant_store.search("knight_memory", vector=[0.1, ...], limit=5)

Each hit: {"id": str, "score": float, "payload": dict}
"""
from __future__ import annotations

import os
import time
from typing import Any

QDRANT_URL  = os.environ.get("QDRANT_URL", "")          # cloud: https://...qdrant.io
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "")   # cloud JWT
QDRANT_HOST = os.environ.get("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
VECTOR_SIZE = int(os.environ.get("QDRANT_VECTOR_SIZE", "384"))  # all-MiniLM-L6-v2 default
DISTANCE    = os.environ.get("QDRANT_DISTANCE", "Cosine")


class _DarkStore:
    """In-memory fallback when Qdrant is unreachable."""

    def __init__(self) -> None:
        self._store: dict[str, list[dict]] = {}

    def upsert(self, collection: str, id: str, vector: list[float], payload: dict) -> None:
        self._store.setdefault(collection, [])
        self._store[collection] = [r for r in self._store[collection] if r["id"] != id]
        self._store[collection].append({"id": id, "vector": vector, "payload": payload})

    def search(self, collection: str, vector: list[float], limit: int = 5) -> list[dict]:
        import math
        rows = self._store.get(collection, [])
        if not rows:
            return []

        def _cosine(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(x * x for x in b))
            return dot / (na * nb) if na and nb else 0.0

        scored = sorted(rows, key=lambda r: _cosine(vector, r["vector"]), reverse=True)
        return [{"id": r["id"], "score": _cosine(vector, r["vector"]), "payload": r["payload"]}
                for r in scored[:limit]]

    def delete(self, collection: str, id: str) -> None:
        if collection in self._store:
            self._store[collection] = [r for r in self._store[collection] if r["id"] != id]

    @property
    def backend(self) -> str:
        return "dark"


class QdrantStore:
    """Live Qdrant client with transparent fallback to _DarkStore."""

    def __init__(self) -> None:
        self._client = None
        self._dark = _DarkStore()
        self._last_attempt: float = 0
        self._retry_interval: float = 30.0
        self._connect()

    def _connect(self) -> bool:
        try:
            from qdrant_client import QdrantClient
            if QDRANT_URL and QDRANT_API_KEY:
                # Cloud: HTTPS + JWT auth
                c = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=10.0)
            else:
                # Local: plain TCP
                c = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=2.0)
            c.get_collections()  # probe
            self._client = c
            return True
        except Exception:
            self._client = None
            return False

    def _live(self) -> bool:
        if self._client is not None:
            return True
        now = time.monotonic()
        if now - self._last_attempt >= self._retry_interval:
            self._last_attempt = now
            return self._connect()
        return False

    def _ensure_collection(self, collection: str, size: int) -> None:
        from qdrant_client.models import Distance, VectorParams
        existing = {c.name for c in self._client.get_collections().collections}
        if collection not in existing:
            # qdrant_client >=1.7 uses Distance.COSINE (uppercase); fall back for older
            dist = getattr(Distance, DISTANCE.upper(), getattr(Distance, DISTANCE, Distance.COSINE))
            self._client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=size, distance=dist),
            )

    def upsert(self, collection: str, id: str, vector: list[float], payload: dict | None = None) -> bool:
        """Insert or overwrite a vector. Returns True on success."""
        payload = payload or {}
        if not self._live():
            self._dark.upsert(collection, id, vector, payload)
            return False
        try:
            from qdrant_client.models import PointStruct
            self._ensure_collection(collection, len(vector))
            self._client.upsert(
                collection_name=collection,
                points=[PointStruct(id=_str_to_uint(id), vector=vector, payload={**payload, "_id": id})],
            )
            return True
        except Exception:
            self._client = None
            self._dark.upsert(collection, id, vector, payload)
            return False

    def search(self, collection: str, vector: list[float], limit: int = 5) -> list[dict]:
        """Return top-k nearest neighbours as [{id, score, payload}]."""
        if not self._live():
            return self._dark.search(collection, vector, limit)
        try:
            self._ensure_collection(collection, len(vector))
            # qdrant_client >=1.14 uses query_points; fall back to search for older versions
            if hasattr(self._client, "query_points"):
                resp = self._client.query_points(
                    collection_name=collection,
                    query=vector,
                    limit=limit,
                )
                hits = resp.points
            else:
                hits = self._client.search(
                    collection_name=collection,
                    query_vector=vector,
                    limit=limit,
                )
            return [
                {"id": h.payload.get("_id", str(h.id)), "score": h.score, "payload": h.payload}
                for h in hits
            ]
        except Exception:
            self._client = None
            return self._dark.search(collection, vector, limit)

    def delete(self, collection: str, id: str) -> bool:
        """Delete a point by string id. Returns True if Qdrant was live."""
        if not self._live():
            self._dark.delete(collection, id)
            return False
        try:
            from qdrant_client.models import PointIdsList
            self._client.delete(
                collection_name=collection,
                points_selector=PointIdsList(points=[_str_to_uint(id)]),
            )
            return True
        except Exception:
            self._client = None
            self._dark.delete(collection, id)
            return False

    @property
    def backend(self) -> str:
        return "qdrant" if self._client is not None else "dark"

    def stats(self) -> dict:
        info: dict[str, Any] = {"backend": self.backend}
        if self._client is not None:
            try:
                cols = self._client.get_collections().collections
                info["collections"] = {c.name: c.vectors_count for c in cols}
            except Exception:
                pass
        return info


def _str_to_uint(s: str) -> int:
    """Stable uint64 from a string id (for Qdrant point ids)."""
    import hashlib
    return int(hashlib.md5(s.encode()).hexdigest()[:16], 16) % (2 ** 63)


# Module-level singleton
qdrant_store = QdrantStore()
