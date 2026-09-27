# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for the Production Engineering Plane (DG-310 through DG-440).
==========================================================================
Verifies Contract Registry, Config Contracts, Migration Engine, Key Lifecycle,
Release Proofs, Universal Safe Mode, and Bounded Backpressure.
"""
from __future__ import annotations

import json
import pytest

from packages.contracts.registry import ContractRegistryVerifier
from control_plane.production.config_contract import ConfigClassification, ConfigContract
from control_plane.production.key_lifecycle import KeyLifecycleManager, SignerClass
from control_plane.production.migration_engine import (
    MigrationEngine,
    MigrationPlan,
    MigrationStep,
)
from control_plane.production.release_proof import ReleaseProofEngine
from control_plane.production.safe_mode import OperatingPosture, SafeModeGovernor
from control_plane.production.backpressure_queue import (
    BackpressureQueue,
    EffectClass,
    OverloadPolicy,
    QueueItem,
)
from control_plane.runes.runic_router import route_rune


# 1. DG-310: Contract Registry
def test_contract_registry_verification():
    verifier = ContractRegistryVerifier()
    ok, errors = verifier.verify_registry()
    assert ok is True, f"Contract registry verification failed: {errors}"
    schemas = verifier.get_registered_schemas()
    assert len(schemas) > 0
    assert "task/1" in schemas


# 2. DG-320: Configuration Contract
def test_config_contract_validation_success():
    cfg = ConfigContract()
    ok, errors = cfg.validate()
    assert ok is True, f"Config validation failed: {errors}"
    assert cfg.is_reloadable("LOG_LEVEL") is True
    assert cfg.is_reloadable("BIFROST_PORT") is False
    assert len(cfg.compute_checksum()) == 64


def test_config_contract_missing_authority_critical():
    bad_data = {
        "schema_version": "camelot-config/1",
        "config_id": "bad_cfg",
        "entries": {
            "LOG_LEVEL": {"value": "DEBUG", "classification": "RELOADABLE"}
        },
    }
    cfg = ConfigContract(bad_data)
    ok, errors = cfg.validate()
    assert ok is False
    assert any("Missing mandatory AUTHORITY_CRITICAL" in err for err in errors)


def test_config_contract_raw_secret_reference_rejected():
    bad_data = {
        "schema_version": "camelot-config/1",
        "config_id": "leak_cfg",
        "entries": {
            "SENTINEL_LEASE_SIGNER_KEY": {"value": "0x1", "classification": "AUTHORITY_CRITICAL"},
            "AUTHORITY_EPOCH_SIGNER_KEY": {"value": "0x2", "classification": "AUTHORITY_CRITICAL"},
            "ANYA_GATE_VERIFICATION_SECRET": {"value": "0x3", "classification": "AUTHORITY_CRITICAL"},
            "LEAKY_SECRET": {"value": "super_secret_raw_token", "classification": "SECRET_REFERENCE"},
        },
    }
    cfg = ConfigContract(bad_data)
    ok, errors = cfg.validate()
    assert ok is False
    assert any("contains raw value instead of reference" in err for err in errors)


# 3. DG-340: Domain-Restricted Signer Classes & Key Lifecycle
def test_key_lifecycle_domain_separation():
    mgr = KeyLifecycleManager(current_epoch=2)
    mgr.register_key("compiler_key", SignerClass.CONTEXT_COMPILER, "0xCOMPILER_PUB", key_epoch=2)
    mgr.register_key("epoch_key", SignerClass.EPOCH, "0xEPOCH_PUB", key_epoch=2)

    # Compiler key signing context packet -> ALLOWED
    auth_ok, reason = mgr.verify_signing_authorization("compiler_key", "CONTEXT_PACKET")
    assert auth_ok is True

    # Compiler key attempting to sign an authority epoch increment -> PROHIBITED
    auth_fail, reason = mgr.verify_signing_authorization("compiler_key", "AUTHORITY_EPOCH_INCREMENT")
    assert auth_fail is False
    assert "DOMAIN_VIOLATION" in reason

    # Epoch key signing epoch increment -> ALLOWED
    auth_epoch_ok, _ = mgr.verify_signing_authorization("epoch_key", "AUTHORITY_EPOCH_INCREMENT")
    assert auth_epoch_ok is True


def test_key_lifecycle_revocation_and_stale_epoch():
    mgr = KeyLifecycleManager(current_epoch=5)
    mgr.register_key("stale_key", SignerClass.POLICY, "0xPOLICY_PUB", key_epoch=4)

    # Stale epoch rejected
    ok, reason = mgr.verify_signing_authorization("stale_key", "POLICY_DECISION")
    assert ok is False
    assert "stale" in reason

    # Revocation check
    mgr.register_key("active_key", SignerClass.POLICY, "0xPOLICY_PUB", key_epoch=5)
    mgr.revoke_key("active_key", reason="ROTATED")
    ok_rev, reason_rev = mgr.verify_signing_authorization("active_key", "POLICY_DECISION")
    assert ok_rev is False
    assert "REVOKED" in reason_rev


# 4. DG-330: State Migration Engine & Automated Retreat
def test_migration_engine_success():
    engine = MigrationEngine()
    current_state = {"schema": "v1.0", "records": [1, 2, 3]}

    def reader():
        return json.dumps(current_state, sort_keys=True)

    def restorer(snap):
        nonlocal current_state
        current_state = json.loads(snap)

    plan = MigrationPlan(
        plan_id="mig_001",
        target_subsystem="database",
        from_version="v1.0",
        to_version="v2.0",
        precheck_fns=[lambda: len(current_state["records"]) == 3],
        steps=[
            MigrationStep(
                step_id="add_record",
                description="Add record 4",
                action_fn=lambda: current_state["records"].append(4) or True,
            )
        ],
        verification_fns=[lambda: len(current_state["records"]) == 4],
    )

    receipt = engine.execute_migration(plan, reader, restorer)
    assert receipt.status == "PROMOTED"
    assert "PROMOTE" in receipt.stages_completed
    assert len(current_state["records"]) == 4


def test_migration_engine_retreat_on_verification_failure():
    engine = MigrationEngine()
    current_state = {"schema": "v1.0", "records": [1, 2, 3]}

    def reader():
        return json.dumps(current_state, sort_keys=True)

    def restorer(snap):
        nonlocal current_state
        current_state = json.loads(snap)

    plan = MigrationPlan(
        plan_id="mig_fail_verify",
        target_subsystem="database",
        from_version="v1.0",
        to_version="v2.0",
        precheck_fns=[lambda: True],
        steps=[
            MigrationStep(
                step_id="step_dirty",
                description="Dirty state mutation",
                action_fn=lambda: current_state["records"].append(999) or True,
                rollback_fn=lambda: current_state["records"].remove(999) if 999 in current_state["records"] else True,
            )
        ],
        verification_fns=[lambda: False],  # Verification intentionally fails
    )

    receipt = engine.execute_migration(plan, reader, restorer)
    assert receipt.status == "RETREATED"
    assert "RETREAT" in receipt.stages_completed
    assert 999 not in current_state["records"]
    assert len(current_state["records"]) == 3  # Fully restored to snapshot


# 5. DG-350: Release Proof Generation and Verification
def test_release_proof_generation_and_verification():
    key_mgr = KeyLifecycleManager()
    key_mgr.register_key("rel_key", SignerClass.RELEASE, "0xREL_PUB")
    engine = ReleaseProofEngine(key_manager=key_mgr)

    proof = engine.generate_release_proof(
        version="v10001.00",
        source_commit="commit_abc123",
        release_key_id="rel_key",
        min_state_version="v1.0",
    )

    assert proof["schema_version"] == "camelot-release-proof/1"
    assert proof["release"]["version"] == "v10001.00"
    assert len(proof["proof_signature"]) == 64

    ok, errors = engine.verify_release_proof(proof, "v10001.00", current_state_version="v10001.00")
    assert ok is True, f"Release proof verification failed: {errors}"


# 6. DG-390: Universal Safe Mode Governor
def test_safe_mode_transitions_and_operation_filter():
    gov = SafeModeGovernor()
    assert gov.current_posture == OperatingPosture.NORMAL

    # NORMAL allows all
    allowed, _ = gov.check_operation_allowed("SPAWN_BACKGROUND_WORKER")
    assert allowed is True

    # Transition to FROZEN
    gov.transition_to(OperatingPosture.FROZEN, reason="Threat detected", triggered_by="SENTINEL_MONITOR")
    assert gov.current_posture == OperatingPosture.FROZEN

    # In FROZEN: writes denied, reads allowed
    denied, reason = gov.check_operation_allowed("FILE_MUTATION")
    assert denied is False
    assert "AUTHORITY_FROZEN" in reason

    read_ok, _ = gov.check_operation_allowed("READ_CANONICAL_STATE")
    assert read_ok is True
    diag_ok, _ = gov.check_operation_allowed("DIAGNOSTICS")
    assert diag_ok is True

    # Attempting to exit FROZEN to NORMAL without quorum token raises PermissionError
    with pytest.raises(PermissionError):
        gov.transition_to(OperatingPosture.NORMAL, reason="Operator attempt")

    # With Quorum Token, transitions to RECOVERY
    rec = gov.transition_to(
        OperatingPosture.RECOVERY,
        reason="Quorum recovery",
        recovery_quorum_token="QUORUM_ARTHUR_RESTORE",
    )
    assert gov.current_posture == OperatingPosture.RECOVERY


# 7. DG-400: Backpressure Queue & Retry Semantics
def test_backpressure_retry_semantics():
    queue = BackpressureQueue(max_depth=5, max_inflight=2)

    # PURE allows up to 10 retries
    fails = 0
    def failing_pure():
        nonlocal fails
        fails += 1
        if fails < 3:
            raise ValueError("Transient math error")
        return 42

    item = QueueItem(item_id="item_pure", task_name="math", effect_class=EffectClass.PURE, execute_fn=failing_pure)
    queue.enqueue(item)

    # Process turns: retry 1, retry 2, complete on 3
    res1 = queue.process_next()
    assert res1["status"] == "RETRY_QUEUED"
    res2 = queue.process_next()
    assert res2["status"] == "RETRY_QUEUED"
    res3 = queue.process_next()
    assert res3["status"] == "COMPLETED"
    assert res3["result"] == 42


def test_backpressure_irreversible_write_zero_retries():
    queue = BackpressureQueue(max_depth=5, max_inflight=2)

    def failing_write():
        raise RuntimeError("Payment gateway timeout")

    item = QueueItem(item_id="item_payment", task_name="pay", effect_class=EffectClass.IRREVERSIBLE_WRITE, execute_fn=failing_write)
    queue.enqueue(item)

    res = queue.process_next()
    assert res["status"] == "FAILED_TO_DEAD_LETTER"
    assert queue.dead_letter_count == 1


# 8. Runic Router Integration
def test_production_runes():
    res_safe = route_rune("//SAFE_MODE STATUS")
    assert res_safe.metadata["status"] == "OK"

    res_proof = route_rune("//RELEASE_PROOF v10001.00")
    assert res_proof.metadata["status"] == "RELEASE_PROOF_CERTIFIED"

    res_mig = route_rune("//MIGRATION STATUS")
    assert res_mig.metadata["status"] == "MIGRATION_ENGINE_READY"
