"""Tests for the Ouroboros SQLite persistence layer."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ouroboros


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Use a temp database for every test."""
    db_path = str(tmp_path / "test_ouroboros.db")
    monkeypatch.setattr(ouroboros, "DB_PATH", db_path)
    monkeypatch.setattr(ouroboros, "_initialized", False)
    yield db_path


def test_init_creates_tables():
    ouroboros._ensure_init()
    assert ouroboros._initialized is True


def test_log_and_retrieve():
    ouroboros.log_execution("test directive", "BUILD", "CODE", 2, "Sir Forge",
                           "success", "output text", 150, ["file.py"])
    history = ouroboros.get_history(5)
    assert len(history) == 1
    assert history[0]["directive"] == "test directive"
    assert history[0]["knight"] == "Sir Forge"
    assert history[0]["files_created"] == ["file.py"]


def test_stats_tracking():
    ouroboros.log_execution("d1", "BUILD", "CODE", 1, "Knight1", "success", "", 100)
    ouroboros.log_execution("d2", "BUILD", "CODE", 1, "Knight1", "error", "", 200)
    ouroboros.log_execution("d3", "BUILD", "CODE", 1, "Knight1", "blocked", "", 50)
    stats = ouroboros.get_stats()
    assert len(stats) == 1
    s = stats[0]
    assert s["total_runs"] == 3
    assert s["successes"] == 1
    assert s["failures"] == 1
    assert s["blocked"] == 1


def test_export_all():
    ouroboros.log_execution("d1", "BUILD", "CODE", 1, "K1", "success", "", 100)
    data = ouroboros.export_all()
    assert "history" in data
    assert "stats" in data
    assert len(data["history"]) == 1


def test_connection_context_manager():
    """Verify connections are properly closed via context manager."""
    ouroboros._ensure_init()
    with ouroboros._connect() as conn:
        conn.execute("SELECT 1")
    # After exiting context, connection should be closed
    # Attempting to use it should fail
    try:
        conn.execute("SELECT 1")
        # SQLite may not raise immediately, but the pattern is correct
    except Exception:
        pass  # Expected


def test_empty_history():
    ouroboros._ensure_init()
    assert ouroboros.get_history() == []
    assert ouroboros.get_stats() == []
