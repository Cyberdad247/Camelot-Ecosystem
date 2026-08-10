# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Worldtree Cloudbrain Connector
"""
Connects Camelot OS memory tiers to external NotebookLM (Gemini Notebook) Cloudbrain nodes.

Backend priority:
  1. notebooklm-py real async SDK  (vfs/notebooklm_client.py)
  2. Legacy notebooklmpy stub       (backwards compat)
  3. Silent skip                    (no backend configured)

Authentication (one-time):
  > .venv\Scripts\notebooklm login
"""

from __future__ import annotations

import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(_CAMELOT_ROOT / "vfs"))

# ── Real notebooklm-py SDK ────────────────────────────────────────────────────
try:
    from notebooklm_client import (
        push_note as _nlm_push_note,
        push_source as _nlm_push_source,
        query_notebook as _nlm_query,
        list_notebooks as _nlm_list,
    )
    _NLM_REAL = True
except ImportError:
    _NLM_REAL = False
    _nlm_push_note = _nlm_push_source = _nlm_query = _nlm_list = None  # type: ignore

# ── Legacy stub ───────────────────────────────────────────────────────────────
try:
    from notebooklmpy import NotebookLM as _LegacyNLM
except ImportError:
    _LegacyNLM = None

# ── Worldtree Notebook Registry ───────────────────────────────────────────────
KNIGHT_NOTEBOOKS: Dict[str, str] = {
    "SIR_BORIS":           "f7707daa-2d10-4db8-8fda-be4661a27793",
    "SIR_ALEX":            "f490c05e-d8c4-4008-87e1-5f901bf57c6a",
    "SIR_FORGE":           "91c5da8b-e2de-4a56-b7fd-c8b76c00afc7",
    "SIR_SENTINEL":        "07cbb441-f008-424c-820a-85676210be39",
    "SIR_DEBUG":           "fdc42a4a-3060-4eac-b57c-8e6009ed634a",
    "SIR_GHOST":           "422a184b-93e7-4dfd-8a12-75d2268b6c60",
    "LADY_APIS":           "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f",
    "MERLIN_OMEGA":        "af927fde-d7eb-42ee-8c79-51b3e78ef39b",
    "SIR_HELIO":           "56820318-bb91-451f-aac4-4b46424898cf",
    "SIR_SONUS":           "b8a1c3d5-e2f4-4687-9a01-234567890abc",
    "SIR_CODEX":           "8c656cfa-a189-409e-a72d-07692a47f17e",
    "LADY_MNEMOSYNE":      "mnemosyne-cloudbrain-vfs-1100",
    "ANYA_QUANTUM_MANTRA": "anya-glyph-engine-vfs-1200",
    "CAMELOT_V1000":       "camelot-os-v1000-excalibur-a",
}

NOTEBOOK_DOMAIN_TAGS: Dict[str, List[str]] = {
    "SIR_BORIS":           ["architecture", "crucible", "design", "review"],
    "SIR_ALEX":            ["planning", "dag", "orchestration", "tasks"],
    "SIR_FORGE":           ["kinetic", "build", "execution", "code"],
    "SIR_SENTINEL":        ["security", "audit", "iron_gate", "guard"],
    "SIR_DEBUG":           ["debug", "heal", "piv", "repair"],
    "SIR_GHOST":           ["privacy", "secrets", "air_gap", "scan"],
    "LADY_APIS":           ["research", "bashr", "foraging", "context"],
    "MERLIN_OMEGA":        ["reasoning", "got", "tot", "deep_think", "math"],
    "SIR_HELIO":           ["voice", "tts", "audio", "realtime"],
    "SIR_SONUS":           ["voice", "audio", "multivoice", "phonetic"],
    "SIR_CODEX":           ["kinetic", "rapid", "prototype", "openai"],
    "LADY_MNEMOSYNE":      ["memory", "vfs", "mnemosyne", "sweep", "brief"],
    "ANYA_QUANTUM_MANTRA": ["glyph", "quantum", "vfs", "token", "compression"],
    "CAMELOT_V1000":       ["sovereign", "os", "broadcast", "excalibur", "system"],
}

RUNE_SYMBOLECT: Dict[str, List[str]] = {
    "\u16B1": ["LADY_APIS", "MERLIN_OMEGA"],                              # ᚱ RESEARCH
    "\u16A0": ["SIR_FORGE", "SIR_CODEX", "CAMELOT_V1000"],               # ᚠ FORGE
    "\u16D7": ["LADY_MNEMOSYNE", "ANYA_QUANTUM_MANTRA"],                  # ᛗ MEMORY
    "\u16DC": ["SIR_SENTINEL", "SIR_GHOST"],                              # ᛜ GUARD
    "\u16DE": ["SIR_DEBUG"],                                              # ᛞ DEBUG
    "\u16A2": ["SIR_HELIO", "SIR_SONUS"],                                 # ᚢ VOICE
    "\u16A8": ["SIR_BORIS", "SIR_ALEX"],                                  # ᚨ ARCHITECT
    "\u16DF": list(KNIGHT_NOTEBOOKS.keys()),                               # ᛟ SOVEREIGN
}


