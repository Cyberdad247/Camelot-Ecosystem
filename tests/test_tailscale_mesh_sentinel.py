# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from pathlib import Path
from control_plane.infra.tailscale_mesh_sentinel import (
    TailscaleMeshSentinel,
    PathStatus,
    MeshHealthReport,
    boot_tailscale_sentinel,
)


def test_path_status_dataclass():
    ps = PathStatus(
        name="TEST_PATH",
        target="127.0.0.1:5555",
        reachable=True,
        latency_ms=2.5,
    )
    assert ps.name == "TEST_PATH"
    assert ps.reachable is True
    assert ps.latency_ms == 2.5


def test_mesh_health_report_structure():
    rep = MeshHealthReport(
        timestamp="2026-10-04T00:00:00Z",
        host_tailscale_ip="100.118.224.52",
        tailscale_service_running=True,
        cloudflare_warp_active=False,
        active_routing_path="WIFI",
        paths={},
        android_always_on_configured=True,
        overall_status="HEALTHY_OPTIMAL",
    )
    d = rep.to_dict()
    assert d["overall_status"] == "HEALTHY_OPTIMAL"
    assert d["android_always_on_configured"] is True


def test_sentinel_assessment(tmp_path):
    sentinel = TailscaleMeshSentinel(home=tmp_path)
    report = sentinel.assess_mesh_health()
    assert isinstance(report, MeshHealthReport)
    assert report.active_routing_path != ""
    assert (tmp_path / "03_VAULT" / "runtime_state" / "mesh_heartbeats.json").exists()


def test_boot_tailscale_sentinel(tmp_path):
    ok, msg = boot_tailscale_sentinel(tmp_path)
    assert ok is True
    assert "Always-On Mesh Sentinel" in msg
