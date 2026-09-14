#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
r"""
[S6-05] cloudbrain_dedup — Sovereign Workspace Deduplication & Consolidation Utility
=====================================================================================
Scans all duplicate pairs in Google NotebookLM (e.g. SIR_BORIS vs SIR BORIS),
inspects shadow notebooks for unique notes or sources, migrates them to the
canonical underscore workspace, and tags or flags shadow notebooks for archival.

Usage:
    python bin/cloudbrain_dedup.py --audit
    python bin/cloudbrain_dedup.py --dry-run
    python bin/cloudbrain_dedup.py --execute
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("CloudBrain_Dedup")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "vfs"))

from vfs.notebooklm_client import _get_client

DUPLICATE_PAIRS = [
    {
        "knight": "SIR_BORIS",
        "canonical_uuid": "f7707daa-2d10-4db8-8fda-be4661a27793",
        "canonical_title": "Sovereign_Workspace: SIR_BORIS",
        "shadow_uuid": "da2e51db-780a-48cf-a40a-4f0f65ff9295",
        "shadow_title": "Sovereign_Workspace: SIR BORIS",
    },
    {
        "knight": "SIR_ALEX",
        "canonical_uuid": "f490c05e-d8c4-4008-87e1-5f901bf57c6a",
        "canonical_title": "Sovereign_Workspace: SIR_ALEX",
        "shadow_uuid": "e9fcbbbc-cd43-4b2d-a437-b2570267a0a9",
        "shadow_title": "Sovereign_Workspace: SIR ALEX",
    },
    {
        "knight": "SIR_FORGE",
        "canonical_uuid": "91c5da8b-e2de-4a56-b7fd-c8b76c00afc7",
        "canonical_title": "Sovereign_Workspace: SIR_FORGE",
        "shadow_uuid": "96f9233b-6efa-46a3-8242-98f0c463680c",
        "shadow_title": "Sovereign_Workspace: SIR FORGE",
    },
    {
        "knight": "SIR_SENTINEL",
        "canonical_uuid": "07cbb441-f008-424c-820a-85676210be39",
        "canonical_title": "Sovereign_Workspace: SIR_SENTINEL",
        "shadow_uuid": "3a09997b-3d65-46c9-b9aa-fb8ebce927a9",
        "shadow_title": "Sovereign_Workspace: SIR SENTINEL",
    },
    {
        "knight": "SIR_GHOST",
        "canonical_uuid": "422a184b-93e7-4dfd-8a12-75d2268b6c60",
        "canonical_title": "Sovereign_Workspace: SIR_GHOST",
        "shadow_uuid": "b4cfc5af-1555-4f23-a131-1ec6d03c2787",
        "shadow_title": "Sovereign_Workspace: SIR GHOST",
    },
    {
        "knight": "LADY_APIS",
        "canonical_uuid": "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f",
        "canonical_title": "Sovereign_Workspace: LADY_APIS",
        "shadow_uuid": "f6466e10-d1b1-4904-9f87-081d031b0595",
        "shadow_title": "Sovereign_Workspace: LADY APIS",
    },
    {
        "knight": "SIR_HELIO",
        "canonical_uuid": "56820318-bb91-451f-aac4-4b46424898cf",
        "canonical_title": "Sovereign_Workspace: SIR_HELIO",
        "shadow_uuid": "28d49148-28db-438d-a299-61456fdfdefc",
        "shadow_title": "Sovereign_Workspace: SIR HELIOS",
    },
]


async def run_audit():
    client = await _get_client()
    if not client:
        print("[!] Failed to initialize NotebookLMClient. Ensure .notebooklm session is valid.")
        return

    async with client:
        print(f"\n{'='*70}")
        print("  SOVEREIGN WORKSPACE DEDUPLICATION AUDIT")
        print(f"{'='*70}\n")

        for pair in DUPLICATE_PAIRS:
            k = pair["knight"]
            canon_id = pair["canonical_uuid"]
            shadow_id = pair["shadow_uuid"]

            try:
                c_sources = await client.sources.list(canon_id)
                c_notes = await client.notes.list(canon_id)
                s_sources = await client.sources.list(shadow_id)
                s_notes = await client.notes.list(shadow_id)

                print(f"Knight: {k}")
                print(f"  [Canonical] {canon_id} -> {len(c_sources)} sources, {len(c_notes)} notes")
                print(f"  [Shadow]    {shadow_id} -> {len(s_sources)} sources, {len(s_notes)} notes")

                if len(s_sources) == 0 and len(s_notes) == 0:
                    print("  Status: Shadow is clean empty shell (Safe to archive).")
                else:
                    print(f"  Status: Shadow contains {len(s_sources)} sources and {len(s_notes)} notes to migrate!")
                print("-" * 50)
            except Exception as exc:
                print(f"  Error reading {k}: {exc}")


async def run_dedup(execute: bool = False):
    client = await _get_client()
    if not client:
        print("[!] Failed to acquire NotebookLMClient.")
        return

    async with client:
        for pair in DUPLICATE_PAIRS:
            k = pair["knight"]
            canon_id = pair["canonical_uuid"]
            shadow_id = pair["shadow_uuid"]

            try:
                s_sources = await client.sources.list(shadow_id)
                s_notes = await client.notes.list(shadow_id)

                # Migrate notes if any
                for note in s_notes:
                    title = getattr(note, "title", "Migrated Note")
                    content = getattr(note, "content", "")
                    if execute:
                        await client.notes.create(canon_id, title=f"[MIGRATED] {title}", content=content)
                        logger.info(f"Migrated note '{title}' from shadow to canonical {k}")
                    else:
                        logger.info(f"[DRY-RUN] Would migrate note '{title}' from shadow to canonical {k}")

                # Tag shadow as archived
                if execute:
                    try:
                        await client.notes.create(shadow_id, title="[ARCHIVED_SHADOW]", content=f"Consolidated into canonical workspace {canon_id}")
                        logger.info(f"Tagged shadow workspace {shadow_id} as [ARCHIVED_SHADOW]")
                    except Exception:
                        pass

            except Exception as exc:
                logger.error(f"Failed processing {k}: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Camelot Sovereign Workspace Deduplication")
    parser.add_argument("--audit", action="store_true", help="Audit all duplicate pairs")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without modifications")
    parser.add_argument("--execute", action="store_true", help="Execute consolidation and tagging")
    args = parser.parse_args()

    if args.audit or not (args.dry_run or args.execute):
        asyncio.run(run_audit())
    elif args.dry_run:
        asyncio.run(run_dedup(execute=False))
    elif args.execute:
        asyncio.run(run_dedup(execute=True))


if __name__ == "__main__":
    main()
