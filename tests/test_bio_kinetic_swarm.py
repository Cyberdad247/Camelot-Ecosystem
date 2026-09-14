# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for Bio-Kinetic Swarm Coordinator & Nanobot Embedding Engine.
"""
from __future__ import annotations

import pytest
from control_plane.swarm.bio_kinetic_swarm import (
    BioKineticSwarmCoordinator,
    NanobotEmbeddingEngine,
    BioKineticCell
)

def test_nanobot_self_healing_missing_import():
    engine = NanobotEmbeddingEngine()
    code = "data = json.loads('{}')"
    error = "NameError: name 'json' is not defined"
    report = engine.inspect_and_heal("cell_test_01", code, error)
    
    assert report.status == "HEALED"
    assert report.repaired_code is not None
    assert "import json\n" in report.repaired_code

def test_nanobot_self_healing_syntax_balance():
    engine = NanobotEmbeddingEngine()
    code = "obj = {'key': 'val'"
    error = "SyntaxError: invalid syntax"
    report = engine.inspect_and_heal("cell_test_02", code, error)
    
    assert report.status == "HEALED"
    assert report.repaired_code == "obj = {'key': 'val'}"

def test_parallel_swarm_cellular_diode():
    swarm = BioKineticSwarmCoordinator(max_workers=3)
    tasks = [
        {
            "knight_id": "SIR_CODEX",
            "domain": "Parallel_Task_1",
            "task_fn": lambda: "Task 1 Success",
            "code_payload": ""
        },
        {
            "knight_id": "SIR_FORGE",
            "domain": "Parallel_Task_2_Failing",
            "task_fn": lambda: (_ for _ in ()).throw(RuntimeError("Unrecoverable failure")),
            "code_payload": ""
        },
        {
            "knight_id": "SIR_SYNTAX",
            "domain": "Parallel_Task_3",
            "task_fn": lambda: "Task 3 Success",
            "code_payload": ""
        }
    ]

    results = swarm.dispatch_parallel_knights(tasks)
    assert len(results) == 3

    # Ensure cellular diode isolated the failure without crashing the other two
    statuses = [res["status"] for res in results.values()]
    assert "NOMINAL" in statuses
    assert "ISOLATED_FAILURE" in statuses

    # Apoptosis verified: all active cells cleared
    assert len(swarm.active_cells) == 0
