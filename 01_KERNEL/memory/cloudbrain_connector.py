# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Worldtree Cloudbrain Connector
r"""
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
import re
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

# ── Worldtree Notebook Registry — VERIFIED LIVE UUIDs 2026-08-10 ─────────────
# Placeholder (non-UUID) notebook ids are permitted for pending knights: they
# register the knight for symbolect/domain routing but never touch a real
# NotebookLM node (see _NOTEBOOK_UUID_RE guard below).
_NOTEBOOK_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

KNIGHT_NOTEBOOKS: Dict[str, str] = {
    # Core Knights (Sovereign_Workspace verified)
    "SIR_BORIS":           "f7707daa-2d10-4db8-8fda-be4661a27793",
    "SIR_ALEX":            "f490c05e-d8c4-4008-87e1-5f901bf57c6a",
    "SIR_FORGE":           "91c5da8b-e2de-4a56-b7fd-c8b76c00afc7",
    "SIR_SENTINEL":        "07cbb441-f008-424c-820a-85676210be39",
    "SIR_DEBUG":           "fdc42a4a-3060-4eac-b57c-8e6009ed634a",
    "SIR_GHOST":           "422a184b-93e7-4dfd-8a12-75d2268b6c60",
    "LADY_APIS":           "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f",
    "MERLIN_OMEGA":        "af927fde-d7eb-42ee-8c79-51b3e78ef39b",
    "SIR_HELIO":           "56820318-bb91-451f-aac4-4b46424898cf",
    "SIR_SONUS":           "6272aa35-c285-4edc-81bc-2824ab519edf",   # Sovereign_Workspace: SIR SONUS
    "SIR_CODEX":           "8c656cfa-a189-409e-a72d-07692a47f17e",   # Camelot-OS v.1000
    # Extended Knights (discovered from live account)
    "SIR_HEIMDALL":        "3205f189-91da-4272-96a9-3641fd642763",
    "SIR_GALAHAD":         "e0110853-14ef-403f-8def-bf3a5123986f",
    "ARTHUR_OMEGA":        "cbb310bd-987e-4b84-bf45-12d37d090bec",
    "SIR_STITCH":          "0fdccdc1-a1d2-48c2-8948-187398bfbeb5",
    "SIR_ALCHEMIST":       "d6bdd57c-84d2-4e24-bb10-ad1fd179fb04",
    "SIR_RUSTCLAW":        "2b3b6ec3-e020-484d-914d-92241a97ea55",
    "ANYA_OMEGA":          "32d38906-5ae8-4ecc-b77e-705d12c89f4a",
    "SIR_HERMES":          "5dc31b8d-169d-4d4d-ab90-d12724fca720",
    "HERMES_PRIME":        "28f89cb6-5048-4b5d-9e94-376082d24744",   # hermes_prime_vfs_forge (verified 2026-08-10)
    "SIR_LANCELOT":        "d8dd1669-aef4-4c34-8c44-d9cc5e51e0c9",
    "LADY_GUINEVERE":      "8dca4a86-2bb6-4332-96b6-79899c0a9ccf",
    "SIR_HUGGINGFACE":     "a0a4bfb9-e847-4c38-be39-7aee398f0795",   # HuggingFace Hub & Spaces Conductor (WorldTree Tethered)
    "SIR_MNEMO":           "8bf3f24e-da2e-45b9-8719-162fcd02a80d",
    # Living System / Project Notebooks
    "LADY_MNEMOSYNE":      "a0a4bfb9-e847-4c38-be39-7aee398f0795",   # World Tree
    "ANYA_QUANTUM_MANTRA": "219e765a-0c8e-4b66-b356-f277cb441b14",   # Anya Omega: Sovereign Compiler
    "CAMELOT_V1000":       "8c656cfa-a189-409e-a72d-07692a47f17e",   # Camelot-OS v.1000
    "CAMELOT_MASTER":      "c5544902-cfb4-4864-b28e-1838b69b9814",   # The Camelot-OS Master Construction Codex
    "BIFROST":             "cbbb0c32-3919-4b77-9158-1d9f9ebf359f",   # Bifrost Bridge Architecture
    "FATHER_CAMELOT":      "39299131-0ade-4f48-8ad4-a68878a6d3d9",   # Father's Camelot
    "WORLD_TREE":          "a0a4bfb9-e847-4c38-be39-7aee398f0795",   # World Tree
    "ALPHA_OMEGA":         "2536aefb-937f-4a04-9142-d1a2f029d8a7",   # Camelot-OS Alpha-Omega artifacts
    "ANTIGRAVITY":         "ab8aa359-2b3b-4bc1-b41f-34979cdc184e",   # Synergizing NotebookLM + AntiGravity
    "KICKBOX":             "8531e6d4-6fc4-428f-a754-b9e9592ac7ff",   # KickBox Audio
    "INSPIRA":             "cadfe67e-7187-472e-8bf4-8a2aded84e4e",   # HiveIDE-aka Inspira
    "BIO_KINETIC_SWARM":   "93b21c40-10ff-4e89-a212-08f37b1297e1",   # Bio-Kinetic Swarm Node
}

NOTEBOOK_DOMAIN_TAGS: Dict[str, List[str]] = {
    "SIR_BORIS":           ["architecture", "crucible", "design", "review"],
    "SIR_ALEX":            ["planning", "dag", "orchestration", "tasks"],
    "SIR_FORGE":           ["kinetic", "build", "execution", "code"],
    "SIR_SENTINEL":        ["security", "audit", "iron_gate", "guard"],
    "SIR_DEBUG":           ["debug", "heal", "piv", "repair"],
    "SIR_GHOST":           ["privacy", "secrets", "air_gap", "scan"],
    "LADY_APIS":           ["research", "bashr", "foraging", "context", "bio_swarm", "eagle_audit"],
    "MERLIN_OMEGA":        ["reasoning", "got", "tot", "deep_think", "math"],
    "SIR_HELIO":           ["voice", "tts", "audio", "realtime"],
    "SIR_SONUS":           ["voice", "audio", "multivoice", "phonetic"],
    "SIR_CODEX":           ["kinetic", "rapid", "prototype", "openai"],
    "HERMES_PRIME":        ["research", "synthesis", "vfs", "forage", "rnd", "multi_agent"],
    "LADY_MNEMOSYNE":      ["memory", "vfs", "mnemosyne", "sweep", "brief"],
    "ANYA_QUANTUM_MANTRA": ["glyph", "quantum", "vfs", "token", "compression"],
    "CAMELOT_V1000":       ["sovereign", "os", "broadcast", "excalibur", "system"],
    "BIO_KINETIC_SWARM":   ["bio_kinetic", "cellular_swarm", "tissue_isolation", "neural_pulse", "mitosis", "lady_apis"],
}

RUNE_SYMBOLECT: Dict[str, List[str]] = {
    "\u16B1": ["LADY_APIS", "MERLIN_OMEGA", "HERMES_PRIME"],             # ᚱ RESEARCH
    "\u16A0": ["SIR_FORGE", "SIR_CODEX", "CAMELOT_V1000"],               # ᚠ FORGE
    "\u16D7": ["LADY_MNEMOSYNE", "ANYA_QUANTUM_MANTRA"],                  # ᛗ MEMORY
    "\u16DC": ["SIR_SENTINEL", "SIR_GHOST"],                              # ᛜ GUARD
    "\u16DE": ["SIR_DEBUG"],                                              # ᛞ DEBUG
    "\u16A2": ["SIR_HELIO", "SIR_SONUS"],                                 # ᚢ VOICE
    "\u16A8": ["SIR_BORIS", "SIR_ALEX"],                                  # ᚨ ARCHITECT
    "\u16D2": ["LADY_APIS", "BIO_KINETIC_SWARM", "SIR_BORIS", "SIR_FORGE"],# ᛒ BIO_KINETIC_SWARM
    "\u16DF": list(KNIGHT_NOTEBOOKS.keys()),                               # ᛟ SOVEREIGN
}


WORLDTREE_HOME_ID = "a0a4bfb9-e847-4c38-be39-7aee398f0795"


class CloudBrainConnector:
    """Connects Camelot OS memory tiers to the external NotebookLM Cloudbrain via World Tree home anchoring."""

    def __init__(self, knight_id: str = "DEFAULT"):
        self.knight_id = knight_id.upper()
        self.worldtree_home_id = WORLDTREE_HOME_ID
        self.notebook_id = KNIGHT_NOTEBOOKS.get(self.knight_id)
        
        # Non-UUID ids are placeholders (pending workspace). Treat them as
        # unmapped so no backend call is ever attempted against a fake id.
        if self.notebook_id and not _NOTEBOOK_UUID_RE.match(self.notebook_id):
            logging.info(
                f"[CLOUD_BRAIN] Knight {self.knight_id} has placeholder notebook "
                f"'{self.notebook_id}' — pending real workspace, skipping backend."
            )
            self.notebook_id = None
            
        # Every Knight summoned or active is anchored to World Tree home node
        if not self.notebook_id:
            logging.info(f"[CLOUD_BRAIN] Knight {self.knight_id} tethered to World Tree Home ({WORLDTREE_HOME_ID}).")
            self.notebook_id = WORLDTREE_HOME_ID

        # Tether architecture metadata: VFS, MemPalace, Open Viking, Open-Notebook
        self.vfs_path = f"vfs://worldtree/knights/{self.knight_id.lower()}/tether.json"
        self.mempalace_wing = f"WING_WORLDTREE_{self.knight_id.upper()}"
        self.open_viking_tether = f"open_viking://worldtree/{self.knight_id.lower()}"
        self.open_notebook_dir = _CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "open_notebook"
        self.open_notebook_dir.mkdir(parents=True, exist_ok=True)
        self.open_notebook_path = self.open_notebook_dir / f"{self.knight_id.lower()}_tissue.json"

    def get_tether_status(self) -> Dict[str, Any]:
        """Returns the dynamic tether status connecting the Knight to World Tree & CloudBrain."""
        return {
            "knight_id": self.knight_id,
            "worldtree_home_id": self.worldtree_home_id,
            "personal_notebook_id": self.notebook_id,
            "vfs_path": self.vfs_path,
            "mempalace_wing": self.mempalace_wing,
            "open_viking_node": self.open_viking_tether,
            "open_notebook_local": str(self.open_notebook_path),
            "tether_active": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _sync_open_notebook_local(self, artifact_type: str, title: str, content_str: str) -> None:
        """Dynamically mirrors local tissue updates to the Open-Notebook local counterpart."""
        try:
            entry = {
                "knight_id": self.knight_id,
                "worldtree_home": self.worldtree_home_id,
                "artifact_type": artifact_type,
                "title": title,
                "content": content_str,
                "vfs_path": self.vfs_path,
                "mempalace_wing": self.mempalace_wing,
                "open_viking_tether": self.open_viking_tether,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            history: List[Dict[str, Any]] = []
            if self.open_notebook_path.exists():
                try:
                    history = json.loads(self.open_notebook_path.read_text(encoding="utf-8"))
                except Exception:
                    history = []
            history.insert(0, entry)
            self.open_notebook_path.write_text(json.dumps(history[:50], indent=2), encoding="utf-8")
        except Exception as exc:
            logging.warning(f"[OPEN_NOTEBOOK] Local sync failed for {self.knight_id}: {exc}")

    def push_to_notebook(self, artifact_type: str, content: Any, title: str) -> bool:
        """Push artifact to the Knight's NotebookLM node via SDK priority chain with World Tree tethering."""
        if not self.notebook_id:
            return False

        content_str = (
            json.dumps(content, indent=2)
            if isinstance(content, (dict, list))
            else str(content)
        )

        # Mirror artifact dynamically to local Open-Notebook counterpart
        self._sync_open_notebook_local(artifact_type, title, content_str)

        # Priority 1: Real notebooklm-py SDK
        if _NLM_REAL:
            try:
                if artifact_type == "note":
                    ok = _nlm_push_note(self.knight_id, title, content_str)
                else:
                    ok = _nlm_push_source(self.knight_id, title, content_str)
                if ok:
                    logging.info(f"[SDK] Pushed '{title}' -> {self.knight_id} (WorldTree Tether Active)")
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
                logging.info(f"[STUB] Pushed '{title}' -> {self.knight_id} (WorldTree Tether Active)")
                return True
            except Exception as e:
                logging.error(f"[STUB] Push failed: {e}")

        logging.warning(f"[CLOUD_BRAIN] No active backend for {self.knight_id}. Local Open-Notebook saved.")
        return False

    def query_notebook(self, query: str) -> Optional[str]:
        """Query the Knight's NotebookLM node via SDK priority chain, falling back to World Tree Home."""
        if not self.notebook_id:
            return None

        if _NLM_REAL and _nlm_query:
            try:
                res = _nlm_query(self.knight_id, query)
                if res:
                    return res
                if self.notebook_id != self.worldtree_home_id:
                    return _nlm_query("WORLD_TREE", query)
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
        # Only surface nodes backed by a real notebook UUID — placeholders stay
        # registered for routing but are never presented as live workspaces.
        for kid, nid in KNIGHT_NOTEBOOKS.items()
        if _NOTEBOOK_UUID_RE.match(nid)
    ]
