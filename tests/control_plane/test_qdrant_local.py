# SPDX-License-Identifier: MIT
"""Unit tests for Local Embedded Qdrant Manager."""

import shutil
import tempfile
from pathlib import Path
from control_plane.infra.qdrant_manager import LocalQdrantManager


def test_qdrant_local_store_and_search():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        manager = LocalQdrantManager(storage_dir=temp_dir, vector_dim=64)
        store_res = manager.store_context(
            knight_id="SIR_HELIOS",
            text="High altitude telemetry and truth verification",
            metadata={"domain": "telemetry"},
        )
        assert store_res["success"] is True
        assert store_res["knight_id"] == "SIR_HELIOS"

        hits = manager.search_context(knight_id="SIR_HELIOS", query_text="telemetry verification", limit=2)
        assert len(hits) >= 1
        assert hits[0]["payload"]["knight_id"] == "SIR_HELIOS"
        assert hits[0]["payload"]["domain"] == "telemetry"

        status = manager.get_status()
        assert status["status"] == "HEALTHY"
        assert status["points_count"] == 1
        manager.close()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
