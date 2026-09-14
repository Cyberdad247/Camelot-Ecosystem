#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
r"""
[S6-06] cloudbrain_hydrate — Continuous Repo-to-CloudBrain Hydration Pipeline
=============================================================================
Reads living Camelot-OS system instructions (AGENTS.md, CLAUDE.md, directives)
and artifacts, generates structured Merlin Semantic Crystals, and pushes them
into target Knight CloudBrain nodes and the WorldTree root.

Usage:
    python bin/cloudbrain_hydrate.py --knight SIR_BORIS
    python bin/cloudbrain_hydrate.py --worldtree
    python bin/cloudbrain_hydrate.py --all-core
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("CloudBrain_Hydrate")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "vfs"))

from vfs.notebooklm_client import push_source_async, push_note_async
from merlin.context.merlin_infinite_context import merlin_context

AGENTS_MD = REPO_ROOT / "AGENTS.md"
CLAUDE_MD = REPO_ROOT / "03_VAULT" / "training" / "configs" / "CLAUDE.md"
PROVENANCE_LEDGER = REPO_ROOT / "PROVENANCE_LEDGER.md"


async def hydrate_knight(knight_id: str, as_source: bool = True):
    kid = knight_id.upper()
    logger.info(f"Initiating hydration for {kid}...")

    # 1. Read living constitution
    constitution_text = AGENTS_MD.read_text(encoding="utf-8") if AGENTS_MD.exists() else "Sovereign OS"
    title = f"Living_Constitution_{kid}_Hydration"

    # 2. Crystallize via Merlin Infinite Context Engine
    crystal = merlin_context.crystallize(
        raw_text=constitution_text[:12000],  # Fits comfortably in single high-density source
        title=title,
        target_knight=kid,
    )

    logger.info(f"Generated crystal {crystal.crystal_id} for {kid} (Category: {crystal.category})")

    # 3. Push to CloudBrain
    if as_source:
        ok = await push_source_async(kid, crystal.crystal_id, crystal.full_markdown_source)
    else:
        ok = await push_note_async(kid, crystal.crystal_id, crystal.l0_flash_summary)

    if ok:
        logger.info(f"[SUCCESS] Hydrated {kid} CloudBrain node with living system instructions!")
    else:
        logger.warning(f"[MIRRORED] Failed remote push for {kid}. Local VFS tissue saved.")


async def hydrate_worldtree():
    logger.info("Initiating World Tree Root Hydration...")
    text = "# CAMELOT-OS LIVING SYSTEM MANIFEST & ANCHOR\n\n"
    if AGENTS_MD.exists():
        text += "## System Constitution\n" + AGENTS_MD.read_text(encoding="utf-8")[:8000] + "\n\n"

    crystal = merlin_context.crystallize(
        raw_text=text,
        title="WorldTree_Root_Living_Constitution_Sync",
        target_knight="WORLD_TREE",
    )

    ok = await push_source_async("WORLD_TREE", crystal.crystal_id, crystal.full_markdown_source)
    logger.info(f"World Tree hydration status: {'SUCCESS' if ok else 'MIRRORED_LOCAL'}")


def main():
    parser = argparse.ArgumentParser(description="Camelot Repo-to-CloudBrain Hydration")
    parser.add_argument("--knight", type=str, help="Hydrate a specific Knight by ID (e.g. SIR_BORIS, SIR_CODEX)")
    parser.add_argument("--worldtree", action="store_true", help="Hydrate the World Tree root node")
    parser.add_argument("--all-core", action="store_true", help="Hydrate all core Round Table knights")
    args = parser.parse_args()

    if args.knight:
        asyncio.run(hydrate_knight(args.knight))
    elif args.worldtree:
        asyncio.run(hydrate_worldtree())
    elif args.all_core:
        core = ["SIR_BORIS", "SIR_ALEX", "SIR_FORGE", "SIR_CODEX", "SIR_SENTINEL", "MERLIN_OMEGA", "ANYA_OMEGA"]
        for k in core:
            asyncio.run(hydrate_knight(k))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
