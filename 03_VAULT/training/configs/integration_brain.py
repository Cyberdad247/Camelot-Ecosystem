"""
integration_brain.py — CAMELOT Unified Cloud Brain
Dual-tier memory router: NotebookLM (ST) + open-notebooklm/Appwrite via Modal (LT)

Tier routing:
  auto  → ST for session/synthesis; LT for archive/persist/search keywords
  short → NotebookLM only
  long  → Modal/Appwrite only
  both  → async fan-out, merge results

ENV:
  LONG_TERM_BACKEND=stub   (default) LT stubs gracefully until Modal deployed
  LONG_TERM_BACKEND=modal  route to Modal open-notebooklm endpoint
  MODAL_ENDPOINT=https://... Modal deployment URL
  APPWRITE_ENDPOINT=https://... Appwrite instance URL
  APPWRITE_PROJECT=...     Appwrite project ID
  APPWRITE_API_KEY=...     Appwrite API key
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any

# ── Config ──────────────────────────────────────────────────────────────────

LONG_TERM_BACKEND      = os.environ.get("LONG_TERM_BACKEND", "modal")
# Modal per-function URLs (deployed 2026-04-22)
_MODAL_BASE            = "https://cyberdad247--camelot-lt-memory"
MODAL_HEALTH_URL       = os.environ.get("MODAL_HEALTH_URL",    f"{_MODAL_BASE}-health.modal.run")
MODAL_STORE_URL        = os.environ.get("MODAL_STORE_URL",     f"{_MODAL_BASE}-store.modal.run")
MODAL_SYNTHESIZE_URL   = os.environ.get("MODAL_SYNTHESIZE_URL",f"{_MODAL_BASE}-synthesize.modal.run")
# Legacy single-endpoint alias (unused — per-function URLs take precedence)
MODAL_ENDPOINT         = os.environ.get("MODAL_ENDPOINT", _MODAL_BASE)
APPWRITE_ENDPOINT      = os.environ.get("APPWRITE_ENDPOINT", "").rstrip("/")
APPWRITE_PROJECT       = os.environ.get("APPWRITE_PROJECT", "")
APPWRITE_API_KEY       = os.environ.get("APPWRITE_API_KEY", "")

# Keywords that signal long-term / sovereign storage intent
_LT_KEYWORDS = frozenset({
    "archive", "persist", "history", "ledger", "permanent",
    "long-term", "sovereign", "store", "recall", "search",
    "catalog", "remember", "vault", "index",
})

# ── Short-Term: NotebookLM (notebooklm_bridge.py) ───────────────────────────

async def _st_synthesize(query: str) -> str:
    from notebooklm_bridge import async_synthesize
    result = await async_synthesize(query)
    return result or "[ST: no synthesis returned]"


async def _st_health() -> tuple[bool, str, float]:
    from notebooklm_bridge import async_health_probe
    return await async_health_probe()


async def _st_store(title: str, content: str) -> dict[str, Any]:
    from notebooklm_bridge import async_sync_state
    return await async_sync_state(content=content, note_title=title)


# ── Long-Term: open-notebooklm + Appwrite via Modal ─────────────────────────

async def _lt_synthesize(query: str) -> str:
    if LONG_TERM_BACKEND == "stub":
        return f"[LT-stub: Modal not yet deployed]"
    try:
        import websockets
        import json
        ws_url = MODAL_SYNTHESIZE_URL.replace('https://', 'wss://').replace('http://', 'ws://')
        async with websockets.connect(ws_url, open_timeout=5.0) as ws:
            await ws.send(json.dumps({"query": query}))
            response = await asyncio.wait_for(ws.recv(), timeout=30.0)
            data = json.loads(response)
            return data.get("result", "[LT: empty response]")
    except Exception as e:
        return f"[LT: Modal unreachable via WS — {type(e).__name__}: {e}]"


async def _lt_health() -> tuple[bool, str, float]:
    t0 = time.perf_counter()
    if LONG_TERM_BACKEND == "stub":
        lat = (time.perf_counter() - t0) * 1000
        return False, "LT stub — Modal/Appwrite not yet deployed", lat
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(MODAL_HEALTH_URL)
            ok = r.status_code == 200
            lat = (time.perf_counter() - t0) * 1000
            return ok, f"Modal {'online' if ok else 'degraded'} (Volume)", lat
    except Exception as e:
        lat = (time.perf_counter() - t0) * 1000
        return False, f"Modal unreachable: {type(e).__name__}", lat


async def _lt_store(title: str, content: str) -> dict[str, Any]:
    if LONG_TERM_BACKEND == "stub":
        return {"status": "stub", "title": title, "chars": len(content),
                "note": "enable LONG_TERM_BACKEND=modal to persist"}
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                MODAL_STORE_URL,
                json={"title": title, "content": content},
            )
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ── Router (delegated to SIR_MNEMO) ──────────────────────────────────────────

def _route(query: str, tier: str, context: dict | None = None) -> str:
    """Delegate tier resolution to SIR_MNEMO. Fallback to keyword scan if unavailable."""
    if tier in ("short", "long", "both"):
        return tier
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from knights.mnemo import route_query
        decision = route_query(query, context)
        return decision.tier
    except Exception:
        # Fallback: simple keyword scan
        if any(kw in query.lower() for kw in _LT_KEYWORDS):
            return "both"
        return "short"


# ── Public async API ─────────────────────────────────────────────────────────

async def async_synthesize(query: str, tier: str = "auto") -> str:
    tier = _route(query, tier)
    if tier == "short":
        return await _st_synthesize(query)
    if tier == "long":
        return await _lt_synthesize(query)
    # both — async fan-out, merge non-stub results
    st_res, lt_res = await asyncio.gather(
        _st_synthesize(query),
        _lt_synthesize(query),
        return_exceptions=True,
    )
    parts = []
    if isinstance(st_res, str) and not st_res.startswith("[ST: no"):
        parts.append(f"[ST]\n{st_res}")
    if isinstance(lt_res, str) and not lt_res.startswith("[LT-stub"):
        parts.append(f"[LT]\n{lt_res}")
    return "\n\n".join(parts) if parts else (st_res if isinstance(st_res, str) else "[Integration Brain: no synthesis]")


async def async_store(title: str, content: str, tier: str = "both") -> dict[str, Any]:
    """Dual-write by default — both tiers receive every store."""
    if tier == "short":
        return {"short_term": await _st_store(title, content)}
    if tier == "long":
        return {"long_term": await _lt_store(title, content)}
    st, lt = await asyncio.gather(
        _st_store(title, content),
        _lt_store(title, content),
        return_exceptions=True,
    )
    return {
        "short_term": st if not isinstance(st, Exception) else str(st),
        "long_term":  lt if not isinstance(lt, Exception) else str(lt),
    }


async def async_health_probe() -> tuple[bool, str, float]:
    t0 = time.perf_counter()
    (st_ok, st_msg, _), (lt_ok, lt_msg, _) = await asyncio.gather(
        _st_health(), _lt_health()
    )
    lat = (time.perf_counter() - t0) * 1000
    if st_ok and lt_ok:
        msg = f"Integration Brain FULL: {st_msg} | LT: {lt_msg}"
    elif st_ok:
        msg = f"Integration Brain ST: {st_msg} | LT: {lt_msg}"
    else:
        msg = f"Integration Brain DARK: ST({st_msg}) LT({lt_msg})"
    return (st_ok or lt_ok), msg, lat


# ── Sync wrappers (hud.py / awaken boot phase) ───────────────────────────────

def synthesize(query: str, tier: str = "auto") -> str:
    try:
        return asyncio.run(async_synthesize(query, tier))
    except RuntimeError as e:
        return f"[IB: sync call from running loop: {e}]"


def store(title: str, content: str, tier: str = "both") -> dict[str, Any]:
    try:
        return asyncio.run(async_store(title, content, tier))
    except RuntimeError as e:
        return {"error": f"sync call from running loop: {e}"}


def health_probe() -> tuple[bool, str, float]:
    try:
        return asyncio.run(async_health_probe())
    except RuntimeError as e:
        return False, f"IB health_probe from running loop: {e}", 0.0
