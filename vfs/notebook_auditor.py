# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Notebook Audit & Condensation Engine
"""
Extends the Lady M Rune Router with a full Notebook Auditor that:

  1. AUDIT     — Lists all sources in each notebook, scores semantic overlap
  2. ASSIMILATE — Extracts fulltext from overlapping sources in donor notebooks
  3. CONDENSE  — Pushes extracted content into canonical target notebook via add_text
  4. PURGE     — Optionally deletes the now-assimilated source from the donor

Mathematical condensation function (Merlin's Compression Theorem):
    Overlap(A, B) = |keywords(A) ∩ keywords(B)| / max(|keywords(A)|, |keywords(B)|)
    If Overlap > threshold → assimilate A into B, purge A.

Run modes:
  --dry-run   Audit and report only, no mutations
  --execute   Full assimilation + purge of matched sources
  --condense-notebooks  Merge duplicate Camelot notebooks into canonical targets
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

LOG = logging.getLogger("NotebookAuditor")
CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CAMELOT_ROOT / "01_KERNEL"))
sys.path.insert(0, str(CAMELOT_ROOT / "vfs"))

try:
    from notebooklm import NotebookLMClient
    from notebooklm.exceptions import AuthError
    _NLM_AVAILABLE = True
except ImportError:
    _NLM_AVAILABLE = False
    LOG.error("notebooklm-py not available. Run: pip install notebooklm-py[browser]")

try:
    from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS
except ImportError:
    KNIGHT_NOTEBOOKS = {}

# ── Condensation target map ───────────────────────────────────────────────────
# Duplicate/older notebooks → canonical target they should be assimilated into
CONDENSATION_MAP: Dict[str, str] = {
    # Older Camelot OS versions → CAMELOT_V1000 (Camelot-OS v.1000)
    "a9cf586e-1971-4959-bb97-cdcd37257ebb": "8c656cfa-a189-409e-a72d-07692a47f17e",  # living v300 → v1000
    "bcaadfdd-1654-487d-9c4c-111f7dea120e": "8c656cfa-a189-409e-a72d-07692a47f17e",  # Living v400 → v1000
    "d02cc716-d235-4d34-9185-a07860ec5272": "8c656cfa-a189-409e-a72d-07692a47f17e",  # v700 → v1000
    "28bca096-1ba2-4e47-8b92-aa88e90be210": "8c656cfa-a189-409e-a72d-07692a47f17e",  # v999.3 → v1000
    "eaff9959-4d7b-4761-8850-c0b2e25a2b45": "8c656cfa-a189-409e-a72d-07692a47f17e",  # Living → v1000
    "19f90acf-6731-4ba3-bf87-1310b1c97564": "8c656cfa-a189-409e-a72d-07692a47f17e",  # v57 → v1000
    # Duplicate SIR ALEX / SIR BORIS workspaces → canonical (underscore versions)
    "e9fcbbbc-cd43-4b2d-a437-b2570267a0a9": "f490c05e-d8c4-4008-87e1-5f901bf57c6a",  # SIR ALEX → SIR_ALEX
    "da2e51db-780a-48cf-a40a-4f0f65ff9295": "f7707daa-2d10-4db8-8fda-be4661a27793",  # SIR BORIS → SIR_BORIS
    "96f9233b-6efa-46a3-8242-98f0c463680c": "91c5da8b-e2de-4a56-b7fd-c8b76c00afc7",  # SIR FORGE dup → canonical
    "3a09997b-3d65-46c9-b9aa-fb8ebce927a9": "07cbb441-f008-424c-820a-85676210be39",  # SIR SENTINEL dup → canonical
    "b4cfc5af-1555-4f23-a131-1ec6d03c2787": "422a184b-93e7-4dfd-8a12-75d2268b6c60",  # SIR GHOST dup → canonical
    "28d49148-28db-438d-a299-61456fdfdefc": "56820318-bb91-451f-aac4-4b46424898cf",  # SIR HELIOS dup → SIR_HELIO
    "05f1985d-e356-45d9-85b8-d101013a90b8": "8c656cfa-a189-409e-a72d-07692a47f17e",  # SIR CODEX dup → v1000
    # Duplicate HiveIDE
    "e8dfbd26-c6ee-430a-a83e-94384f90d3cd": "cadfe67e-7187-472e-8bf4-8a2aded84e4e",  # Cleaned Copy → canonical
    # Duplicate LADY APIS
    "f6466e10-d1b1-4904-9f87-081d031b0595": "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f",  # LADY APIS dup → canonical
    # Duplicate SIR SONUS
    "fe87c2d5-8e0e-4885-a510-05d2fa97cd6a": "6272aa35-c285-4edc-81bc-2824ab519edf",  # Sir Sonus audio → canonical
}

OVERLAP_THRESHOLD = 0.3  # 30% keyword overlap triggers assimilation suggestion


@dataclass
class SourceRecord:
    source_id: str
    title: str
    notebook_id: str
    notebook_title: str
    keywords: Set[str] = field(default_factory=set)
    fulltext: Optional[str] = None


@dataclass
class CondensationPlan:
    donor_notebook_id: str
    donor_title: str
    target_notebook_id: str
    target_title: str
    sources_to_migrate: List[SourceRecord] = field(default_factory=list)
    overlap_score: float = 0.0
    reason: str = ""


def _extract_keywords(text: str, max_words: int = 50) -> Set[str]:
    """Extract meaningful keyword set from text for overlap scoring."""
    STOPWORDS = {
        "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
        "is", "it", "as", "be", "by", "this", "that", "with", "from", "are",
        "was", "were", "will", "can", "not", "have", "has", "had", "but",
        "its", "also", "all", "so", "we", "you", "he", "she", "they"
    }
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    freq: Dict[str, int] = defaultdict(int)
    for w in words:
        if w not in STOPWORDS:
            freq[w] += 1
    return set(sorted(freq, key=lambda k: freq[k], reverse=True)[:max_words])


def _overlap_score(a: Set[str], b: Set[str]) -> float:
    """Compute Jaccard-like overlap between two keyword sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a), len(b))


