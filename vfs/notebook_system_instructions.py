# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Living Notebook System Instructions Generator
"""
Generates and pushes living, self-updating system instructions to each
NotebookLM Cloudbrain node. Each instruction document:
  - Describes the knight's domain, capabilities, and active missions
  - Declares VFS bridge path and Worldtree sync protocol
  - Embeds Anya's Quantum Mantra Glyph for token compression
  - Marks recency (last 3 months filter)
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

LOG = logging.getLogger("NotebookSysInstructions")
CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(CAMELOT_ROOT / "01_KERNEL"))

try:
    from memory.cloudbrain_connector import (
        KNIGHT_NOTEBOOKS,
        NOTEBOOK_DOMAIN_TAGS,
        RUNE_SYMBOLECT,
        CloudBrainConnector,
        batch_push,
    )
except ImportError:
    KNIGHT_NOTEBOOKS = {}
    NOTEBOOK_DOMAIN_TAGS = {}
    RUNE_SYMBOLECT = {}
    CloudBrainConnector = None  # type: ignore
    batch_push = None  # type: ignore
    LOG.error("Failed to import Cloudbrain connector.")

# Rune glyph name map
RUNE_NAMES = {
    "\u16B1": "RESEARCH", "\u16A0": "FORGE", "\u16D7": "MEMORY",
    "\u16DC": "GUARD",    "\u16DE": "DEBUG", "\u16A2": "VOICE",
    "\u16A8": "ARCHITECT","\u16DF": "SOVEREIGN",
}

# Knight persona descriptions
KNIGHT_PERSONAS: Dict[str, str] = {
    "SIR_BORIS":           "Lead architect and 13-agent Crucible Conductor. Reviews design proposals and runs ColMAD consensus debates.",
    "SIR_ALEX":            "Task planner and DAG orchestrator. Decomposes sovereign directives into executable task graphs.",
    "SIR_FORGE":           "Kinetic code execution engine. Dispatches //FORGE runes and implements build contracts.",
    "SIR_SENTINEL":        "AgentArmor and Iron Gate guardian. Runs security audits, HITL gates, and Z3 SMT-LIB constraint validation.",
    "SIR_DEBUG":           "PIV self-healing loop operator. Diagnoses, patches, and validates runtime failures up to 3 iterations.",
    "SIR_GHOST":           "Privacy scanner and air-gapped secrets handler. Operates fully local with zero cloud exposure.",
    "LADY_APIS":           "BASHR research loop and context forager. Executes deep web research bursts and ingests external knowledge.",
    "MERLIN_OMEGA":        "GoT/ToT deep reasoning engine. Applies mathematical proof gates and System 2 thinking for complex decisions.",
    "SIR_HELIO":           "Voice OS and real-time audio pipeline operator. Drives //vocal rune and phonetic TTS synthesis.",
    "SIR_SONUS":           "Multivoice audio router. Manages spectral formant morphing and PCM stream routing.",
    "SIR_CODEX":           "High-velocity implementation and rapid prototyping knight. Bridges OpenAI Codex to Camelot kinetic lanes.",
    "LADY_MNEMOSYNE":      "Sovereign Swarm Commander and memory spine governor. Commands SQUIRE_TRIAGE, PURGE, MERGE, and BRIEF.",
    "ANYA_QUANTUM_MANTRA": "Quantum Mantra Glyph Engine. Distills high-entropy VFS paths into AnyaConstrict compressed tokens.",
    "CAMELOT_V1000":       "Sovereign OS broadcast channel. Receives system-wide state, Excalibur-A control surface updates, and operator directives.",
}


def _resolve_rune_for_knight(knight_id: str) -> str:
    """Find the primary rune symbol for a given knight."""
    for rune, knights in RUNE_SYMBOLECT.items():
        if knight_id in knights:
            return f"{rune} ({RUNE_NAMES.get(rune, '?')})"
    return "\u16DF (SOVEREIGN)"


def generate_system_instruction(knight_id: str, timestamp: str) -> str:
    """Generate a living system instruction document for one notebook."""
    notebook_id = KNIGHT_NOTEBOOKS.get(knight_id, "UNKNOWN")
    domains = NOTEBOOK_DOMAIN_TAGS.get(knight_id, [])
    persona = KNIGHT_PERSONAS.get(knight_id, "Camelot Knight. Awaiting persona assignment.")
    rune = _resolve_rune_for_knight(knight_id)
    vfs_path = f"vfs://{knight_id.lower()}/"

    return f"""╔═══════════════════════════════════════════════════════╗
