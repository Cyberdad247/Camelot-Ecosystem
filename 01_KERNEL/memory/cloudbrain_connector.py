import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Fallback or hypothetical notebooklm wrapper based on previous code
try:
    from notebooklmpy import NotebookLM
except ImportError:
    NotebookLM = None

# Mapping of Knight names to NotebookLM IDs
KNIGHT_NOTEBOOKS: Dict[str, str] = {
    "SIR_BORIS":          "f7707daa-2d10-4db8-8fda-be4661a27793",
    "SIR_ALEX":           "f490c05e-d8c4-4008-87e1-5f901bf57c6a",
    "SIR_FORGE":          "91c5da8b-e2de-4a56-b7fd-c8b76c00afc7",
    "SIR_SENTINEL":       "07cbb441-f008-424c-820a-85676210be39",
    "SIR_DEBUG":          "fdc42a4a-3060-4eac-b57c-8e6009ed634a",
    "SIR_GHOST":          "422a184b-93e7-4dfd-8a12-75d2268b6c60",
    "LADY_APIS":          "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f",
    "MERLIN_OMEGA":       "af927fde-d7eb-42ee-8c79-51b3e78ef39b",
    "SIR_HELIO":          "56820318-bb91-451f-aac4-4b46424898cf",
    "SIR_SONUS":          "b8a1c3d5-e2f4-4687-9a01-234567890abc",
    "SIR_CODEX":          "8c656cfa-a189-409e-a72d-07692a47f17e",
    "LADY_MNEMOSYNE":     "mnemosyne-cloudbrain-vfs-1100",
    "ANYA_QUANTUM_MANTRA":"anya-glyph-engine-vfs-1200",
    "CAMELOT_V1000":      "camelot-os-v1000-excalibur-a",
}

# Domain vectors — maps each notebook to its capability domain tags
NOTEBOOK_DOMAIN_TAGS: Dict[str, List[str]] = {
    "SIR_BORIS":          ["architecture", "crucible", "design", "review"],
    "SIR_ALEX":           ["planning", "dag", "orchestration", "tasks"],
    "SIR_FORGE":          ["kinetic", "build", "execution", "code"],
    "SIR_SENTINEL":       ["security", "audit", "iron_gate", "guard"],
    "SIR_DEBUG":          ["debug", "heal", "piv", "repair"],
    "SIR_GHOST":          ["privacy", "secrets", "air_gap", "scan"],
    "LADY_APIS":          ["research", "bashr", "foraging", "context"],
    "MERLIN_OMEGA":       ["reasoning", "got", "tot", "deep_think", "math"],
    "SIR_HELIO":          ["voice", "tts", "audio", "realtime"],
    "SIR_SONUS":          ["voice", "audio", "multivoice", "phonetic"],
    "SIR_CODEX":          ["kinetic", "rapid", "prototype", "openai"],
    "LADY_MNEMOSYNE":     ["memory", "vfs", "mnemosyne", "sweep", "brief"],
    "ANYA_QUANTUM_MANTRA":["glyph", "quantum", "vfs", "token", "compression"],
    "CAMELOT_V1000":      ["sovereign", "os", "broadcast", "excalibur", "system"],
}

# Rune Symbolect assignment table
RUNE_SYMBOLECT: Dict[str, List[str]] = {
    "\u16B1":  ["LADY_APIS", "MERLIN_OMEGA"],                                           # ᚱ RESEARCH
    "\u16A0":  ["SIR_FORGE", "SIR_CODEX", "CAMELOT_V1000"],                            # ᚠ FORGE
    "\u16D7":  ["LADY_MNEMOSYNE", "ANYA_QUANTUM_MANTRA"],                               # ᛗ MEMORY
    "\u16DC":  ["SIR_SENTINEL", "SIR_GHOST"],                                           # ᛜ GUARD
    "\u16DE":  ["SIR_DEBUG"],                                                            # ᛞ DEBUG
    "\u16A2":  ["SIR_HELIO", "SIR_SONUS"],                                              # ᚢ VOICE
    "\u16A8":  ["SIR_BORIS", "SIR_ALEX"],                                               # ᚨ ARCHITECT
    "\u16DF":  list(KNIGHT_NOTEBOOKS.keys()),                                            # ᛟ SOVEREIGN (broadcast)
}


