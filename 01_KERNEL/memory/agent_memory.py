# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY

# -*- coding: utf-8 -*-
"""
Redis Agent Memory — Python client for @redis-iris/agent-memory v0.0.5
=======================================================================
Session memory (chat turns) and long-term semantic memory backed by
the Redis Agent Memory cloud API (gcp-us-east4.memory.redis.io).

Routes (all prefixed /v1/stores/{storeId}/):
  POST   session-memory/events        add a chat turn
  GET    session-memory               list sessions
  GET    session-memory/{sessionId}   get session turns
  POST   long-term-memory             bulk create memories
  POST   long-term-memory/search      semantic search
  PATCH  long-term-memory/{id}        update memory
  DELETE long-term-memory             bulk delete

Config (env vars):
  REDIS_AGENT_MEMORY_URL        https://gcp-us-east4.memory.redis.io
  REDIS_AGENT_MEMORY_STORE_ID   9554270fe8574d1ea5f5fb40140b4b7b
  REDIS_AGENT_MEMORY_API_KEY    mem1_...
"""

from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone
from typing import Any

import httpx

_BASE_URL = os.environ.get("REDIS_AGENT_MEMORY_URL", "https://gcp-us-east4.memory.redis.io")
_STORE_ID = os.environ.get("REDIS_AGENT_MEMORY_STORE_ID", "")
_API_KEY  = os.environ.get("REDIS_AGENT_MEMORY_API_KEY", "")

_TIMEOUT       = httpx.Timeout(10.0, connect=5.0)
_RETRY_MAX     = 3
_RETRY_BACKOFF = 1.5


def _prefix() -> str:
    return f"{_BASE_URL.rstrip('/')}/v1/stores/{_STORE_ID}"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json",
    }


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _post(path: str, body: dict) -> dict:
    url = f"{_prefix()}{path}"
    for attempt in range(_RETRY_MAX):
        try:
            resp = httpx.post(url, json=body, headers=_headers(), timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500 or attempt == _RETRY_MAX - 1:
                raise
        except (httpx.ConnectError, httpx.TimeoutException):
            if attempt == _RETRY_MAX - 1:
                raise
        time.sleep(_RETRY_BACKOFF * (attempt + 1))
    return {}


def _get(path: str, params: dict | None = None) -> dict:
    url = f"{_prefix()}{path}"
    for attempt in range(_RETRY_MAX):
        try:
            resp = httpx.get(url, params=params, headers=_headers(), timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500 or attempt == _RETRY_MAX - 1:
                raise
        except (httpx.ConnectError, httpx.TimeoutException):
            if attempt == _RETRY_MAX - 1:
                raise
        time.sleep(_RETRY_BACKOFF * (attempt + 1))
    return {}


# ---------------------------------------------------------------------------
# Session Memory
# ---------------------------------------------------------------------------

def add_session_event(
    session_id: str,
    actor_id: str,
    role: str,                        # "USER" | "ASSISTANT" | "SYSTEM"
    content: str | list[dict],
    created_at: str | None = None,
) -> dict:
    """Append a chat turn to session memory."""
    if isinstance(content, str):
        content = [{"text": content}]
    payload: dict[str, Any] = {
        "sessionId": session_id,
        "actorId": actor_id,
        "role": role.upper(),
        "content": content,
        "createdAt": created_at or _iso_now(),
    }
    return _post("/session-memory/events", payload)


def list_sessions() -> dict:
    """List all sessions in this store."""
    return _get("/session-memory")


def get_session_memory(session_id: str) -> dict:
    """Retrieve all turns for a session."""
    return _get(f"/session-memory/{session_id}")


# ---------------------------------------------------------------------------
# Long-term Memory
# ---------------------------------------------------------------------------

def bulk_create_long_term_memories(memories: list[dict]) -> dict:
    """
    Store facts/knowledge for semantic retrieval.

    memories: [{"id": "mem-1", "text": "fact", "memoryType": "semantic"}]
    memoryType options: "semantic" | "episodic" | "message"
    """
    return _post("/long-term-memory", {"memories": memories})


def search_long_term_memory(text: str, limit: int = 5) -> list[dict]:
    """Semantic search over long-term memories. Returns ranked results."""
    resp = _post("/long-term-memory/search", {"text": text, "limit": limit})
    return resp.get("items", resp.get("results", []))


def bulk_delete_long_term_memories(ids: list[str]) -> dict:
    """Bulk delete long-term memories by ID."""
    url = f"{_prefix()}/long-term-memory"
    for attempt in range(_RETRY_MAX):
        try:
            resp = httpx.request("DELETE", url, json={"ids": ids}, headers=_headers(), timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500 or attempt == _RETRY_MAX - 1:
                raise
        except (httpx.ConnectError, httpx.TimeoutException):
            if attempt == _RETRY_MAX - 1:
                raise
        time.sleep(_RETRY_BACKOFF * (attempt + 1))
    return {}


# ---------------------------------------------------------------------------
# Health probe
# ---------------------------------------------------------------------------

def ping() -> tuple[bool, int, str]:
    """
    Probe the Agent Memory service.
    Returns (reachable, status_code, message).
    """
    if not _API_KEY or not _STORE_ID:
        return False, 0, "not configured (missing env vars)"
    try:
        r = httpx.get(
            f"{_BASE_URL.rstrip('/')}/health",
            timeout=httpx.Timeout(5.0, connect=3.0),
        )
        if r.status_code != 200:
            return False, r.status_code, f"health check failed ({r.status_code})"

        r2 = httpx.get(
            f"{_prefix()}/session-memory",
            headers=_headers(),
            timeout=httpx.Timeout(5.0, connect=3.0),
        )
        if 200 <= r2.status_code < 300:
            return True, r2.status_code, "live + authenticated"
        return False, r2.status_code, f"service live but auth rejected ({r2.status_code})"
    except Exception as e:
        return False, 0, f"unreachable: {e.__class__.__name__}"


# ---------------------------------------------------------------------------
# Module-level singleton (mirrors local_store usage pattern)
# ---------------------------------------------------------------------------

class AgentMemoryClient:
    """Drop-in integration point for HydrationManager L1.5 tier."""

    def is_configured(self) -> bool:
        return bool(_API_KEY and _STORE_ID)

    def add_turn(self, session_id: str, role: str, text: str, actor_id: str = "camelot") -> bool:
        try:
            add_session_event(session_id, actor_id, role, text)
            return True
        except Exception:
            return False

    def get_session(self, session_id: str) -> dict | None:
        try:
            return get_session_memory(session_id)
        except Exception:
            return None

    def store_fact(self, id: str, text: str) -> bool:
        safe_id = re.sub(r"[^A-Za-z0-9-]", "-", id)[:200]
        try:
            bulk_create_long_term_memories([{"id": safe_id, "text": text, "memoryType": "semantic"}])
            return True
        except Exception:
            return False

    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        try:
            return search_long_term_memory(query, top_k)
        except Exception:
            return []

    def purge_all(self) -> bool:
        try:
            recalled = search_long_term_memory("*", limit=100)
            ids = [item["id"] for item in recalled if "id" in item]
            if ids:
                bulk_delete_long_term_memories(ids)
            return True
        except Exception:
            return False

    def ping(self) -> tuple[bool, int, str]:
        return ping()


agent_memory = AgentMemoryClient()
