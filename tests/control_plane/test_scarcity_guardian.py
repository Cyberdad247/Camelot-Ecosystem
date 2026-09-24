# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import os
import pytest
from pathlib import Path
from control_plane.infra.scarcity_guardian import (
    DockerFootprintViolation,
    PSIReading,
    ScarcityGuardian,
    parse_psi_pressure_data,
    read_system_psi,
    verify_zero_docker_compliance,
)


def test_parse_psi_pressure_data():
    sample_psi = """some avg10=28.45 avg60=14.12 avg300=8.03 total=1289452
full avg10=12.20 avg60=6.05 avg300=2.11 total=482103
"""
    reading = parse_psi_pressure_data(sample_psi)
    assert reading.some_avg10 == 28.45
    assert reading.some_avg60 == 14.12
    assert reading.some_avg300 == 8.03
    assert reading.some_total_us == 1289452
    assert reading.full_avg10 == 12.20
    assert reading.full_avg60 == 6.05
    assert reading.full_avg300 == 2.11
    assert reading.full_total_us == 482103


def test_read_system_psi_from_file(tmp_path: Path):
    psi_file = tmp_path / "memory_pressure"
    psi_file.write_text(
        "some avg10=35.00 avg60=20.00 avg300=10.00 total=5000\nfull avg10=15.00 avg60=8.00 avg300=4.00 total=2000\n",
        encoding="utf-8",
    )
    reading = read_system_psi(psi_file)
    assert reading is not None
    assert reading.some_avg10 == 35.00


def test_verify_zero_docker_compliance_clean():
    res = verify_zero_docker_compliance(check_docker_socket=False)
    assert res["zero_docker_verified"] is True
    assert res["runtime_substrate"] == "BARE_METAL_SYSTEMD_WASM"


def test_verify_zero_docker_compliance_rejects_socket(tmp_path: Path):
    fake_docker_sock = tmp_path / "docker.sock"
    fake_docker_sock.touch()
    with pytest.raises(DockerFootprintViolation, match="Active Docker socket detected"):
        verify_zero_docker_compliance(check_docker_socket=True, socket_path_override=fake_docker_sock)


def test_verify_zero_docker_compliance_rejects_env():
    old_env = os.environ.get("DOCKER_HOST")
    try:
        os.environ["DOCKER_HOST"] = "tcp://127.0.0.1:2375"
        with pytest.raises(DockerFootprintViolation, match="DOCKER_HOST environment variable active"):
            verify_zero_docker_compliance(check_docker_socket=False)
    finally:
        if old_env is not None:
            os.environ["DOCKER_HOST"] = old_env
        else:
            os.environ.pop("DOCKER_HOST", None)


def test_vps_hub_hard_cap_and_psi_pressure():
    guardian = ScarcityGuardian()
    
    # 1. Normal VPS state
    profile_normal = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=4000.0)
    assert profile_normal.hard_cap_mb == 7372.8
    assert profile_normal.pressure_percentage < 60.0
    assert profile_normal.is_critical is False

    # 2. Critical via memory usage (>= 90%)
    profile_high_ram = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=7000.0)
    assert profile_high_ram.pressure_percentage >= 90.0
    assert profile_high_ram.is_critical is True

    # 3. Critical via PSI stall even if RAM usage is below 90%
    psi_stall = PSIReading(some_avg10=32.5)  # threshold is 25.0%
    profile_psi_critical = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=5500.0, psi=psi_stall)
    assert profile_psi_critical.is_critical is True


def test_s26_ultra_audio_slice_protection():
    guardian = ScarcityGuardian()
    # 350 MB active slice on S26 Ultra
    profile_s26 = guardian.evaluate_node_pressure("S26_EDGE_ORB", current_used_mb=175.0)
    assert profile_s26.hard_cap_mb == 350.0
    assert profile_s26.pressure_percentage == 50.0

    profile_s26_spike = guardian.evaluate_node_pressure("S26_EDGE_ORB", current_used_mb=320.0)
    assert profile_s26_spike.pressure_percentage >= 90.0
    assert profile_s26_spike.is_critical is True


def test_scarcity_enforcement_with_signal_emitter_and_hysteresis():
    guardian = ScarcityGuardian()
    emitted_signals: list[tuple[str, str]] = []

    def mock_emitter(signal: str, pid: str):
        emitted_signals.append((signal, pid))

    pills = [
        {"pill_id": "audio_sentinel_orb", "priority": "HIGH"},
        {"pill_id": "wasm_scraper_worker", "priority": "LOW"},
        {"pill_id": "graph_sync_drone", "priority": "MEDIUM"},
    ]

    # 1. Trigger throttle under pressure
    crit_profile = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=7100.0)
    res_crit = guardian.enforce_scarcity_policy(crit_profile, pills, signal_emitter=mock_emitter)
    assert res_crit["status"] == "THROTTLED"
    assert "audio_sentinel_orb" not in guardian.throttled_pills
    assert "wasm_scraper_worker" in guardian.throttled_pills
    assert "graph_sync_drone" in guardian.throttled_pills
    assert ("SIGSTOP", "wasm_scraper_worker") in emitted_signals
    assert ("SIGSTOP", "graph_sync_drone") in emitted_signals
    assert ("SIGSTOP", "audio_sentinel_orb") not in emitted_signals

    # 2. Hysteresis test: Memory drops to 85% (below 90%, but above recovery 80%)
    emitted_signals.clear()
    intermediate_profile = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=6270.0)  # ~85%
    assert 80.0 <= intermediate_profile.pressure_percentage < 90.0
    res_inter = guardian.enforce_scarcity_policy(intermediate_profile, pills, signal_emitter=mock_emitter)
    # Must stay THROTTLED due to hysteresis
    assert res_inter["status"] == "THROTTLED"
    assert len(guardian.throttled_pills) == 2
    assert len(emitted_signals) == 0

    # 3. Recovery test: Memory drops to 70% (below recovery threshold 80%)
    recovered_profile = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=5000.0)
    res_rec = guardian.enforce_scarcity_policy(recovered_profile, pills, signal_emitter=mock_emitter)
    assert res_rec["status"] == "CONVERGED"
    assert len(guardian.throttled_pills) == 0
    assert ("SIGCONT", "wasm_scraper_worker") in emitted_signals
    assert ("SIGCONT", "graph_sync_drone") in emitted_signals


def test_emit_scarcity_telemetry():
    guardian = ScarcityGuardian()
    profile = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=4500.0)
    policy_res = {"status": "CONVERGED", "throttled_count": 0}
    
    envelope = guardian.emit_scarcity_telemetry(profile, policy_res)
    assert envelope["schema_version"] == "operator-evidence/1"
    assert envelope["kind"] == "infra.scarcity.telemetry"
    assert envelope["actor"]["id"] == "scarcity_guardian"
    assert envelope["integrity"] == "verified"
    assert envelope["receipt_ref"].startswith("receipt://infra/scarcity/vps_hub/")
    assert envelope["payload_redacted"]["zero_docker_verified"] is True
    assert envelope["payload_redacted"]["hard_cap_mb"] == 7372.8
