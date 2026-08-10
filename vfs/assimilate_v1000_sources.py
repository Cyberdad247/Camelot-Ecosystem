# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Master v.1000 Assimilation & Token Compression Engine
"""
Audits all sources in the Camelot-OS v.1000 NotebookLM node, passes them
through the //ASSIMILATION protocol + Anya Quantum Mantra Glyph Engine,
synthesizes a single Master Sovereign Glyph Codex, pushes it to v.1000,
and purges the raw unstructured sources to achieve maximum token reduction.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("V1000_Assimilator")
CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CAMELOT_ROOT / "01_KERNEL"))
sys.path.insert(0, str(CAMELOT_ROOT / "vfs"))

try:
    from notebooklm import NotebookLMClient
    from notebooklm.exceptions import AuthError
    _NLM = True
except ImportError:
    _NLM = False
    LOG.error("notebooklm-py missing")

try:
    from anya_glyph_engine import VFSGlyphEngine
except ImportError:
    VFSGlyphEngine = None

V1000_NOTEBOOK_ID = "8c656cfa-a189-409e-a72d-07692a47f17e"  # Camelot-OS v.1000


class V1000MasterAssimilator:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client: Optional[Any] = None
        self._cm: Optional[Any] = None

    async def _connect(self) -> bool:
        if not _NLM:
            return False
        auth_path = r"C:\Users\vizio\.notebooklm\storage_state.json"
        try:
            self._cm = await NotebookLMClient.from_storage(path=auth_path if os.path.exists(auth_path) else None)
            self.client = await self._cm.__aenter__()
            return True
        except Exception as e:
            LOG.error(f"Client init failed: {e}")
            return False

    async def execute(self) -> Dict[str, Any]:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
        mode = "DRY RUN" if self.dry_run else "LIVE EXECUTE"
        LOG.info(f"\n{'='*60}\n  CAMELOT-OS v.1000 MASTER ASSIMILATION [{mode}]\n{'='*60}")

        if not await self._connect():
            return {"error": "Auth failed"}

        # 1. Resolve notebook dynamically from live account
        LOG.info("[ASSIMILATE] Listing live notebooks to resolve Camelot-OS v.1000...")
        live_nbs = await self.client.notebooks.list()
        target_nb = None
        for nb in live_nbs:
            if "camelot-os v.1000" in nb.title.lower() or nb.id == V1000_NOTEBOOK_ID:
                target_nb = nb
                break

        if not target_nb:
            LOG.error("[ASSIMILATE] Could not locate Camelot-OS v.1000 notebook in live account.")
            return {"error": "notebook_not_found"}

        target_id = target_nb.id
        LOG.info(f"[ASSIMILATE] Target notebook matched: '{target_nb.title}' (ID: {target_id})")

        # Fetch Notes (822 notes migrated from previous condensation)
        LOG.info(f"[ASSIMILATE] Fetching notes from '{target_nb.title}'...")
        try:
            items = await self.client.notes.list(target_id)
            is_note_type = True
        except Exception:
            items = await self.client.sources.list(target_id)
            is_note_type = False

        LOG.info(f"[ASSIMILATE] Found {len(items)} items in target notebook for assimilation")

        if not items:
            LOG.info("[ASSIMILATE] No items found to assimilate.")
            return {"status": "empty"}

        # 2. Extract content and compile Anya Glyphs
        assimilated_concepts = []
        item_ids_to_purge = []
        total_tokens_reduced = 0

        for idx, item in enumerate(items, 1):
            item_title = getattr(item, "title", f"Item_{idx}")
            item_ids_to_purge.append(item.id)

            raw_text = getattr(item, "content", None) or getattr(item, "text", None) or item_title
            tokens = len(raw_text) // 4
            total_tokens_reduced += tokens

            if idx % 50 == 0 or idx == len(items):
                LOG.info(f"  [{idx}/{len(items)}] Distilled: '{item_title[:45]}' (~{tokens} tokens)")

            # Compress via Anya Glyph Engine
            if VFSGlyphEngine:
                glyph = VFSGlyphEngine.construct_vfs_glyph(
                    intent_focus=f"Assimilated: {item_title}",
                    path=f"vfs://v1000/{item_title[:30]}"
                )
                if glyph and glyph.compiled_glyph:
                    node = glyph.compiled_glyph
                    assimilated_concepts.append({
                        "title": item_title,
                        "q_focus": node.q_focus,
                        "task_type": node.task_type,
                        "determinism": node.determinism,
                        "raw_token_weight": tokens
                    })

        # 3. Synthesize Master Sovereign Glyph Codex
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        master_codex = {
            "title": "CAMELOT-OS v.1000 SOVEREIGN MASTER GLYPH CODEX",
            "version": "v1000.54 COSMOS",
            "assimilated_timestamp": timestamp,
            "total_items_assimilated": len(items),
            "total_tokens_compressed": total_tokens_reduced,
            "compression_ratio": f"{len(items)}:1",
            "quantum_mantra_engine": "ANYA_v6_seed",
            "harmony_gate_status": "PURE_CONVERGENCE",
            "concepts_digest": assimilated_concepts
        }

        codex_json = json.dumps(master_codex, indent=2)

        # 4. Push Master Codex to target notebook as Note
        LOG.info(f"\n[PUSH] Seeding Master Sovereign Glyph Codex ({total_tokens_reduced} tokens compressed)...")
        codex_title = f"[MASTER CODEX] Camelot-OS v.1000 Sovereign Digest ({timestamp})"
        if not self.dry_run:
            try:
                await self.client.notes.create(target_id, title=codex_title, content=codex_json)
                LOG.info("✅ Master Sovereign Glyph Codex successfully pinned as Note!")
            except Exception as e:
                LOG.error(f"Failed to push Master Codex: {e}")

        # 5. Purge unneeded items (leave only Master Codex)
        purged_count = 0
        LOG.info(f"\n[PURGE] Purging {len(item_ids_to_purge)} items from target notebook...")
        for sid in item_ids_to_purge:
            if not self.dry_run:
                try:
                    if is_note_type:
                        await self.client.notes.delete(target_id, sid)
                    else:
                        await self.client.sources.delete(target_id, sid)
                    purged_count += 1
                except Exception as e:
                    LOG.error(f"  Failed to delete item {sid}: {e}")

        # Cleanup
        if self._cm:
            try:
                await self._cm.__aexit__(None, None, None)
            except Exception:
                pass

        LOG.info(f"\n{'='*60}")
        LOG.info(f"  v.1000 MASTER ASSIMILATION & PURGE COMPLETE")
        LOG.info(f"  Items Assimilated       : {len(items)}")
        LOG.info(f"  Tokens Compressed       : {total_tokens_reduced}")
        LOG.info(f"  Purged Items            : {purged_count if not self.dry_run else 0} (Dry: {len(items)})")
        LOG.info(f"{'='*60}\n")

        return {
            "status": "success",
            "sources_assimilated": len(sources),
            "tokens_compressed": total_tokens_reduced,
            "purged": purged_count if not self.dry_run else 0,
            "mode": mode
        }


def run_master_assimilation(dry_run: bool = False):
    assimilator = V1000MasterAssimilator(dry_run=dry_run)
    return asyncio.run(assimilator.execute())


if __name__ == "__main__":
    execute = "--execute" in sys.argv
    run_master_assimilation(dry_run=not execute)
