# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Titan Ledger - Neural Archive Storage System
Assimilated from CC_v32_Kingdom

SQLite-based persistent storage with:
- Artifact versioning
- Deployment tracking
- Snapshot management
- Neural Archive search (recall_wisdom)
"""

import hashlib
import json
import os
import sqlite3
import time
from typing import Any, Dict, List


class SystemGlyph:
    """System state snapshot generator."""

    @staticmethod
    def generate(kernel, knights: dict) -> str:
        """
        Generate cryptographic snapshot of system state.

        Args:
            kernel: Merlin kernel instance
            knights: Dictionary of Knight agents

        Returns:
            JSON string representation of system glyph
        """
        swarm_map = {}
        for name, k in knights.items():
            swarm_map[name.upper()] = {"ROLE": k.role, "TOOLS": list(k.tools.keys()) if hasattr(k, "tools") else []}

        glyph = {
            "ID": "CHIMERA_OS_v32",
            "KERNEL": kernel.name if hasattr(kernel, "name") else "Merlin_v32",
            "PROTO": "NEURAL_VAULT",
            "TS": int(time.time()),
            "COMP": {"MEM": "Titan_Ledger_SQL", "SEC": "Chivalry_Gate"},
            "AGENTS": swarm_map,
            "STATE": {"VER": "32.8.1", "HASH": "NEURAL_ARCHIVE_ACTIVE"},
        }
        return json.dumps(glyph, separators=(",", ":"))


class Ledger:
    """
    Titan Ledger - Persistent storage system.

    Features:
    - WAL mode for performance
    - Artifact versioning with physical file write
    - Deployment audit trail
    - Neural Archive for wisdom recall
    """

    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "titan_ledger.db")

    @staticmethod
    def _get_connection():
        """Get SQLite connection with WAL mode."""
        conn = sqlite3.connect(Ledger.DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")  # Performance optimization
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def initialize():
        """Initialize database schema."""
        conn = Ledger._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                timestamp REAL,
                glyph_hash TEXT,
                payload TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                filename TEXT,
                version TEXT,
                author TEXT,
                content TEXT,
                timestamp REAL
            )
        """
        )

        # FTS5 Virtual Table for high-performance search
        try:
            cursor.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS artifacts_fts USING fts5(filename, content, author, content='artifacts', content_rowid='id')"
            )
            # Trigger to keep FTS index in sync
            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS artifacts_ai AFTER INSERT ON artifacts BEGIN
                    INSERT INTO artifacts_fts(rowid, filename, content, author) VALUES (new.id, new.filename, new.content, new.author);
                END;
            """
            )
        except sqlite3.OperationalError:
            print("⚠️ [LEDGER] FTS5 not supported. Falling back to LIKE search.")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS builds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT,
                status TEXT,
                auditor TEXT,
                timestamp REAL
            )
        """
        )

        conn.commit()
        conn.close()

    @staticmethod
    def record_snapshot(glyph_str: str):
        """Record system snapshot to ledger."""
        glyph_hash = hashlib.sha256(glyph_str.encode()).hexdigest()
        conn = Ledger._get_connection()
        conn.execute(
            "INSERT INTO snapshots (type, timestamp, glyph_hash, payload) VALUES (?, ?, ?, ?)",
            ("CHIMERA_v32", time.time(), glyph_hash, glyph_str),
        )
        conn.commit()
        conn.close()
        print(f"📜 [LEDGER] SNAPSHOT SECURED: {glyph_hash[:8]}")

    @staticmethod
    def record_artifact(filename: str, content: str, author: str, version: str):
        """
        Record artifact to ledger and write to disk.

        Args:
            filename: Artifact filename (sanitized to prevent traversal)
            content: File content
            author: Creator (e.g., "SirSyntax")
            version: Version string
        """
        # SEC-005: Sanitize filename to prevent directory traversal
        safe_filename = os.path.basename(filename)
        artifact_id = hashlib.sha256(f"{safe_filename}{time.time()}".encode()).hexdigest()[:8]
        ts = time.time()

        conn = Ledger._get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO artifacts (id, filename, version, author, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (artifact_id, safe_filename, version, author, content, ts),
        )
        conn.commit()
        conn.close()

        # Physical write to artifacts directory
        art_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts")
        os.makedirs(art_dir, exist_ok=True)

        try:
            with open(os.path.join(art_dir, safe_filename), "w", encoding="utf-8") as f:
                f.write(content)
            print(f"📜 [LEDGER] Artifact Forged: {safe_filename}")
        except Exception as e:
            print(f"⚠️ [LEDGER] File write error: {e}")

    @staticmethod
    def recall_wisdom(query: str) -> List[Dict[str, Any]]:
        """
        Neural Archive: Search historical artifacts using high-performance FTS5.

        Args:
            query: Search query

        Returns:
            List of matching artifacts (max 3)
        """
        conn = Ledger._get_connection()

        try:
            # PERF-002: Use FTS5 MATCH for high-performance semantic-like search
            results = conn.execute(
                "SELECT filename, content, author FROM artifacts_fts WHERE artifacts_fts MATCH ? ORDER BY rank LIMIT 3",
                (query,),
            ).fetchall()
            conn.close()
            return [dict(r) for r in results]
        except Exception:
            # Fallback to legacy search if FTS5 fails or is unavailable
            words = query.lower().split()
            if not words:
                conn.close()
                return []

            search_clause = " OR ".join(["content LIKE ?" for _ in words])
            params = [f"%{w}%" for w in words]

            try:
                results = conn.execute(
                    f"SELECT filename, content, author FROM artifacts WHERE {search_clause} ORDER BY timestamp DESC LIMIT 3",
                    params,
                ).fetchall()
                conn.close()
                return [dict(r) for r in results]
            except Exception as e:
                print(f"⚠️ [LEDGER] Wisdom recall error: {e}")
                conn.close()
                return []

    @staticmethod
    def record_deployment(version: str, status: str, auditor: str):
        """Record deployment event."""
        conn = Ledger._get_connection()
        conn.execute(
            "INSERT INTO builds (version, status, auditor, timestamp) VALUES (?, ?, ?, ?)",
            (version, status, auditor, time.time()),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_data() -> Dict[str, List[Dict]]:
        """Get all ledger data."""
        conn = Ledger._get_connection()
        data = {
            "snapshots": [dict(r) for r in conn.execute("SELECT * FROM snapshots ORDER BY timestamp DESC").fetchall()],
            "artifacts": [dict(r) for r in conn.execute("SELECT * FROM artifacts ORDER BY timestamp DESC").fetchall()],
            "builds": [dict(r) for r in conn.execute("SELECT * FROM builds ORDER BY timestamp DESC").fetchall()],
        }
        conn.close()
        return data


# Initialize on import
Ledger.initialize()