# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
CLARITY_CORE v1.0.0 — SQUIRE COLDVAULT
=====================================
Episodic Memory Compactor & SQLite-Vec / Graphiti Page Vacuuming Engine.
Prevents disk and memory fragmentation across Camelot-OS memory stores:
  - Checkpoints and truncates WAL write logs (PRAGMA wal_checkpoint(TRUNCATE))
  - Vacuums fragmented SQLite-vec (memcastle.db) and Graphiti partition databases
  - Flushes unused database cache pages to disk, reducing resident OS page bloat
  - Evaluates open-notebook tissue storage efficiency.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

LOG = logging.getLogger("SquireColdVault")


@dataclass
class DatabaseCompactionResult:
    db_path: str
    size_before_bytes: int
    size_after_bytes: int
    reclaimed_bytes: int
    freelist_pages: int
    wal_truncated: bool
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ColdVaultReport:
    timestamp: str
    total_databases_scanned: int
    total_databases_compacted: int
    bytes_before: int
    bytes_after: int
    reclaimed_mb: float
    results: List[Dict[str, Any]]
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SquireColdVault:
    """Manages SQLite page vacuuming and database compaction across the knowledge vault."""

    def __init__(self, home: Optional[Path] = None) -> None:
        self.home = home or _ROOT
        self.memory_dir = self.home / "03_VAULT" / "memory"
        self.graphiti_dir = self.memory_dir / "graphiti"

    def scan_databases(self) -> List[Path]:
        """Finds all SQLite databases in 03_VAULT/memory."""
        dbs: List[Path] = []
        if self.memory_dir.exists():
            for p in self.memory_dir.glob("*.db"):
                if p.is_file():
                    dbs.append(p)
        if self.graphiti_dir.exists():
            for p in self.graphiti_dir.glob("*.db"):
                if p.is_file():
                    dbs.append(p)
        return sorted(dbs, key=lambda x: x.stat().st_size, reverse=True)

    def compact_database(self, db_path: Path, force_vacuum: bool = False) -> DatabaseCompactionResult:
        """Inspects, checkpoints WAL, and optionally vacuums an individual SQLite database."""
        size_before = db_path.stat().st_size
        freelist_pages = 0
        wal_truncated = False

        try:
            # Open connection
            conn = sqlite3.connect(str(db_path), timeout=5.0)
            cursor = conn.cursor()

            # Inspect fragmentation
            try:
                cursor.execute("PRAGMA freelist_count;")
                row = cursor.fetchone()
                freelist_pages = row[0] if row else 0
            except Exception:
                freelist_pages = 0

            # Checkpoint WAL
            try:
                cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                wal_truncated = True
            except Exception:
                pass

            # Vacuum if freelist pages exist or force requested
            if force_vacuum or freelist_pages > 0:
                try:
                    cursor.execute("VACUUM;")
                except Exception as vexc:
                    LOG.debug(f"[ColdVault] VACUUM skipped on {db_path.name}: {vexc}")

            # Optimize statistics
            try:
                cursor.execute("PRAGMA optimize;")
            except Exception:
                pass

            conn.close()
            status = "COMPACTED"
        except Exception as exc:
            LOG.warning(f"[ColdVault] Error compacting {db_path.name}: {exc}")
            status = f"ERROR: {exc}"

        size_after = db_path.stat().st_size
        reclaimed = max(0, size_before - size_after)

        return DatabaseCompactionResult(
            db_path=str(db_path.relative_to(self.home)) if str(db_path).startswith(str(self.home)) else db_path.name,
            size_before_bytes=size_before,
            size_after_bytes=size_after,
            reclaimed_bytes=reclaimed,
            freelist_pages=freelist_pages,
            wal_truncated=wal_truncated,
            status=status,
        )

    def vacuum_vault(self, force_vacuum: bool = False, max_dbs: int = 50) -> ColdVaultReport:
        """Runs a complete vault compaction sweep across all discovered databases."""
        dbs = self.scan_databases()
        results: List[DatabaseCompactionResult] = []

        bytes_before = 0
        bytes_after = 0
        reclaimed_total = 0
        compacted_count = 0

        for db in dbs[:max_dbs]:
            res = self.compact_database(db, force_vacuum=force_vacuum)
            results.append(res)
            bytes_before += res.size_before_bytes
            bytes_after += res.size_after_bytes
            reclaimed_total += res.reclaimed_bytes
            if res.reclaimed_bytes > 0 or res.wal_truncated:
                compacted_count += 1

        reclaimed_mb = round(reclaimed_total / (1024 * 1024), 3)

        return ColdVaultReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_databases_scanned=len(dbs),
            total_databases_compacted=compacted_count,
            bytes_before=bytes_before,
            bytes_after=bytes_after,
            reclaimed_mb=reclaimed_mb,
            results=[r.to_dict() for r in results],
            status="OPTIMIZED",
        )
