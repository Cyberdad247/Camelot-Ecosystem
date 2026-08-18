# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import socket
import sys
from datetime import datetime

# Path enforcement
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))


def check_port(port, name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect(("localhost", port))
            return True
        except Exception:
            return False


def run_diagnostics():
    print("🦁 [CAMELOT] Initiating Sovereign Engine Diagnostics...")
    print("-" * 50)

    results = {
        "VIDENEPTUS (Router)": "ONLINE" if os.path.exists("CAMELOT_OS/01_KERNEL/merlin_omega.py") else "MISSING",
        "APEE v6.0 (Compiler)": "ONLINE" if os.path.exists("CAMELOT_OS/01_KERNEL/api_server.py") else "MISSING",
        "PROMETHEUS (Planner)": (
            "ONLINE" if os.path.exists("CAMELOT_OS/01_KERNEL/BRIDGE/GENKIT/run_flow.ts") else "MISSING"
        ),
        "OUROBOROS (Memory)": "ONLINE" if check_port(8001, "Kernel API") else "OFFLINE (Wait for API)",
        "ANTIGRAVITY (Kinetic)": "ENFORCED" if os.path.exists("CAMELOT_OS/tools/antigravity.py") else "VIOLATED",
        "AETHER (Swarm)": (
            "READY" if os.path.exists("CAMELOT_OS/00_SECURE_ARCHIVE/LEGACY_SRC/swarm/swarm.go") else "MISSING"
        ),
        "UKG (Knowledge)": "STANDBY" if os.path.exists("CAMELOT_OS/03_VAULT/UKG/UKG_MEMORY.jsonld") else "MISSING",
    }

    for engine, status in results.items():
        color = "\033[92m" if "ONLINE" in status or "READY" in status or "ENFORCED" in status else "\033[91m"
        reset = "\033[0m"
        print(f"Engine: {engine:<25} Status: {color}{status}{reset}")

    # Check for recent kinetically logged actions
    print("-" * 50)
    if os.path.exists("CAMELOT_OS/PROVENANCE_LEDGER.md"):
        with open("CAMELOT_OS/PROVENANCE_LEDGER.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_action = lines[-1].strip() if lines else "None"
            print(f"Last Logged Action: {last_action}")

    print("-" * 50)
    print(f"Diagnostics Complete: {datetime.now().isoformat()}")


if __name__ == "__main__":
    run_diagnostics()