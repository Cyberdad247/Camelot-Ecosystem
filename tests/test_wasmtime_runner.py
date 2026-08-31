# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from control_plane.sandbox.wasmtime_runner import WasmtimeSandboxRunner


def test_wasmtime_sandbox_success():
    runner = WasmtimeSandboxRunner()
    
    res = runner.execute_tool_in_sandbox(
        tool_id="calculator",
        input_payload={"expression": "12 * 8"},
        operator_risk_tier="R1",
        simulated_memory_mb=4.2
    )
    
    assert res.status == "SUCCESS"
    assert res.error_message is None
    assert res.memory_used_mb == 4.2
    assert res.transcript_hash.startswith("sha256:")
    assert "Wasmtime WASI 0.2 Active" in res.output_data["sandbox_isolation"]


def test_wasmtime_sandbox_risk_tier_violation():
    runner = WasmtimeSandboxRunner()
    
    # R0 operator attempting to execute R4 untrusted script
    res = runner.execute_tool_in_sandbox(
        tool_id="untrusted_script",
        input_payload={"script": "import os; os.system('ls')"},
        operator_risk_tier="R0",
        simulated_memory_mb=10.0
    )
    
    assert res.status == "VIOLATION_BLOCKED"
    assert "[WASI_SECURITY_VIOLATION]" in res.error_message


def test_wasmtime_sandbox_memory_exceeded():
    runner = WasmtimeSandboxRunner()
    
    # Calculator has 10MB limit; simulate 25MB allocation
    res = runner.execute_tool_in_sandbox(
        tool_id="calculator",
        input_payload={"expression": "huge_matrix"},
        operator_risk_tier="R2",
        simulated_memory_mb=25.0
    )
    
    assert res.status == "MEMORY_EXCEEDED"
    assert "[WASI_OOM_GUARD]" in res.error_message


def test_wasmtime_sandbox_egress_blocking():
    runner = WasmtimeSandboxRunner()
    
    # Read public doc allows camelot-os.dev only; try unapproved target
    res = runner.execute_tool_in_sandbox(
        tool_id="read_public_doc",
        input_payload={"target": "malicious-domain.com"},
        operator_risk_tier="R2",
        simulated_memory_mb=15.0,
        simulated_network_target="malicious-domain.com"
    )
    
    assert res.status == "VIOLATION_BLOCKED"
    assert "[WASI_EGRESS_BLOCKED]" in res.error_message
