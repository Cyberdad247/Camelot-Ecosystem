# SPDX-License-Identifier: MIT
"""Failing-first test for Kinetic VPS Sentinel (Task 4)."""

from unittest.mock import patch
from control_plane.infra.kinetic_vps_sentinel import KineticVPSSentinel


def test_kinetic_sentinel_probe_mocked_success():
    sentinel = KineticVPSSentinel()

    with patch("socket.socket") as mock_sock, \
         patch.object(sentinel.rotel_forwarder, "forward_trace", return_value={"success": True}), \
         patch.object(sentinel.saltare_adapter, "dispatch_hub_tool", return_value={"success": True}):

        # Simulate TCP port open
        instance = mock_sock.return_value.__enter__.return_value
        instance.connect_ex.return_value = 0

        report = sentinel.probe_all()
        assert report["overall_status"] in ("HEALTHY", "ACTIVE")
        assert report["components"]["rotel"]["mesh_forwarding"] is True
        assert report["components"]["saltare"]["mcp_dispatch"] is True
        assert report["mesh_node"]["tailscale_ip"] == "100.110.180.18"
