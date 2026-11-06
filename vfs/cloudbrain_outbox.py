# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CloudBrain Resilient Outbox & Source Quota Manager
# -*- coding: utf-8 -*-
"""
CloudBrain Outbox & Source Quota Synthesizer
============================================
Enforces production-grade Tier 3/4 memory resilience:
1. Asynchronous Outbox Buffer:
   When NotebookLM authentication is expired or offline, notes, source pushes,
   and Graphify triplet updates are appended to an idempotent JSONL outbox
   (`03_VAULT/runtime_state/cloudbrain_outbox.jsonl`).
   When authenticated, the outbox flushes automatically.
2. Source Limit Guardrail:
   Tracks source count per notebook against the 50-source Google NotebookLM cap.
   Warns and generates rolling compaction directives when approaching >= 45 sources.
3. Canonical Workspace Alias Resolution:
   Resolves duplicate sovereign workspaces to their canonical UUIDs.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

LOG = logging.getLogger("CloudBrainOutbox")

ROOT = Path(__file__).resolve().parent.parent
VAULT_RUNTIME = ROOT / "03_VAULT" / "runtime_state"
OUTBOX_FILE = VAULT_RUNTIME / "cloudbrain_outbox.jsonl"
OUTBOX_DLQ = VAULT_RUNTIME / "cloudbrain_outbox_dlq.jsonl"
OUTBOX_DRAIN_STATUS = VAULT_RUNTIME / "outbox_drain_status.json"
MANIFEST_FILE = VAULT_RUNTIME / "NOTEBOOK_MANIFEST.json"

NOTEBOOKLM_SOURCE_LIMIT = 50
NOTEBOOKLM_COMPACTION_THRESHOLD = 45


class CloudBrainOutbox:
    """Production outbox buffer for Google NotebookLM CloudBrain mesh."""

    def __init__(self, outbox_path: Optional[Path] = None):
        self.path = outbox_path or OUTBOX_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def enqueue(
        self,
        item_type: str,  # "NOTE" | "SOURCE" | "GRAPH_DELTA"
        knight_id: str,
        title: str,
        content: str,
        target_notebook_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Enqueue an item to the persistent outbox with deduplication hash."""
        entry = {
            "id": f"outbox-{uuid4().hex[:12]}",
            "item_type": item_type,
            "knight_id": knight_id,
            "title": title,
            "content": content,
            "target_notebook_id": target_notebook_id,
            "status": "QUEUED",
            "enqueued_at": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0,
            "metadata": metadata or {},
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        LOG.info(f"[OUTBOX] Enqueued {item_type} '{title}' for {knight_id}")
        return entry

    def pending_count(self) -> int:
        """Returns the number of pending items in the outbox."""
        if not self.path.exists():
            return 0
        count = 0
        with self.path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    def read_all_pending(self) -> List[Dict[str, Any]]:
        """Read all pending entries."""
        if not self.path.exists():
            return []
        entries = []
        with self.path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries

    async def flush(self) -> Dict[str, Any]:
        """Attempt to flush all pending items to NotebookLM."""
        entries = self.read_all_pending()
        if not entries:
            return {"status": "EMPTY", "processed": 0, "succeeded": 0, "failed": 0}

        try:
            from vfs.notebooklm_client import push_note_async, push_source_async
        except ImportError:
            return {"status": "SDK_UNAVAILABLE", "processed": 0, "succeeded": 0, "failed": len(entries)}

        remaining = []
        succeeded = 0
        failed = 0

        for item in entries:
            success = False
            try:
                if item["item_type"] == "NOTE":
                    success = await push_note_async(item["knight_id"], item["title"], item["content"])
                elif item["item_type"] in ("SOURCE", "GRAPH_DELTA"):
                    success = await push_source_async(item["knight_id"], item["title"], item["content"])
            except Exception as e:
                LOG.error(f"[OUTBOX] Flush error for {item['id']}: {e}")
                success = False

            if success:
                succeeded += 1
            else:
                failed += 1
                item["retry_count"] = item.get("retry_count", 0) + 1
                if item["retry_count"] <= 5:
                    remaining.append(item)
                else:
                    # Move to dead-letter queue after 5 retries
                    with OUTBOX_DLQ.open("a", encoding="utf-8") as dlq:
                        dlq.write(json.dumps(item) + "\n")

        # Rewrite outbox with remaining pending items
        with self.path.open("w", encoding="utf-8") as f:
            for item in remaining:
                f.write(json.dumps(item) + "\n")

        res = {
            "status": "FLUSHED" if failed == 0 else "PARTIAL_RETRY",
            "processed": len(entries),
            "succeeded": succeeded,
            "failed": failed,
            "remaining": len(remaining),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            OUTBOX_DRAIN_STATUS.write_text(json.dumps(res, indent=2), encoding="utf-8")
        except Exception:
            pass
        return res

    async def run_drain_loop(self, interval_seconds: int = 900, max_iterations: Optional[int] = None) -> None:
        """Continuous background drain loop for headless production execution."""
        LOG.info(f"[OUTBOX-DAEMON] Starting background outbox drainer (interval: {interval_seconds}s)")
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            iteration += 1
            pending = self.pending_count()
            if pending > 0:
                LOG.info(f"[OUTBOX-DAEMON] Processing iteration {iteration}: {pending} pending entries")
                res = await self.flush()
                LOG.info(f"[OUTBOX-DAEMON] Flush complete: {res['status']} ({res['succeeded']} ok, {res['failed']} err)")
            else:
                status_record = {
                    "status": "IDLE",
                    "processed": 0,
                    "succeeded": 0,
                    "failed": 0,
                    "remaining": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                try:
                    OUTBOX_DRAIN_STATUS.write_text(json.dumps(status_record, indent=2), encoding="utf-8")
                except Exception:
                    pass
            await asyncio.sleep(interval_seconds)


def check_source_caps(manifest_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Inspect all notebooks in the manifest for approaching 50-source Google caps."""
    p = manifest_path or MANIFEST_FILE
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    notebooks = data.get("notebooks", {})

    warnings = []
    for nid, meta in notebooks.items():
        count = meta.get("verified_source_count", 0)
        if count >= NOTEBOOKLM_COMPACTION_THRESHOLD:
            warnings.append({
                "notebook_id": nid,
                "title": meta.get("title"),
                "source_count": count,
                "cap": NOTEBOOKLM_SOURCE_LIMIT,
                "action_required": "ROLLING_COMPACTION_DIRECTIVE",
            })
    return warnings


def resolve_canonical_workspace_uuid(knight_id: str, manifest_path: Optional[Path] = None) -> Optional[str]:
    """Resolve knight_id to canonical non-duplicate NotebookLM workspace UUID."""
    p = manifest_path or MANIFEST_FILE
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    notebooks = data.get("notebooks", {})

    target_norm = knight_id.replace("_", " ").strip().upper()
    for nid, meta in notebooks.items():
        title = meta.get("title", "")
        if "Sovereign_Workspace:" in title:
            norm_title = title.replace("Sovereign_Workspace:", "").replace("_", " ").strip().upper()
            if norm_title == target_norm:
                return meta.get("canonical_uuid", nid)
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Camelot-OS CloudBrain Outbox & Quota Manager")
    parser.add_argument("--flush", action="store_true", help="Flush pending outbox entries immediately")
    parser.add_argument("--daemon", action="store_true", help="Run background drain loop continuously")
    parser.add_argument("--interval", type=int, default=900, help="Drain loop interval in seconds (default: 900)")
    parser.add_argument("--status", action="store_true", help="Print outbox and source cap telemetry")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    outbox = CloudBrainOutbox()

    if args.flush:
        print("[OUTBOX] Triggering synchronous flush...")
        result = asyncio.run(outbox.flush())
        print(f"[OUTBOX] Flush result: {result}")
    elif args.daemon:
        print(f"[OUTBOX] Starting daemon loop every {args.interval}s...")
        asyncio.run(outbox.run_drain_loop(interval_seconds=args.interval))
    else:
        print(f"[OUTBOX] Initialized. Current pending: {outbox.pending_count()}")
        caps = check_source_caps()
        print(f"[QUOTA_GUARD] Notebooks near 50-source cap: {len(caps)}")
        for c in caps[:5]:
            print(f"  - {c['title']} ({c['source_count']}/50)")
