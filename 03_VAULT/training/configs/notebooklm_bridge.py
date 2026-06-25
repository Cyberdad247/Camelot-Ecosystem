"""Cloud Brain bridge — notebooklm-py native import (Phase Omega₁ Kernel Fusion).

Replaces the subprocess-based nlm CLI with an in-process httpx RPC client.
Lazy synthesis: health probe at //BOOT, full Oracle query deferred until //PLAN.
"""
from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CANONICAL_NOTEBOOK_ID = "8c656cfa-a189-409e-a72d-07692a47f17e"
CANONICAL_NOTEBOOK_TITLE = "Camelot-OS v.1000"
SYNC_NOTE_TITLE = "Camelot-OS Canonical Sync Snapshot"
# Client ceiling. Health probe (notebooks.list) resolves in ~2s; chat.ask can
# take 30-60s depending on notebook size and Gemini backend load. Keep the
# ceiling well above the slowest realistic synthesis.
CLIENT_TIMEOUT_S = 90.0
SYNTHESIS_TTL_S = 900

NLM_LEGACY_COOKIES = Path.home() / ".notebooklm-mcp-cli" / "profiles" / "default" / "cookies.json"
REPO_ROOT = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
LEDGER_PATH = REPO_ROOT / "PROVENANCE_LEDGER.md"
LEDGER_SYNC_STATUS_PATH = REPO_ROOT / "logs" / "defense_grid" / "ledger_sync_status.json"
VERIFICATION_PATH = REPO_ROOT / "verification.md"
VERSION_PATH = REPO_ROOT / "VERSION"

_client = None
_synthesis_cache: dict[str, tuple[float, Any]] = {}


def _describe_connection_failure(exc: Exception) -> str:
    """Explain Living Notebook connection failures with local context when possible."""
    if os.environ.get("CODEX_SANDBOX_NETWORK_DISABLED") == "1":
        return (
            "Living Notebook blocked by sandboxed outbound network policy "
            f"({type(exc).__name__}: {exc})"
        )
    return f"Living Notebook unreachable: {type(exc).__name__}: {exc}"


def _read_text(path: Path, *, tail_lines: int | None = None, max_chars: int | None = None) -> str:
    if not path.exists():
        return f"[missing: {path}]"
    text = path.read_text(encoding="utf-8", errors="replace")
    if tail_lines is not None:
        text = "\n".join(text.splitlines()[-tail_lines:])
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars].rstrip() + "\n...[truncated]"
    return text


def _build_sync_snapshot(*, extra_summary: str = "") -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    version = _read_text(VERSION_PATH, max_chars=64).strip() or "unknown"
    ledger_tail = _read_text(LEDGER_PATH, tail_lines=80, max_chars=12000)
    verification_excerpt = _read_text(VERIFICATION_PATH, max_chars=8000)
    ledger_sync_status = _read_text(LEDGER_SYNC_STATUS_PATH, max_chars=8000)

    sections = [
        "# Camelot-OS Canonical Sync Snapshot",
        "",
        f"- Generated UTC: {timestamp}",
        f"- Repo Root: {REPO_ROOT}",
        f"- Version: {version}",
        f"- Canonical Notebook ID: {CANONICAL_NOTEBOOK_ID}",
    ]
    if extra_summary.strip():
        sections.extend(["", "## Operator Summary", extra_summary.strip()])

    sections.extend(
        [
            "",
            "## Provenance Ledger Tail",
            "```text",
            ledger_tail,
            "```",
            "",
            "## Verification Matrix",
            "```markdown",
            verification_excerpt,
            "```",
            "",
            "## Ledger Sync Status",
            "```json",
            ledger_sync_status,
            "```",
        ]
    )
    return "\n".join(sections)


def _ensure_storage_state() -> Path:
    """Ensure notebooklm-py storage_state.json exists."""
    from notebooklm.auth import get_storage_path
    storage_path = get_storage_path()
    if storage_path.exists():
        return storage_path
    
    raise FileNotFoundError(
        f"No auth state found at {storage_path}. "
        "Run 'notebooklm login' in your terminal to authenticate."
    )


async def _build_client():
    global _client
    if _client is None:
        from notebooklm import NotebookLMClient
        from notebooklm.auth import load_auth_from_storage, fetch_tokens, AuthTokens
        _ensure_storage_state()
        cookies = load_auth_from_storage()
        csrf, session = await fetch_tokens(cookies)
        tokens = AuthTokens(cookies=cookies, csrf_token=csrf, session_id=session)
        _client = NotebookLMClient(auth=tokens, timeout=CLIENT_TIMEOUT_S)
    return _client


