# SPDX-License-Identifier: MIT
from control_plane.dispatch.vps_mobile_mesh_bridge import load_mesh_topology

def test_sovereign_mesh_topology_structure():
    topo = load_mesh_topology()
    assert "nodes" in topo
    nodes = topo["nodes"]
    
    # Assert primary nodes exist
    assert "cybertronia" in nodes
    assert "vashawns_s26_ultra" in nodes
    assert "fothers_camelot" in nodes
    assert "lakesha" in nodes
    assert "camelot_relay_modal" in nodes
    assert "kba_services" in nodes
    assert "motorola_moto_g_power" in nodes
    assert "vps_hub_kvm563" in nodes

    # Assert IP mappings match the canonical Tailscale inventory
    assert nodes["cybertronia"]["tailscale_ip"] == "100.118.224.52"
    assert nodes["vashawns_s26_ultra"]["tailscale_ip"] == "100.106.246.126"
    assert nodes["fothers_camelot"]["tailscale_ip"] == "100.121.48.50"
    assert nodes["lakesha"]["tailscale_ip"] == "100.100.155.55"
    assert nodes["camelot_relay_modal"]["tailscale_ip"] == "100.84.98.39"
    assert nodes["kba_services"]["tailscale_ip"] == "100.71.218.75"
    assert nodes["motorola_moto_g_power"]["tailscale_ip"] == "100.89.129.105"
    assert nodes["motorola_moto_g_power"]["designation"] == "AUXILIARY_MOBILE_SENTINEL"
    assert "Auxiliary Mobile Sentinel" in nodes["motorola_moto_g_power"]["role"]
    assert nodes["motorola_moto_g_power"]["status"] in ("AUXILIARY", "ONLINE_STANDBY")
    assert nodes["vps_hub_kvm563"]["public_ip"] == "162.35.107.134"


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
