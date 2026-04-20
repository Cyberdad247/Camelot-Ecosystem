# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
EXP_LEDGER STORAGE
Camelot OS v33.0 - Pure Experience Tracking
==============================================================================
NO Ejection. NO Incentives. ONLY Learning.
==============================================================================
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BASE_EXP_VALUE = 10  # ALWAYS 10. NO multipliers. NO bonuses.
ARCHIVE_AFTER_DAYS = 365
STORAGE_ROOT = Path("Titan_Ω_Hypergraph")
ARCHIVE_ROOT = STORAGE_ROOT / "Archive" / "EXP"


# ==============================================================================
# DATA MODELS
# ==============================================================================


@dataclass
class EXPTrigger:
    """Information about what triggered the EXP entry."""

    prompt_hash: str
    complication_type: str
    cartridge: str
    rune_phase: str = ""
    context_snapshot: dict = field(default_factory=dict)


@dataclass
class EXPResolution:
    """Information about how the complication was resolved."""

    solution_steps: list[str]
    knight_responsible: str
    validation_signature: str
    fix_code_snippet: str = ""


@dataclass
class EXPOutcome:
    """Outcome of the resolution."""

    time_to_resolve_sec: float
    success: bool = True


@dataclass
class EXPEntry:
    """A single EXP ledger entry."""

    exp_id: str
    timestamp: str
    trigger: EXPTrigger
    resolution: EXPResolution
    outcome: EXPOutcome
    tags: list[str]
    exp_value: int = BASE_EXP_VALUE  # ALWAYS 10
    last_reused: Optional[str] = None
    archived: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "exp_id": self.exp_id,
            "timestamp": self.timestamp,
            "trigger": {
                "prompt_hash": self.trigger.prompt_hash,
                "complication_type": self.trigger.complication_type,
                "cartridge": self.trigger.cartridge,
                "rune_phase": self.trigger.rune_phase,
                "context_snapshot": self.trigger.context_snapshot,
            },
            "resolution": {
                "solution_steps": self.resolution.solution_steps,
                "fix_code_snippet": self.resolution.fix_code_snippet,
                "knight_responsible": self.resolution.knight_responsible,
                "validation_signature": self.resolution.validation_signature,
            },
            "outcome": {
                "time_to_resolve_sec": self.outcome.time_to_resolve_sec,
                "success": self.outcome.success,
            },
            "tags": self.tags,
            "exp_value": self.exp_value,
            "last_reused": self.last_reused,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "EXPEntry":
        """Create from database row."""
        return cls(
            exp_id=row["exp_id"],
            timestamp=row["timestamp"],
            trigger=EXPTrigger(
                prompt_hash=row["prompt_hash"],
                complication_type=row["complication_type"],
                cartridge=row["cartridge"],
                rune_phase=row["rune_phase"] or "",
                context_snapshot=json.loads(row["context_snapshot"] or "{}"),
            ),
            resolution=EXPResolution(
                solution_steps=json.loads(row["solution_steps"] or "[]"),
                fix_code_snippet=row["fix_code_snippet"] or "",
                knight_responsible=row["knight_responsible"],
                validation_signature=row["validation_signature"],
            ),
            outcome=EXPOutcome(
                time_to_resolve_sec=row["time_to_resolve_sec"] or 0,
                success=bool(row["success"]),
            ),
            tags=json.loads(row["tags"] or "[]"),
            exp_value=row["exp_value"],
            last_reused=row["last_reused"],
            archived=bool(row["archived"]),
        )


# ==============================================================================
# EXP LEDGER STORAGE CLASS
# ==============================================================================


