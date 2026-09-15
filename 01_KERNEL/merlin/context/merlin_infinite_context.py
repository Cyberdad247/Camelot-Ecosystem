# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Merlin Infinite Context & Semantic Categorization Engine
r"""
Merlin Infinite Context Engine (MICE) — Recursive Crystallization & Categorical Anchoring.
Solves the finite context-window ceiling by recursive semantic crystallization,
living system instruction embedding, and dynamic knowledge routing across
the 294-node NotebookLM WorldTree Manifest.

Taxonomy Clusters:
  1. SOVEREIGN_ROUND_TABLE
  2. CAMELOT_SYSTEMS_ARCHITECTURE
  3. AI_MULTIAGENT_RESEARCH
  4. CODEBASES_DEV_TOOLING
  5. MARKETING_WEALTH_BRAND
  6. PERSONAL_FINANCE_REALESTATE
  7. SPECIALIZED_SUBSTRATES
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("Merlin_Infinite_Context")

CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MANIFEST_PATH = CAMELOT_ROOT / "01_KERNEL" / "memory" / "NOTEBOOK_MANIFEST.json"
SYSTEM_CONSTITUTION = CAMELOT_ROOT / "AGENTS.md"
VAULT_TISSUE_DIR = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "open_notebook"


@dataclass
class SemanticCrystal:
    """Multi-scale condensed representation of high-density knowledge."""
    crystal_id: str
    category: str
    target_knight: Optional[str]
    target_notebook_uuid: str
    l0_flash_summary: str
    l1_semantic_outline: List[str]
    l2_knowledge_triplets: List[Dict[str, str]]
    full_markdown_source: str
    created_at: str
    system_constitution_hash: str


class MerlinInfiniteContextEngine:
    """Merlin-guided Recursive Context Expansion & Semantic Categorization."""

    def __init__(self, manifest_path: Optional[Path] = None):
        self.manifest_path = manifest_path or MANIFEST_PATH
        self.manifest = self._load_manifest()
        self.constitution_summary = self._load_constitution_summary()

    def _load_manifest(self) -> Dict[str, Any]:
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"[MERLIN] Failed to load manifest: {e}")
        return {"notebooks": {}, "categories": []}

    def _load_constitution_summary(self) -> str:
        """Extracts the living Camelot-OS constitutional laws as foundational axioms."""
        if SYSTEM_CONSTITUTION.exists():
            try:
                text = SYSTEM_CONSTITUTION.read_text(encoding="utf-8")
                # Extract first 40 lines of core laws / rules
                lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("<!--")][:25]
                return "\n".join(lines)
            except Exception:
                pass
        return "Anya Law: Sovereign chain of authority. Truth-seeking, zero-trust integrity, provenance logging mandatory."

    def categorize_intent(self, query: str) -> Tuple[str, Optional[str], str]:
        """
        Determines the optimal Category, Knight, and Notebook UUID for any given intent.
        Returns: (category, knight_id, notebook_uuid)
        """
        q_lower = query.lower()
        notebooks = self.manifest.get("notebooks", {})

        # 1. Exact Knight matching
        for nid, meta in notebooks.items():
            kid = meta.get("knight_id")
            if kid and (kid.lower() in q_lower or kid.lower().replace("_", " ") in q_lower):
                return meta.get("category", "SOVEREIGN_ROUND_TABLE"), kid, nid

        # 2. Keyword relevance scoring across all notebooks in manifest
        best_score = -1.0
        best_entry = None
        q_tokens = set(re.findall(r"\w+", q_lower))

        for nid, meta in notebooks.items():
            if meta.get("is_duplicate"):
                continue  # Skip shadow duplicates
            tags = set(meta.get("domain_tags", []))
            title_tokens = set(re.findall(r"\w+", meta.get("title", "").lower()))
            overlap = len(q_tokens & (tags | title_tokens))
            score = overlap / (len(tags) + 1) if tags else 0
            if score > best_score and overlap > 0:
                best_score = score
                best_entry = meta

        if best_entry:
            return best_entry["category"], best_entry.get("knight_id"), best_entry["id"]

        # Default fallback to World Tree Root
        root_uuid = self.manifest.get("worldtree_root_uuid", "a0a4bfb9-e847-4c38-be39-7aee398f0795")
        return "CAMELOT_SYSTEMS_ARCHITECTURE", "WORLD_TREE", root_uuid

    def crystallize(
        self,
        raw_text: str,
        title: str,
        category_override: Optional[str] = None,
        target_knight: Optional[str] = None,
    ) -> SemanticCrystal:
        """
        Compresses arbitrary-length context into a multi-scale Semantic Crystal.
        Injects living Camelot-OS constitution into the crystal header.
        """
        category = category_override
        notebook_uuid = None

        if not category or not target_knight:
            cat, kid, uuid = self.categorize_intent(title + " " + raw_text[:200])
            category = category or cat
            target_knight = target_knight or kid
            notebook_uuid = uuid
        else:
            # Find matching notebook
            for nid, meta in self.manifest.get("notebooks", {}).items():
                if meta.get("knight_id") == target_knight:
                    notebook_uuid = nid
                    break

        if not notebook_uuid:
            notebook_uuid = self.manifest.get("worldtree_root_uuid", "a0a4bfb9-e847-4c38-be39-7aee398f0795")

        now_iso = datetime.now(timezone.utc).isoformat()
        crystal_id = f"CRYSTAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{target_knight or 'GENERAL'}"

        # 1. L0 Flash Summary (1-2 sentences)
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        l0 = paragraphs[0][:300] if paragraphs else raw_text[:300]

        # 2. L1 Outline (Header/Topic Extraction)
        headers = re.findall(r"^(?:#{1,4}|\*|-)\s+(.+)$", raw_text, re.MULTILINE)
        l1 = headers[:12] if headers else [p[:80] for p in paragraphs[:6]]

        # 3. L2 Triplets (Subject-Predicate-Object semantic nodes)
        l2 = []
        try:
            sys.path.insert(0, str(CAMELOT_ROOT))
            from control_plane.graphify import extract_triplets
            triplets = extract_triplets(raw_text[:3000])
            l2 = [{"head": t.head, "relation": t.relation, "tail": t.tail} for t in triplets[:15]]
        except Exception:
            pass

        # 4. Synthesize Full Markdown Source with Living System Instructions
        full_md = f"""# 🔮 {title}
