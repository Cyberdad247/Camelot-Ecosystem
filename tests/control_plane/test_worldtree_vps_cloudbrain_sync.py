# SPDX-License-Identifier: MIT
"""
Regression tests for the probe-based WorldTree CloudBrain VPS sync engine.

Pins the contract that the engine NEVER preserves stale tissue values:
- live_probes / services_state are rebuilt from actual TCP/HTTP probes
- deployed_commit comes from a live SSH git probe when available
- drift is computed from the probe results, not copied forward
- commit probe failure degrades to the existing value WITH a marker,
  never silently masquerading as verified state
- HTTP health probes (worldtree_http_status / bifrost_health_status) are
  recorded from real probes; failure surfaces as None -> PROBE_FAILED,
  never a fabricated 200
"""

import json

import control_plane.runners.worldtree_vps_cloudbrain_sync as sync_mod
from control_plane.runners.worldtree_vps_cloudbrain_sync import (
    SERVICE_PORT_MAP,
    WorldTreeCloudBrainVPSSync,
    _probe_vps_live_state,
)

SHA = "27e66d0113879dc39b8122a51284624bcb95e692"
SUBJECT = "feat(vps-hub): implement Omni-Voice DAG, VPS Nexus deployment"


def _fake_tcp_prober(open_ports):
    def _probe(host, port, timeout=2.0):
        return port in open_ports

    return _probe


def _fake_commit_prober(result):
    def _probe(target, workdir, timeout=8.0):
        return result

    return _probe


def _fake_http_prober(status):
    def _probe(url, timeout=4.0):
        return status

    return _probe


def _dead_http_prober(url, timeout=4.0):
    return None


def _all_open():
    return {22} | set(SERVICE_PORT_MAP.values())


def test_probe_vps_live_state_aggregates_services_and_drift():
    # 8095 closed, everything else open -> drift detected, 1 stopped service.
    state = _probe_vps_live_state(
        tcp_prober=_fake_tcp_prober(_all_open() - {8095}),
        commit_prober=_fake_commit_prober((SHA, SUBJECT)),
        http_prober=_dead_http_prober,
        ssh_http_prober=_dead_http_prober,
    )
    assert state["deployed_commit"] == SHA
    assert state["deployed_commit_summary"] == SUBJECT
    assert state["ports"][8095] is False
    assert state["ports"][3001] is True
    assert state["stopped_services"] == ["vps_mobile_mesh_bridge"]
    assert state["drift_detected"] is True


def test_probe_vps_live_state_all_open_no_drift():
    state = _probe_vps_live_state(
        tcp_prober=_fake_tcp_prober(_all_open()),
        commit_prober=_fake_commit_prober((SHA, SUBJECT)),
        http_prober=_fake_http_prober(200),
        ssh_http_prober=_fake_http_prober(200),
    )
    assert state["stopped_services"] == []
    assert state["drift_detected"] is False
    assert state["ports"][8095] is True
    assert state["worldtree_http_status"] == 200
    assert state["bifrost_health_status"] == 200


def test_probe_routes_tailscale_bound_ports_at_ts_ip(monkeypatch):
    """Ports in TS_IP_BOUND_PORTS must be probed at the tailscale0 address,
    everything else at loopback — the on-box probe must honor the bind
    plane of the service (regression pin for the :8095 false-STOPPED bug)."""
    calls = []

    def _recording_prober(host, port, timeout=2.0):
        calls.append((host, port))
        return True

    monkeypatch.setattr(sync_mod, "VPS_TAILSCALE_IP", "100.110.180.18")
    state = _probe_vps_live_state(
        tcp_prober=_recording_prober,
        commit_prober=_fake_commit_prober((SHA, SUBJECT)),
        http_prober=_dead_http_prober,
        ssh_http_prober=_dead_http_prober,
    )
    by_port = {port: host for host, port in calls}
    assert by_port[8095] == "100.110.180.18"
    assert by_port[80] == "127.0.0.1"
    assert by_port[3001] == "127.0.0.1"
    assert by_port[9000] == "127.0.0.1"  # receiver: loopback bind
    # Truthed map: multivoice/honcho are gone (never deployed).
    assert 7680 not in by_port and 8000 not in by_port
    assert state["drift_detected"] is False


def test_probe_vps_live_state_http_failures_recorded_as_none():
    """HTTP probe failure must surface as None (recorded as PROBE_FAILED
    downstream), never as a fabricated 200."""

    def _boom(url, timeout=4.0):
        raise RuntimeError("unreachable")

    state = _probe_vps_live_state(
        tcp_prober=_fake_tcp_prober(_all_open()),
        commit_prober=_fake_commit_prober((SHA, SUBJECT)),
        http_prober=_boom,
        ssh_http_prober=_boom,
    )
    assert state["worldtree_http_status"] is None
    assert state["bifrost_health_status"] is None
    assert state["drift_detected"] is False  # HTTP status alone is not drift


