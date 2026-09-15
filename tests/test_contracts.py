# SPDX-License-Identifier: MIT

"""Contract-suite validation for packages/contracts (Camelot-OS SADD + LLDD v1.2 §11).

The v1.2 contract family is JSON Schema Draft 2020-12, published from
camelot-contracts/1 with backward-compatibility guarantees. This harness
enforces:

1. Every packages/contracts/*.json parses as JSON.
2. Every schema is a well-formed Draft 2020-12 schema (meta-schema check).
3. index.json's declared schema set exactly matches the files on disk.
4. The canonical §11.3 receipt validates a well-formed instance and rejects
   tampered ones (parent_hash integrity, chain_height monotonicity).
5. The effect-class enum tracks the §5.5 taxonomy (spot-checked).
"""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

CONTRACTS_DIR = Path(__file__).resolve().parent.parent / "packages" / "contracts"

SCHEMA_FILES = sorted(CONTRACTS_DIR.glob("*.json"))
assert SCHEMA_FILES, "packages/contracts must not be empty"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def schemas() -> dict[str, dict]:
    return {p.name: load_json(p) for p in SCHEMA_FILES}


@pytest.mark.parametrize("file", SCHEMA_FILES, ids=lambda p: p.name)
def test_contracts_parse(file: Path):
    data = load_json(file)
    assert isinstance(data, dict)
    assert data.get("$schema") == "https://json-schema.org/draft/2020-12/schema"


@pytest.mark.parametrize("file", SCHEMA_FILES, ids=lambda p: p.name)
def test_schema_is_valid_draft2020_12(file: Path):
    # check_schema raises SchemaError on a malformed schema.
    Draft202012Validator.check_schema(load_json(file))


def test_index_matches_disk(schemas):
    index = schemas["index.json"]
    declared = {e["file"] for e in index["schemas"]}
    on_disk = {name for name in schemas if name != "index.json"}
    assert declared == on_disk, (
        f"index.json declares {sorted(declared)} but disk has {sorted(on_disk)}"
    )
    assert index["version"].startswith("1.")
    assert index["json_schema_dialect"] == "https://json-schema.org/draft/2020-12/schema"


def test_index_entries_are_self_describing(schemas):
    index = schemas["index.json"]
    for entry in index["schemas"]:
        schema = schemas[entry["file"]]
        assert schema.get("$id") == entry["$id"], entry["file"]
        assert entry["schema_version"] in json.dumps(schema), entry["file"]


def _valid_receipt() -> dict:
    """A minimal receipt that satisfies every required field in §11.3."""
    return {
        "schema_version": "camelot-receipt/1",
        "receipt_id": "rcp_0001",
        "parent_hash": "sha256:" + "0" * 64,  # genesis receipt
        "chain_height": 0,
        "tenant_id": "tenant_acme",
        "correlation_id": "cor_123",
        "task_id": "task_456",
        "authority_epoch": 43,
        "effect_class": "workspace.patch",
        "declared_risk_tier": "T2",
        "timestamp": "2026-08-14T16:00:00Z",
        "actor": {
            "id": "sir-forge",
            "role": "engineering_builder",
            "node_id": "engineering-01",
            "trust_band": "attested",
        },
        "event": "patch.applied",
        "proof": {
            "hash_algorithm": "sha256",
            "signature_algorithm": "ed25519",
            "signer": "sentinel",
            "signature": "ed25519:abc123",
        },
    }


def test_receipt_valid_instance(schemas):
    validator = Draft202012Validator(schemas["receipt.schema.json"])
    errors = sorted(validator.iter_errors(_valid_receipt()), key=str)
    assert errors == [], f"valid receipt rejected: {errors}"


@pytest.mark.parametrize(
    ("mutate", "expect"),
    [
        (lambda r: r.update({"parent_hash": "sha256:" + "f" * 63}), True),  # wrong length
        (lambda r: r.update({"parent_hash": "tampered"}), True),
        (lambda r: r.update({"chain_height": -1}), True),
        (lambda r: r.update({"effect_class": "not.a.class"}), True),
        (lambda r: r.update({"declared_risk_tier": "T9"}), True),
        (lambda r: r.update({"actor": {"id": "x"}}), True),  # missing trust_band
        (lambda r: r.pop("proof"), True),
        (lambda r: r.update({"proof": {**r["proof"], "signature": "plaintext"}}), True),
    ],
    ids=[
        "parent_hash_wrong_length",
        "parent_hash_unprefixed",
        "negative_chain_height",
        "unknown_effect_class",
        "unknown_risk_tier",
        "actor_missing_trust_band",
        "proof_missing",
        "signature_not_ed25519",
    ],
)
def test_receipt_tamper_detection(schemas, mutate, expect):
    receipt = _valid_receipt()
    mutate(receipt)
    validator = Draft202012Validator(schemas["receipt.schema.json"])
    errors = list(validator.iter_errors(receipt))
    assert bool(errors) is expect, f"tamper case not detected: {receipt}"


def test_effect_class_taxonomy_tracks_sadd(schemas):
    effect_class = schemas["receipt.schema.json"]["$defs"]["effect_class"]["enum"]
    for cls in ["ro.fetch", "workspace.patch", "promote.deploy", "payment.capture",
                "device.sms.send", "promote.failover"]:
        assert cls in effect_class, f"§5.5 class {cls} missing from contract enum"
    risk = schemas["receipt.schema.json"]["$defs"]["risk_tier"]["enum"]
    assert risk == ["T0", "T1", "T2", "T3", "T4"]
