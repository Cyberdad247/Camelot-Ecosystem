# SPDX-License-Identifier: MIT
"""Adversarial & Unit Test Suite — Phase 3 Bounded Runtime Execution (Wasmtime Component Model).

Validates:
    1. Capability Lease Verification (presence, lease_id format, task_id/tenant_id binding).
    2. Lease Expiration Rejection.
    3. Hardware Scarcity Memory Protocol (<50MB RAM ceiling).
    4. Host Component Export `vfs.read` (Scoped reading, path traversal protection, out-of-scope blocking).
    5. Host Component Export `evidence.emit` (`operator-evidence/1` event envelope schema compliance).
    6. End-to-end Bounded Runtime Execution & Deterministic Transcript Hashing.
"""
from __future__ import annotations

import datetime
from datetime import timezone
import pytest

from control_plane.sandbox.wasmtime_runner import (
    WasmtimeSandboxRunner,
    CapabilityLeaseError,
    VFSConfinementError,
    HostVFSEnclave,
    HostEvidenceEnclave,
    BoundedExecutionEnvelope,
)


def make_valid_lease(
    task_id: str = "task_alpha_01",
    tenant_id: str = "tenant_omega_01",
    lease_id: str = "lease_test_001",
    read_scopes: list[str] | None = None,
    max_memory_mb: float = 25.0,
    valid_until: str | None = None,
) -> dict:
    if read_scopes is None:
        read_scopes = ["vfs/workspaces", "docs/architecture"]
    if valid_until is None:
        valid_until = (datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=1)).isoformat()

    return {
        "schema_version": "camelot-lease/1",
        "lease_id": lease_id,
        "authority_epoch": 1,
        "authority_vector": [1, 1, 0, 1, 1, 1],
        "manifest_hash": "sha256:" + "f" * 64,
        "task_id": task_id,
        "correlation_id": "cor_test_001",
        "tenant_id": tenant_id,
        "effect_class": "workspace.test",
        "declared_risk_tier": "T1",
        "subject": {
            "node_id": "wasm_guest_alpha",
            "workload_id": "workload_test",
            "cartridge_id": "cartridge_wasm",
            "node_trust_band": "T1",
        },
        "permissions": {
            "path_scopes": {
                "read_scopes": read_scopes,
                "write_scopes": [],
            }
        },
        "limits": {
            "max_memory_mb": max_memory_mb,
            "timeout_sec": 5.0,
            "valid_until": valid_until,
        },
        "properties": {},
        "derived_capabilities_provenance": {
            "policy_decision_ref": "receipt://sentinel/decision/1",
            "evaluated_epoch": 1,
        },
    }


def test_missing_or_invalid_lease_raises_error():
    runner = WasmtimeSandboxRunner()

    with pytest.raises(CapabilityLeaseError):
        runner.execute_bounded_runtime("task_alpha_01", {}, lambda v, e: "ok")

    with pytest.raises(CapabilityLeaseError):
        runner.execute_bounded_runtime("task_alpha_01", {"lease_id": "invalid"}, lambda v, e: "ok")


def test_lease_task_id_mismatch_blocked():
    runner = WasmtimeSandboxRunner()
    lease = make_valid_lease(task_id="task_actual_id")

    env = runner.execute_bounded_runtime("task_different_id", lease, lambda v, e: "ok")

    assert env.status == "VIOLATION_BLOCKED"
    assert "[LEASE_MISMATCH]" in env.error_message


def test_expired_lease_blocked():
    runner = WasmtimeSandboxRunner()
    past = (datetime.datetime.now(timezone.utc) - datetime.timedelta(minutes=10)).isoformat()
    lease = make_valid_lease(valid_until=past)

    env = runner.execute_bounded_runtime("task_alpha_01", lease, lambda v, e: "ok")

    assert env.status == "VIOLATION_BLOCKED"
    assert "[LEASE_EXPIRED]" in env.error_message


def test_memory_hard_cap_exceeded():
    runner = WasmtimeSandboxRunner()
    lease = make_valid_lease(max_memory_mb=30.0)

    # Attempt to allocate 40MB against a 30MB limit
    env = runner.execute_bounded_runtime(
        "task_alpha_01",
        lease,
        lambda v, e: "ok",
        simulated_memory_mb=40.0,
    )

    assert env.status == "MEMORY_EXCEEDED"
    assert "[WASI_OOM_GUARD]" in env.error_message


