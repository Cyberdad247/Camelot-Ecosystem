# SPDX-License-Identifier: MIT
import json


from control_plane.dispatch import vps_mobile_mesh_bridge as bridge
from control_plane.dispatch.vps_mobile_mesh_bridge import load_mesh_topology
from control_plane.infra import mesh_topology as mt


def test_state_file_cannot_override_the_single_source(tmp_path, monkeypatch):
    """The state file may enrich metadata but must not own the node set or address.

    `load_mesh_topology` used to return the file verbatim on its first line, so a
    stale file resurrected nodes that were absent from the tailnet on every read —
    the projection written to replace them was never reached. This asserts the
    inversion holds even against a deliberately hostile file.
    """
    hostile = tmp_path / "hostile.json"
    hostile.write_text(
        json.dumps(
            {
                "nodes": {
                    # A node absent from the tailnet, with its retired address.
                    "kba_services": {"tailscale_ip": "100.71.218.75", "role": "phantom"},
                    # The hub, pointed somewhere else entirely.
                    "vps_hub_kvm563": {
                        "tailscale_ip": "10.0.0.1",
                        "public_ip": "1.2.3.4",
                        "os": "Ubuntu 24.04 LTS",  # metadata: allowed through
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(bridge, "TOPOLOGY_PATH", str(hostile))
    topo = load_mesh_topology()
    nodes = topo["nodes"]

    assert "kba_services" not in nodes, "state file resurrected an absent node"
    assert nodes["vps_hub_kvm563"]["tailscale_ip"] == mt.HUB_TAILSCALE_IP
    assert nodes["vps_hub_kvm563"]["public_ip"] == mt.HUB_PUBLIC_IP
    # Metadata the source does not carry is still honoured.
    assert nodes["vps_hub_kvm563"]["os"] == "Ubuntu 24.04 LTS"
    # The source owns the node set, so the hostile file cannot shrink it either.
    # The hub is served under its historical alias id (see bridge.SERVED_HUB_ID).
    assert bridge.SERVED_HUB_ID in nodes
    assert {n["tailscale_ip"] for n in nodes.values()} == set(mt.active_ips())


def test_served_topology_matches_the_single_source():
    """The state file is read *first* by `load_mesh_topology`, so a stale file
    silently overrides the single source. That is exactly how the two absent
    nodes kept being served after the Python inventories were corrected.
    """
    nodes = load_mesh_topology()["nodes"]
    served = {n["tailscale_ip"] for n in nodes.values()}
    assert served == set(mt.active_ips()), (
        "sovereign_mesh_topology.json disagrees with mesh_topology.MESH_NODES"
    )
    assert set(mt.absent_ips()).isdisjoint(served), (
        "an absent-from-tailnet node is being published as active"
    )

def test_sovereign_mesh_topology_structure():
    topo = load_mesh_topology()
    assert "nodes" in topo
    nodes = topo["nodes"]
    
    # Assert primary nodes exist
    assert "cybertronia" in nodes
    assert "vashawns_s26_ultra" in nodes
    assert "fothers_camelot" in nodes
    assert "lakesha" in nodes
    assert "macbook_pro_3" in nodes
    assert "motorola_moto_g_power" in nodes
    assert "vps_hub_kvm563" in nodes

    # These two are absent from the tailnet. They must not be published as active
    # nodes: a node that cannot be reached can only report OFFLINE, which masks a
    # real node going down. They are carried in `absent_nodes` instead.
    assert "camelot_relay_modal" not in nodes
    assert "kba_services" not in nodes
    absent = topo["absent_nodes"]
    assert absent["camelot_relay_modal"]["tailscale_ip"] == "100.84.98.39"
    assert absent["kba_services"]["tailscale_ip"] == "100.71.218.75"
    assert absent["kba_services"]["status"] == "ABSENT_FROM_TAILNET"

    # Assert IP mappings match the canonical Tailscale inventory
    assert nodes["cybertronia"]["tailscale_ip"] == "100.118.224.52"
    assert nodes["vashawns_s26_ultra"]["tailscale_ip"] == "100.106.246.126"
    assert nodes["fothers_camelot"]["tailscale_ip"] == "100.121.48.50"
    assert nodes["lakesha"]["tailscale_ip"] == "100.100.155.55"
    assert nodes["macbook_pro_3"]["tailscale_ip"] == "100.113.101.43"
    assert nodes["motorola_moto_g_power"]["tailscale_ip"] == "100.89.129.105"
    assert nodes["motorola_moto_g_power"]["designation"] == "AUXILIARY_MOBILE_SENTINEL"
    assert "Auxiliary Mobile Sentinel" in nodes["motorola_moto_g_power"]["role"]
    assert nodes["motorola_moto_g_power"]["status"] in ("AUXILIARY", "ONLINE_STANDBY")
    assert nodes["vps_hub_kvm563"]["public_ip"] == "162.35.107.134"
    vps_tailscale_ip = nodes["vps_hub_kvm563"]["tailscale_ip"]
    cliproxy_link = nodes["vps_hub_kvm563"]["inference_links"]["cliproxy_sie"]
    assert cliproxy_link["selector"] == "cliproxy:default"
    assert cliproxy_link["governing_knight"] == "HERMES_PRIME"
    assert cliproxy_link["vps_node"] == "vps_hub_kvm563"
    bifrost_bridge = cliproxy_link["bifrost_bridge"]
    assert bifrost_bridge["module"] == "control_plane/dispatch/bifrost.py"
    assert bifrost_bridge["gateway_url"] == f"http://{vps_tailscale_ip}:3001"
    assert bifrost_bridge["mesh_bridge_url"] == f"http://{vps_tailscale_ip}:8095"
    assert bifrost_bridge["co_governors"] == ["HERMES_PRIME", "SIR_HEIMDALL"]
    assert bifrost_bridge["auth"]["secret_values_serialized"] is False
    assert cliproxy_link["secret_values_serialized"] is False


def test_heimdall_bifrost_governance_mesh_inventory():
    from control_plane.infra.heimdall_bifrost_governance import read_governance_status
    status = read_governance_status()
    assert "mesh_inventory" in status
    mesh = status["mesh_inventory"]
    assert mesh["account"] == "Cyberdad247@github"
    assert mesh["node_count"] >= 7
    node_names = [n["name"] for n in mesh["nodes"]]
    assert "motorola-moto-g-power-5g---2024" in node_names
    assert "vashawns-s26-ultra" in node_names
    assert "cybertronia" in node_names
    moto_node = next(n for n in mesh["nodes"] if n["name"] == "motorola-moto-g-power-5g---2024")
    assert moto_node["tailscale_ip"] == "100.89.129.105"
