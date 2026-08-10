# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Lady M Rune Symbolect Router
"""
Mathematical Rune-to-Notebook assignment router for Lady Mnemosyne.

Assignment function (Merlin's Theorem):
    Φ(task) = argmax_n [ CosSim(task_embedding, notebook_domain[n]) * recency_weight[n] ]

Implemented as a keyword-intersection spectral routing function.
Each Rune maps to a subgraph of the Worldtree.
"""

from __future__ import annotations

import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LOG = logging.getLogger("LadyM_RuneRouter")
CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(CAMELOT_ROOT / "01_KERNEL"))

try:
    from memory.cloudbrain_connector import (
        KNIGHT_NOTEBOOKS,
        NOTEBOOK_DOMAIN_TAGS,
        RUNE_SYMBOLECT,
        batch_push,
        route_by_domain,
        list_all_notebooks,
    )
except ImportError:
    KNIGHT_NOTEBOOKS = {}
    NOTEBOOK_DOMAIN_TAGS = {}
    RUNE_SYMBOLECT = {}
    batch_push = None  # type: ignore
    route_by_domain = None  # type: ignore
    list_all_notebooks = None  # type: ignore
    LOG.error("[RUNE_ROUTER] Failed to import Worldtree Cloudbrain connector.")


# ── Rune glyph → name mapping ──────────────────────────────────────────────────
RUNE_NAMES: Dict[str, str] = {
    "\u16B1": "RESEARCH",
    "\u16A0": "FORGE",
    "\u16D7": "MEMORY",
    "\u16DC": "GUARD",
    "\u16DE": "DEBUG",
    "\u16A2": "VOICE",
    "\u16A8": "ARCHITECT",
    "\u16DF": "SOVEREIGN",
}

# ── Rune keyword triggers ───────────────────────────────────────────────────────
RUNE_KEYWORD_TRIGGERS: Dict[str, List[str]] = {
    "\u16B1": ["research", "find", "search", "query", "investigate", "scout", "bashr"],
    "\u16A0": ["build", "forge", "code", "implement", "deploy", "execute", "kinetic", "compile"],
    "\u16D7": ["memory", "store", "remember", "vfs", "mempalace", "glyph", "compress", "token"],
    "\u16DC": ["secure", "guard", "audit", "scan", "ghost", "sentinel", "secret", "iron_gate"],
    "\u16DE": ["debug", "heal", "fix", "repair", "error", "bug", "piv"],
    "\u16A2": ["voice", "speak", "tts", "audio", "phonetic", "helio", "sonus"],
    "\u16A8": ["plan", "architect", "design", "strategy", "dag", "orchestrate", "review"],
    "\u16DF": ["broadcast", "all", "sovereign", "system", "excalibur", "os", "camelot"],
}


class RuneRouter:
    """
    Lady M's Rune Symbolect Router — assigns inbound tasks to the
    correct Worldtree Cloudbrain subgraph via mathematical rune scoring.
    """

    def resolve_rune(self, text: str) -> Tuple[str, str]:
        """
        Detect explicit rune glyph OR auto-classify text via keyword scoring.

        Returns: (rune_glyph, rune_name)
        """
        # 1. Check for explicit rune glyph in text
        for rune in RUNE_NAMES:
            if rune in text:
                LOG.info(f"[RUNE] Explicit rune detected: {rune} ({RUNE_NAMES[rune]})")
                return rune, RUNE_NAMES[rune]

        # 2. Keyword scoring: score each rune by term frequency in text
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        for rune, keywords in RUNE_KEYWORD_TRIGGERS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[rune] = score

        if scores:
            best_rune = max(scores, key=lambda r: scores[r])
            LOG.info(f"[RUNE] Auto-classified as: {RUNE_NAMES[best_rune]} (score={scores[best_rune]})")
            return best_rune, RUNE_NAMES[best_rune]

        # 3. Default → SOVEREIGN broadcast
        LOG.info("[RUNE] No match found. Defaulting to SOVEREIGN broadcast.")
        return "\u16DF", "SOVEREIGN"

    def route(self, task: str, content: str, artifact_type: str = "note") -> Dict[str, bool]:
        """
        Full routing pipeline:
          1. Resolve rune from task text
          2. Get target notebooks for that rune
          3. Optionally refine by domain similarity
          4. Batch push to all targets
        """
        rune, rune_name = self.resolve_rune(task)
        target_knights = RUNE_SYMBOLECT.get(rune, list(KNIGHT_NOTEBOOKS.keys()))

        # Refine ordering by domain similarity within the rune's subgraph
        task_words = re.findall(r"\w+", task.lower())
        if route_by_domain:
            domain_ranked = route_by_domain(task_words)
            # Keep only those in rune's target set, domain-ranked first
            refined = [k for k in domain_ranked if k in target_knights]
            remaining = [k for k in target_knights if k not in refined]
            target_knights = refined + remaining

        LOG.info(f"[RUNE_ROUTER] ᚱune: {rune} ({rune_name}) → Dispatching to {target_knights}")

        title = f"[{rune} {rune_name}] {task[:80]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        enriched_content = (
            f"=== WORLDTREE RUNE DISPATCH ===\n"
            f"Rune: {rune} ({rune_name})\n"
            f"Task: {task}\n"
            f"Timestamp: {timestamp}\n"
            f"Target Notebooks: {', '.join(target_knights)}\n"
            f"{'='*40}\n\n"
            f"{content}"
        )

        if batch_push:
            return batch_push(
                artifact_type=artifact_type,
                content=enriched_content,
                title=title,
                target_knights=target_knights,
            )
        return {k: False for k in target_knights}

    def worldtree_report(self) -> str:
        """Generate a full Worldtree state report for Lady M's SQUIRE_BRIEF."""
        lines = [
            "╔══════════════════════════════════════════╗",
            "║     WORLDTREE RUNE SYMBOLECT REGISTRY    ║",
            "╚══════════════════════════════════════════╝",
            "",
        ]
        if list_all_notebooks:
            for node in list_all_notebooks():
                lines.append(f"  [{node['knight_id']}]")
                lines.append(f"    VFS Path  : {node['vfs_path']}")
                lines.append(f"    Domains   : {', '.join(node['domain_tags'])}")
                lines.append(f"    Notebook  : {node['notebook_id']}")
                lines.append("")

        lines.append("── Rune Symbolect Dispatch Table ────────────")
        for rune, name in RUNE_NAMES.items():
            targets = RUNE_SYMBOLECT.get(rune, [])
            lines.append(f"  {rune} {name:<12} → {', '.join(targets)}")
        lines.append("")
        lines.append("⚜️  Lady Mnemosyne | Worldtree Rune Router | Camelot v1000")
        return "\n".join(lines)


# Singleton for import
router = RuneRouter()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    r = RuneRouter()
    print(r.worldtree_report())
    print("\n── Test Routing ──")
    result = r.route(
        task="debug the failing PIV loop in the heal sequence",
        content="Test content for rune routing validation.",
    )
    print(f"Route result: {result}")
