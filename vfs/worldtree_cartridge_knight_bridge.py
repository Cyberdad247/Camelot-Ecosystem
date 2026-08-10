# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Worldtree-Cartridge-Knight Unified VFS Bridge
"""
Unified VFS Router mapping:
  Worldtree (275+ Gemini Notebooks) <---> Scabbard Cartridges (ANT/BEAVER/SPIDER/OCTOPUS) <---> Knight Brains

Uniform VFS URI format:
  vfs://worldtree/knights/{knight_id}/brain       -> Knight Memory & RPG State
  vfs://worldtree/knights/{knight_id}/cartridge   -> Active Scabbard Package Binding
  vfs://worldtree/knights/{knight_id}/notebook    -> NotebookLM Cloudbrain ID
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("WorldtreeCartridgeBridge")
CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CAMELOT_ROOT / "01_KERNEL"))
sys.path.insert(0, str(CAMELOT_ROOT / "vfs"))

try:
    from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS, CloudBrainConnector
except ImportError:
    KNIGHT_NOTEBOOKS = {}
    CloudBrainConnector = None

try:
    from knight_rpg_system import KnightRPGSystem, KNIGHT_CLASSES
except ImportError:
    KnightRPGSystem = None
    KNIGHT_CLASSES = {}

# Scabbard Cartridge Default Knight Assignments
CARTRIDGE_KNIGHT_MAP: Dict[str, List[str]] = {
    "ANT":      ["LADY_APIS", "SIR_SCAVENGER"],                    # Scraping & Extraction
    "BEAVER":   ["SIR_FORGE", "SIR_CODEX", "SIR_ALCHEMIST"],        # AST & Code Refactoring
    "SPIDER":   ["MERLIN_OMEGA", "LADY_APIS", "SIR_HERMES"],        # BASHR Web Research & Foraging
    "OCTOPUS":  ["SIR_BORIS", "SIR_ALEX", "LADY_MNEMOSYNE"]         # Multi-Agent Swarm Orchestration
}


class WorldtreeCartridgeKnightBridge:
    """Provides a unified VFS abstraction for reading/writing Knight brains and dispatching cartridges."""

    def __init__(self):
        self.rpg = KnightRPGSystem() if KnightRPGSystem else None

    def resolve_vfs_uri(self, uri: str) -> Dict[str, Any]:
        """
        Parses `vfs://worldtree/knights/{knight_id}/{target}` into actionable node metadata.
        Target options: `brain`, `cartridge`, `notebook`
        """
        clean = uri.replace("vfs://worldtree/knights/", "").strip("/")
        parts = clean.split("/")

        knight_id = parts[0].upper()
        target = parts[1].lower() if len(parts) > 1 else "brain"

        notebook_id = KNIGHT_NOTEBOOKS.get(knight_id, "UNMAPPED")
        cartridges = [c for c, knights in CARTRIDGE_KNIGHT_MAP.items() if knight_id in knights]
        if not cartridges:
            cartridges = ["BEAVER"]  # Default code execution cartridge

        rpg_data = self.rpg.roster.get(knight_id, {}) if self.rpg else {}

        return {
            "vfs_uri": uri,
            "knight_id": knight_id,
            "target": target,
            "notebook_id": notebook_id,
            "bound_cartridges": cartridges,
            "level": rpg_data.get("level", 1),
            "tier": rpg_data.get("skill_graph_tier", "S1 Atomic"),
            "class": rpg_data.get("title", "Knight of Camelot"),
            "primary_stat": rpg_data.get("primary_stat", "Kinetic"),
            "rune": rpg_data.get("rune", "ᛟ"),
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }

    def push_to_knight_vfs(self, uri: str, content: Any, title: str) -> bool:
        """Pushes data through the VFS URI to the Knight's Cloudbrain node + awards XP."""
        resolved = self.resolve_vfs_uri(uri)
        knight_id = resolved["knight_id"]

        LOG.info(f"🌐 [VFS BRIDGE] Pushing to {uri} ({resolved['class']})...")

        if CloudBrainConnector:
            cb = CloudBrainConnector(knight_id=knight_id)
            ok = cb.push_to_notebook(artifact_type="note", content=content, title=title)
        else:
            ok = False

        if ok and self.rpg:
            # Award XP to knight for active brain update
            self.rpg.award_xp(knight_id, 150, f"VFS Push: {title}")

        return ok

    def list_all_vfs_knights(self) -> List[Dict[str, Any]]:
        """Returns VFS endpoints for all registered knights in the Round Table."""
        endpoints = []
        for knight_id in KNIGHT_CLASSES:
            endpoints.append(self.resolve_vfs_uri(f"vfs://worldtree/knights/{knight_id}/brain"))
        return endpoints


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    bridge = WorldtreeCartridgeKnightBridge()
    res = bridge.resolve_vfs_uri("vfs://worldtree/knights/SIR_FORGE/brain")
    print("\n── VFS Resolution Test ──")
    print(json.dumps(res, indent=2))
    print(f"\nTotal VFS Knight Endpoints: {len(bridge.list_all_vfs_knights())}")
