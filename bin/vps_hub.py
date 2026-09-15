#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
r"""
Camelot-OS Hub & Control Plane (VPS KVM563) Access Client
=========================================================
Operator Authority: King Arthur (VaShawn O. Head / Vizion)
Governing Agent:    HERMES_PRIME (Hermes Research & Mesh Synthesis)
VPS Host:           KVM563 (vps3573819.trouble-free.net)
Public IP:          162.35.107.134
Tailscale IP:       100.71.218.75 (kba-services) / 100.84.98.39 (relay)

Capabilities:
1. --status    : Live ping & TCP service probe (SSH, Bifrost :3001, Mesh Bridge :8095)
2. --ssh       : Open interactive SSH shell to the VPS
3. --telemetry : Pull remote Hermes Prime & Open-Notebook VFS telemetry
"""

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VPS_PUBLIC_IP = "162.35.107.134"
VPS_HOSTNAME = "vps3573819.trouble-free.net"
VPS_TAILSCALE_IP = "100.110.180.18"
VPS_KBA_TAILSCALE = "100.71.218.75"
VPS_SSH_PORT = 22
VPS_HTTP_PORT = 80
VPS_BIFROST_PORT = 3001
VPS_MESH_BRIDGE_PORT = 8095

def probe_port(host: str, port: int, timeout: float = 3.0) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def get_vps_status() -> dict:
    ssh_ok = probe_port(VPS_PUBLIC_IP, VPS_SSH_PORT, timeout=3.0)
    http_ok = probe_port(VPS_PUBLIC_IP, VPS_HTTP_PORT, timeout=3.0)
    bifrost_ok = probe_port(VPS_PUBLIC_IP, VPS_BIFROST_PORT, timeout=2.0)
    mesh_ok = probe_port(VPS_PUBLIC_IP, VPS_MESH_BRIDGE_PORT, timeout=2.0)
    
    return {
        "host_server": "KVM563",
        "vm_id": "vps3573819",
        "public_ip": VPS_PUBLIC_IP,
        "tailscale_ip": VPS_KBA_TAILSCALE,
        "assigned_agent": "HERMES_PRIME (NousResearch Hermes Agent)",
        "co_governor": "SIR_HEIMDALL (Bifrost Boundary)",
        "services": {
            "hermes_dashboard_80": "ONLINE (http://162.35.107.134/)" if http_ok else "OFFLINE",
            "openai_api_gateway": "ONLINE (http://162.35.107.134/api/v1)" if http_ok else "OFFLINE",
            "ssh_port_22": "ONLINE" if ssh_ok else "OFFLINE / FIREWALLED",
            "bifrost_gateway_3001": "ONLINE" if bifrost_ok else "STANDBY / PRIVATE_TS",
            "mesh_bridge_8095": "ONLINE" if mesh_ok else "STANDBY / PRIVATE_TS"
        }
    }

def print_status():
    print("=" * 80)
    print("🏰 CAMELOT-OS HUB & CONTROL PLANE (VPS KVM563) TELEMETRY")
    print("=" * 80)
    status = get_vps_status()
    print(f"• Host Server        : {status['host_server']} ({status['vm_id']})")
    print(f"• Public IP          : {status['public_ip']} ({VPS_HOSTNAME})")
    print(f"• Tailscale IP       : {VPS_TAILSCALE_IP} (vps-camelot-hub)")
    print(f"• Assigned Agent     : {status['assigned_agent']}")
    print("\n📡 Service Ports & Ingress:")
    for s, state in status["services"].items():
        icon = "🟢" if "ONLINE" in state else "🟡"
        print(f"   {icon} {s:<22} : {state}")
    print("=" * 80)

def connect_ssh(user: str = "root"):
    print(f"\n🔐 Initiating SSH Session to Camelot Hub ({user}@{VPS_PUBLIC_IP})...")
    ssh_cmd = ["ssh", f"{user}@{VPS_PUBLIC_IP}"]
    try:
        subprocess.run(ssh_cmd)
    except Exception as e:
        print(f"❌ SSH Execution Error: {e}")

def run_hermes_command(args_list: list[str]):
    subcmd = " ".join(args_list) if args_list else ""
    if subcmd:
        full_cmd = f"docker exec -it hermes hermes {subcmd}"
    else:
        full_cmd = "docker exec -it hermes hermes"
    print(f"🚀 Dispatching to Hermes Agent on VPS: {full_cmd}")
    ssh_cmd = ["ssh", "-t", f"root@{VPS_PUBLIC_IP}", full_cmd]
    try:
        subprocess.run(ssh_cmd)
    except Exception as e:
        print(f"❌ Hermes Execution Error: {e}")

def open_dashboard():
    url = f"http://{VPS_PUBLIC_IP}/"
    print(f"🌐 Opening Hermes Web Dashboard: {url}")
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception as e:
        print(f"❌ Could not launch browser: {e}")

def main():
    parser = argparse.ArgumentParser(description="Camelot-OS Hub VPS Access Client")
    parser.add_argument("--status", action="store_true", help="Probe and display VPS status")
    parser.add_argument("--ssh", action="store_true", help="Launch SSH connection to VPS")
    parser.add_argument("--hermes", nargs="*", help="Execute Hermes Agent command inside container")
    parser.add_argument("--dashboard", action="store_true", help="Open Hermes web dashboard in browser")
    parser.add_argument("--model", action="store_true", help="Interactive Hermes model picker")
    parser.add_argument("--logs", action="store_true", help="View Hermes container logs")
    parser.add_argument("--user", type=str, default="root", help="SSH username (default: root)")
    args, remaining = parser.parse_known_args()

    if args.ssh:
        connect_ssh(args.user)
    elif args.dashboard:
        open_dashboard()
    elif args.model:
        run_hermes_command(["model"])
    elif args.logs:
        run_hermes_command(["logs"])
    elif args.hermes is not None:
        cmd = args.hermes + remaining
        run_hermes_command(cmd)
    else:
        print_status()

if __name__ == "__main__":
    main()

