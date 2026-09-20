# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from control_plane.memory.worldtree_graph_sync import WorldTreeGraphSyncEngine, WORLDTREE_ROOT_UUID


def test_worldtree_cypher_staging_and_batch_commit(tmp_path):
    engine = WorldTreeGraphSyncEngine(sync_dir=tmp_path)
    
    # 1. Stage Cypher Fact 1
    stmt1 = engine.stage_bitemporal_fact_cypher(
        tenant_id="tenant_sovereign_001",
        namespace="ravenry.mail",
        subject="Arthur_Operator",
        predicate="approved_plan_hash",
        object_value="sha256:4a8b8c2d9e1f",
        valid_from="2026-08-30T22:00:00Z",
        recorded_from="2026-08-30T22:05:00Z",
        confidence=0.99
    )
    
    assert stmt1.statement_id.startswith("cypher_")
    assert stmt1.worldtree_anchor == WORLDTREE_ROOT_UUID
    assert "MERGE (root:WorldTreeRoot" in stmt1.cypher_query
    assert stmt1.status == "STAGED"
    
    # 2. Stage Cypher Fact 2
    stmt2 = engine.stage_bitemporal_fact_cypher(
        tenant_id="tenant_sovereign_001",
        namespace="knight.telemetry",
        subject="Sir_Codex",
        predicate="completed_task",
        object_value="wasm_sandbox_runner",
        valid_from="2026-08-30T22:10:00Z",
        recorded_from="2026-08-30T22:10:05Z",
        confidence=1.0
    )
    assert len(engine.staged_statements) == 2
    
    # 3. Commit Batch across 38 Knights
    summary = engine.commit_sync_batch(knights_count=38)
    assert summary.batch_id.startswith("batch_")
    assert summary.total_facts_staged == 2
    assert summary.total_facts_committed == 2
    assert summary.knights_tethered == 38
    assert len(engine.staged_statements) == 0
