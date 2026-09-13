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
    assert nodes["vps_hub_kvm563"]["public_ip"] == "162.35.107.134"
