#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
r"""
[S6-08] worldtree_nav — World Tree Navigational CloudBrain & Open-Notebook VKG CLI
==================================================================================
Prime Directive: Operates the World Tree as the central Navigational CloudBrain
to all 294 Google NotebookLM nodes, dynamically linked to VPS-hosted Open-Notebook
for finalized VKG crystals.

Usage:
    python bin/worldtree_nav.py --status
    python bin/worldtree_nav.py --push-atlas
    python bin/worldtree_nav.py --list-crystals
    python bin/worldtree_nav.py --forge "Leech Lattice Swarm Quantization" --category CAMELOT_SYSTEMS_ARCHITECTURE
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
logger = logging.getLogger("WorldTree_Nav")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "vfs"))

from vfs.worldtree_vkg_sync import worldtree_vkg_sync, WORLDTREE_UUID, VPS_IP, VPS_TS_IP
from vfs.notebooklm_client import push_source_async, query_notebook_async


async def push_atlas_to_worldtree():
    logger.info("Generating Master WorldTree Navigational Atlas...")
    atlas_md = worldtree_vkg_sync.generate_navigational_atlas_markdown()
    title = f"WORLDTREE_MASTER_NAVIGATIONAL_ATLAS_{datetime_now_tag()}"

    logger.info(f"Generated Atlas ({len(atlas_md)} bytes). Pushing to WORLD_TREE ({WORLDTREE_UUID})...")
    ok = await push_source_async("WORLD_TREE", title, atlas_md)

    if ok:
        logger.info(f"[SUCCESS] Master Navigational Atlas successfully pushed into live WORLD_TREE CloudBrain!")
        print(f"\n🌐 Master Navigational Atlas is now active inside WORLD_TREE ({WORLDTREE_UUID}).")
        print("Gemini in the World Tree is now grounded with complete navigational routing across all 294 notebooks!")
    else:
        logger.error("[FAILED] Failed to push Navigational Atlas to WORLD_TREE.")


def datetime_now_tag() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def show_status():
    manifest = worldtree_vkg_sync.manifest
    total_nbs = len(manifest.get("notebooks", {}))
    categories = manifest.get("categories", [])
    crystals = worldtree_vkg_sync.list_vkg_crystals()

    print("\n" + "=" * 76)
    print("  🌳 WORLDTREE NAVIGATIONAL CLOUDBRAIN & VPS OPEN-NOTEBOOK MATRIX")
    print("=" * 76)
    print(f"• WorldTree Home UUID : {WORLDTREE_UUID}")
    print(f"• Total CloudBrains   : {total_nbs} NotebookLM Nodes")
    print(f"• Taxonomy Clusters   : {len(categories)} Categories")
    print(f"• VPS Control Plane   : KVM563 ({VPS_IP} / Tailscale: {VPS_TS_IP})")
    print(f"• Finalized Crystals  : {len(crystals)} Machine-Actionable VKG Crystals")
    print("\n📁 Managed Clusters:")
    for cat in categories:
        count = sum(1 for n in manifest.get("notebooks", {}).values() if n.get("category") == cat)
        print(f"   - {cat:<32} : {count} Nodes")
    print("=" * 76 + "\n")


def list_crystals():
    crystals = worldtree_vkg_sync.list_vkg_crystals()
    print(f"\n💎 Finalized Open-Notebook VKG Crystals ({len(crystals)} Found):")
    print("-" * 76)
    for c in crystals:
        print(f"• [{c['crystal_id']}] {c['title']}")
        print(f"   Category: {c['category']} | Anchor: {c['anchor_knight']} | Nodes: {c['node_count']} | Edges: {c['edge_count']}")
        print(f"   VFS: {c['vfs_coordinate']} | SHA256: {c['sha256']}")
        print("-" * 76)


def forge_crystal(title: str, category: str, knight: str):
    print(f"\n🔨 Forging VKG Crystal for: {title}...")
    sample_text = f"Concrete architectural knowledge and invariant specification for {title}. " \
                  f"Governed by {knight} within the {category} cluster. " \
                  f"Guaranteed by Anya Law and verifiable across the Bifrost Bridge."
    crystal = worldtree_vkg_sync.forge_vkg_crystal(
        title=title,
        knowledge_text=sample_text,
        category=category,
        anchor_knight=knight,
    )
    print(f"✅ Crystal Forged: {crystal.crystal_id}")
    print(f"• VFS Coordinate: {crystal.vfs_coordinate}")
    print(f"• Nodes: {len(crystal.nodes)} | Edges: {len(crystal.edges)}")


def main():
    parser = argparse.ArgumentParser(description="World Tree Navigational CloudBrain CLI")
    parser.add_argument("--status", action="store_true", help="Display World Tree and Open-Notebook status")
    parser.add_argument("--push-atlas", action="store_true", help="Push Navigational Atlas to live WORLD_TREE node")
    parser.add_argument("--list-crystals", action="store_true", help="List all finalized VKG crystals")
    parser.add_argument("--forge", type=str, help="Forge a finalized VKG crystal with given title")
    parser.add_argument("--category", type=str, default="CAMELOT_SYSTEMS_ARCHITECTURE", help="Category for forged crystal")
    parser.add_argument("--knight", type=str, default="WORLD_TREE", help="Anchor knight for forged crystal")
    args = parser.parse_args()

    if args.push_atlas:
        asyncio.run(push_atlas_to_worldtree())
    elif args.list_crystals:
        list_crystals()
    elif args.forge:
        forge_crystal(args.forge, args.category, args.knight)
    else:
        show_status()


if __name__ == "__main__":
    main()