async def _async_health():
    client = await _build_client()
    async with client:
        notebooks = await client.notebooks.list()
    return len(notebooks) if notebooks else 0


async def async_health_probe() -> tuple[bool, str, float]:
    """Async living-notebook heartbeat. Safe inside an existing event loop."""
    t0 = time.perf_counter()
    try:
        count = await _async_health()
        latency = (time.perf_counter() - t0) * 1000
        return True, f"Cloud Brain online ({count} notebooks)", latency
    except Exception as e:
        latency = (time.perf_counter() - t0) * 1000
        return False, _describe_connection_failure(e), latency


def health_probe() -> tuple[bool, str, float]:
    """Sync living-notebook heartbeat for non-async callers (awaken boot phase)."""
    try:
        return asyncio.run(async_health_probe())
    except RuntimeError as e:
        # Already inside a running loop — callers must use async_health_probe.
        return False, f"sync health_probe called from running loop: {e}", 0.0


async def async_sync_state(
    *,
    notebook_id: str = CANONICAL_NOTEBOOK_ID,
    note_title: str = SYNC_NOTE_TITLE,
    extra_summary: str = "",
    content: str | None = None,
) -> dict[str, Any]:
    """Upsert a canonical NotebookLM note containing the current local working snapshot."""
    note_content = content or _build_sync_snapshot(extra_summary=extra_summary)
    client = await _build_client()
    async with client:
        notes = await client.notes.list(notebook_id)
        existing = next((note for note in notes if note.title == note_title), None)
        if existing:
            await client.notes.update(notebook_id, existing.id, note_content, note_title)
            note_id = existing.id
            action = "updated"
        else:
            created = await client.notes.create(notebook_id, note_title, note_content)
            note_id = created.id
            action = "created"
    return {
        "notebook_id": notebook_id,
        "note_id": note_id,
        "note_title": note_title,
        "action": action,
        "content_chars": len(note_content),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }


def sync_state(
    *,
    notebook_id: str = CANONICAL_NOTEBOOK_ID,
    note_title: str = SYNC_NOTE_TITLE,
    extra_summary: str = "",
    content: str | None = None,
) -> dict[str, Any]:
    """Sync local Camelot state into the canonical short-term NotebookLM notebook."""
    try:
        return asyncio.run(
            async_sync_state(
                notebook_id=notebook_id,
                note_title=note_title,
                extra_summary=extra_summary,
                content=content,
            )
        )
    except RuntimeError as e:
        return {"error": f"sync_state called from running loop: {e}"}


async def async_synthesize(query: str, notebook_id: str = CANONICAL_NOTEBOOK_ID,
                            use_cache: bool = True) -> str | None:
    """Async living-notebook synthesis. TTL-cached. Safe inside a running event loop."""
    cache_key = f"{notebook_id}::{hash(query)}"
    if use_cache and cache_key in _synthesis_cache:
        stamp, payload = _synthesis_cache[cache_key]
        if time.time() - stamp < SYNTHESIS_TTL_S:
            return payload
    try:
        client = await _build_client()
        async with client:
            response = await client.chat.ask(notebook_id=notebook_id, question=query)
        text = response.text if hasattr(response, "text") else str(response)
        _synthesis_cache[cache_key] = (time.time(), text)
        return text
    except Exception as e:
        return f"[Living Notebook synthesis failed: {type(e).__name__}: {e}]"


def synthesize(query: str, notebook_id: str = CANONICAL_NOTEBOOK_ID,
               use_cache: bool = True) -> str | None:
    """Sync living-notebook synthesis for non-async callers."""
    try:
        return asyncio.run(async_synthesize(query, notebook_id, use_cache))
    except RuntimeError as e:
        return f"[Living Notebook synthesis failed: sync call from running loop: {e}]"


def cache_stats() -> dict[str, int]:
    now = time.time()
    fresh = sum(1 for stamp, _ in _synthesis_cache.values()
                if now - stamp < SYNTHESIS_TTL_S)
    return {"entries": len(_synthesis_cache), "fresh": fresh}


# Session age thresholds (days)
_AUTH_WARN_DAYS = 21
_AUTH_CRITICAL_DAYS = 30


