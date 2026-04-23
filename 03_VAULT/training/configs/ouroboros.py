"""Ouroboros Memory System - SQLite persistence for Camelot executions.

Handles all database operations with proper error handling,
connection management, and JSON serialization.
"""

import sqlite3
import json
import os
import logging
from datetime import datetime

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CONFIG_DIR, "ouroboros.db")
LOG_DIR = os.path.join(CONFIG_DIR, "logs")

_initialized = False
logger = logging.getLogger("ouroboros")


def _setup_logging():
    """Initialize file logging if logs directory exists."""
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
    handler = logging.FileHandler(os.path.join(LOG_DIR, "ouroboros.log"), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


_setup_logging()


import contextlib

DB_VERSION = 2  # Bump when schema changes


@contextlib.contextmanager
def _connect():
    """Context manager for database connections — guarantees cleanup."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
    except sqlite3.Error as e:
        logger.error("Database error: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def _ensure_init():
    """Lazy initialization — only create tables on first use."""
    global _initialized
    if _initialized:
        return
    try:
        with _connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    directive TEXT NOT NULL,
                    intent TEXT,
                    domain TEXT,
                    complexity INTEGER,
                    knight TEXT,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    duration_ms INTEGER,
                    files_created TEXT
                );
                CREATE TABLE IF NOT EXISTS stats (
                    knight TEXT PRIMARY KEY,
                    total_runs INTEGER DEFAULT 0,
                    successes INTEGER DEFAULT 0,
                    failures INTEGER DEFAULT 0,
                    blocked INTEGER DEFAULT 0,
                    avg_duration_ms REAL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                );
            """)
            # Migrate: add blocked column if missing (existing DBs)
            try:
                conn.execute("SELECT blocked FROM stats LIMIT 1")
            except sqlite3.OperationalError:
                conn.execute("ALTER TABLE stats ADD COLUMN blocked INTEGER DEFAULT 0")
            # Track schema version
            conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
                         (DB_VERSION,))
            conn.commit()
        _initialized = True
    except sqlite3.Error as e:
        logger.error("Database initialization failed: %s", e)
        print(f"  Warning: Ouroboros DB init failed ({e}). Memory disabled.")
        _initialized = False


def log_execution(directive, intent, domain, complexity, knight, status, result,
                  duration_ms=0, files_created=None):
    """Record an execution and update knight stats."""
    _ensure_init()
    if not _initialized:
        return
    try:
        with _connect() as conn:
            conn.execute(
                """INSERT INTO executions
                   (timestamp, directive, intent, domain, complexity, knight, status, result,
                    duration_ms, files_created)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (datetime.now().isoformat(), directive, intent, domain, complexity, knight,
                 status, result, duration_ms,
                 json.dumps(files_created) if files_created else None)
            )
            # Update stats with proper blocked tracking
            row = conn.execute("SELECT * FROM stats WHERE knight = ?", (knight,)).fetchone()
            if row:
                total = row["total_runs"] + 1
                succ = row["successes"] + (1 if status == "success" else 0)
                fail = row["failures"] + (1 if status == "error" else 0)
                blk = row["blocked"] + (1 if status == "blocked" else 0)
                avg = ((row["avg_duration_ms"] * row["total_runs"]) + duration_ms) / total
                conn.execute(
                    """UPDATE stats SET total_runs=?, successes=?, failures=?,
                       blocked=?, avg_duration_ms=? WHERE knight=?""",
                    (total, succ, fail, blk, avg, knight)
                )
            else:
                conn.execute(
                    """INSERT INTO stats (knight, total_runs, successes, failures, blocked, avg_duration_ms)
                       VALUES (?, 1, ?, ?, ?, ?)""",
                    (knight,
                     1 if status == "success" else 0,
                     1 if status == "error" else 0,
                     1 if status == "blocked" else 0,
                     duration_ms)
                )
            conn.commit()
        logger.info("Logged: [%s] %s -> %s (%s, %dms)", status, knight, directive[:80], domain, duration_ms)
    except sqlite3.Error as e:
        logger.error("Failed to log execution: %s", e)


def get_history(limit=20):
    """Retrieve execution history with deserialized files_created."""
    _ensure_init()
    if not _initialized:
        return []
    try:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT * FROM executions ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        results = []
        for r in rows:
            entry = dict(r)
            # Deserialize files_created from JSON string
            if entry.get("files_created"):
                try:
                    entry["files_created"] = json.loads(entry["files_created"])
                except (json.JSONDecodeError, TypeError):
                    entry["files_created"] = []
            else:
                entry["files_created"] = []
            results.append(entry)
        return results
    except sqlite3.Error as e:
        logger.error("Failed to get history: %s", e)
        return []


def get_stats():
    """Retrieve knight performance statistics."""
    _ensure_init()
    if not _initialized:
        return []
    try:
        with _connect() as conn:
            rows = conn.execute("SELECT * FROM stats ORDER BY total_runs DESC").fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        logger.error("Failed to get stats: %s", e)
        return []


def export_all():
    """Export all data with properly deserialized fields."""
    return {"history": get_history(limit=9999), "stats": get_stats()}
