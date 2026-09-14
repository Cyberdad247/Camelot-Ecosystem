#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
r"""
[S6-07] cloudbrain_snapshot — Autonomous VFS Snapshot & Offline Air-Gap Backup
=============================================================================
Snapshots notes and source metadata from Google NotebookLM cloud nodes into
local VFS files (03_VAULT/runtime_state/open_notebook/) and indexes them into
MemCastle (sqlite-vec KNN vector database) for offline query capability.

Usage:
    python bin/cloudbrain_snapshot.py --knight SIR_BORIS
    python bin/cloudbrain_snapshot.py --all
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("CloudBrain_Snapshot")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "vfs"))

from vfs.notebooklm_client import _get_client
from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS
from control_plane.memcastle import MemCastle

VAULT_DIR = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook"


async def snapshot_knight(client, knight_id: str, mc: MemCastle) -> int:
    kid = knight_id.upper()
    nb_id = KNIGHT_NOTEBOOKS.get(kid)
    if not nb_id:
        return 0

    indexed_count = 0
    try:
        notes = await client.notes.list(nb_id)
        sources = await client.sources.list(nb_id)

        snapshot_data = {
            "knight_id": kid,
            "notebook_uuid": nb_id,
            "snapshot_time": datetime.now(timezone.utc).isoformat(),
            "sources": [{"id": s.id, "title": getattr(s, "title", "Source")} for s in sources],
            "notes": [{"id": n.id, "title": getattr(n, "title", "Note"), "content": getattr(n, "content", "")} for n in notes],
        }

        # Save to local VFS
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        vfs_path = VAULT_DIR / f"{kid.lower()}_snapshot.json"
        vfs_path.write_text(json.dumps(snapshot_data, indent=2), encoding="utf-8")

        # Index notes into MemCastle
        for n in notes:
            content = getattr(n, "content", "")
            title = getattr(n, "title", "")
            if content:
                text_to_index = f"[{kid}] {title}: {content}"
                mc.store(text=text_to_index, source=f"nlm_note:{n.id}", knight=kid)
                indexed_count += 1

        logger.info(f"Snapshotted {kid}: {len(sources)} sources, {len(notes)} notes (Indexed {indexed_count} in MemCastle)")
    except Exception as exc:
        logger.error(f"Snapshot failed for {kid}: {exc}")

    return indexed_count


async def run_snapshots(targets: list[str]):
    client = await _get_client()
    if not client:
        logger.error("Failed to acquire NotebookLMClient.")
        return

    mc = MemCastle()
    total_indexed = 0
    try:
        async with client:
            for kid in targets:
                count = await snapshot_knight(client, kid, mc)
                total_indexed += count
        logger.info(f"Total entries indexed into MemCastle: {total_indexed}")
    finally:
        mc.close()


def main():
    parser = argparse.ArgumentParser(description="Camelot CloudBrain Snapshot & Air-Gap Indexer")
    parser.add_argument("--knight", type=str, help="Knight ID to snapshot")
    parser.add_argument("--all", action="store_true", help="Snapshot all registered knights")
    args = parser.parse_args()

    if args.knight:
        asyncio.run(run_snapshots([args.knight.upper()]))
    elif args.all:
        asyncio.run(run_snapshots(list(KNIGHT_NOTEBOOKS.keys())))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
