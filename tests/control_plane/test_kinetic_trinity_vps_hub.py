# SPDX-License-Identifier: MIT
"""End-to-end integration test for Kinetic Trinity + VPS Hub (Task 5)."""

from control_plane.infra.mesh_topology import HUB_TAILSCALE_IP
from control_plane.infra.kinetic_vps_sentinel import KineticVPSSentinel
from control_plane.infra.rotel_vps_forwarder import RotelVPSForwarder
from control_plane.infra.saltare_hub_adapter import SaltareHubAdapter
from control_plane.infra.cribo_bundle_validator import CriboBundleValidator


def test_kinetic_trinity_modules_import_cleanly():
    forwarder = RotelVPSForwarder()
    adapter = SaltareHubAdapter()
    validator = CriboBundleValidator()
    sentinel = KineticVPSSentinel()
    assert forwarder.hub_ip == HUB_TAILSCALE_IP
    assert adapter.local_port == 8090
    assert sentinel.hub_ip == HUB_TAILSCALE_IP


def test_sentinel_report_structure():
    sentinel = KineticVPSSentinel()
    report = sentinel.probe_all()
    assert "overall_status" in report
    assert "mesh_node" in report
    assert "components" in report
    assert set(report["components"].keys()) == {"rotel", "saltare", "cribo"}
