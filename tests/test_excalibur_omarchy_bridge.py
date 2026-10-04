# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Tests for Excalibur Omarchy Mobile Bridge & Governance Invariants
"""

import pytest
from control_plane.dispatch.excalibur_omarchy_bridge import (
    ExcaliburOmarchyBridge,
    NODE_RAM_LIMIT_MB,
    TARGET_DEVICE_ID,
    TARGET_GPU,
    TARGET_TAILSCALE_IP,
)
from control_plane.security.warp_gate import AlexandriaKeypassVault, WarpGateCryptographicSwitch


@pytest.fixture
def bridge() -> ExcaliburOmarchyBridge:
    return ExcaliburOmarchyBridge()


def test_bridge_hardware_profile(bridge: ExcaliburOmarchyBridge) -> None:
    assert bridge.profile.device_id == TARGET_DEVICE_ID
    assert bridge.profile.tailscale_ip == TARGET_TAILSCALE_IP
    assert TARGET_GPU in bridge.profile.gpu
    assert bridge.profile.ram_limit_mb == NODE_RAM_LIMIT_MB
    assert bridge.profile.ram_limit_mb <= 4096  # Global Law 03


def test_bridge_keypass_generation(bridge: ExcaliburOmarchyBridge) -> None:
    kp = bridge.keypass
    assert kp.knight_id == "EXCALIBUR_MOBILE"
    assert kp.tier == "ARCH"
    assert kp.expires_at == "FOREVER"
    assert kp.status == "ACTIVE"
    assert kp.spark_id == "0x56820318BB91451FAAC44B46424898CF"


def test_bridge_doctor_pass(bridge: ExcaliburOmarchyBridge) -> None:
    doc = bridge.run_doctor()
    assert doc.overall_status == "PASS"
    assert doc.checks["cpu_architecture"]["status"] == "PASS"
    assert doc.checks["adreno_kgsl_vulkan"]["status"] == "PASS"
    assert doc.checks["phantom_process_monitor"]["status"] == "PASS"
    assert doc.checks["ram_governance_law_03"]["status"] == "PASS"
    assert doc.checks["warp_gate_attestation_law_04"]["status"] == "PASS"
    assert len(doc.remediation) == 0


def test_bridge_doctor_ram_ceiling_breach(bridge: ExcaliburOmarchyBridge) -> None:
    doc = bridge.run_doctor({"current_ram_mb": 4500.0})
    assert doc.overall_status == "FAIL"
    assert doc.checks["ram_governance_law_03"]["status"] == "FAIL"
    assert any("mobile node boundary" in r for r in doc.remediation)


def test_bridge_doctor_phantom_process_failure(bridge: ExcaliburOmarchyBridge) -> None:
    doc = bridge.run_doctor({"phantom_processes_disabled": False})
    assert doc.overall_status == "FAIL"
    assert doc.checks["phantom_process_monitor"]["status"] == "FAIL"
    assert any("child process" in r.lower() for r in doc.remediation)


def test_bridge_doctor_unsupported_arch(bridge: ExcaliburOmarchyBridge) -> None:
    doc = bridge.run_doctor({"arch": "x86_64"})
    assert doc.overall_status == "FAIL"
    assert doc.checks["cpu_architecture"]["status"] == "FAIL"


def test_telemetry_envelope_warp_gate_transit(bridge: ExcaliburOmarchyBridge) -> None:
    sample_telemetry = {"fps": 120, "refresh_hz": 120, "gpu_load_pct": 28.5}
    envelope = bridge.create_mobile_telemetry_envelope(sample_telemetry)
    assert envelope.action == "EXCALIBUR_TELEMETRY_INGRESS"
    assert envelope.payload["mobile_node"] == TARGET_DEVICE_ID
    assert envelope.payload["telemetry"]["fps"] == 120

    valid, reason, payload = bridge.switch.verify_and_log_transit(
        envelope, client_addr=TARGET_TAILSCALE_IP
    )
    assert valid is True
    assert reason == "AUTHORIZED"
    assert payload is not None
    assert payload["mobile_node"] == TARGET_DEVICE_ID


def test_bridge_status_shape(bridge: ExcaliburOmarchyBridge) -> None:
    st = bridge.get_status()
    assert st["component"] == "ExcaliburOmarchyBridge"
    assert st["target"]["device_id"] == TARGET_DEVICE_ID
    assert st["governance"]["global_law_03_ram_ceiling_mb"] == 3584
    assert st["governance"]["global_law_04_warp_gate_attestation"] == "ENFORCED"
