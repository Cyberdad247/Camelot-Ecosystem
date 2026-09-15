# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — NotebookLM Real Client Layer
r"""
Wraps the notebooklm-py async client into a synchronous/async bridge
for use across the entire Camelot Worldtree Cloudbrain system.

Authentication:
  Run ONCE from the terminal to persist your Google session:
    > .venv\Scripts\notebooklm login

  Session is stored at: ~/.notebooklm/profiles/default/storage_state.json
  For headless/CI, set env var: NOTEBOOKLM_AUTH_JSON=<json_string>

Usage:
  from vfs.notebooklm_client import push_note, push_source, query_notebook, list_notebooks
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("NotebookLM_Client")

_NOTEBOOK_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(CAMELOT_ROOT / "01_KERNEL"))

try:
    from notebooklm import NotebookLMClient
    from notebooklm.exceptions import AuthError, NotebookNotFoundError, SourceAddError
    NOTEBOOKLM_AVAILABLE = True
except ImportError:
    NotebookLMClient = None
    NOTEBOOKLM_AVAILABLE = False
    LOG.warning("[NLM] notebooklm-py not installed. Run: pip install notebooklm-py[browser]")

# KNIGHT_NOTEBOOKS is imported lazily inside functions to prevent circular imports with cloudbrain_connector.py

def _run_async(coro):
    """Run an async coroutine synchronously — safe for non-async callers."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ── Core async operations ────────────────────────────────────────────────────

async def _get_client() -> Optional[Any]:
    """Acquire authenticated NotebookLMClient from stored session."""
    if not NOTEBOOKLM_AVAILABLE:
        return None
    if os.environ.get("CAMELOT_OFFLINE_CLOUDBRAIN") == "1":
        return None
    
    # Check default profile path first, then ~/.notebooklm/storage_state.json
    possible_paths = [
        Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json",
        Path.home() / ".notebooklm" / "storage_state.json",
        Path(r"C:\Users\vizio\.notebooklm\storage_state.json"),
    ]
    auth_path = next((p for p in possible_paths if p.exists()), None)
    if not auth_path:
        LOG.warning(
            "[NLM] No NotebookLM session found. Run in terminal: .venv\\Scripts\\notebooklm login"
        )
        return None

    try:
        # Use NotebookLMClient.from_storage for full L1/L2/L3 rotation and cookie support
        return await NotebookLMClient.from_storage(path=auth_path)
    except Exception as e:
        LOG.debug(f"[NLM] from_storage failed ({e}), attempting direct cookie extraction fallback...")

    try:
        from notebooklm.auth import AuthTokens, _load_storage_state, extract_cookies_from_storage, fetch_tokens

        state = _load_storage_state(auth_path)
        cookies = extract_cookies_from_storage(state)
        for c in state.get("cookies", []):
            if c.get("domain") == "notebooklm.google.com" and c.get("name") in ("OSID", "__Secure-OSID"):
                cookies[c["name"]] = c.get("value", "")
        csrf_token, session_id = await fetch_tokens(cookies)
        auth = AuthTokens(cookies=cookies, csrf_token=csrf_token, session_id=session_id)
        return NotebookLMClient(auth)
    except (AuthError, ValueError) as e:
        LOG.warning(
            "[NLM] NotebookLM authentication expired or missing. "
            "Run in terminal: .venv\\Scripts\\notebooklm login  (%s)",
            e,
        )
        return None
    except Exception as e:
        LOG.warning(f"[NLM] Client init failed: {e}")
        return None


@asynccontextmanager
async def _open_client():
    """Yield an opened client, or None when no backend is available.

    Wraps client acquisition in async context manager so callers can distinguish
    'no backend' from a live client session.
    """
    if not NOTEBOOKLM_AVAILABLE or os.environ.get("CAMELOT_OFFLINE_CLOUDBRAIN") == "1":
        yield None
        return

    try:
        async with NotebookLMClient.from_storage() as client:
            yield client
            return
    except Exception as e:
        LOG.debug(f"[NLM] Context manager from_storage failed ({e}), trying _get_client()...")

    client = await _get_client()
    if client is None:
        yield None
        return
    async with client:
        yield client


async def _find_notebook_by_id(client, notebook_id: str) -> Optional[Any]:
    """Locate a notebook by its UUID or title fragment with 0-scan fast path."""
    if _NOTEBOOK_UUID_RE.match(notebook_id):
        try:
            return await client.notebooks.get(notebook_id)
        except Exception as e:
            LOG.debug(f"[NLM] Direct notebooks.get({notebook_id}) failed: {e}. Falling back to list scan.")
    try:
        notebooks = await client.notebooks.list()
        for nb in notebooks:
            if notebook_id in (nb.id, nb.title):
                return nb
        # Fuzzy match on title
        for nb in notebooks:
            if notebook_id.lower() in nb.title.lower():
                return nb
        return None
    except Exception as e:
        LOG.error(f"[NLM] list notebooks failed: {e}")
        return None