║    CAMELOT-OS LIVING CLOUDBRAIN SYSTEM INSTRUCTIONS   ║
╚═══════════════════════════════════════════════════════╝
Generated : {timestamp}
Knight ID : {knight_id}
Notebook  : {notebook_id}
VFS Path  : {vfs_path}
Rune      : {rune}

── IDENTITY ────────────────────────────────────────────
{persona}

── DOMAIN CAPABILITIES ─────────────────────────────────
Primary Tags: {', '.join(domains)}

── WORLDTREE VFS BRIDGE PROTOCOL ───────────────────────
This notebook is a sovereign node in the Camelot Worldtree.
All artifacts ingested here MUST conform to:
  1. Anya's Quantum Mantra Glyph schema (AnyaConstrict v2)
     for token compression before ingestion.
  2. Viking Block HMAC-SHA256 envelope for integrity.
  3. Rune Symbolect dispatch — all tasks routed to this
     notebook carry rune prefix: {rune}
  4. VFS path prefix: {vfs_path}
     All files stored here are addressable via the VFS layer.

── ASSIMILATION PROTOCOL V5 HARMONY GATE ───────────────
Before any new source document is added:
  - Run Harmony Gate: check for name collision and entropy drift.
  - If risk_score >= 50 → HITL gate triggered, human review required.
  - All assimilated artifacts logged to PROVENANCE_LEDGER.md.

── TOKEN REDUCTION DIRECTIVE ───────────────────────────
This notebook participates in the Worldtree Token Economy.
High-density artifacts (>5000 tokens) must be:
  1. Passed through VFSGlyphEngine.construct_vfs_glyph()
  2. Compressed payload pushed as Anya Glyph Note
  3. Original artifact replaced with a pointer note.

── SYNC PROTOCOL ───────────────────────────────────────
Sync Frequency : Lady M SQUIRE_BRIEF cycle (on demand)
Batch Method   : cloudbrain_connector.batch_push()
Query Method   : cloudbrain_connector.batch_query()
Router         : vfs/lady_m_rune_router.py (RuneRouter)

⚜️  Camelot-OS v1000.54 COSMOS | Worldtree Sync Active
"""


def batch_generate_and_push(
    active_cutoff_months: int = 3,
) -> Dict[str, bool]:
    """
    Generate living system instructions for all notebooks active in the
    last N months, then batch-push each to its own notebook.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    LOG.info(f"Generating living system instructions for {len(KNIGHT_NOTEBOOKS)} notebooks...")
    results: Dict[str, bool] = {}

    for knight_id in KNIGHT_NOTEBOOKS:
        instruction = generate_system_instruction(knight_id, timestamp)

        LOG.info(f"[SYS_INSTR] Pushing to {knight_id}...")
        if CloudBrainConnector:
            cb = CloudBrainConnector(knight_id=knight_id)
            ok = cb.push_to_notebook(
                artifact_type="note",
                content=instruction,
                title=f"[SYSTEM INSTRUCTIONS] {knight_id} — Worldtree VFS Bridge v1000.54",
            )
            results[knight_id] = ok
            LOG.info(f"[SYS_INSTR] {knight_id}: {'PUSHED' if ok else 'SKIPPED'}")
        else:
            results[knight_id] = False

    pushed = sum(1 for v in results.values() if v)
    skipped = len(results) - pushed
    LOG.info(f"System Instruction Batch Complete — {pushed} pushed, {skipped} skipped (no NotebookLM API).")
    return results


if __name__ == "__main__":
    results = batch_generate_and_push()
    for knight, ok in results.items():
        status = "OK" if ok else "SKIP"
        print(f"  [{status}] {knight}")