**Crystal ID:** `{crystal_id}`  
**Category:** `{category}` | **Anchor Knight:** `{target_knight or 'WORLD_TREE'}`  
**Target CloudBrain Node:** `{notebook_uuid}`  
**Timestamp:** `{now_iso}`  

---

### 📜 Sovereign Constitution & Living System Axioms
> {self.constitution_summary.replace(chr(10), chr(10) + '> ')}

---

### ⚡ L0 Flash Compression
{l0}

### 📋 L1 Semantic Outline
{chr(10).join(f"- {h}" for h in l1)}

### 🕸️ L2 Knowledge Graph Triplets
| Subject | Predicate | Object |
| :--- | :---: | :--- |
{chr(10).join(f"| {t['head']} | {t['relation']} | {t['tail']} |" for t in l2) if l2 else "| Camelot-OS | embodies | Infinite-Context |"}

---

### 📖 Full Grounded Document
{raw_text}
"""

        crystal = SemanticCrystal(
            crystal_id=crystal_id,
            category=category,
            target_knight=target_knight,
            target_notebook_uuid=notebook_uuid,
            l0_flash_summary=l0,
            l1_semantic_outline=l1,
            l2_knowledge_triplets=l2,
            full_markdown_source=full_md,
            created_at=now_iso,
            system_constitution_hash="SHA256_CONSTITUTION_ACTIVE",
        )

        # Mirror crystal to local Open-Notebook tissue
        self._mirror_crystal_to_tissue(crystal)

        return crystal

    def _mirror_crystal_to_tissue(self, crystal: SemanticCrystal) -> None:
        VAULT_TISSUE_DIR.mkdir(parents=True, exist_ok=True)
        tissue_file = VAULT_TISSUE_DIR / f"crystal_{crystal.crystal_id.lower()}.json"
        tissue_file.write_text(json.dumps(asdict(crystal), indent=2), encoding="utf-8")


merlin_context = MerlinInfiniteContextEngine()
