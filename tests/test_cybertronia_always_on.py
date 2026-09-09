# SPDX-License-Identifier: MIT
"""tests/test_cybertronia_always_on.py

Unit and regression tests for Cybertronia Always-On Engine.
Verifies daemon mesh definitions, telemetry persistence, memory guard, and socket probers.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from control_plane.infra.cybertronia_always_on import (
    CybertroniaSupervisor,
    DaemonSpec,
    get_memory_info,
    get_status_overview,
    probe_socket,
)


def test_daemon_specs_contain_core_mesh(tmp_path: Path):
    sup = CybertroniaSupervisor(root=tmp_path)
    specs = sup.get_daemon_specs()
    names = {s.name for s in specs}
    ports = {s.port for s in specs}

    assert "go_router" in names
    assert "bifrost_sidecar" in names
    assert "cognitive_service" in names
    assert "opencodex" in names
    assert "omnivoice" in names
    assert "kitten_tts" in names

    assert 8077 in ports
    assert 8011 in ports
    assert 8092 in ports
    assert 10100 in ports
    assert 3002 in ports
    assert 8300 in ports


def test_memory_info_structure():
    mem = get_memory_info()
    assert isinstance(mem, dict)
    assert "load_pct" in mem
    assert "avail_phys_mb" in mem
    assert "total_phys_mb" in mem
    assert "pressure_alarm" in mem
    assert isinstance(mem["pressure_alarm"], bool)


def test_probe_socket_closed_port():
    # An improbable high ephemeral port should return False
    assert probe_socket("127.0.0.1", 59999, timeout=0.1) is False


def test_emit_telemetry_atomic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_file = tmp_path / "runtime_state" / "cybertronia_always_on.json"
    monkeypatch.setattr("control_plane.infra.cybertronia_always_on.VAULT_STATE", state_file)

    sup = CybertroniaSupervisor(root=tmp_path)
    mock_status = [
        {"name": "go_router", "port": 8077, "live": True, "proc_alive": True, "pid": 1234},
        {"name": "bifrost_sidecar", "port": 8011, "live": True, "proc_alive": True, "pid": 5678},
    ]

    sup.emit_telemetry(mock_status)

    assert state_file.exists()
    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert data["node"] == "cybertronia"
    assert data["tailscale_ip"] == "100.118.224.52"
    assert data["mode"] == "ALWAYS_ON_MASTER"
    assert data["status"] == "ONLINE"
    assert data["healthy_daemons"] == "2/2"
    assert len(data["daemons"]) == 2


def test_supervisor_tick_with_mocked_sockets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    state_file = tmp_path / "runtime_state" / "cybertronia_always_on.json"
    monkeypatch.setattr("control_plane.infra.cybertronia_always_on.VAULT_STATE", state_file)

    sup = CybertroniaSupervisor(root=tmp_path)

    with patch("control_plane.infra.cybertronia_always_on.probe_socket", return_value=True):
        res = sup.run_supervisor_tick()
        assert len(res) == 6
        assert all(r["live"] is True for r in res)

    assert state_file.exists()
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    assert payload["healthy_daemons"] == "6/6"
