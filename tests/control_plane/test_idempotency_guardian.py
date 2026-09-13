# SPDX-License-Identifier: MIT
"""Unit tests for Phase 1B IdempotencyGuardian (Durable WAL & FastMutex)."""
import time
import pytest
from control_plane.dispatch.idempotency_guardian import (
    FastMutexAccelerator,
    IdempotencyConflictError,
    IdempotencyDecision,
    IdempotencyGuardian,
    IdempotencyPayloadMismatchError,
    IdempotencyStatus,
    compute_compound_key,
)


def test_compute_compound_key():
    k1 = compute_compound_key("key_1", "tenant_a", "sha256:1111")
    k2 = compute_compound_key("key_1", "tenant_a", "sha256:1111")
    k3 = compute_compound_key("key_1", "tenant_b", "sha256:1111")
    k4 = compute_compound_key("key_1", "tenant_a", "sha256:2222")

    assert k1 == k2
    assert k1 != k3, "Different tenants must produce distinct compound keys"
    assert k1 != k4, "Different manifests must produce distinct compound keys"
    assert len(k1) == 64


def test_fast_mutex_accelerator():
    mutex = FastMutexAccelerator(default_ttl_sec=0.2)
    tenant = "tenant_test"
    key = "test_key"

    assert mutex.try_acquire(tenant, key) is True
    assert mutex.is_locked(tenant, key) is True
    # Immediate second acquire must fail
    assert mutex.try_acquire(tenant, key) is False

    # Release allows immediate re-acquire
    mutex.release(tenant, key)
    assert mutex.is_locked(tenant, key) is False
    assert mutex.try_acquire(tenant, key) is True

    # TTL expiry allows re-acquire
    time.sleep(0.25)
    assert mutex.is_locked(tenant, key) is False
    assert mutex.try_acquire(tenant, key) is True


def test_idempotency_lifecycle_proceed_commit_replay():
    guardian = IdempotencyGuardian()
    key = "uuid7_001"
    tenant_id = "tenant_alpha"
    manifest_hash = "sha256:abc123"
    correlation_id = "cor_999"

    # 1. First ingress: PROCEED
    decision, rec = guardian.acquire_or_replay(key, tenant_id, manifest_hash, correlation_id)
    assert decision == IdempotencyDecision.PROCEED
    assert rec is not None
    assert rec.status == IdempotencyStatus.IN_FLIGHT

    # 2. Duplicate while in flight: CONFLICT with Retry-After
    with pytest.raises(IdempotencyConflictError) as exc_info:
        guardian.acquire_or_replay(key, tenant_id, manifest_hash, correlation_id)
    assert exc_info.value.key == key
    assert exc_info.value.tenant_id == tenant_id
    assert exc_info.value.status_code == 409
    assert exc_info.value.retry_after_sec >= 1

    # 3. Execution succeeds: commit receipt
    committed = guardian.commit(
        key,
        tenant_id,
        manifest_hash,
        receipt_ref="rcp_001_sealed",
        response_body={"outcome": "SUCCESS", "amount": 100},
    )
    assert committed.status == IdempotencyStatus.COMPLETED
    assert committed.receipt_ref == "rcp_001_sealed"
    assert "amount" in committed.response_body

    # 4. Duplicate after commit: REPLAY
    decision, replay_rec = guardian.acquire_or_replay(key, tenant_id, manifest_hash, "cor_new")
    assert decision == IdempotencyDecision.REPLAY
    assert replay_rec.receipt_ref == "rcp_001_sealed"
    assert replay_rec.response_body == committed.response_body


def test_payload_mismatch_triggers_422():
    """Deviation in payload under the same idempotency key triggers IDEMPOTENCY_PAYLOAD_MISMATCH (HTTP 422)."""
    guardian = IdempotencyGuardian()
    key = "key_fixed_001"
    tenant_id = "tenant_mismatch"
    manifest_original = "sha256:" + "1" * 64
    manifest_deviated = "sha256:" + "2" * 64

    # First ingress registers manifest_original
    decision, _ = guardian.acquire_or_replay(key, tenant_id, manifest_original, "cor_orig")
    assert decision == IdempotencyDecision.PROCEED

    # Second ingress with different manifest under SAME key must raise 422
    with pytest.raises(IdempotencyPayloadMismatchError) as exc_info:
        guardian.acquire_or_replay(key, tenant_id, manifest_deviated, "cor_hacker")

    assert exc_info.value.status_code == 422
    assert exc_info.value.error_code == "IDEMPOTENCY_PAYLOAD_MISMATCH"
    assert exc_info.value.existing_hash == manifest_original
    assert exc_info.value.new_hash == manifest_deviated


def test_cross_tenant_idempotency_isolation():
    """Tenant A and Tenant B using the same client key must not conflict."""
    guardian = IdempotencyGuardian()
    shared_key = "client_txn_007"
    manifest_hash = "sha256:manifest_common"

    dec_a, rec_a = guardian.acquire_or_replay(shared_key, "tenant_a", manifest_hash, "cor_a")
    dec_b, rec_b = guardian.acquire_or_replay(shared_key, "tenant_b", manifest_hash, "cor_b")

    assert dec_a == IdempotencyDecision.PROCEED
    assert dec_b == IdempotencyDecision.PROCEED
    assert rec_a.tenant_id == "tenant_a"
    assert rec_b.tenant_id == "tenant_b"
    assert rec_a.compound_key != rec_b.compound_key

    # Commit Tenant A
    guardian.commit(shared_key, "tenant_a", manifest_hash, "rcp_a")

    # Tenant A replays
    dec_a_re, rec_a_re = guardian.acquire_or_replay(shared_key, "tenant_a", manifest_hash, "cor_a2")
    assert dec_a_re == IdempotencyDecision.REPLAY
    assert rec_a_re.receipt_ref == "rcp_a"

    # Tenant B is still IN_FLIGHT and raises conflict for Tenant B
    with pytest.raises(IdempotencyConflictError):
        guardian.acquire_or_replay(shared_key, "tenant_b", manifest_hash, "cor_b2")


def test_rejection_allows_retry():
    guardian = IdempotencyGuardian()
    key = "uuid7_fail"
    tenant_id = "tenant_gamma"
    manifest_hash = "sha256:bad_plan"

    dec, _ = guardian.acquire_or_replay(key, tenant_id, manifest_hash, "cor_fail")
    assert dec == IdempotencyDecision.PROCEED

    # Reject
    guardian.reject(key, tenant_id, manifest_hash, reason="Policy check failed")

    # Retry permitted
    dec2, rec2 = guardian.acquire_or_replay(key, tenant_id, manifest_hash, "cor_retry")
    assert dec2 == IdempotencyDecision.PROCEED
    assert rec2.status == IdempotencyStatus.IN_FLIGHT


def test_expiry_purges():
    guardian = IdempotencyGuardian()
    key = "uuid7_exp"
    tenant_id = "tenant_delta"
    manifest_hash = "sha256:manifest_exp"

    # Register with 0.1 sec TTL
    guardian.acquire_or_replay(key, tenant_id, manifest_hash, "cor_exp", ttl_seconds=0.1)
    time.sleep(0.15)

    # After expiry, purging removes it and next acquire succeeds
    purged = guardian.purge_expired()
    assert purged >= 1

    dec, rec = guardian.acquire_or_replay(key, tenant_id, manifest_hash, "cor_reacquire")
    assert dec == IdempotencyDecision.PROCEED
