# SPDX-License-Identifier: MIT
"""Failing-first test for Rotel VPS mesh forwarder (Task 1)."""

from unittest.mock import patch, MagicMock
from control_plane.infra.rotel_vps_forwarder import RotelVPSForwarder
from control_plane.infra.mesh_topology import HUB_TAILSCALE_IP


def test_rotel_forwarder_init_defaults():
    forwarder = RotelVPSForwarder()
    assert forwarder.hub_ip == HUB_TAILSCALE_IP
    assert forwarder.port == 8095
    assert forwarder.endpoint == f"http://{HUB_TAILSCALE_IP}:8095/telemetry/event"


def test_rotel_forward_trace_success():
    forwarder = RotelVPSForwarder()
    sample_trace = {
        "component": "soul_router",
        "level": "INFO",
        "message": "Routing intent to SIR_BORIS",
        "metadata": {"weight": 0.85, "knight": "sir_boris"}
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ACK", "received_at": 1789619000}

    with patch("requests.post", return_value=mock_resp) as mock_post:
        result = forwarder.forward_trace(sample_trace)
        assert result["success"] is True
        assert result["response"]["status"] == "ACK"
        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        assert call_args[0] == f"http://{HUB_TAILSCALE_IP}:8095/telemetry/event"
        assert call_kwargs["json"]["component"] == "soul_router"


def test_rotel_forward_trace_network_timeout():
    forwarder = RotelVPSForwarder()
    sample_trace = {"component": "kernel", "level": "WARN", "message": "Degraded"}
    with patch("requests.post", side_effect=TimeoutError("Connection timed out")):
        result = forwarder.forward_trace(sample_trace)
        assert result["success"] is False
        assert ("timeout" in result["error"].lower() or "timed out" in result["error"].lower())
