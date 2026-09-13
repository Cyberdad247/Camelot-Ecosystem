# SPDX-License-Identifier: MIT
"""Verification test for packages/contracts/CONTRACTS.lock determinism gate.

Ensures zero schema drift across language boundaries. Fails immediately
if any contract schema or cross-language binding mutates without lockfile regeneration.
"""
import json
from pathlib import Path
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from packages.contracts.tools.generate_contracts_lock import CANONICAL_16, generate_lock

CONTRACTS_DIR = Path(__file__).resolve().parent.parent / "packages" / "contracts"
LOCK_FILE = CONTRACTS_DIR / "CONTRACTS.lock"


def test_lockfile_exists():
    assert LOCK_FILE.exists(), f"CONTRACTS.lock missing at {LOCK_FILE}"


def test_lockfile_matches_disk_deterministically():
    assert LOCK_FILE.exists()
    on_disk = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    recomputed = generate_lock()

    assert on_disk["lockfile_version"] == recomputed["lockfile_version"]
    assert on_disk["canonicalization_standard"] == "RFC_8785_JCS"
    assert on_disk["contract_count"] == 16
    assert on_disk["lock_hash"] == recomputed["lock_hash"], (
        f"Contract drift detected! Expected lock hash {on_disk['lock_hash']}, "
        f"got {recomputed['lock_hash']}. Run 'python -m packages.contracts.tools.generate_contracts_lock' to regenerate."
    )
    assert on_disk["shared_bindings"] == recomputed["shared_bindings"], "Binding drift detected"
    assert on_disk["schemas"] == recomputed["schemas"], "Schema drift detected"


def test_all_canonical_16_present():
    on_disk = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
    schemas = on_disk["schemas"]
    for contract_id, filename in CANONICAL_16:
        assert contract_id in schemas, f"Missing contract {contract_id} in lockfile"
        entry = schemas[contract_id]
        assert entry["schema_file"] == filename
        assert len(entry["schema_sha256"]) == 64
