# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for OpenNotebookCompactor and TrajectoryHarvestEngine.
"""
from __future__ import annotations

from control_plane.infra.open_notebook_compactor import (
    OpenNotebookCompactor,
    TrajectoryHarvestEngine,
    TrajectorySpan
)

def test_trajectory_harvest_engine(tmp_path):
    engine = TrajectoryHarvestEngine(trajectory_dir=tmp_path)
    span = TrajectorySpan(
        span_id="span_001",
        knight_id="SIR_CODEX",
        task_intent="Compile WASM component",
        tool_invocations=[{"tool": "cargo_build", "status": "OK"}],
        ast_diff_sha256="abc123def456",
        reward_score=0.95
    )
    span_id = engine.record_trajectory(span)
    assert span_id == "span_001"

    trajectories = engine.fetch_trajectories(knight_id="SIR_CODEX", min_reward=0.9)
    assert len(trajectories) == 1
    assert trajectories[0]["task_intent"] == "Compile WASM component"

def test_compactor_loads_and_compacts(tmp_path):
    db_file = tmp_path / "test_uast.db"
    compactor = OpenNotebookCompactor(db_path=db_file)
    manifest = compactor.run_compaction_pass()

    assert manifest["total_repositories"] > 0
    assert manifest["memory_bounded"] is True
    assert manifest["db_size_mb"] < 150.0
    assert len(manifest["shards"]) == manifest["total_repositories"]
