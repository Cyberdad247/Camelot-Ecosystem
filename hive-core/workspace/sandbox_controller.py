# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
HIVE Ephemeral WASM Sandbox Controller
======================================
Manages WASM32-WASI microVM lifecycles inside `/hive-core/workspace/`.
Enforces Copy-on-Write (CoW) page sharing and memory delta limits (Δ ≤ 0.12 MiB).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(CAMELOT_ROOT / "cartridges" / "cartridge-hive-ide-swarm"))

from hive_engine import HiveEngine, MicroVMSandbox

LOG = logging.getLogger("HiveSandboxController")


def spawn_ephemeral_worker(knight_id: str, task_id: Optional[str] = None) -> Dict[str, Any]:
    engine = HiveEngine(root_path=CAMELOT_ROOT)
    sandbox = engine.spawn_sandbox(knight_id=knight_id, task_id=task_id)
    return {
        "sandbox_id": sandbox.sandbox_id,
        "knight_id": sandbox.knight_id,
        "cow_delta_mib": sandbox.cow_delta_mib,
        "memory_allocated_mb": sandbox.memory_allocated_mb,
        "ephemeral_path": str(sandbox.ephemeral_path)
    }


def execute_z3_verification(sandbox_id: str, pdg_clean: bool = True) -> Dict[str, Any]:
    engine = HiveEngine(root_path=CAMELOT_ROOT)
    receipt = engine.verify_z3_gate(sandbox_id=sandbox_id, pdg_taint_clean=pdg_clean)
    return {
        "verification_id": receipt.verification_id,
        "passed": receipt.passed,
        "verifier": receipt.verifier,
        "details": receipt.details
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing WASM MicroVM Sandbox Controller...")
    worker = spawn_ephemeral_worker("SIR_CODEX", "task-init-01")
    print("Spawned worker:", json.dumps(worker, indent=2))
    verif = execute_z3_verification(worker["sandbox_id"])
    print("Verification:", json.dumps(verif, indent=2))
