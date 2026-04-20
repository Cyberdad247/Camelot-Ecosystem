# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json

import jsonschema
from jsonschema import validate


def verify_payload(schema_path, payload):
    with open(schema_path, "r") as f:
        schema = json.load(f)

    try:
        validate(instance=payload, schema=schema)
        print(f"✅ VALIDATION SUCCESS: Payload matches {schema_path}")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ VALIDATION ERROR: {e.message}")
        return False


# Example Tests
if __name__ == "__main__":
    # Test 1: Valid Agent Request
    valid_agent_req = {"intent": "Optimize the quantum lattice.", "agent_id": "MERLIN", "priority": 5}

    # Test 2: Invalid Agent Request (Missing intent)
    invalid_agent_req = {"agent_id": "INVALID_NAME"}

    print("--- Running Kernel Validation Tests ---")
    verify_payload("01_KERNEL/config/schemas/agent_dispatch.schema.json", valid_agent_req)
    verify_payload("01_KERNEL/config/schemas/agent_dispatch.schema.json", invalid_agent_req)