def session_age_check() -> dict[str, Any]:
    """Return NotebookLM auth session age and health.

    Checks the notebooklm-py canonical storage path first, then known
    fallback locations. Also checks browser_profile/Default/Network/Cookies
    as a secondary freshness signal — a recent browser session means the
    Google auth is still live even if storage_state.json wasn't re-saved.
    Returns warn=True at >21 days, critical=True at >30 days.
    """
    storage_path: Path | None = None

    # Prefer the library's own canonical path
    try:
        from notebooklm.auth import get_storage_path
        candidate = get_storage_path()
        if candidate.exists():
            storage_path = candidate
    except Exception:
        pass

    # Known fallback locations
    if storage_path is None:
        fallbacks = [
            Path.home() / ".notebooklm" / "storage_state.json",
            Path.home() / ".notebooklm-mcp-cli" / "profiles" / "default" / "storage_state.json",
            NLM_LEGACY_COOKIES,
        ]
        for c in fallbacks:
            if c.exists():
                storage_path = c
                break

    # Secondary: browser profile cookies (present after any successful browser login,
    # even if ENTER wasn't pressed to save storage_state.json)
    browser_cookies = Path.home() / ".notebooklm" / "browser_profile" / "Default" / "Network" / "Cookies"
    browser_cookie_age: float | None = None
    if browser_cookies.exists():
        browser_cookie_age = (time.time() - browser_cookies.stat().st_mtime) / 86400

    if storage_path is None:
        if browser_cookie_age is not None and browser_cookie_age < 1.0:
            return {
                "exists": True,
                "path": str(browser_cookies),
                "age_days": round(browser_cookie_age, 1),
                "warn": False,
                "critical": False,
                "source": "browser_profile",
                "message": (
                    f"Browser session fresh ({browser_cookie_age * 24:.1f}h old) — "
                    "run: notebooklm login and press ENTER to persist storage_state.json"
                ),
            }
        return {
            "exists": False,
            "age_days": None,
            "warn": True,
            "critical": True,
            "message": "No auth state found — run: notebooklm login",
        }

    age_days = (time.time() - storage_path.stat().st_mtime) / 86400

    # If storage_state.json is old but browser cookies are fresh, use the
    # better signal and prompt the user to re-save
    if browser_cookie_age is not None and browser_cookie_age < age_days:
        effective_age = browser_cookie_age
        source = "browser_profile"
        note = " (browser session fresh; run: notebooklm login + ENTER to persist)"
    else:
        effective_age = age_days
        source = storage_path.name
        note = ""

    warn = effective_age > _AUTH_WARN_DAYS
    critical = effective_age > _AUTH_CRITICAL_DAYS

    msg = f"Auth session {effective_age:.1f}d old ({source}){note}"
    if critical:
        msg += " — CRITICAL: likely expired, run: notebooklm login"
    elif warn:
        msg += " — WARNING: expires soon, run: notebooklm login to refresh"

    return {
        "exists": True,
        "path": str(storage_path),
        "age_days": round(effective_age, 1),
        "warn": warn,
        "critical": critical,
        "source": source,
        "message": msg,
    }


# ---------------------------------------------------------------------------
# Omega₃.2 — LADY_APIS research helpers (research.start / research.poll)
# ---------------------------------------------------------------------------


async def async_research_start(query: str, *, notebook_id: str = CANONICAL_NOTEBOOK_ID,
                                 source: str = "web", mode: str = "fast") -> dict[str, Any]:
    """Kick off a research task. Returns {task_id, status, query}."""
    client = await _build_client()
    async with client:
        task = await client.research.start(
            notebook_id=notebook_id, query=query, source=source, mode=mode,
        )
    task_id = getattr(task, "task_id", None) or getattr(task, "id", None) or str(task)
    return {
        "task_id": task_id,
        "query": query,
        "source": source,
        "mode": mode,
        "notebook_id": notebook_id,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }


async def async_research_poll(*, notebook_id: str = CANONICAL_NOTEBOOK_ID) -> dict[str, Any]:
    """Poll the latest research task on the given notebook."""
    client = await _build_client()
    async with client:
        status = await client.research.poll(notebook_id=notebook_id)
    payload: dict[str, Any] = {"notebook_id": notebook_id,
                                "polled_utc": datetime.now(timezone.utc).isoformat()}
    for attr in ("state", "status", "progress", "result", "task_id", "error"):
        if hasattr(status, attr):
            payload[attr] = getattr(status, attr)
    if not any(k in payload for k in ("state", "status", "result")):
        payload["raw"] = str(status)
    return payload


# ---------------------------------------------------------------------------
# Omega₃.3 — SIR_SONUS studio helpers (artifacts.list_* / generate_*)
# ---------------------------------------------------------------------------


_STUDIO_LIST_MAP = {
    "audio":        "list_audio",
    "video":        "list_video",
    "report":       "list_reports",
    "reports":      "list_reports",
    "quiz":         "list_quizzes",
    "quizzes":      "list_quizzes",
    "flashcards":   "list_flashcards",
    "infographic":  "list_infographics",
    "infographics": "list_infographics",
    "slides":       "list_slide_decks",
    "slide_deck":   "list_slide_decks",
    "data_table":   "list_data_tables",
}


