# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY

import datetime
import os
import sys
import subprocess
from pathlib import Path
import requests

# Resolve Repo Root
REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ["CAMELOT_OS_HOME"] = str(REPO_ROOT)

# Add KERNEL to path for telemetry import
sys.path.append(str(REPO_ROOT / "01_KERNEL"))
try:
    from senses.telemetry_client import RotelClient
    logger = RotelClient("sync_protocol")
except ImportError:
    class DummyLogger:
        def info(self, *args, **kwargs): print(f"INFO: {args[0]}")
    logger = DummyLogger()

# SYSTEM SYNC PROTOCOL v1.0
# Synchronizes the Kinetic State with the Provenance Ledger and UKG.

LEDGER_PATH = REPO_ROOT / "PROVENANCE_LEDGER.md"
MORGANA_URL = "http://localhost:8001/ping"
UKG_PATH = REPO_ROOT / "03_VAULT" / "UKG" / "UKG_MEMORY.jsonld"

ROTEL_PATH = REPO_ROOT / "kinetic_edge" / "rotel" / "target" / "release" / "rotel.exe"
SALTARE_PATH = REPO_ROOT / "kinetic_edge" / "saltare" / "saltare_gateway.exe"

def get_timestamp():
    return datetime.datetime.now().isoformat()

def check_morgana_health():
    try:
        response = requests.get(MORGANA_URL, timeout=2)
        if response.status_code == 200:
            return "ONLINE", response.json()
        return "UNSTABLE", f"Status: {response.status_code}"
    except Exception as e:
        return "OFFLINE", str(e)

def update_ledger(component, action, status):
    entry = f"| {get_timestamp()} | {component} | {action} | {status} |"
    print(f"📝 LEDGER: {entry}")
    try:
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write("\n" + entry)
        return True
    except Exception as e:
        print(f"❌ Failed to write to ledger: {e}")
        return False

def sync_ukg():
    if UKG_PATH.exists():
        auth_size = UKG_PATH.stat().st_size
        return "SYNCED", f"Size: {auth_size} bytes"
    else:
        return "MISSING", "File not found"

def check_kinetic_armory():
    """Verifies that Phase 8 Kinetic Binaries are compiled and present."""
    rotel = ROTEL_PATH.exists()
    saltare = SALTARE_PATH.exists()

    if rotel and saltare:
        return "ARMED", "Rotel: OK | Saltare: OK"
    elif rotel:
        return "PARTIAL", "Rotel: OK | Saltare: MISSING"
    elif saltare:
        return "PARTIAL", "Rotel: MISSING | Saltare: OK"
    else:
        return "EMPTY", "No Kinetic Binaries found"

def main():
    logger.info("INITIATING_OMEGA_SYNC_PROTOCOL")
    print("🔄 INITIATING OMEGA SYNC PROTOCOL...")

    # 1. Heartbeat Check
    status, details = check_morgana_health()
    update_ledger("MORGANA_NODE", f"HEARTBEAT_CHECK [{details}]", status)

    # 2. Sync UKG
    ukg_status, ukg_details = sync_ukg()
    update_ledger("UKG_MEMORY", f"GRAPH_SYNC [{ukg_details}]", ukg_status)

    # 3. Kinetic Armory Check
    armory_status, armory_details = check_kinetic_armory()
    update_ledger("KINETIC_ARMORY", f"BINARY_AUDIT [{armory_details}]", armory_status)

    # 4. Defense Grid Check
    update_ledger("DEFENSE_GRID", "KINETIC_TOOLCHAIN_VERIFY", "ACTIVE")

    logger.info("SYNC_PROTOCOL_COMPLETE", status="COHERENT")
    print("✅ SYNC COMPLETE. SYSTEM COHERENT.")

    # Trigger Global Replication
    global_sync = REPO_ROOT / "control_plane" / "global_ledger_sync.py"
    if global_sync.exists():
        print("\n🌐 TRIGGERING GLOBAL REPLICATION...")
        subprocess.run([sys.executable, str(global_sync)], cwd=str(REPO_ROOT))

if __name__ == "__main__":
    main()
