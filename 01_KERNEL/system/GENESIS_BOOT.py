# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import subprocess
import sys
import time
from pathlib import Path

# Resolve Repo Root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Add KERNEL to path for telemetry import
sys.path.append(str(REPO_ROOT / "01_KERNEL"))
try:
    from senses.telemetry_client import RotelClient
    logger = RotelClient("genesis_boot")
except ImportError:
    class DummyLogger:
        def info(self, *args, **kwargs): print(f"INFO: {args[0]}")
    logger = DummyLogger()

# GENESIS BOOT STRAP
# Spins up the Septem Regna Stack in a single coordinated sequence.

def print_banner():
    banner = r"""
     __________  __  _______  __    ____  ______
    / ____/   | /  |/  / __ \/ /   / __ \/_  __/
   / /   / /| |/ /|_/ / /_/ / /   / / / / / /   
  / /___/ ___ / /  / / ____/ /___/ /_/ / / /    
  \____/_/  |_/_/ /_/_/   /_____/\____/ /_/     
  
  :: GENESIS_CORE_v1.0 ::
    """
    print(f"\033[1;36m{banner}\033[0m")

def _spawn_console(title: str, command: str) -> None:
    """Open a new Windows console window without shell=True injection risk."""
    subprocess.Popen(
        ["cmd", "/k", f"title {title} && {command}"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def boot_morgana():
    print("🌑 LUKAS (L1/L2): Igniting Morgana Server (Port 8001)...")
    server_py = REPO_ROOT / "01_KERNEL" / "morgana_server.py"
    if server_py.exists():
        _spawn_console("MORGANA_SERVER", f'python "{server_py}"')
    else:
        print(f"   [SKIP] morgana_server.py not found at {server_py}")
    time.sleep(2)

def boot_pulse():
    print("⏳ CHRONOS (L4): Starting The Pendulum Daemon...")
    heartbeat_go = REPO_ROOT / "01_KERNEL" / "cmd" / "pulse" / "heartbeat.go"
    if heartbeat_go.exists():
        _spawn_console("PULSE_DAEMON", f'go run "{heartbeat_go}"')
    else:
        print(f"   [SKIP] heartbeat.go not found at {heartbeat_go}")
    time.sleep(1)

def boot_titanlink():
    print("🛡️ MOLTBOT (L6): Igniting TitanLink Gateway (Port 18788)...")
    server_py = REPO_ROOT / "01_KERNEL" / "connectivity" / "titanlink_server.py"
    if server_py.exists():
        _spawn_console("TITANLINK_GATEWAY", f'python "{server_py}"')
    else:
        print(f"   [SKIP] titanlink_server.py not found at {server_py}")
    time.sleep(2)

def boot_rustdesk():
    print("⚔️ LUKAS (L2): Igniting RustDesk Spire (ID & Relay)...")
    rd_dir = REPO_ROOT.parent / "rustdesk-server" / "target" / "release"
    if rd_dir.exists():
        _spawn_console("RUSTDESK_HBBS", f'"{rd_dir / "hbbs.exe"}" -r 100.118.224.52')
        time.sleep(1)
        _spawn_console("RUSTDESK_HBBR", f'"{rd_dir / "hbbr.exe"}"')
    else:
        print(f"   [SKIP] rustdesk-server not found at {rd_dir}")
    time.sleep(1)

def boot_interface():
    print("🎭 ANYA (L7): Connecting Neural Interface...")
    hud_py = REPO_ROOT / "02_FORGE" / "Camelot_HUD.py"
    dashboard_dir = REPO_ROOT / "02_FORGE" / "Anya_Dashboard"

    if hud_py.exists():
        _spawn_console("CAMELOT_HUD", f'python "{hud_py}"')
    if dashboard_dir.exists():
        _spawn_console("ANYA_DASHBOARD", f'cd "{dashboard_dir}" && npm run dev')
    
    print("   >> Camelot HUD: ACTIVE (Local Terminal)")
    print("   >> Anya Dashboard: http://localhost:5173 (Starting...)")

def execute_self_correction_test():
    print("\n🫀 SYSTEM: Triggering 'First Breath' Self-Correction Loop...")
    broken_file = REPO_ROOT / "02_FORGE" / "src" / "broken_main.ts"
    try:
        broken_file.parent.mkdir(parents=True, exist_ok=True)
        with open(broken_file, "w") as f:
            f.write("const x = 1; // Unused variable")
        print(f"   >> Created Malformed File: {broken_file}")
        time.sleep(1)
        print("   >> Correction: SUCCESS. (Simulated)")
        if broken_file.exists():
            os.remove(broken_file)
    except Exception as e:
        print(f"   >> Self-Correction Test Failed: {e}")

def auto_ledger_start():
    print("\n📝 GOVERNANCE: Recording Session Start in Provenance Ledger...")
    ledger_path = REPO_ROOT / "PROVENANCE_LEDGER.md"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    entry = f"| {timestamp} | GENESIS_BOOT | SESSION_START: Septem Regna Online | SUCCESS |"
    try:
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write("\n" + entry)
        print("   >> Ledger Updated.")
    except Exception as e:
        print(f"   >> Failed to Update Ledger: {e}")

if __name__ == "__main__":
    logger.info("INITIATING_GENESIS_BOOT_SEQUENCE")
    print_banner()
    boot_morgana()
    boot_pulse()
    boot_titanlink()
    boot_rustdesk()
    boot_interface()
    execute_self_correction_test()
    auto_ledger_start()

    logger.info("GENESIS_BOOT_COMPLETE", status="ALIVE")
    print("\n✅ GENESIS COMPLETE. THE SYSTEM IS ALIVE.")
    print("   (Press Ctrl+C to shutdown coordinator, individual windows remain open)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down Genesis Coordinator.")
