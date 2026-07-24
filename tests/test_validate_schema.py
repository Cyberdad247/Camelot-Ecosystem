import json
import os
import sys
from unittest.mock import mock_open, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01_KERNEL", "EXCALIBUR", "config")))
import validate_schema


def test_verify_payload_success():
    schema_content = json.dumps(
        {"type": "object", "properties": {"intent": {"type": "string"}}, "required": ["intent"]}
    )
    payload = {"intent": "do something"}

    with patch("builtins.open", mock_open(read_data=schema_content)):
        assert validate_schema.verify_payload("dummy_path", payload)


def test_verify_payload_failure():
    schema_content = json.dumps(
        {"type": "object", "properties": {"intent": {"type": "string"}}, "required": ["intent"]}
    )
    payload = {"other": "do something"}

    with patch("builtins.open", mock_open(read_data=schema_content)):
        assert not validate_schema.verify_payload("dummy_path", payload)


def test_verify_payload_file_not_found():
    with pytest.raises(FileNotFoundError):
        validate_schema.verify_payload("nonexistent_file.json", {})
