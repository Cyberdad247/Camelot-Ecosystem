# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Unit tests for Dynamic Forefront Topology & VPS Fabric Toggle

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from control_plane.dispatch.vps_fabric_toggle import (
    DynamicTopologyManager,
    TopologyMode,
)


@pytest.fixture
def temp_manager(tmp_path: Path):
    state_file = tmp_path / "vps_fabric_state.json"
    return DynamicTopologyManager(state_file=state_file)


def test_initial_state(temp_manager: DynamicTopologyManager):
    status = temp_manager.get_status()
    assert status["active_mode"] == TopologyMode.VPS_FOREFRONT.value
    assert status["forefront_node"] == "vps_hub_kvm563"
    assert status["local_fallback_engaged"] is False
    assert status["bifrost_bridge_active"] is True


def test_set_topology_mode(temp_manager: DynamicTopologyManager):
    temp_manager.set_topology_mode(TopologyMode.LOCAL_FOREFRONT)
    status = temp_manager.get_status()
    assert status["active_mode"] == TopologyMode.LOCAL_FOREFRONT.value
    assert status["forefront_node"] == "cybertronia"
    assert status["fabric_nodes"]["cybertronia"]["role"] == "SOVEREIGN_FOREFRONT_HOST"
    assert status["fabric_nodes"]["vps_hub_kvm563"]["role"] == "REMOTE_RELAY_BRIDGE"

    temp_manager.set_topology_mode(TopologyMode.HYBRID_FEDERATED)
    assert temp_manager.get_status()["active_mode"] == TopologyMode.HYBRID_FEDERATED.value


def test_trigger_local_fallback_and_restore(temp_manager: DynamicTopologyManager):
    fb = temp_manager.trigger_local_fallback(reason="NETWORK_SEVERED")
    assert fb["status"] == "LOCAL_FALLBACK_ENGAGED"
    assert fb["forefront_node"] == "cybertronia"
    assert temp_manager.config.local_fallback_engaged is True
    assert temp_manager.config.bifrost_bridge_active is False

    restored = temp_manager.restore_vps_forefront()
    assert restored["active_mode"] == TopologyMode.VPS_FOREFRONT.value
    assert temp_manager.config.local_fallback_engaged is False
    assert temp_manager.config.bifrost_bridge_active is True


def test_route_task_to_fabric(temp_manager: DynamicTopologyManager):
    route = temp_manager.route_task_to_fabric("BUILD_ARTIFACT", {"target": "wasm"})
    assert route["orchestrator"] == "vps_hub_kvm563"
    assert route["execution_fabric_target"] == "cybertronia"
    assert route["bifrost_bridge_active"] is True


def test_poll_and_reconcile_triggers_fallback_on_consecutive_failures(temp_manager: DynamicTopologyManager):
    with patch.object(temp_manager, "check_vps_reachability") as mock_probe:
        mock_probe.return_value = {
            "reachable": False,
            "connected_endpoint": None,
            "latencies_ms": {},
            "timestamp": "2026-10-18T20:00:00Z",
        }

        # Failure 1
        res1, f1 = temp_manager.poll_and_reconcile(consecutive_failures=0, max_failures=3)
        assert res1["action"] == "HEARTBEAT_MISSED"
        assert f1 == 1
        assert temp_manager.config.local_fallback_engaged is False

        # Failure 2
        res2, f2 = temp_manager.poll_and_reconcile(consecutive_failures=f1, max_failures=3)
        assert res2["action"] == "HEARTBEAT_MISSED"
        assert f2 == 2
        assert temp_manager.config.local_fallback_engaged is False

        # Failure 3 -> triggers fallback
        res3, f3 = temp_manager.poll_and_reconcile(consecutive_failures=f2, max_failures=3)
        assert res3["action"] == "AUTO_TRIGGERED_LOCAL_FALLBACK"
        assert f3 == 3
        assert temp_manager.config.local_fallback_engaged is True
        assert temp_manager.config.active_mode == TopologyMode.LOCAL_FOREFRONT


def test_poll_and_reconcile_auto_restores_on_recovery(temp_manager: DynamicTopologyManager):
    # Start in fallback
    temp_manager.trigger_local_fallback(reason="SIMULATED_OUTAGE")
    assert temp_manager.config.local_fallback_engaged is True

    with patch.object(temp_manager, "check_vps_reachability") as mock_probe:
        mock_probe.return_value = {
            "reachable": True,
            "connected_endpoint": "100.110.180.18:3001",
            "latencies_ms": {"100.110.180.18:3001": 15.2},
            "timestamp": "2026-10-18T20:01:00Z",
        }

        res, failures = temp_manager.poll_and_reconcile(consecutive_failures=3, max_failures=3)
        assert res["action"] == "AUTO_RESTORED_VPS_FOREFRONT"
        assert failures == 0
        assert temp_manager.config.local_fallback_engaged is False
        assert temp_manager.config.active_mode == TopologyMode.VPS_FOREFRONT
