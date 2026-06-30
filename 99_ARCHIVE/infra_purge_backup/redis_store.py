# -*- coding: utf-8 -*-
"""
Redis-backed memory store — replaces QdrantStore
=================================================
Uses Redis hashes for vector + payload persistence with Python-side
cosine similarity on retrieval.  Falls back to an in-process dict store
when Redis is unreachable (same _DarkStore as qdrant_store).

Collections map to Redis hash keys:  camelot:mem:{collection}:{id}
Index set per collection:            camelot:mem:{collection}:__ids__

Usage:
    from redis_store import redis_store

    redis_store.upsert("knight_memory", id="t1", vector=[0.1,...], payload={"text":"..."})
    hits = redis_store.search("knight_memory", vector=[0.1,...], limit=5)
    redis_store.delete("knight_memory", id="t1")

Response-channel helpers (pub/sub):
    redis_store.publish(channel, message)          # worker calls this
    redis_store.subscribe_one(channel, timeout)    # AudioSession calls this
"""
from __future__ import annotations

import json
import math
import os
import time
from typing import Any

REDIS_HOST    = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT    = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB      = int(os.environ.get("REDIS_DB", "0"))
KEY_PREFIX    = "camelot:mem"
CHAN_PREFIX   = "camelot:resp"
RETRY_INTERVAL = 30.0  # seconds between reconnect attempts


# ── Pure-Python fallback ──────────────────────────────────────────────────────

class _DarkStore:
    def __init__(self) -> None:
        self._cols: dict[str, dict[str, dict]] = {}

    def upsert(self, col: str, id: str, vector: list[float], payload: dict) -> None:
        self._cols.setdefault(col, {})[id] = {"vector": vector, "payload": payload}

    def search(self, col: str, vector: list[float], limit: int) -> list[dict]:
        rows = self._cols.get(col, {})
        scored = sorted(
            rows.items(),
            key=lambda kv: _cosine(vector, kv[1]["vector"]),
            reverse=True,
        )
        return [
            {"id": k, "score": _cosine(vector, v["vector"]), "payload": v["payload"]}
            for k, v in scored[:limit]
        ]

    def delete(self, col: str, id: str) -> None:
        self._cols.get(col, {}).pop(id, None)

    def publish(self, channel: str, message: str) -> None:
        pass  # no-op in dark mode

    def subscribe_one(self, channel: str, timeout: float) -> str | None:
        return None


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


# ── Redis store ───────────────────────────────────────────────────────────────

class RedisStore:
    """Persistent vector memory + pub/sub response channel backed by Redis."""

    def __init__(self) -> None:
        self._r = None
        self._dark = _DarkStore()
        self._last_attempt: float = 0.0
        self._connect()

    # ── Connection ────────────────────────────────────────────────────────────

    def _connect(self) -> bool:
        try:
            import redis as _redis
            r = _redis.Redis(
                host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
                socket_connect_timeout=1.0, socket_timeout=1.0,
                decode_responses=True,
            )
            r.ping()
            self._r = r
            return True
        except Exception:
            self._r = None
            return False

    def _live(self) -> bool:
        if self._r is not None:
            try:
                self._r.ping()
                return True
            except Exception:
                self._r = None
        now = time.monotonic()
        if now - self._last_attempt >= RETRY_INTERVAL:
            self._last_attempt = now
            return self._connect()
        return False

    @property
    def backend(self) -> str:
        return "redis" if self._r is not None else "dark"

    # ── Vector memory ─────────────────────────────────────────────────────────

    def upsert(self, collection: str, id: str, vector: list[float], payload: dict | None = None) -> bool:
        payload = payload or {}
        if not self._live():
            self._dark.upsert(collection, id, vector, payload)
            return False
        try:
            key = f"{KEY_PREFIX}:{collection}:{id}"
            self._r.hset(key, mapping={
                "vector":  json.dumps(vector),
                "payload": json.dumps(payload),
            })
            self._r.sadd(f"{KEY_PREFIX}:{collection}:__ids__", id)
            return True
        except Exception:
            self._r = None
            self._dark.upsert(collection, id, vector, payload)
            return False

    def search(self, collection: str, vector: list[float], limit: int = 5) -> list[dict]:
        if not self._live():
            return self._dark.search(collection, vector, limit)
        try:
            ids = list(self._r.smembers(f"{KEY_PREFIX}:{collection}:__ids__"))
            if not ids:
                return []
            pipe = self._r.pipeline()
            for id in ids:
                pipe.hgetall(f"{KEY_PREFIX}:{collection}:{id}")
            rows = pipe.execute()
            scored = []
            for id, row in zip(ids, rows):
                if not row:
                    continue
                v = json.loads(row["vector"])
                p = json.loads(row["payload"])
                scored.append({"id": id, "score": _cosine(vector, v), "payload": p})
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:limit]
        except Exception:
            self._r = None
            return self._dark.search(collection, vector, limit)

    def delete(self, collection: str, id: str) -> bool:
        if not self._live():
            self._dark.delete(collection, id)
            return False
        try:
            self._r.delete(f"{KEY_PREFIX}:{collection}:{id}")
            self._r.srem(f"{KEY_PREFIX}:{collection}:__ids__", id)
            return True
        except Exception:
            self._r = None
            self._dark.delete(collection, id)
            return False

    # ── Response channel (pub/sub) ────────────────────────────────────────────

    def publish(self, channel: str, message: str) -> bool:
        """Publish a message to a response channel. Returns True if Redis is live."""
        if not self._live():
            return False
        try:
            self._r.publish(f"{CHAN_PREFIX}:{channel}", message)
            return True
        except Exception:
            self._r = None
            return False

    def subscribe_one(self, channel: str, timeout: float = 30.0) -> str | None:
        """Block until a message arrives on the channel or timeout. Returns message or None."""
        if not self._live():
            return None
        try:
            import redis as _redis
            # Use a separate non-decoded connection for pubsub
            r2 = _redis.Redis(
                host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
                socket_connect_timeout=1.0, decode_responses=True,
            )
            ps = r2.pubsub()
            ps.subscribe(f"{CHAN_PREFIX}:{channel}")
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                msg = ps.get_message(ignore_subscribe_messages=True, timeout=0.5)
                if msg and msg["type"] == "message":
                    ps.unsubscribe()
                    r2.close()
                    return msg["data"]
            ps.unsubscribe()
            r2.close()
            return None
        except Exception:
            self._r = None
            return None

    def stats(self) -> dict[str, Any]:
        info: dict[str, Any] = {"backend": self.backend}
        if self._r is not None:
            try:
                info["redis_info"] = {
                    k: v for k, v in self._r.info("memory").items()
                    if k in ("used_memory_human", "maxmemory_human")
                }
                cols = {k.split(":")[2] for k in self._r.scan_iter(f"{KEY_PREFIX}:*:__ids__")}
                info["collections"] = list(cols)
            except Exception:
                pass
        return info


# ── Module-level singleton ────────────────────────────────────────────────────

redis_store = RedisStore()