async def async_studio_list(artifact_type: str = "audio", *,
                             notebook_id: str = CANONICAL_NOTEBOOK_ID) -> dict[str, Any]:
    """List existing studio artifacts of a given type."""
    method_name = _STUDIO_LIST_MAP.get(artifact_type.lower())
    if method_name is None:
        return {"error": f"unknown artifact_type: {artifact_type!r}",
                "supported": sorted(set(_STUDIO_LIST_MAP))}
    client = await _build_client()
    async with client:
        method = getattr(client.artifacts, method_name)
        items = await method(notebook_id=notebook_id)
    rows: list[dict[str, Any]] = []
    for item in items or []:
        rows.append({
            "id": getattr(item, "id", None),
            "title": getattr(item, "title", None),
            "state": getattr(item, "state", None) or getattr(item, "status", None),
            "type": artifact_type,
        })
    return {"notebook_id": notebook_id, "artifact_type": artifact_type,
            "count": len(rows), "items": rows}


_STUDIO_GEN_MAP = {
    "audio":       "generate_audio",
    "video":       "generate_video",
    "report":      "generate_report",
    "infographic": "generate_infographic",
    "slides":      "generate_slide_deck",
    "quiz":        "generate_quiz",
    "flashcards":  "generate_flashcards",
    "data_table":  "generate_data_table",
    "mind_map":    "generate_mind_map",
}


async def async_studio_generate(artifact_type: str, *,
                                  notebook_id: str = CANONICAL_NOTEBOOK_ID,
                                  instructions: str | None = None,
                                  source_ids: list[str] | None = None) -> dict[str, Any]:
    """Start generation of a studio artifact. Returns task metadata; does NOT block."""
    method_name = _STUDIO_GEN_MAP.get(artifact_type.lower())
    if method_name is None:
        return {"error": f"unknown artifact_type: {artifact_type!r}",
                "supported": sorted(set(_STUDIO_GEN_MAP))}
    client = await _build_client()
    async with client:
        method = getattr(client.artifacts, method_name)
        kwargs: dict[str, Any] = {"notebook_id": notebook_id}
        if source_ids is not None:
            kwargs["source_ids"] = source_ids
        if instructions is not None and "instructions" in method.__code__.co_varnames:
            kwargs["instructions"] = instructions
        task = await method(**kwargs)
    return {
        "notebook_id": notebook_id,
        "artifact_type": artifact_type,
        "task_id": getattr(task, "task_id", None) or getattr(task, "id", None) or str(task),
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Omega₃.4 — MASON source helpers (sources.list / add_url / add_text / delete)
# ---------------------------------------------------------------------------


async def async_sources_list(notebook_id: str = CANONICAL_NOTEBOOK_ID) -> dict[str, Any]:
    client = await _build_client()
    async with client:
        sources = await client.sources.list(notebook_id=notebook_id)
    rows: list[dict[str, Any]] = []
    for s in sources or []:
        rows.append({
            "id":    getattr(s, "id", None),
            "title": getattr(s, "title", None),
            "type":  getattr(s, "source_type", None) or getattr(s, "type", None),
            "state": getattr(s, "state", None),
        })
    return {"notebook_id": notebook_id, "count": len(rows), "sources": rows}


async def async_sources_add(*, url: str | None = None, text: str | None = None,
                              title: str | None = None,
                              notebook_id: str = CANONICAL_NOTEBOOK_ID,
                              wait: bool = False) -> dict[str, Any]:
    if not url and not text:
        return {"error": "sources_add requires either 'url' or 'text'"}
    client = await _build_client()
    async with client:
        if url:
            result = await client.sources.add_url(
                notebook_id=notebook_id, url=url, wait=wait,
            )
        else:
            result = await client.sources.add_text(
                notebook_id=notebook_id,
                title=title or "Camelot-OS note",
                content=text,
                wait=wait,
            )
    return {
        "notebook_id": notebook_id,
        "source_id": getattr(result, "id", None) or getattr(result, "source_id", None),
        "title": getattr(result, "title", title),
        "kind": "url" if url else "text",
    }


async def async_sources_delete(source_id: str, *,
                                 notebook_id: str = CANONICAL_NOTEBOOK_ID) -> dict[str, Any]:
    client = await _build_client()
    async with client:
        await client.sources.delete(notebook_id=notebook_id, source_id=source_id)
    return {"notebook_id": notebook_id, "source_id": source_id, "deleted": True}
