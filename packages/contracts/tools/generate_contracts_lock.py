#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate packages/contracts/CONTRACTS.lock deterministic lockfile.

Pins schema version, RFC 8785 canonical hash, and generated cross-language binding hashes
for the 16 canonical L2 contracts.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

CONTRACTS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = CONTRACTS_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from packages.contracts.canonicalize import canonicalize_json, sha256_canonical

CANONICAL_16 = [
    ("actor/1", "actor.schema.json"),
    ("tenant/1", "tenant.schema.json"),
    ("workspace/1", "workspace.schema.json"),
    ("task/1", "task.schema.json"),
    ("effect-manifest/1", "effect-manifest.schema.json"),
    ("policy-decision/1", "policy-decision.schema.json"),
    ("approval-certificate/1", "approval-certificate.schema.json"),
    ("capability-lease/1", "capability-lease.schema.json"),
    ("vfs-attestation/2", "vfs-attestation.schema.json"),
    ("evidence-envelope/1", "evidence-envelope.schema.json"),
    ("gideon-verdict/1", "gideon-verdict.schema.json"),
    ("arthur-resolution/1", "arthur-resolution.schema.json"),
    ("receipt/2", "receipt.schema.json"),
    ("authority-epoch/1", "authority-epoch.schema.json"),
    ("promotion/1", "promotion.schema.json"),
    ("workspace-event/1", "workspace-event.schema.json"),
]


def file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def generate_lock() -> dict[str, Any]:
    ts_bindings = CONTRACTS_DIR / "generated" / "ts" / "types.ts"
    go_bindings = CONTRACTS_DIR / "generated" / "go" / "types.go"
    rust_bindings = CONTRACTS_DIR / "generated" / "rust" / "src" / "types.rs"

    ts_hash = file_sha256(ts_bindings)
    go_hash = file_sha256(go_bindings)
    rust_hash = file_sha256(rust_bindings)

    schemas_lock = {}
    for contract_id, filename in CANONICAL_16:
        schema_path = CONTRACTS_DIR / filename
        if not schema_path.exists():
            raise FileNotFoundError(f"Missing canonical schema: {schema_path}")

        schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
        canonical_jcs = canonicalize_json(schema_data)
        schema_sha256 = hashlib.sha256(canonical_jcs.encode("utf-8")).hexdigest()

        schemas_lock[contract_id] = {
            "schema_file": filename,
            "schema_version": schema_data.get("properties", {}).get("schema_version", {}).get("const")
            or schema_data.get("properties", {}).get("schema_version", {}).get("enum", [contract_id])[0],
            "schema_sha256": schema_sha256,
            "canonical_bytes_len": len(canonical_jcs.encode("utf-8")),
        }

    # Compute aggregate lock hash
    canonical_schemas_jcs = canonicalize_json(schemas_lock)
    lock_hash = hashlib.sha256(canonical_schemas_jcs.encode("utf-8")).hexdigest()

    lockfile = {
        "lockfile_version": "1.0.0",
        "canonicalization_standard": "RFC_8785_JCS",
        "contract_count": len(CANONICAL_16),
        "lock_hash": lock_hash,
        "shared_bindings": {
            "ts_sha256": ts_hash,
            "go_sha256": go_hash,
            "rust_sha256": rust_hash,
        },
        "schemas": schemas_lock,
    }
    return lockfile


def main():
    lock = generate_lock()
    lock_path = CONTRACTS_DIR / "CONTRACTS.lock"
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"[CONTRACTS.lock] Generated successfully at {lock_path}")
    print(f"[CONTRACTS.lock] Aggregate lock hash: {lock['lock_hash']}")
    print(f"[CONTRACTS.lock] Canonical contracts pinned: {lock['contract_count']}")


if __name__ == "__main__":
    main()
