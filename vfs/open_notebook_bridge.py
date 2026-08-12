# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — WorldTree Open-Notebook Dynamic Bridge
r"""
Connects summoned/active Knights to their dynamic local counterpart (Open-Notebook)
and tethers them to the World Tree Home node (a0a4bfb9-e847-4c38-be39-7aee398f0795).

Architecture Integrations:
  * WorldTree Home Node  : a0a4bfb9-e847-4c38-be39-7aee398f0795
  * VFS Path            : vfs://worldtree/knights/<knight_id>/
  * MemPalace Wing      : WING_WORLDTREE_<KNIGHT_ID>
  * Open Viking Node    : open_viking://worldtree/<knight_id>
  * Open-Notebook Local : 03_VAULT/runtime_state/open_notebook/<knight_id>_tissue.json
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent
_OPEN_NOTEBOOK_DIR = _CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "open_notebook"
_OPEN_NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)

WORLDTREE_HOME_ID = "a0a4bfb9-e847-4c38-be39-7aee398f0795"


class OpenNotebookBridge:
    """Manages dynamic local counterpart synchronization and WorldTree tethering for all Knights."""

    def __init__(self, knight_id: str = "ANYA_OMEGA"):
        self.knight_id = knight_id.upper()
        self.worldtree_home_id = WORLDTREE_HOME_ID
        self.vfs_path = f"vfs://worldtree/knights/{self.knight_id.lower()}/tether.json"
        self.mempalace_wing = f"WING_WORLDTREE_{self.knight_id.upper()}"
        self.open_viking_tether = f"open_viking://worldtree/{self.knight_id.lower()}"
        self.local_tissue_path = _OPEN_NOTEBOOK_DIR / f"{self.knight_id.lower()}_tissue.json"

    def get_tether_manifest(self) -> Dict[str, Any]:
        """Returns complete tether manifest linking WorldTree, VFS, MemPalace, Open-Viking, and Open-Notebook."""
        return {
            "knight_id": self.knight_id,
            "worldtree_home": self.worldtree_home_id,
            "vfs_path": self.vfs_path,
            "mempalace_wing": self.mempalace_wing,
            "open_viking_tether": self.open_viking_tether,
            "open_notebook_local": str(self.local_tissue_path),
            "status": "ACTIVE_TETHERED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def sync_local_tissue(self, title: str, content: Any, artifact_type: str = "tissue") -> Dict[str, Any]:
        """Syncs local tissue artifact dynamically into the Open-Notebook local counterpart."""
        content_str = json.dumps(content, indent=2) if isinstance(content, (dict, list)) else str(content)
        entry = {
            "knight_id": self.knight_id,
            "worldtree_home": self.worldtree_home_id,
            "artifact_type": artifact_type,
            "title": title,
            "content": content_str,
            "vfs_path": self.vfs_path,
            "mempalace_wing": self.mempalace_wing,
            "open_viking_tether": self.open_viking_tether,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

        history: List[Dict[str, Any]] = []
        if self.local_tissue_path.exists():
            try:
                history = json.loads(self.local_tissue_path.read_text(encoding="utf-8"))
            except Exception:
                history = []

        history.insert(0, entry)
        self.local_tissue_path.write_text(json.dumps(history[:100], indent=2), encoding="utf-8")
        logging.info(f"[OPEN_NOTEBOOK] Synced '{title}' to {self.local_tissue_path.name}")
        return entry


def audit_all_knight_tethers() -> Dict[str, Any]:
    """Audits tether configuration for all registered Knights against WorldTree home."""
    import sys
    sys.path.insert(0, str(_CAMELOT_ROOT / "01_KERNEL"))
    from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS

    tethers = {}
    for knight in KNIGHT_NOTEBOOKS:
        bridge = OpenNotebookBridge(knight_id=knight)
        tethers[knight] = bridge.get_tether_manifest()

    return {
        "worldtree_home": WORLDTREE_HOME_ID,
        "total_knights_tethered": len(tethers),
        "tethers": tethers,
    }


if __name__ == "__main__":
    report = audit_all_knight_tethers()
    print(json.dumps(report, indent=2))
