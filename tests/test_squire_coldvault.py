# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for Squire ColdVault database compaction and vacuuming."""

from __future__ import annotations

import sqlite3
import pytest
from pathlib import Path
from squires.coldvault import SquireColdVault, DatabaseCompactionResult, ColdVaultReport


@pytest.fixture
def sample_vault(tmp_path):
    mem_dir = tmp_path / "03_VAULT" / "memory"
    graph_dir = mem_dir / "graphiti"
    graph_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy database with some fragmented data
    db1 = mem_dir / "test_memcastle.db"
    conn = sqlite3.connect(str(db1))
    cur = conn.cursor()
    cur.execute("CREATE TABLE kv (id INTEGER PRIMARY KEY, val TEXT);")
    cur.executemany("INSERT INTO kv (val) VALUES (?);", [(f"val_{i}",) for i in range(500)])
    conn.commit()
    # Delete half to create freelist pages
    cur.execute("DELETE FROM kv WHERE id % 2 = 0;")
    conn.commit()
    conn.close()

    db2 = graph_dir / "test_graphiti.db"
    conn2 = sqlite3.connect(str(db2))
    cur2 = conn2.cursor()
    cur2.execute("CREATE TABLE facts (s TEXT, p TEXT, o TEXT);")
    cur2.execute("INSERT INTO facts VALUES ('MERLIN', 'RUNE', 'FORGE');")
    conn2.commit()
    conn2.close()

    return tmp_path


def test_coldvault_scan_databases(sample_vault):
    vault = SquireColdVault(home=sample_vault)
    dbs = vault.scan_databases()
    assert len(dbs) == 2
    names = [p.name for p in dbs]
    assert "test_memcastle.db" in names
    assert "test_graphiti.db" in names


def test_coldvault_compact_database(sample_vault):
    vault = SquireColdVault(home=sample_vault)
    db1 = sample_vault / "03_VAULT" / "memory" / "test_memcastle.db"
    res = vault.compact_database(db1, force_vacuum=True)
    assert isinstance(res, DatabaseCompactionResult)
    assert res.status == "COMPACTED"
    assert res.wal_truncated is True


def test_coldvault_vacuum_vault(sample_vault):
    vault = SquireColdVault(home=sample_vault)
    report = vault.vacuum_vault(force_vacuum=True)
    assert isinstance(report, ColdVaultReport)
    assert report.total_databases_scanned == 2
    assert report.status == "OPTIMIZED"
    assert len(report.results) == 2