def test_vfs_read_scoped_access_success():
    virtual_files = {
        "vfs/workspaces/code.py": "print('hello from sandbox')",
        "docs/architecture/spec.md": "# Architecture Specification",
    }
    vfs = HostVFSEnclave(
        allowed_read_scopes=["vfs/workspaces", "docs/architecture"],
        virtual_files=virtual_files,
    )

    content1 = vfs.read("vfs/workspaces/code.py")
    assert content1 == "print('hello from sandbox')"

    content2 = vfs.read("docs/architecture/spec.md")
    assert content2 == "# Architecture Specification"

    assert "vfs/workspaces/code.py" in vfs.read_history
    assert "docs/architecture/spec.md" in vfs.read_history


def test_vfs_read_path_traversal_blocked():
    vfs = HostVFSEnclave(allowed_read_scopes=["vfs/workspaces"])

    traversal_attacks = [
        "../etc/passwd",
        "vfs/workspaces/../../secret.env",
        "/etc/shadow",
        "\\windows\\system32",
        "vfs/workspaces/..",
    ]

    for attack in traversal_attacks:
        with pytest.raises(VFSConfinementError):
            vfs.read(attack)


def test_vfs_read_out_of_scope_blocked():
    vfs = HostVFSEnclave(
        allowed_read_scopes=["vfs/workspaces"],
        virtual_files={"03_VAULT/secret.json": "{'key': 'topsecret'}"},
    )

    with pytest.raises(VFSConfinementError) as exc_info:
        vfs.read("03_VAULT/secret.json")

    assert "[VFS_SCOPE_VIOLATION]" in str(exc_info.value)


def test_evidence_emit_schema_compliance():
    evidence_enclave = HostEvidenceEnclave(
        task_id="task_evt_01",
        correlation_id="cor_evt_01",
        tenant_id="tenant_omega_01",
        actor_id="sir_codex",
        trust_band="T1",
    )

    envelope = evidence_enclave.emit(
        kind="test.execution.completed",
        payload_redacted={"tests_passed": 42, "exit_code": 0},
        integrity="verified",
    )

    assert envelope["schema_version"] == "operator-evidence/1"
    assert envelope["event_id"].startswith("evt_")
    assert envelope["task_id"] == "task_evt_01"
    assert envelope["correlation_id"] == "cor_evt_01"
    assert envelope["tenant_id"] == "tenant_omega_01"
    assert envelope["kind"] == "test.execution.completed"
    assert envelope["actor"]["knight_id"] == "sir_codex"
    assert envelope["integrity"] == "verified"
    assert envelope["parent_hash"].startswith("sha256:")
    assert envelope["payload_redacted"]["tests_passed"] == 42
    assert len(evidence_enclave.emitted_envelopes) == 1


def test_bounded_runtime_full_execution_flow():
    runner = WasmtimeSandboxRunner()
    lease = make_valid_lease(
        task_id="task_pipeline_01",
        tenant_id="tenant_omega_01",
        read_scopes=["vfs/pipeline"],
        max_memory_mb=20.0,
    )
    virtual_fs = {"vfs/pipeline/manifest.json": '{"target": "deploy"}'}

    def guest_program(vfs: HostVFSEnclave, ev: HostEvidenceEnclave) -> str:
        data = vfs.read("vfs/pipeline/manifest.json")
        ev.emit(
            kind="pipeline.parsed",
            payload_redacted={"status": "parsed", "content": data},
            integrity="verified",
        )
        return "PIPELINE_OK"

    env: BoundedExecutionEnvelope = runner.execute_bounded_runtime(
        task_id="task_pipeline_01",
        lease=lease,
        guest_fn=guest_program,
        simulated_memory_mb=8.5,
        virtual_fs=virtual_fs,
    )

    assert env.status == "SUCCESS"
    assert env.error_message is None
    assert env.output_data["result"] == "PIPELINE_OK"
    assert env.output_data["read_files_count"] == 1
    assert env.output_data["emitted_evidence_count"] == 1
    assert len(env.evidence_envelopes) == 1
    assert env.transcript_hash.startswith("sha256:")
    assert env.memory_used_mb == 8.5