class CloudBrainConnector:
    """Connects Camelot OS memory tiers to the external NotebookLM Cloudbrain."""

    def __init__(self, knight_id: str = "DEFAULT"):
        self.knight_id = knight_id.upper()
        self.notebook_id = KNIGHT_NOTEBOOKS.get(self.knight_id)
        if not self.notebook_id:
            logging.warning(f"[CLOUD_BRAIN] Unmapped Knight ID: {knight_id}.")

    def push_to_notebook(self, artifact_type: str, content: Any, title: str) -> bool:
        """Push artifact to the Knight's NotebookLM node via SDK priority chain."""
        if not self.notebook_id:
            return False

        content_str = (
            json.dumps(content, indent=2)
            if isinstance(content, (dict, list))
            else str(content)
        )

        # Priority 1: Real notebooklm-py SDK
        if _NLM_REAL:
            try:
                if artifact_type == "note":
                    ok = _nlm_push_note(self.knight_id, title, content_str)
                else:
                    ok = _nlm_push_source(self.knight_id, title, content_str)
                if ok:
                    logging.info(f"[SDK] Pushed '{title}' -> {self.knight_id}")
                return ok
            except Exception as e:
                logging.error(f"[SDK] Push failed for {self.knight_id}: {e}")

        # Priority 2: Legacy notebooklmpy stub
        if _LegacyNLM:
            try:
                ws = _LegacyNLM(notebook_id=self.notebook_id)
                if artifact_type == "note":
                    ws.create_note(title=title, content=content_str)
                else:
                    ws.add_source(text=content_str, title=title)
                logging.info(f"[STUB] Pushed '{title}' -> {self.knight_id}")
                return True
            except Exception as e:
                logging.error(f"[STUB] Push failed: {e}")

        logging.warning(f"[CLOUD_BRAIN] No active backend for {self.knight_id}. Auth required.")
        return False

    def query_notebook(self, query: str) -> Optional[str]:
        """Query the Knight's NotebookLM node via SDK priority chain."""
        if not self.notebook_id:
            return None

        if _NLM_REAL and _nlm_query:
            try:
                return _nlm_query(self.knight_id, query)
            except Exception as e:
                logging.error(f"[SDK] Query failed for {self.knight_id}: {e}")

        if _LegacyNLM:
            try:
                ws = _LegacyNLM(notebook_id=self.notebook_id)
                return ws.query(query)
            except Exception as e:
                logging.error(f"[STUB] Query failed: {e}")

        return None


# ── Worldtree Batch Operations ────────────────────────────────────────────────

def batch_push(
    artifact_type: str,
    content: Any,
    title: str,
    target_knights: Optional[List[str]] = None,
    max_workers: int = 6,
) -> Dict[str, bool]:
    """Fan-out push to multiple Cloudbrain nodes concurrently."""
    targets = target_knights or list(KNIGHT_NOTEBOOKS.keys())
    results: Dict[str, bool] = {}

    def _push_one(knight_id: str) -> Tuple[str, bool]:
        cb = CloudBrainConnector(knight_id=knight_id)
        ok = cb.push_to_notebook(artifact_type, content, title)
        return knight_id, ok

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_push_one, k): k for k in targets}
        for fut in as_completed(futures):
            kid, ok = fut.result()
            results[kid] = ok
            logging.info(f"[BATCH_PUSH] {kid}: {'OK' if ok else 'SKIP'}")

    return results


def batch_query(
    query: str,
    target_knights: Optional[List[str]] = None,
    max_workers: int = 6,
) -> Dict[str, Optional[str]]:
    """Fan-out query across multiple Cloudbrain nodes concurrently."""
    targets = target_knights or list(KNIGHT_NOTEBOOKS.keys())
    results: Dict[str, Optional[str]] = {}

    def _query_one(knight_id: str) -> Tuple[str, Optional[str]]:
        cb = CloudBrainConnector(knight_id=knight_id)
        return knight_id, cb.query_notebook(query)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_query_one, k): k for k in targets}
        for fut in as_completed(futures):
            kid, resp = fut.result()
            results[kid] = resp

    return results


def route_by_domain(task_keywords: List[str]) -> List[str]:
    """
    Mathematical domain router.
    Φ(task, n) = |intersection(task_keywords, domain_tags[n])| / |domain_tags[n]|
    Returns notebooks sorted by descending relevance score.
    """
    kw_set = {k.lower() for k in task_keywords}
    scores: Dict[str, float] = {}
    for knight, tags in NOTEBOOK_DOMAIN_TAGS.items():
        tag_set = set(tags)
        score = len(kw_set & tag_set) / len(tag_set) if tag_set else 0.0
        if score > 0:
            scores[knight] = score
    return sorted(scores, key=lambda k: scores[k], reverse=True)


def list_all_notebooks() -> List[Dict[str, Any]]:
    """Returns structured list of all registered Worldtree Cloudbrain nodes."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "knight_id": kid,
            "notebook_id": nid,
            "domain_tags": NOTEBOOK_DOMAIN_TAGS.get(kid, []),
            "vfs_path": f"vfs://{kid.lower()}/",
            "last_checked": now,
        }
        for kid, nid in KNIGHT_NOTEBOOKS.items()
    ]