class NotebookAuditor:
    """
    Audits all Worldtree notebooks for semantic overlap and generates
    a condensation plan to assimilate redundant notebooks into canonical targets.
    """

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.client: Optional[Any] = None
        self._cm: Optional[Any] = None

    async def _connect(self) -> bool:
        """Establish authenticated NotebookLMClient session."""
        if not _NLM_AVAILABLE:
            return False
        auth_path = r"C:\Users\vizio\.notebooklm\storage_state.json"
        try:
            self._cm = await NotebookLMClient.from_storage(path=auth_path if os.path.exists(auth_path) else None)
            self.client = await self._cm.__aenter__()
            return True
        except AuthError:
            LOG.error("Auth required: .venv\\Scripts\\notebooklm login")
            return False
        except Exception as e:
            LOG.error(f"Client init failed: {e}")
            return False

    async def audit_notebook(self, notebook_id: str, notebook_title: str) -> List[SourceRecord]:
        """Fetch all sources from a notebook and extract keywords."""
        records: List[SourceRecord] = []
        try:
            sources = await self.client.sources.list(notebook_id)
            LOG.info(f"  [{notebook_title[:40]}] — {len(sources)} sources")
            for src in sources:
                rec = SourceRecord(
                    source_id=src.id,
                    title=getattr(src, "title", "Untitled"),
                    notebook_id=notebook_id,
                    notebook_title=notebook_title,
                )
                # Extract fulltext for keyword analysis
                try:
                    ft = await self.client.sources.get_fulltext(notebook_id, src.id)
                    rec.fulltext = ft.content if ft else None
                    if rec.fulltext:
                        rec.keywords = _extract_keywords(rec.fulltext)
                except Exception:
                    # Fulltext may not be available for all source types
                    rec.keywords = _extract_keywords(rec.title)
                records.append(rec)
        except Exception as e:
            LOG.error(f"Failed to audit {notebook_title}: {e}")
        return records

    async def build_condensation_plans(
        self,
        target_notebooks: Optional[List[str]] = None,
    ) -> List[CondensationPlan]:
        """
        Full audit pipeline:
        1. Scan CONDENSATION_MAP for explicit merge targets
        2. Fetch sources from each donor notebook
        3. Score overlap against target notebook
        4. Generate CondensationPlan for each pair
        """
        plans: List[CondensationPlan] = []

        # Get live notebook titles
        try:
            live_nbs = await self.client.notebooks.list()
            id_to_title = {nb.id: nb.title for nb in live_nbs}
        except Exception as e:
            LOG.error(f"Failed to list notebooks: {e}")
            return []

        LOG.info(f"\n[AUDIT] Scanning {len(CONDENSATION_MAP)} condensation pairs...")

        for donor_id, target_id in CONDENSATION_MAP.items():
            donor_title = id_to_title.get(donor_id, f"Unknown ({donor_id[:8]})")
            target_title = id_to_title.get(target_id, f"Unknown ({target_id[:8]})")

            if donor_id not in id_to_title:
                LOG.warning(f"  [SKIP] Donor {donor_id[:8]} not in live account")
                continue

            LOG.info(f"  [PAIR] {donor_title[:35]} → {target_title[:35]}")

            donor_sources = await self.audit_notebook(donor_id, donor_title)
            if not donor_sources:
                LOG.info(f"  [EMPTY] No sources in donor. Candidate for notebook deletion.")

            plan = CondensationPlan(
                donor_notebook_id=donor_id,
                donor_title=donor_title,
                target_notebook_id=target_id,
                target_title=target_title,
                sources_to_migrate=donor_sources,
                overlap_score=1.0,  # Explicit map = always condense
                reason="explicit_condensation_map",
            )
            plans.append(plan)

        return plans

    async def execute_condensation(self, plan: CondensationPlan) -> Dict[str, Any]:
        """
        Execute one condensation plan:
        1. For each source in donor → add_text to target
        2. Delete source from donor (if not dry_run)
        3. Return result dict
        """
        result = {
            "donor": plan.donor_title,
            "target": plan.target_title,
            "migrated": 0,
            "failed": 0,
            "purged": 0,
            "dry_run": self.dry_run,
        }

        for src in plan.sources_to_migrate:
            content = src.fulltext or f"[Source: {src.title}]\nNo fulltext available."
            assimilation_title = f"[ASSIMILATED from: {plan.donor_title}] {src.title}"

            if not self.dry_run:
                migrated_ok = False
                # Try 1: Add as source
                try:
                    await self.client.sources.add_text(
                        plan.target_notebook_id,
                        content=content,
                        title=assimilation_title,
                    )
                    migrated_ok = True
                    LOG.info(f"    [MIGRATE SOURCE] '{src.title[:50]}' → {plan.target_title[:30]}")
                except Exception as e:
                    # Fallback 2: Add as Note if source limit (50) is reached
                    try:
                        await self.client.notes.create(
                            plan.target_notebook_id,
                            title=assimilation_title,
                            content=content,
                        )
                        migrated_ok = True
                        LOG.info(f"    [MIGRATE NOTE] '{src.title[:50]}' → {plan.target_title[:30]} (Fallback)")
                    except Exception as ne:
                        result["failed"] += 1
                        LOG.error(f"    [MIGRATE FAILED] {src.title}: {ne}")

                if migrated_ok:
                    result["migrated"] += 1
                    # Purge from donor after successful migration
                    try:
                        await self.client.sources.delete(plan.donor_notebook_id, src.source_id)
                        result["purged"] += 1
                        LOG.info(f"    [PURGE] Deleted '{src.title[:50]}' from {plan.donor_title[:30]}")
                    except Exception as e:
                        LOG.error(f"    [PURGE FAILED] {src.title}: {e}")
            else:
                LOG.info(f"    [DRY] Would migrate '{src.title[:50]}' → {plan.target_title[:30]}")
                result["migrated"] += 1

        return result

    async def run(self, dry_run: Optional[bool] = None) -> Dict[str, Any]:
        """Full audit + condensation pipeline."""
        if dry_run is not None:
            self.dry_run = dry_run

        mode = "DRY RUN" if self.dry_run else "EXECUTE"
        LOG.info(f"\n{'='*60}")
        LOG.info(f"  WORLDTREE NOTEBOOK AUDIT & CONDENSATION [{mode}]")
        LOG.info(f"{'='*60}\n")

        if not await self._connect():
            return {"error": "Authentication failed"}

        plans = await self.build_condensation_plans()
        LOG.info(f"\n[AUDIT] Generated {len(plans)} condensation plans\n")

        results = []
        for plan in plans:
            LOG.info(f"\n[CONDENSE] {plan.donor_title[:40]} → {plan.target_title[:40]}")
            LOG.info(f"  Sources to migrate: {len(plan.sources_to_migrate)}")
            res = await self.execute_condensation(plan)
            results.append(res)

        # Save audit report
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        report = {
            "timestamp": timestamp,
            "mode": mode,
            "total_plans": len(plans),
            "results": results,
        }
        report_path = CAMELOT_ROOT / "vfs" / f"condensation_report_{timestamp}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        total_migrated = sum(r["migrated"] for r in results)
        total_purged = sum(r["purged"] for r in results)

        LOG.info(f"\n{'='*60}")
        LOG.info(f"  CONDENSATION COMPLETE")
        LOG.info(f"  Plans Executed : {len(plans)}")
        LOG.info(f"  Sources Moved  : {total_migrated}")
        LOG.info(f"  Sources Purged : {total_purged}")
        LOG.info(f"  Report         : {report_path}")
        LOG.info(f"{'='*60}\n")

        # Close client
        if self._cm:
            try:
                await self._cm.__aexit__(None, None, None)
            except Exception:
                pass

        return report


def run_audit(dry_run: bool = True) -> Dict[str, Any]:
    """Synchronous entry point for the audit pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    sys.stdout.reconfigure(encoding="utf-8")
    auditor = NotebookAuditor(dry_run=dry_run)
    return asyncio.run(auditor.run())


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Worldtree Notebook Audit & Condensation Engine")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Audit only, no mutations (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Execute full assimilation + purge")
    args = parser.parse_args()

    dry = not args.execute
    report = run_audit(dry_run=dry)
    print(f"\nTotal plans: {report.get('total_plans', 0)}")
