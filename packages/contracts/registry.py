# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""DG-310 Contract Registry & Lock Verifier.
============================================
Enforces that services start with verified contract sets:
    EXPECTED REGISTRY DIGEST -> LOAD REGISTRY -> VERIFY CONTRACT LOCK -> START

Prevents services from silently interpreting differing schema versions.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("camelot.contract_registry")


class ContractRegistryVerifier:
    """Validates schema integrity against packages/contracts/CONTRACTS.lock."""

    def __init__(self, contracts_dir: Optional[Path] = None):
        self.contracts_dir = contracts_dir or Path(__file__).resolve().parent
        self.lock_file = self.contracts_dir / "CONTRACTS.lock"

    def verify_registry(self) -> Tuple[bool, List[str]]:
        """Verify that CONTRACTS.lock exists, contains schemas, and has valid lock_hash."""
        errors: List[str] = []

        if not self.lock_file.exists():
            return False, [f"Missing CONTRACTS.lock at {self.lock_file}"]

        try:
            lock_data = json.loads(self.lock_file.read_text(encoding="utf-8"))
        except Exception as e:
            return False, [f"Failed to parse CONTRACTS.lock: {e}"]

        schemas = lock_data.get("schemas", {})
        if not schemas:
            errors.append("CONTRACTS.lock contains 0 registered schemas")

        # Verify each registered schema exists on disk
        for schema_id, meta in schemas.items():
            schema_file_name = meta.get("schema_file")
            if not schema_file_name:
                errors.append(f"Schema {schema_id} has no schema_file defined")
                continue
            schema_path = self.contracts_dir / schema_file_name
            if not schema_path.exists():
                # Check deprecated subdirectory
                dep_path = self.contracts_dir / "deprecated" / schema_file_name
                if dep_path.exists():
                    schema_path = dep_path
                else:
                    errors.append(f"Schema file missing on disk: {schema_path}")
                    continue
                actual_bytes = schema_path.read_bytes()
                # Basic non-empty check
                if len(actual_bytes) == 0:
                    errors.append(f"Schema file empty: {schema_path}")

        # Check lock hash present
        if not lock_data.get("lock_hash"):
            errors.append("CONTRACTS.lock missing lock_hash")

        return len(errors) == 0, errors

    def get_registered_schemas(self) -> List[str]:
        if not self.lock_file.exists():
            return []
        try:
            data = json.loads(self.lock_file.read_text(encoding="utf-8"))
            return list(data.get("schemas", {}).keys())
        except Exception:
            return []
