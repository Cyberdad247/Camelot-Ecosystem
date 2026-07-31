import json
import os
import sys

sys.path.insert(0, os.path.abspath("01_KERNEL"))
from EXCALIBUR.config.validate_schema import verify_payload  # noqa: E402


def test_verify_payload_valid(tmp_path):
    schema_path = tmp_path / "schema.json"
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        },
        "required": ["name", "age"]
    }
    with open(schema_path, "w") as f:
        json.dump(schema, f)

    payload = {"name": "Alice", "age": 30}

    # Should be valid
    assert verify_payload(str(schema_path), payload) is True


def test_verify_payload_invalid(tmp_path):
    schema_path = tmp_path / "schema.json"
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        },
        "required": ["name", "age"]
    }
    with open(schema_path, "w") as f:
        json.dump(schema, f)

    # Missing age
    payload = {"name": "Alice"}

    # Should be invalid
    assert verify_payload(str(schema_path), payload) is False


def test_verify_payload_invalid_json(tmp_path):
    schema_path = tmp_path / "schema.json"
    with open(schema_path, "w") as f:
        f.write("invalid json")

    payload = {"name": "Alice"}

    import pytest
    with pytest.raises(json.JSONDecodeError):
        verify_payload(str(schema_path), payload)
