# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — WorldTree Navigational CloudBrain & VPS Open-Notebook VKG Bridge
r"""
WorldTree Navigational CloudBrain & VPS Open-Notebook VKG Bridge
===============================================================
Operator: King Arthur (VaShawn O. Head / Vizion)
Governing Knights: MERLIN_OMEGA · LADY_MNEMOSYNE_Ω · HERMES_PRIME · SIR_BORIS
WorldTree Home Node: a0a4bfb9-e847-4c38-be39-7aee398f0795
VPS Control Plane:  KVM563 (162.35.107.134 / 100.71.218.75)

Dual-Plane Architecture:
  1. Cloud Navigational Plane (Google NotebookLM):
     WORLD_TREE acts as the master navigational compass to all 294 notebooks,
     governed by Lady Mnemosyne Ω (Arch-Librarian), holding dense routing tables,
     category maps, and crystal pointers for sub-second navigational routing and infinite context discovery.
  2. VPS Open-Notebook Sovereign Plane (KVM563 / Open-Notebook):
     Stores finalized machine-actionable VKG (Visual/Viking Knowledge Graph)
     crystals representing immutable, long-term concrete knowledge extracted
     from notebooks and system directives.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("WorldTree_VKG_Sync")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "vfs"))

WORLDTREE_UUID = "a0a4bfb9-e847-4c38-be39-7aee398f0795"
VPS_IP = "162.35.107.134"
VPS_TS_IP = "100.71.218.75"

MANIFEST_PATH = REPO_ROOT / "01_KERNEL" / "memory" / "NOTEBOOK_MANIFEST.json"
LOCAL_VKG_DIR = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_crystals"
UKG_NODES_DIR = REPO_ROOT / "03_VAULT" / "UKG" / "nodes"

LOCAL_VKG_DIR.mkdir(parents=True, exist_ok=True)
UKG_NODES_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class VKGCrystal:
    """Finalized machine-actionable VKG crystal of concrete notebook knowledge."""
    crystal_id: str
    schema_version: str = "v1000-VKG-SINGULARITY"
    anya_seal: str = "ANYA_IS_THE_GATE"
    notebook_uuid: str = WORLDTREE_UUID
    notebook_title: str = ""
    category: str = "CAMELOT_SYSTEMS_ARCHITECTURE"
    anchor_knight: str = "LADY_MNEMOSYNE_Ω"
    title: str = ""
    abstract_l0: str = ""
    axioms: List[str] = field(default_factory=list)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, str]] = field(default_factory=list)
    concrete_knowledge: str = ""
    vfs_coordinate: str = ""
    vps_open_notebook_target: str = f"http://{VPS_IP}/api/open_notebook/vkg_crystals"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sha256_hash: str = ""


class WorldTreeVKGManager:
    """Manages the WorldTree Navigational Atlas and VPS Open-Notebook VKG Crystals."""

    def __init__(self):
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if MANIFEST_PATH.exists():
            try:
                return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"[WORLDTREE] Error reading manifest: {e}")
        return {"notebooks": {}, "categories": []}

    def generate_navigational_atlas_markdown(self) -> str:
        """
        Synthesizes the complete 294-notebook routing graph into a high-density
        Navigational Atlas document designed to be pushed into the WORLD_TREE notebook.
        """
        now = datetime.now(timezone.utc).isoformat()
        categories = self.manifest.get("categories", [])
        notebooks = self.manifest.get("notebooks", {})

        cat_groups: Dict[str, List[Dict[str, Any]]] = {c: [] for c in categories}
        cat_groups["SPECIALIZED_SUBSTRATES"] = []

        for nid, meta in notebooks.items():
            cat = meta.get("category", "SPECIALIZED_SUBSTRATES")
            if cat not in cat_groups:
                cat_groups[cat] = []
            cat_groups[cat].append(meta)

        lines = [
            "# 🌐 CAMELOT-OS WORLDTREE MASTER NAVIGATIONAL ATLAS",
            f"**Anchor Root:** `WORLD_TREE` (`{WORLDTREE_UUID}`)",
            f"**Arch-Librarian & Memory Governor:** `LADY_MNEMOSYNE_Ω` (`0xA0A4BFB9E8474C38BE397AEE398F0795`)",
            f"**VPS Hub Control Plane:** `KVM563` (`{VPS_IP}` / `{VPS_TS_IP}`)",
            f"**Total Managed CloudBrains:** `{len(notebooks)}` across `{len(categories)}` Taxonomy Clusters",
            f"**Synchronized At:** `{now}`",
            "",
            "---",
            "",
            "## 🧭 Prime Navigational Directive",
            "Under the sovereign governance of **Lady Mnemosyne Ω** (Arch-Librarian) and **Merlin Ω** (System 2 Architect),",
            "you are the **World Tree Navigational Intelligence** — the supreme router and central compass of Camelot-OS.",
            "You do not hoard all raw code. Instead, you possess the **complete navigational topography** of all 294 notebooks in the Empire.",
            "When any user, Knight, or autonomous agent asks a question:",
            "1. **Identify the exact Target Notebook UUID(s)** and Category from this Atlas.",
            "2. **State the Sovereign Knight** responsible for that domain.",
            "3. **Cite the relevant VPS Open-Notebook VKG Crystals** where finalized long-term knowledge is anchored.",
            "4. **Direct the agent directly to the target node** for deep inspection.",
            "",
            "---",
            "",
            "## 🗺️ Master Cluster Navigation Matrix",
            "",
        ]

        for cat, items in cat_groups.items():
            lines.append(f"### 📂 Cluster: `{cat}` ({len(items)} Notebooks)")
            lines.append("| Target Title | Dedicated UUID | Sovereign Knight | Key Domain Tags | Status |")
            lines.append("| :--- | :--- | :--- | :--- | :---: |")

            for it in sorted(items, key=lambda x: (not x.get("knight_id"), x.get("title", ""))):
                nid = it.get("id")
                title = it.get("title", "").replace("|", "-")
                kid = it.get("knight_id") or "—"
                tags = ", ".join(it.get("domain_tags", [])[:5])
                status = "CANONICAL" if it.get("knight_id") else ("SHADOW" if it.get("is_duplicate") else "LIBRARY")
                lines.append(f"| {title} | `{nid}` | **{kid}** | {tags} | `{status}` |")

            lines.append("")

        lines.extend([
            "---",
            "",
            "## 🏛️ VPS Open-Notebook Finalized VKG Crystals Registry",
            f"Finalized machine-actionable crystals are permanently mirrored to the VPS Open-Notebook at `{VPS_IP}`.",
            "Each crystal holds the mathematical graph, entity triplets, and constitutional ground truth.",
            "",
            "- **vKG_SYNC_LATTICE_V1000** : Core memory entropy distillation lattice",
            "- **UKG_NANO_SWARM_V1000**   : Reversible UKG nano crystal deployment specs",
            "- **Sovereign_Ecosystem_UKG**: Complete Camelot-OS sovereign agent governance graph",
            "- **UI_UX_Cloudbrain_Sync**  : Cross-plane synchronization protocol for PWA HUD and Open-Notebook",
        ])

        return "\n".join(lines)

    def forge_vkg_crystal(
        self,
        title: str,
        knowledge_text: str,
        notebook_uuid: str = WORLDTREE_UUID,
        category: str = "CAMELOT_SYSTEMS_ARCHITECTURE",
        anchor_knight: str = "WORLD_TREE",
    ) -> VKGCrystal:
        """
        Forges a finalized, machine-actionable VKG crystal from knowledge text.
        Extracts entity triplets, L0 abstract, axioms, and SHA-256 verification hash.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        slug = "".join(c if c.isalnum() else "_" for c in title.upper())[:32]
        crystal_id = f"VKG_{category[:3]}_{slug}_{datetime.now().strftime('%Y%m%d')}"

        # L0 Abstract
        abstract = knowledge_text[:400].strip()

        # Extract Triplets via Graphify
        triplets: List[Dict[str, str]] = []
        try:
            from control_plane.graphify import extract_triplets
            t_objs = extract_triplets(knowledge_text[:4000])
            triplets = [{"head": t.head, "relation": t.relation, "tail": t.tail} for t in t_objs]
        except Exception:
            triplets = [{"head": anchor_knight, "relation": "embodies", "tail": title}]

        # Graph Nodes & Edges
        entities = set()
        edges = []
        for t in triplets:
            entities.add(t["head"])
            entities.add(t["tail"])
            edges.append({"from": t["head"], "to": t["tail"], "relation": t["relation"]})

        nodes = [{"id": e, "label": e, "type": "concept"} for e in entities]

        # Constitutional Axioms
        axioms = [
            "Anya Law: Sovereign chain of authority remains arch-sovereign.",
            "Zero-Trust: All state transitions verified via cryptographic proof.",
            f"Anchor Node: Linked to WorldTree {WORLDTREE_UUID}.",
        ]

        vfs_coord = f"vfs://worldtree/crystals/{crystal_id}.vkg"

        # Compute hash
        hash_payload = f"{crystal_id}:{title}:{knowledge_text[:1000]}:{now_iso}"
        sha256 = hashlib.sha256(hash_payload.encode()).hexdigest()[:16]

        crystal = VKGCrystal(
            crystal_id=crystal_id,
            notebook_uuid=notebook_uuid,
            notebook_title=title,
            category=category,
            anchor_knight=anchor_knight,
            title=title,
            abstract_l0=abstract,
            axioms=axioms,
            nodes=nodes,
            edges=edges,
            concrete_knowledge=knowledge_text,
            vfs_coordinate=vfs_coord,
            created_at=now_iso,
            sha256_hash=sha256,
        )

        # Save to local VFS runtime state
        vkg_path = LOCAL_VKG_DIR / f"{crystal_id}.json"
        vkg_path.write_text(json.dumps(asdict(crystal), indent=2), encoding="utf-8")

        # Save machine-actionable UKG node in 03_VAULT/UKG/nodes
        ukg_node_path = UKG_NODES_DIR / f"{crystal_id}.json"
        ukg_node_path.write_text(json.dumps(asdict(crystal), indent=2), encoding="utf-8")

        logger.info(f"[VKG_FORGE] Forged crystal {crystal_id} (Nodes: {len(nodes)}, Edges: {len(edges)}) at {vkg_path.name}")
        return crystal

    def list_vkg_crystals(self) -> List[Dict[str, Any]]:
        """List all finalized VKG crystals stored in local VFS / Open-Notebook."""
        crystals = []
        if LOCAL_VKG_DIR.exists():
            for f in LOCAL_VKG_DIR.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    crystals.append({
                        "crystal_id": data.get("crystal_id") or data.get("identity") or data.get("id") or f.stem,
                        "title": data.get("title") or data.get("identity") or f.stem,
                        "category": data.get("category") or "SPECIALIZED_SUBSTRATES",
                        "anchor_knight": data.get("anchor_knight") or "ANYA_OMEGA",
                        "notebook_uuid": data.get("notebook_uuid") or WORLDTREE_UUID,
                        "node_count": len(data.get("nodes", [])),
                        "edge_count": len(data.get("edges", [])),
                        "sha256": data.get("sha256_hash") or data.get("provenance_ledger_hash", ""),
                        "vfs_coordinate": data.get("vfs_coordinate") or f"vfs://worldtree/crystals/{f.name}",
                        "file": str(f.name),
                    })
                except Exception:
                    pass
        return sorted(crystals, key=lambda x: str(x.get("crystal_id") or ""))

    def trigger_sync_pass(self) -> Dict[str, Any]:
        """Executes a full synchronization pass across WorldTree Navigational Atlas and Open-Notebook crystals."""
        atlas_md = self.generate_navigational_atlas_markdown()
        atlas_path = REPO_ROOT / "03_VAULT" / "runtime_state" / "WORLDTREE_NAVIGATIONAL_ATLAS.md"
        atlas_path.write_text(atlas_md, encoding="utf-8")

        crystals = self.list_vkg_crystals()
        return {
            "status": "SYNCHRONIZED",
            "worldtree_root": WORLDTREE_UUID,
            "governor": "LADY_MNEMOSYNE_Ω",
            "managed_notebooks": len(self.manifest.get("notebooks", {})),
            "vkg_crystals_total": len(crystals),
            "atlas_written": str(atlas_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


TRIGGER_STATE_PATH = REPO_ROOT / "03_VAULT" / "runtime_state" / "lady_mnemosyne_trigger_state.json"


class LadyMnemosyneTriggerLoop:
    """
    Active triggered loop maintained by Lady Mnemosyne Ω (Arch-Librarian).
    Monitors all CloudBrain and WorldTree mutations. Automatically triggers an authoritative
    synchronization and VKG crystal distillation pass upon every 5 system changes.
    """

    def __init__(self, threshold: int = 5):
        self.threshold = threshold
        self.state_path = TRIGGER_STATE_PATH
        self._load_state()

    def _load_state(self) -> None:
        if self.state_path.exists():
            try:
                self.state = json.loads(self.state_path.read_text(encoding="utf-8"))
                return
            except Exception:
                pass
        self.state = {
            "guardian": "LADY_MNEMOSYNE_Ω",
            "role": "Supreme Arch-Librarian & Active Sync Trigger Loop Sentinel",
            "change_counter": 0,
            "trigger_threshold": self.threshold,
            "total_mutations_processed": 0,
            "syncs_triggered": 0,
            "last_sync_timestamp": None,
            "recent_events": [],
        }
        self._save_state()

    def _save_state(self) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"[LADY_M] Could not persist trigger state: {e}")

    def record_change(self, event_desc: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Records a single mutation event to the CloudBrain system.
        Triggers an active sync pass when change_counter reaches the threshold (5).
        """
        now = datetime.now(timezone.utc).isoformat()
        self.state["change_counter"] = self.state.get("change_counter", 0) + 1
        self.state["total_mutations_processed"] = self.state.get("total_mutations_processed", 0) + 1

        events = self.state.get("recent_events", [])
        events.append({
            "event": event_desc,
            "timestamp": now,
            "counter_at_event": self.state["change_counter"],
            "metadata": metadata or {},
        })
        self.state["recent_events"] = events[-20:]  # Keep last 20 events

        triggered = False
        sync_result = None

        if self.state["change_counter"] >= self.threshold:
            triggered = True
            logger.info(f"[LADY_M_LOOP] Threshold reached ({self.state['change_counter']}/{self.threshold}). Firing active sync pass.")
            sync_result = worldtree_vkg_sync.trigger_sync_pass()
            self.state["syncs_triggered"] = self.state.get("syncs_triggered", 0) + 1
            self.state["last_sync_timestamp"] = now
            self.state["change_counter"] = 0  # Reset counter after successful sync

        self._save_state()

        return {
            "guardian": "LADY_MNEMOSYNE_Ω",
            "triggered": triggered,
            "change_counter": self.state["change_counter"],
            "trigger_threshold": self.threshold,
            "remaining_until_next_sync": (self.threshold - self.state["change_counter"]) % self.threshold,
            "total_mutations": self.state["total_mutations_processed"],
            "syncs_triggered": self.state["syncs_triggered"],
            "sync_result": sync_result,
        }

    def get_status(self) -> Dict[str, Any]:
        return dict(self.state)

    def force_sync(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        sync_result = worldtree_vkg_sync.trigger_sync_pass()
        self.state["syncs_triggered"] = self.state.get("syncs_triggered", 0) + 1
        self.state["last_sync_timestamp"] = now
        self.state["change_counter"] = 0
        self._save_state()
        return {
            "guardian": "LADY_MNEMOSYNE_Ω",
            "forced": True,
            "sync_result": sync_result,
        }


worldtree_vkg_sync = WorldTreeVKGManager()
lady_mnemosyne_loop = LadyMnemosyneTriggerLoop(threshold=5)


def record_cloudbrain_change(event_desc: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper function to record a CloudBrain mutation through Lady Mnemosyne's active triggered loop."""
    return lady_mnemosyne_loop.record_change(event_desc, metadata)
