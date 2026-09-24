# SPDX-License-Identifier: MIT
"""
Tests for Sir Heimdall, Multivoice-Router, and Hermes Layer VPS Integration.
"""

from __future__ import annotations

import json
from pathlib import Path

from control_plane.infra.hermes_bridge import CHANNELS
from control_plane.multivoice_bridge import MultivoiceBridge
from control_plane.runes.runic_router import RUNIC_COMMANDS, normalize_rune, route_rune


def test_multivoice_runes_present_in_table():
    assert "//MULTIVOICE_STATUS" in RUNIC_COMMANDS
    assert "//MULTIVOICE_ROUTE" in RUNIC_COMMANDS
    assert "//LOCK_BIFROST_mTLS" in RUNIC_COMMANDS
    assert RUNIC_COMMANDS["//MULTIVOICE_STATUS"]["knight"] == "sir_heimdall"
    assert RUNIC_COMMANDS["//MULTIVOICE_ROUTE"]["knight"] == "sir_sonus"


def test_multivoice_runes_aliases():
    assert normalize_rune("//multivoice-status") == "//MULTIVOICE_STATUS"
    assert normalize_rune("$multivoice-status") == "//MULTIVOICE_STATUS"
    assert normalize_rune("//multivoice_status") == "//MULTIVOICE_STATUS"
    assert normalize_rune("//multivoice-route") == "//MULTIVOICE_ROUTE"
    assert normalize_rune("$multivoice-route") == "//MULTIVOICE_ROUTE"
    assert normalize_rune("//lock-bifrost-mtls") == "//LOCK_BIFROST_mTLS"


def test_lock_bifrost_mtls_includes_port_7680():
    res = route_rune("//LOCK_BIFROST_MTLS", context={"hydrate": False})
    meta = res.metadata
    assert meta.get("action") == "lock_bifrost_mtls"
    assert meta.get("guardian") == "SIR_HEIMDALL"
    assert 7680 in meta.get("ports_guarded", [])
    assert 3001 in meta.get("ports_guarded", [])
    assert 8095 in meta.get("ports_guarded", [])
    assert meta.get("status") == "LOCKED"


def test_hermes_bus_channels_contain_multivoice_and_heimdall():
    assert "multivoice.voice" in CHANNELS
    assert "multivoice.routes" in CHANNELS
    assert "multivoice.telemetry" in CHANNELS
    assert "heimdall.perimeter" in CHANNELS


def test_multivoice_bridge_vps_failover_and_heimdall_lock():
    bridge = MultivoiceBridge(
        base_url="http://127.0.0.1:9999",  # unrouted port
        vps_url="http://100.71.218.75:9999",  # unrouted port
        timeout_s=0.1
    )
    stats = bridge.fetch_affinity()
    # Offline should fail gracefully without throwing exception
    assert stats.connected is False
    assert "router offline" in stats.detail or stats.connected is False

    lock = bridge.fetch_heimdall_perimeter_lock()
    assert lock["status"] == "LOCKED"
    assert lock["guardian"] == "SIR_HEIMDALL"
    assert 7680 in lock["ports_guarded"]


def test_multivoice_router_deployment_artifacts():
    repo_root = Path(__file__).resolve().parent.parent.parent
    deploy_dir = repo_root / "deploy" / "multivoice-router"
    assert (deploy_dir / "server.ts").exists()
    assert (deploy_dir / "docker-compose.yml").exists()
    assert (deploy_dir / "systemd" / "multivoice-router.service").exists()
    assert (deploy_dir / "setup.sh").exists()
    assert (deploy_dir / ".env.example").exists()

    server_content = (deploy_dir / "server.ts").read_text(encoding="utf-8")
    assert "/metrics" in server_content
    assert "/v1/usage" in server_content
    assert "/api/heimdall/lock" in server_content
    assert "/api/hermes/bridge" in server_content


def test_open_notebook_tissues_integrity():
    repo_root = Path(__file__).resolve().parent.parent.parent
    state_dir = repo_root / "03_VAULT" / "runtime_state" / "open_notebook"

    # 1. Sir Heimdall tissue
    heimdall_tissue = json.loads((state_dir / "sir_heimdall_tissue.json").read_text(encoding="utf-8"))
    titles = [item.get("title") for item in heimdall_tissue]
    assert "MULTIVOICE_ROUTER_HERMES_PERIMETER_GATE" in titles

    # 2. Hermes Prime tissue
    hermes_tissue = json.loads((state_dir / "hermes_prime_tissue.json").read_text(encoding="utf-8"))
    hermes_types = [item.get("artifact_type") for item in hermes_tissue]
    assert "multivoice_router_engine" in hermes_types

    # 3. VPS Hub tissue
    vps_tissue = json.loads((state_dir / "vps_hub_kvm563_tissue.json").read_text(encoding="utf-8"))
    assert vps_tissue[0].get("co_guardian") == "SIR_HEIMDALL"
    assert vps_tissue[0].get("services", {}).get("multivoice_router") == 7680


def test_multivoice_status_and_route_dispatch():
    res_status = route_rune("//MULTIVOICE_STATUS", context={"hydrate": False})
    assert res_status.knight == "sir_heimdall"
    assert res_status.metadata.get("guardian") == "SIR_HEIMDALL"

    res_route = route_rune("//MULTIVOICE_ROUTE synthesize greeting in Aoede voice", context={"hydrate": False})
    assert res_route.knight == "sir_sonus"
    assert res_route.metadata.get("action") == "multivoice_route"
    assert res_route.metadata.get("guardian") == "SIR_HEIMDALL"
    assert res_route.metadata.get("status") == "ROUTED"