async def push_note_async(knight_id: str, title: str, content: str) -> bool:
    """Push a note to a knight's Notebook (async)."""
    async with _open_client() as client:
        if not client:
            return False
        try:
            from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS
        except ImportError:
            KNIGHT_NOTEBOOKS = {}
        notebook_id = KNIGHT_NOTEBOOKS.get(knight_id.upper())
        if not notebook_id:
            LOG.warning(f"[NLM] No notebook mapped for {knight_id}")
            return False

        nb = await _find_notebook_by_id(client, notebook_id)
        if not nb:
            LOG.warning(f"[NLM] Notebook not found for {knight_id} (id={notebook_id})")
            return False

        try:
            await client.notes.create(nb.id, title=title, content=content)
            LOG.info(f"[NLM] Note pushed to {knight_id}: '{title}'")
            return True
        except Exception as e:
            LOG.error(f"[NLM] Note push failed for {knight_id}: {e}")
            return False


async def push_source_async(knight_id: str, title: str, content: str) -> bool:
    """Push a text source to a knight's Notebook (async)."""
    async with _open_client() as client:
        if not client:
            return False
        try:
            from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS
        except ImportError:
            KNIGHT_NOTEBOOKS = {}
        notebook_id = KNIGHT_NOTEBOOKS.get(knight_id.upper())
        if not notebook_id:
            return False

        nb = await _find_notebook_by_id(client, notebook_id)
        if not nb:
            return False

        try:
            await client.sources.add_text(nb.id, content=content, title=title)
            LOG.info(f"[NLM] Source pushed to {knight_id}: '{title}'")
            return True
        except SourceAddError as e:
            LOG.error(f"[NLM] Source add failed for {knight_id}: {e}")
            return False
        except Exception as e:
            LOG.error(f"[NLM] Source push error for {knight_id}: {e}")
            return False


async def list_notebooks_async() -> List[Dict[str, Any]]:
    """List all available notebooks from the authenticated account (async)."""
    async with _open_client() as client:
        if not client:
            return []
        try:
            notebooks = await client.notebooks.list()
            return [
                {
                    "id": nb.id,
                    "title": nb.title,
                    "source_count": getattr(nb, "sources_count", getattr(nb, "source_count", 0)),
                }
                for nb in notebooks
            ]
        except Exception as e:
            LOG.error(f"[NLM] List notebooks failed: {e}")
            return []


async def query_notebook_async(knight_id: str, question: str) -> Optional[str]:
    """Query a notebook via chat (async)."""
    async with _open_client() as client:
        if not client:
            return None
        try:
            from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS
        except ImportError:
            KNIGHT_NOTEBOOKS = {}
        notebook_id = KNIGHT_NOTEBOOKS.get(knight_id.upper())
        if not notebook_id:
            return None
        nb = await _find_notebook_by_id(client, notebook_id)
        if not nb:
            return None
        try:
            result = await client.chat.ask(nb.id, question)
            if hasattr(result, "answer"):
                return str(result.answer)
            return str(result)
        except Exception as e:
            LOG.error(f"[NLM] Chat query failed for {knight_id}: {e}")
            return None


# ── Public synchronous API ─────────────────────────────────────────────────

def push_note(knight_id: str, title: str, content: str) -> bool:
    """Synchronously push a note to a Cloudbrain Notebook node."""
    return _run_async(push_note_async(knight_id, title, content))


def push_source(knight_id: str, title: str, content: str) -> bool:
    """Synchronously push a text source to a Cloudbrain Notebook node."""
    return _run_async(push_source_async(knight_id, title, content))


def list_notebooks() -> List[Dict[str, Any]]:
    """Synchronously list all available Gemini Notebooks."""
    return _run_async(list_notebooks_async())


def query_notebook(knight_id: str, question: str) -> Optional[str]:
    """Query a notebook via chat (best-effort — may not be available in all contexts)."""
    return _run_async(query_notebook_async(knight_id, question))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    print("[NLM] Fetching notebook list...")
    nbs = list_notebooks()
    if nbs:
        print(f"Found {len(nbs)} notebooks:")
        for nb in nbs:
            print(f"  [{nb['id']}] {nb['title']}")
    else:
        print("No notebooks found. Ensure you are authenticated: .venv\\Scripts\\notebooklm login")
