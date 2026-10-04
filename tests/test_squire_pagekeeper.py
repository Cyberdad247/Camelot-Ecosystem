# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for Squire PageKeeper memory governance and working set trimming."""

from __future__ import annotations

import os
import pytest
from squires.pagekeeper import SquirePageKeeper, MemoryAuditStatus, NODE_MAX_RAM_MB


def test_pagekeeper_system_memory():
    keeper = SquirePageKeeper()
    total_mb, free_mb, used_mb, pct = keeper.get_system_memory()
    assert total_mb > 0
    assert free_mb > 0
    assert used_mb >= 0
    assert 0.0 <= pct <= 100.0


def test_pagekeeper_process_memory():
    keeper = SquirePageKeeper()
    proc_mb = keeper.get_process_memory()
    assert proc_mb > 0.0
    # Process memory should conform to the 4GB node ceiling under test
    assert proc_mb < NODE_MAX_RAM_MB


def test_pagekeeper_audit():
    keeper = SquirePageKeeper(node_ceiling_mb=4096.0, pressure_threshold_pct=95.0)
    audit = keeper.audit()
    assert isinstance(audit, MemoryAuditStatus)
    assert audit.total_physical_mb > 0
    assert audit.node_compliant is True
    assert isinstance(audit.to_dict(), dict)
    assert "timestamp" in audit.to_dict()


def test_pagekeeper_trim_self():
    keeper = SquirePageKeeper()
    reclaimed = keeper.trim_self()
    assert isinstance(reclaimed, float)
    assert reclaimed >= 0.0


def test_pagekeeper_govern_cycle():
    keeper = SquirePageKeeper(pressure_threshold_pct=99.0)
    # Govern with force_trim=False on normal system shouldn't force trim unless pressured
    status = keeper.govern(force_trim=False)
    assert isinstance(status, MemoryAuditStatus)
    assert status.action_taken in ("NO_ACTION_REQUIRED", status.action_taken)

    # Govern with force_trim=True should execute trim
    forced_status = keeper.govern(force_trim=True)
    assert "TRIM_EXECUTED" in forced_status.action_taken
