# SPDX-License-Identifier: MIT

import ouroboros


def test_ouroboros_parity(monkeypatch, tmp_path):
    # Isolate path
    monkeypatch.setenv("CAMELOT_OS_HOME", str(tmp_path))
    if hasattr(ouroboros, "clear_ledger"):
        ouroboros.clear_ledger()
    db_path = str(tmp_path / "ouroboros_test.db")
    monkeypatch.setattr(ouroboros, "DB_PATH", db_path)
    monkeypatch.setattr(ouroboros, "_initialized", False)

    # Reset Rust engine ledger if available
    rust_engine = getattr(ouroboros, "_rust_engine", None)
    assert rust_engine is not None, "Rust engine binding is not loaded"

    # We want to measure the initial size of the Rust ring buffer
    initial_ring_size = rust_engine.trigger_pending_compression()

    # Log 1000 executions
    for i in range(1000):
        ouroboros.log_execution(
            directive=f"parity-test-directive-{i}",
            intent="test intent",
            domain="test domain",
            complexity=1,
            knight="sir_forge",
            status="success",
            result="test result",
            duration_ms=5,
            files_created=["file1.txt"]
        )

    # Assert history length is exactly 1000
    history = ouroboros.get_history(limit=2000)
    sentinel_rows = [r for r in history if r["directive"].startswith("parity-test-directive-")]
    assert len(sentinel_rows) == 1000, f"History row count mismatch: {len(sentinel_rows)}"

    # Assert Rust ring length increased by exactly 1000
    final_ring_size = rust_engine.trigger_pending_compression()
    added_to_ring = final_ring_size - initial_ring_size
    assert added_to_ring == 1000, f"Rust ring size mismatch: {added_to_ring}"

