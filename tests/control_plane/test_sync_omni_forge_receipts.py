# SPDX-License-Identifier: MIT
"""
Tests for //SYNC_OMNI_FORGE_DATABASES receipts.db bootstrap (#1).

The sync handler must create tools/arthurian-omni-forge/data/receipts.db
with the exact hive_receipts schema consumed by the Omni-Forge ReceiptStore
(src/lib/foundry-persistence.ts) when it is absent — a SYNCED status over a
missing artifact is a false-green. Schema-only: no seed rows, so the Forge
owns chain genesis and the merkle root is unaffected.
"""

import sqlite3

import pytest

from control_plane.runes import runic_router as rr

EXPECTED_COLUMNS = ["id", "payload", "sha256", "timestamp"]


def _hive_receipts_columns(db_path):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("PRAGMA table_info(hive_receipts);").fetchall()
    return [r[1] for r in rows]


def test_sync_creates_receipts_db_with_forge_schema(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "CAMELOT_HOME", tmp_path)
    res = rr._handle_sync_omni_forge_databases("", {})

    assert res["status"] == "SYNCED"
    assert res["details"]["receipts_exists"] is True
    assert res["details"]["receipts_created"] is True

    rcpt_db = tmp_path / "tools" / "arthurian-omni-forge" / "data" / "receipts.db"
    assert rcpt_db.exists()
    assert _hive_receipts_columns(rcpt_db) == EXPECTED_COLUMNS
    with sqlite3.connect(rcpt_db) as conn:
        assert conn.execute("PRAGMA journal_mode;").fetchone()[0].lower() == "wal"
        assert conn.execute("SELECT COUNT(*) FROM hive_receipts;").fetchone()[0] == 0


def test_sync_never_clobbers_existing_receipts_chain(tmp_path, monkeypatch):
    data_dir = tmp_path / "tools" / "arthurian-omni-forge" / "data"
    data_dir.mkdir(parents=True)
    rcpt_db = data_dir / "receipts.db"
    with sqlite3.connect(rcpt_db) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            "CREATE TABLE hive_receipts (id TEXT PRIMARY KEY, payload TEXT NOT NULL,"
            " sha256 TEXT NOT NULL, timestamp TEXT NOT NULL);"
        )
        conn.execute(
            "INSERT INTO hive_receipts VALUES ('rcp_genesis', '{}', 'sha256:00', '2026-01-01T00:00:00Z');"
        )
        conn.commit()

    monkeypatch.setattr(rr, "CAMELOT_HOME", tmp_path)
    res = rr._handle_sync_omni_forge_databases("", {})

    assert res["status"] == "SYNCED"
    assert res["details"]["receipts_created"] is False
    with sqlite3.connect(rcpt_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM hive_receipts;").fetchone()[0] == 1