class CloudBrainConnector:
    """Connects Camelot OS memory tiers to the external NotebookLM Cloud Brain."""

    def __init__(self, knight_id: str = "DEFAULT"):
        self.knight_id = knight_id.upper()
        self.notebook_id = KNIGHT_NOTEBOOKS.get(self.knight_id)
        if not self.notebook_id:
            logging.warning(f"[CLOUD_BRAIN] Unmapped Knight ID: {knight_id}. Cloud Brain sync disabled.")

    def push_to_notebook(self, artifact_type: str, content: Any, title: str) -> bool:
        """Push high-complexity artifacts to the Knight's NotebookLM workspace."""
        if not self.notebook_id or not NotebookLM:
            return False

        try:
            if isinstance(content, dict) or isinstance(content, list):
                content_str = json.dumps(content, indent=2)
            else:
                content_str = str(content)

            # Initialize workspace connection
            ws = NotebookLM(notebook_id=self.notebook_id)
            
            # Push based on artifact type (source or note)
            if artifact_type == "source":
                ws.add_source(text=content_str, title=title)
            elif artifact_type == "note":
                ws.create_note(title=title, content=content_str)
            else:
                ws.add_source(text=content_str, title=title)
            
            logging.info(f"[CLOUD_BRAIN] Successfully pushed artifact '{title}' to {self.knight_id}'s Notebook.")
            return True
        except Exception as e:
            logging.error(f"[CLOUD_BRAIN] Push failed for {self.knight_id}: {str(e)}")
            return False

    def query_notebook(self, query: str) -> Optional[str]:
        """Retrieve synthesized insights from the Knight's NotebookLM workspace."""
        if not self.notebook_id or not NotebookLM:
            return None

        try:
            ws = NotebookLM(notebook_id=self.notebook_id)
            result = ws.query(query)
            logging.info(f"[CLOUD_BRAIN] Successfully queried {self.knight_id}'s Notebook.")
            return result
        except Exception as e:
            logging.error(f"[CLOUD_BRAIN] Query failed for {self.knight_id}: {str(e)}")
            return None


# ── Worldtree Batch Operations ─────────────────────────────────────────────────

def batch_push(
    artifact_type: str,
    content: Any,
    title: str,
    target_knights: Optional[List[str]] = None,
    max_workers: int = 6,
) -> Dict[str, bool]:
    """Fan-out push to multiple Cloudbrain nodes concurrently.

    Args:
        target_knights: list of knight IDs. If None, broadcasts to all.
        max_workers: concurrent thread limit (default 6 for 14 nodes).
    Returns:
        dict mapping knight_id -> success bool.
    """
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
            status = "OK" if ok else "SKIP"
            logging.info(f"[BATCH_PUSH] {kid}: {status}")

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
    """Mathematical domain router: returns ordered list of best-fit notebook IDs.

    Scoring: Φ(task, n) = |intersection(task_keywords, domain_tags[n])| / |domain_tags[n]|
    Returns all notebooks with score > 0, sorted descending by score.
    """
    scores: Dict[str, float] = {}
    kw_set = {k.lower() for k in task_keywords}
    for knight, tags in NOTEBOOK_DOMAIN_TAGS.items():
        tag_set = set(tags)
        score = len(kw_set & tag_set) / len(tag_set) if tag_set else 0.0
        if score > 0:
            scores[knight] = score

    return sorted(scores, key=lambda k: scores[k], reverse=True)


def list_all_notebooks() -> List[Dict[str, Any]]:
    """Returns a structured list of all registered Worldtree Cloudbrain nodes."""
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
