# SPDX-License-Identifier: MIT

from __future__ import annotations

import json

from control_plane.heimdall_bifrost_governance import (
    REQUIRED_BRIDGE_COMPONENTS,
    boot_heimdall_bifrost_governance,
    dispatch_to_nano_knight,
    write_governance_status,
)


def _write_mesh_manifest(tmp_path):
    runtime = tmp_path / "03_VAULT" / "runtime_state"
    runtime.mkdir(parents=True)
    (runtime / "bifrost_router_mesh_manifest.json").write_text(
        json.dumps(
            {
                "components": [
                    {"name": name, "status": "integrated"}
                    for name in REQUIRED_BRIDGE_COMPONENTS
                ]
            }
        ),
        encoding="utf-8",
    )


def test_write_governance_status_registers_heimdall_swarm(tmp_path):
    _write_mesh_manifest(tmp_path)

    status = write_governance_status(tmp_path)

    assert status["ready"] is True
    assert status["owner"] == "sir_heimdall"
    assert status["governed_surface"] == "bifrost_bridge"
    assert status["bridge_mesh"]["missing_components"] == []
    assert len(status["nano_knights"]) >= 5
    assert status["auth"]["secret_values_serialized"] is False
    assert (tmp_path / "03_VAULT" / "runtime_state" / "heimdall_bifrost_governance_latest.json").exists()


def test_dispatch_routes_router_mesh_event_to_mesh_probe(tmp_path):
    _write_mesh_manifest(tmp_path)

    routed = dispatch_to_nano_knight({"channel": "router.mesh", "detail": "probe"}, tmp_path)

    assert routed["owner"] == "sir_heimdall"
    assert routed["route"]["nano_knight"] == "heimdall.mesh_probe"
    assert routed["governance_ready"] is True


def test_boot_reports_missing_router_components(tmp_path):
    runtime = tmp_path / "03_VAULT" / "runtime_state"
    runtime.mkdir(parents=True)
    (runtime / "bifrost_router_mesh_manifest.json").write_text(
        json.dumps({"components": [{"name": "CLIProxyAPI", "status": "integrated"}]}),
        encoding="utf-8",
    )

    ok, detail = boot_heimdall_bifrost_governance(tmp_path)

    assert ok is False
    assert "OmniRoute" in detail