def test_probe_vps_live_state_commit_probe_failure_returns_none():
    state = _probe_vps_live_state(
        tcp_prober=_fake_tcp_prober(_all_open()),
        commit_prober=_fake_commit_prober((None, None)),
        http_prober=_dead_http_prober,
        ssh_http_prober=_dead_http_prober,
    )
    assert state["deployed_commit"] is None
    assert state["drift_detected"] is True  # commit unverifiable counts as drift


def test_probe_vps_live_state_never_raises_on_prober_exception():
    def _boom(host, port, timeout=2.0):
        raise RuntimeError("network gone")

    state = _probe_vps_live_state(
        tcp_prober=_boom,
        commit_prober=_fake_commit_prober((None, None)),
        http_prober=_dead_http_prober,
        ssh_http_prober=_dead_http_prober,
    )
    assert state["ports"] == {p: False for p in SERVICE_PORT_MAP.values()}
    assert state["deployed_commit"] is None


def test_sync_rebuilds_live_probes_instead_of_preserving_stale(tmp_path, monkeypatch):
    """Stale tissue says all-open; live probes say otherwise -> tissue must
    reflect the LIVE result, not the preserved stale one."""
    tissue_file = sync_mod.OPEN_NOTEBOOK_DIR / "vps_hub_kvm563_tissue.json"
    original = tissue_file.read_text(encoding="utf-8")
    try:
        stale = json.loads(original)
        stale[0]["live_probes"] = {
            "ssh_port_22": "OPEN",
            "caddy_port_80": "OPEN",
            "bifrost_port_3001": "OPEN",
            "worldtree_http_status": 200,
            "bifrost_health_status": 200,
        }
        stale[0]["deployed_commit"] = "0000000000000000000000000000000000000000"
        tissue_file.write_text(json.dumps(stale, indent=2), encoding="utf-8")

        monkeypatch.setattr(
            sync_mod,
            "_probe_vps_live_state",
            lambda: _probe_vps_live_state(
                tcp_prober=_fake_tcp_prober(_all_open() - {8095, 8000}),
                commit_prober=_fake_commit_prober((SHA, SUBJECT)),
                http_prober=_fake_http_prober(200),
                ssh_http_prober=_fake_http_prober(200),
            ),
        )

        engine = WorldTreeCloudBrainVPSSync()
        result = engine.sync_vps_hub_to_worldtree()
        assert result["status"] == "SUCCESS"

        fresh = json.loads(tissue_file.read_text(encoding="utf-8"))[0]
        assert fresh["deployed_commit"] == SHA  # stale sha replaced by probe
        assert fresh["services_state"]["vps_mobile_mesh_bridge"].startswith("STOPPED")
        assert fresh["services_state"]["bifrost_gateway"].startswith("RUNNING")
        # Truthed map: never-deployed services must not appear at all.
        assert "honcho_self_hosted" not in fresh["services_state"]
        assert "multivoice_router" not in fresh["services_state"]
        # Deployed 2026-09-23: receiver must be back in the map.
        assert "webhook_receiver" in fresh["services_state"]
        assert "multivoice_router" not in fresh["services"]
        assert "honcho_self_hosted" not in fresh["services"]
        assert "webhook_receiver" in fresh["services"]
        assert fresh["live_probes"]["worldtree_http_status"] == 200
        assert fresh["live_probes"]["bifrost_health_status"] == 200
        assert fresh["drift"]["detected"] is True
        assert sorted(fresh["drift"]["stopped_services"]) == [
            "vps_mobile_mesh_bridge",
        ]
        assert fresh["last_synced"] >= fresh["timestamp"]
    finally:
        tissue_file.write_text(original, encoding="utf-8")


def test_sync_commit_probe_failure_falls_back_with_marker(tmp_path, monkeypatch):
    tissue_file = sync_mod.OPEN_NOTEBOOK_DIR / "vps_hub_kvm563_tissue.json"
    original = tissue_file.read_text(encoding="utf-8")
    try:
        # Seed a known last-recorded commit for the fallback path to retain.
        seeded = json.loads(original)
        seeded[0]["deployed_commit"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        seeded[0]["deployed_commit_summary"] = "last recorded commit"
        tissue_file.write_text(json.dumps(seeded, indent=2), encoding="utf-8")

        monkeypatch.setattr(
            sync_mod,
            "_probe_vps_live_state",
            lambda: _probe_vps_live_state(
                tcp_prober=_fake_tcp_prober(_all_open()),
                commit_prober=_fake_commit_prober((None, None)),
                http_prober=_dead_http_prober,
                ssh_http_prober=_dead_http_prober,
            ),
        )
        result = WorldTreeCloudBrainVPSSync().sync_vps_hub_to_worldtree()
        assert result["status"] == "SUCCESS"

        fresh = json.loads(tissue_file.read_text(encoding="utf-8"))[0]
        assert fresh["deployed_commit"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        assert fresh["deployed_commit_verified_at"] is None
        assert fresh["deployed_commit_verification"].startswith("probe_unavailable")
    finally:
        tissue_file.write_text(original, encoding="utf-8")
