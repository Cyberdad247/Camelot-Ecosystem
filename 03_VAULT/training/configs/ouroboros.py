"""Ouroboros Memory System - Rust engine memory ledger forwarder.
"""

import json
import logging

logger = logging.getLogger("ouroboros")

_rust_engine = None
try:
    import ouroboros_engine as _oe
    _rust_engine = _oe
except (ImportError, OSError, RuntimeError, ValueError):
    _rust_engine = None


def log_execution(directive, intent, domain, complexity, knight, status, result,
                  duration_ms=0, files_created=None):
    """Record an execution in the Rust engine memory ring and WAL."""
    if _rust_engine is not None:
        try:
            files_str = json.dumps(files_created) if files_created else None
            _rust_engine.log_execution(
                directive=str(directive),
                intent=str(intent) if intent is not None else None,
                domain=str(domain) if domain is not None else None,
                complexity=int(complexity) if complexity is not None else 0,
                knight=str(knight),
                status=str(status),
                result=str(result) if result is not None else None,
                duration_ms=int(duration_ms),
                files_created=files_str
            )
        except Exception as exc:
            logger.warning("Ouroboros Rust engine log_execution failed: %s", exc)


def get_history(limit=20):
    """Retrieve execution history from the Rust engine memory ring."""
    if _rust_engine is not None:
        try:
            return _rust_engine.get_history(limit=limit)
        except Exception as exc:
            logger.warning("Ouroboros Rust engine get_history failed: %s", exc)
    return []


def get_stats():
    """Retrieve knight performance statistics from the Rust engine memory ring."""
    if _rust_engine is not None:
        try:
            return _rust_engine.get_stats()
        except Exception as exc:
            logger.warning("Ouroboros Rust engine get_stats failed: %s", exc)
    return []


def export_all():
    """Export all data from the Rust engine memory ring."""
    if _rust_engine is not None:
        try:
            return _rust_engine.export_all()
        except Exception as exc:
            logger.warning("Ouroboros Rust engine export_all failed: %s", exc)
    return {"history": [], "stats": []}
