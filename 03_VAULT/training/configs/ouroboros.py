"""Ouroboros Memory System - Rust engine memory ledger forwarder with SQLite fallback."""

import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = str(Path.home() / "CAMELOT_OS" / "data" / "ouroboros.db")
_initialized = False

logger = logging.getLogger("ouroboros")

_rust_engine = None
try:
    import ouroboros_engine as _oe

    _rust_engine = _oe
except (ImportError, OSError, RuntimeError, ValueError):
    _rust_engine = None


def _ensure_init():
    """Create tables if they don't exist (SQLite fallback path)."""
    global _initialized
    if _initialized:
        return
    _db_path = Path(DB_PATH)
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                directive TEXT NOT NULL,
                intent TEXT,
                domain TEXT,
                complexity INTEGER DEFAULT 0,
                knight TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                duration_ms INTEGER DEFAULT 0,
                files_created TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
    _initialized = True


@contextmanager
def _connect():
    """Return a SQLite connection (for the fallback persistence path)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _sqlite_log(directive, intent, domain, complexity, knight, status, result,
                duration_ms=0, files_created=None):
    """Write an execution record to the local SQLite fallback."""
    _ensure_init()
    files_str = json.dumps(files_created) if files_created is not None else None
    with _connect() as conn:
        conn.execute(
            """INSERT INTO executions
               (directive, intent, domain, complexity, knight, status, result, duration_ms, files_created)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(directive), str(intent) if intent else None,
             str(domain) if domain else None, int(complexity) if complexity else 0,
             str(knight), str(status), str(result) if result else None,
             int(duration_ms), files_str),
        )
        conn.commit()


def _sqlite_history(limit=20):
    """Read execution history from the SQLite fallback."""
    _ensure_init()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM executions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    results = []
    for row in rows:
        d = dict(row)
        files = d.get("files_created")
        if files:
            try:
                d["files_created"] = json.loads(files)
            except (json.JSONDecodeError, TypeError):
                d["files_created"] = [files] if files else []
        else:
            d["files_created"] = []
        results.append(d)
    return results


def _sqlite_stats():
    """Compute knight performance stats from the SQLite fallback."""
    _ensure_init()
    with _connect() as conn:
        rows = conn.execute(
            """SELECT
                 knight,
                 COUNT(*) AS total_runs,
                 SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successes,
                 SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS failures,
                 SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END) AS blocked,
                 CAST(ROUND(AVG(duration_ms)) AS INTEGER) AS avg_duration_ms
               FROM executions
               GROUP BY knight"""
        ).fetchall()
    return [dict(r) for r in rows]


def _sqlite_export():
    """Export all data from the SQLite fallback."""
    return {"history": _sqlite_history(limit=10_000), "stats": _sqlite_stats()}


def log_execution(directive, intent, domain, complexity, knight, status, result,
                  duration_ms=0, files_created=None):
    """Record an execution in the Rust engine memory ring and WAL, or SQLite fallback."""
    if _rust_engine is not None:
        try:
            files_str = json.dumps(files_created) if files_created is not None else None
            _rust_engine.log_execution(
                directive=str(directive),
                intent=str(intent) if intent is not None else None,
                domain=str(domain) if domain is not None else None,
                complexity=int(complexity) if complexity is not None else 0,
                knight=str(knight),
                status=str(status),
                result=str(result) if result is not None else None,
                duration_ms=int(duration_ms),
                files_created=files_str,
            )
        except Exception as exc:
            logger.warning("Ouroboros Rust engine log_execution failed: %s", exc)
    else:
        _sqlite_log(directive, intent, domain, complexity, knight, status, result,
                     duration_ms=duration_ms, files_created=files_created)


def get_history(limit=20):
    """Retrieve execution history from the Rust engine memory ring or SQLite fallback."""
    if _rust_engine is not None:
        try:
            return _rust_engine.get_history(limit=limit)
        except Exception as exc:
            logger.warning("Ouroboros Rust engine get_history failed: %s", exc)
    return _sqlite_history(limit=limit)


def get_stats():
    """Retrieve knight performance statistics from the Rust engine or SQLite fallback."""
    if _rust_engine is not None:
        try:
            return _rust_engine.get_stats()
        except Exception as exc:
            logger.warning("Ouroboros Rust engine get_stats failed: %s", exc)
    return _sqlite_stats()


def export_all():
    """Export all data from the Rust engine memory ring or SQLite fallback."""
    if _rust_engine is not None:
        try:
            return _rust_engine.export_all()
        except Exception as exc:
            logger.warning("Ouroboros Rust engine export_all failed: %s", exc)
    return _sqlite_export()
