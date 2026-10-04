# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Unit tests for Excalibur Mobile Dispatcher and Real-World Operational Modes
"""

import pytest
from control_plane.dispatch.excalibur_mobile_dispatcher import (
    ExcaliburMobileDispatcher,
    MobileTaskRequest,
    OperationalMode,
    NODE_RAM_LIMIT_MB,
    TARGET_DEVICE_ID,
    TARGET_TAILSCALE_IP,
)


@pytest.fixture
def dispatcher() -> ExcaliburMobileDispatcher:
    return ExcaliburMobileDispatcher()


def test_dispatcher_mode_transitions(dispatcher: ExcaliburMobileDispatcher) -> None:
    assert dispatcher.current_mode == OperationalMode.WORKSTATION

    dispatcher.set_mode(OperationalMode.AIR_GAPPED_FIELD)
    assert dispatcher.current_mode == OperationalMode.AIR_GAPPED_FIELD

    dispatcher.set_mode(OperationalMode.FOUNDRY_BACKGROUND)
    assert dispatcher.current_mode == OperationalMode.FOUNDRY_BACKGROUND

    dispatcher.set_mode(OperationalMode.HARDWARE_VAULT)
    assert dispatcher.current_mode == OperationalMode.HARDWARE_VAULT


def test_dispatch_air_gapped_task(dispatcher: ExcaliburMobileDispatcher) -> None:
    req = MobileTaskRequest(
        task_id="TEST-AIRGAP-1",
        action="INCIDENT_TRIAGE",
        target_module="03_VAULT/runtime_state",
        payload={"depth": 2},
        mode=OperationalMode.AIR_GAPPED_FIELD,
    )
    res = dispatcher.dispatch_task(req)
    assert res.status == "SUCCESS"
    assert res.execution_node == TARGET_DEVICE_ID
    assert res.results["air_gapped"] is True
    assert res.results["cloud_egress_blocked"] is True
    assert res.ram_usage_mb <= NODE_RAM_LIMIT_MB
    assert len(res.envelope_signature) == 64


def test_dispatch_foundry_task(dispatcher: ExcaliburMobileDispatcher) -> None:
    req = MobileTaskRequest(
        task_id="TEST-FOUNDRY-1",
        action="RUN_EDGE_TESTS",
        target_module="tests",
        payload={"suite": "smoke"},
        mode=OperationalMode.FOUNDRY_BACKGROUND,
    )
    res = dispatcher.dispatch_task(req)
    assert res.status == "SUCCESS"
    assert res.results["foundry_lane"] == "BACKGROUND_TEST_CYCLE"
    assert res.results["tests_passed"] == 48


def test_dispatch_workstation_task(dispatcher: ExcaliburMobileDispatcher) -> None:
    req = MobileTaskRequest(
        task_id="TEST-WS-1",
        action="INIT_HYPRLAND",
        target_module="Termux:X11",
        payload={"display": ":0"},
        mode=OperationalMode.WORKSTATION,
    )
    res = dispatcher.dispatch_task(req)
    assert res.status == "SUCCESS"
    assert res.results["display_refresh"] == "120Hz"
    assert "Turnip/KGSL" in res.results["compositor"]


def test_mobile_cockpit_summary(dispatcher: ExcaliburMobileDispatcher) -> None:
    summary = dispatcher.get_mobile_cockpit_summary()
    assert TARGET_DEVICE_ID in summary["cockpit"].lower() or "s26 ultra" in summary["cockpit"].lower()
    assert summary["preflight_doctor"] == "PASS"
    assert summary["refresh_hz"] == 120
    assert summary["ram_limit_mb"] == NODE_RAM_LIMIT_MB
    assert summary["keypass"]["tier"] == "ARCH"
    assert summary["keypass"]["spark_id"] == "0x56820318BB91451FAAC44B46424898CF"
