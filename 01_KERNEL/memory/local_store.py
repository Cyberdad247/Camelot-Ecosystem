# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# -*- coding: utf-8 -*-
"""
Local-backed memory store
=================================================
Uses SQLite for vector + payload persistence with Python-side
cosine similarity on retrieval. 

Collections map to tables.

Usage:
    from local_store import local_store

    local_store.upsert("knight_memory", id="t1", vector=[0.1,...], payload={"text":"..."})
    hits = local_store.search("knight_memory", vector=[0.1,...], limit=5)
    local_store.delete("knight_memory", id="t1")

Response-channel helpers (pub/sub):
    local_store.publish(channel, message)          # worker calls this
    local_store.subscribe_one(channel, timeout)    # AudioSession calls this
"""
from __future__ import annotations

import json
import math
import sqlite3
import time
from pathlib import Path
from typing import Any

DB_PATH = Path("data/memory_store.sqlite3")


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


class LocalStore:
    """Persistent vector memory + pub/sub response channel backed by SQLite."""

    def __init__(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self._setup()
        self._channels: dict[str, list[str]] = {}

    def _setup(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vectors (
                    collection TEXT,
                    id TEXT,
                    vector TEXT,
                    payload TEXT,
                    PRIMARY KEY (collection, id)
                )
                """
            )

    @property
    def backend(self) -> str:
        return "sqlite"

    def upsert(self, collection: str, id: str, vector: list[float], payload: dict | None = None) -> bool:
        payload = payload or {}
        try:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO vectors (collection, id, vector, payload)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(collection, id) DO UPDATE SET
                        vector=excluded.vector,
                        payload=excluded.payload
                    """,
                    (collection, id, json.dumps(vector), json.dumps(payload))
                )
            return True
        except Exception:
            return False

    def search(self, collection: str, vector: list[float], limit: int = 5) -> list[dict]:
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "SELECT id, vector, payload FROM vectors WHERE collection = ?",
                (collection,)
            )
            rows = cursor.fetchall()
            scored = []
            for id, v_str, p_str in rows:
                v = json.loads(v_str)
                p = json.loads(p_str)
                scored.append({"id": id, "score": _cosine(vector, v), "payload": p})
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:limit]
        except Exception:
            return []

    def delete(self, collection: str, id: str) -> bool:
        try:
            with self._conn:
                self._conn.execute(
                    "DELETE FROM vectors WHERE collection = ? AND id = ?",
                    (collection, id)
                )
            return True
        except Exception:
            return False

    # ── Response channel (pub/sub) ────────────────────────────────────────────

    def publish(self, channel: str, message: str) -> bool:
        """Publish a message to a response channel."""
        try:
            if channel not in self._channels:
                self._channels[channel] = []
            self._channels[channel].append(message)
            return True
        except Exception:
            return False

    def subscribe_one(self, channel: str, timeout: float = 30.0) -> str | None:
        """Block until a message arrives on the channel or timeout. Returns message or None."""
        try:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if channel in self._channels and self._channels[channel]:
                    return self._channels[channel].pop(0)
                time.sleep(0.5)
            return None
        except Exception:
            return None

    def stats(self) -> dict[str, Any]:
        info: dict[str, Any] = {"backend": self.backend}
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT DISTINCT collection FROM vectors")
            cols = [row[0] for row in cursor.fetchall()]
            info["collections"] = cols
        except Exception:
            pass
        return info


local_store = LocalStore()
