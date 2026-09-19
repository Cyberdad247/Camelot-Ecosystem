# SPDX-License-Identifier: MIT
"""Unit tests for VPS Fallback Governing Law under 4GB scarcity constraint."""

import time
from pathlib import Path

import pytest

from control_plane.dispatch.vps_fallback_governing_law import (
    BoundedEdgeOutbox,
    FallbackState,
    MAX_OUTBOX_ENTRIES,
    MAX_RSS_BYTES,
    VPSFallbackGovernor,
)


@pytest.fixture
def temp_db(tmp_path):
    return tmp_path / "edge_outbox.db"


def test_outbox_enqueue_and_eviction_cap(temp_db):
    outbox = BoundedEdgeOutbox(temp_db)
    assert outbox.pending_count() == 0

    # Enqueue a batch
    for i in range(10):
        outbox.enqueue("collect_telemetry", {"index": i}, f"env_{i}")
    assert outbox.pending_count() == 10

    rows = outbox.fetch_pending(limit=5)
    assert len(rows) == 5
    assert rows[0][1] == "collect_telemetry"

    # Mark delivered
    outbox.mark_delivered([rows[0][0]])
    assert outbox.pending_count() == 9


def test_governor_evaluates_memory_scarcity_boundary(temp_db):
    gov = VPSFallbackGovernor(temp_db)

    # Exceeding 256MB RSS
    res = gov.evaluate_action(
        "collect_telemetry",
        vps_reachable=True,
        current_rss_bytes=MAX_RSS_BYTES + 1024,
    )
    assert not res.allowed
    assert res.state == FallbackState.RESTRICTED_SAFE
    assert res.reason == "memory-rss-limit-exceeded"


def test_governor_evaluates_offline_forbidden_action(temp_db):
    gov = VPSFallbackGovernor(temp_db)

    res = gov.evaluate_action(
        "vfs_mutation",
        vps_reachable=False,
        current_rss_bytes=50 * 1024 * 1024,
    )
    assert not res.allowed
    assert res.reason == "forbidden-action-during-offline-fallback"


def test_governor_evaluates_valid_offline_fallback(temp_db):
    gov = VPSFallbackGovernor(temp_db)
    now = int(time.time())

    res = gov.evaluate_action(
        "collect_telemetry",
        vps_reachable=False,
        current_rss_bytes=50 * 1024 * 1024,
        snapshot_issued_at=now - 300,
        now=now,
    )
    assert res.allowed
    assert res.state == FallbackState.OFFLINE_AUTONOMOUS
    assert res.reason == "policy-compliant"


def test_governor_restricts_when_snapshot_expired(temp_db):
    gov = VPSFallbackGovernor(temp_db)
    now = int(time.time())

    # Snapshot 4000s old (>3600s TTL)
    res = gov.evaluate_action(
        "collect_telemetry",
        vps_reachable=False,
        current_rss_bytes=50 * 1024 * 1024,
        snapshot_issued_at=now - 4000,
        now=now,
    )
    assert not res.allowed
    assert res.state == FallbackState.RESTRICTED_SAFE
    assert res.reason == "policy-snapshot-expired-fallback-restricted"

    # But health_probe is still allowed in restricted safe mode
    res_health = gov.evaluate_action(
        "health_probe",
        vps_reachable=False,
        current_rss_bytes=50 * 1024 * 1024,
        snapshot_issued_at=now - 4000,
        now=now,
    )
    assert res_health.allowed