class EXPLedger:
    """
    Persona-specific EXP Ledger storage.

    PRINCIPLES:
    - Each persona has their own isolated ledger
    - NO cross-persona access
    - NO ejection logic
    - NO incentive logic
    - EXP is ALWAYS 10 per resolved complication
    """

    def __init__(self, persona_id: str):
        self.persona_id = persona_id
        self.storage_path = STORAGE_ROOT / persona_id / "EXP_Ledger"
        self.db_path = self.storage_path / "ledger.db"
        self._ensure_storage()
        self._init_schema()

    def _ensure_storage(self) -> None:
        """Create storage directory if it doesn't exist."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        # Also ensure archive path exists
        archive_path = ARCHIVE_ROOT / self.persona_id
        archive_path.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with WAL mode."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_schema(self) -> None:
        """Initialize the database schema."""
        schema_path = Path(__file__).parent / "exp_ledger_schema.sql"

        if schema_path.exists():
            with open(schema_path, "r") as f:
                schema_sql = f.read()
        else:
            # Fallback inline schema
            schema_sql = """
            CREATE TABLE IF NOT EXISTS exp_ledger (
                exp_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                prompt_hash TEXT NOT NULL,
                complication_type TEXT NOT NULL,
                cartridge TEXT NOT NULL,
                rune_phase TEXT,
                context_snapshot TEXT,
                solution_steps TEXT NOT NULL,
                fix_code_snippet TEXT,
                knight_responsible TEXT NOT NULL,
                validation_signature TEXT NOT NULL,
                time_to_resolve_sec REAL,
                success INTEGER NOT NULL DEFAULT 1,
                tags TEXT,
                exp_value INTEGER NOT NULL DEFAULT 10,
                last_reused TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                archived INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_exp_prompt_hash ON exp_ledger(prompt_hash);
            CREATE INDEX IF NOT EXISTS idx_exp_complication_type ON exp_ledger(complication_type);
            """

        with self._get_connection() as conn:
            conn.executescript(schema_sql)

    # ==========================================================================
    # CRUD OPERATIONS
    # ==========================================================================

    def create_entry(
        self,
        trigger: EXPTrigger,
        resolution: EXPResolution,
        outcome: EXPOutcome,
        tags: list[str],
    ) -> str:
        """
        Create a new EXP entry.

        Returns the exp_id of the created entry.
        EXP value is ALWAYS 10. NO multipliers.
        """
        exp_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO exp_ledger (
                    exp_id, timestamp, prompt_hash, complication_type,
                    cartridge, rune_phase, context_snapshot,
                    solution_steps, fix_code_snippet, knight_responsible,
                    validation_signature, time_to_resolve_sec, success,
                    tags, exp_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    exp_id,
                    timestamp,
                    trigger.prompt_hash,
                    trigger.complication_type,
                    trigger.cartridge,
                    trigger.rune_phase,
                    json.dumps(trigger.context_snapshot),
                    json.dumps(resolution.solution_steps),
                    resolution.fix_code_snippet,
                    resolution.knight_responsible,
                    resolution.validation_signature,
                    outcome.time_to_resolve_sec,
                    1 if outcome.success else 0,
                    json.dumps(tags),
                    BASE_EXP_VALUE,  # ALWAYS 10
                ),
            )
            conn.commit()

        return exp_id

    def query_by_hash(self, prompt_hash: str) -> Optional[EXPEntry]:
        """Query for an exact prompt hash match."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM exp_ledger WHERE prompt_hash = ? AND archived = 0 LIMIT 1",
                (prompt_hash,),
            )
            row = cursor.fetchone()
            if row:
                return EXPEntry.from_row(row)
        return None

    def query_by_type_and_tags(
        self,
        complication_type: str,
        tags: list[str],
        min_matching_tags: int = 2,
    ) -> list[EXPEntry]:
        """
        Query for entries matching complication type and at least N tags.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM exp_ledger 
                WHERE complication_type = ? AND archived = 0
                ORDER BY timestamp DESC
                """,
                (complication_type,),
            )

            results = []
            for row in cursor.fetchall():
                entry_tags = json.loads(row["tags"] or "[]")
                matching = len(set(tags) & set(entry_tags))
                if matching >= min_matching_tags:
                    results.append(EXPEntry.from_row(row))

            return results

    def query_matching(
        self,
        prompt_hash: str,
        complication_type: str,
        tags: list[str],
    ) -> Optional[EXPEntry]:
        """
        Query for matching entry: exact hash OR (type + 2 tags).
        Used by Experience_Check phase.
        """
        # First try exact hash match
        entry = self.query_by_hash(prompt_hash)
        if entry:
            return entry

        # Then try type + tags match
        matches = self.query_by_type_and_tags(complication_type, tags, min_matching_tags=2)
        if matches:
            return matches[0]  # Return most recent

        return None

    def update_last_reused(self, exp_id: str) -> None:
        """Update the last_reused timestamp (for analytics only)."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE exp_ledger SET last_reused = ? WHERE exp_id = ?",
                (timestamp, exp_id),
            )
            conn.commit()

    def get_entry(self, exp_id: str) -> Optional[EXPEntry]:
        """Get a specific entry by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM exp_ledger WHERE exp_id = ?",
                (exp_id,),
            )
            row = cursor.fetchone()
            if row:
                return EXPEntry.from_row(row)
        return None

    def get_all_entries(self, include_archived: bool = False) -> list[EXPEntry]:
        """Get all entries for this persona."""
        with self._get_connection() as conn:
            if include_archived:
                cursor = conn.execute("SELECT * FROM exp_ledger ORDER BY timestamp DESC")
            else:
                cursor = conn.execute("SELECT * FROM exp_ledger WHERE archived = 0 ORDER BY timestamp DESC")
            return [EXPEntry.from_row(row) for row in cursor.fetchall()]

    def get_stats(self) -> dict:
        """Get statistics for this persona's ledger."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_entries,
                    SUM(exp_value) as total_exp,
                    SUM(CASE WHEN last_reused IS NOT NULL THEN 1 ELSE 0 END) as reused_count,
                    AVG(time_to_resolve_sec) as avg_resolution_time
                FROM exp_ledger WHERE archived = 0
                """
            )
            row = cursor.fetchone()
            return {
                "persona_id": self.persona_id,
                "total_entries": row["total_entries"] or 0,
                "total_exp": row["total_exp"] or 0,
                "reused_count": row["reused_count"] or 0,
                "avg_resolution_time_sec": round(row["avg_resolution_time"] or 0, 2),
            }

    # ==========================================================================
    # ARCHIVAL (NO DELETION)
    # ==========================================================================

    def archive_old_entries(self, days: int = ARCHIVE_AFTER_DAYS) -> int:
        """
        Archive entries older than specified days.
        ARCHIVAL ≠ DELETION. Entries remain searchable.

        Returns count of archived entries.
        """
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE exp_ledger 
                SET archived = 1 
                WHERE timestamp < ? AND archived = 0
                """,
                (cutoff,),
            )
            conn.commit()
            return cursor.rowcount


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================


def generate_prompt_hash(prompt: str) -> str:
    """Generate SHA-256 hash of user prompt."""
    return hashlib.sha256(prompt.encode()).hexdigest()


def check_novelty(ledger: EXPLedger, prompt_hash: str) -> bool:
    """Check if a prompt is novel (not in ledger)."""
    existing = ledger.query_by_hash(prompt_hash)
    return existing is None


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    # Quick test
    print("[TEST] Creating EXP Ledger for Sir_Syntax...")

    ledger = EXPLedger("Sir_Syntax")

    # Create test entry
    trigger = EXPTrigger(
        prompt_hash=generate_prompt_hash("test prompt"),
        complication_type="SyntaxError",
        cartridge="B_ENGINEERING",
        rune_phase="Atomize",
        context_snapshot={"lang": "python"},
    )

    resolution = EXPResolution(
        solution_steps=["Check imports", "Add missing module"],
        knight_responsible="Sir_Syntax",
        validation_signature="Sir_Zenith_TEST",
        fix_code_snippet="import pandas as pd",
    )

    outcome = EXPOutcome(time_to_resolve_sec=5.2, success=True)

    exp_id = ledger.create_entry(trigger, resolution, outcome, ["python", "import"])
    print(f"[OK] Created entry: {exp_id}")

    # Query it back
    entry = ledger.get_entry(exp_id)
    print(f"[OK] Retrieved: {entry.exp_value} EXP (should ALWAYS be 10)")

    # Get stats
    stats = ledger.get_stats()
    print(f"[OK] Stats: {stats}")

    print("[DONE] EXP Ledger test complete.")