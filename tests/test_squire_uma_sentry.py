# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Unit tests for Squire UMA_Sentry cross-node memory balancing and task offloading."""

from __future__ import annotations

import pytest
from squires.uma_sentry import SquireUMASentry, FleetMemoryBalance, OffloadPlan


def test_uma_sentry_fleet_memory_balance():
    sentry = SquireUMASentry()
    balance = sentry.get_fleet_memory_balance()
    assert isinstance(balance, FleetMemoryBalance)
    assert balance.cybertronia_total_mb > 0
    assert balance.excalibur_total_mb > 0
    assert balance.excalibur_free_mb > 0
    assert balance.vps_free_mb > 0
    assert isinstance(balance.to_dict(), dict)


def test_uma_sentry_plan_offload_low_memory():
    # When threshold is 100%, small task runs locally
    sentry = SquireUMASentry(pressure_threshold_pct=100.0)
    plan = sentry.plan_offload(
        task_id="task-test-01",
        action="lint",
        target_module="test_mod",
        payload={"code": "print('hello')"},
        estimated_ram_mb=100.0,
    )
    assert isinstance(plan, OffloadPlan)
    assert plan.target_node == "CYBERTRONIA_LOCAL"
    assert plan.approved is False
    assert plan.compression_enabled is True


def test_uma_sentry_plan_offload_high_memory():
    # When task is heavy (>= 750 MB) or pressure is low, offload is approved
    sentry = SquireUMASentry(pressure_threshold_pct=10.0)
    plan = sentry.plan_offload(
        task_id="task-test-02",
        action="deep_ast_scan",
        target_module="full_repo",
        payload={"repo": "CAMELOT_OS", "depth": 10},
        estimated_ram_mb=1000.0,
    )
    assert isinstance(plan, OffloadPlan)
    assert plan.target_node == "EXCALIBUR_S26_ULTRA"
    assert plan.target_mode == "FOUNDRY_BACKGROUND"
    assert plan.approved is True
    assert "payload_compression" in plan.metrics


def test_uma_sentry_dispatch_offload_local():
    sentry = SquireUMASentry(pressure_threshold_pct=100.0)
    res = sentry.dispatch_offload(
        task_id="task-test-03",
        action="check",
        target_module="quick",
        payload={"key": "val"},
        estimated_ram_mb=50.0,
    )
    assert res["status"] == "LOCAL_EXECUTION"
    assert res["execution_node"] == "CYBERTRONIA_LOCAL"
