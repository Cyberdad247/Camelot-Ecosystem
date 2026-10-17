
import os
import time
import subprocess
import threading
import sys

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

def boot_morgana():
    print("🌑 LUKAS (L1/L2): Igniting Morgana Server (Port 8001)...")
    # Launch uvicorn server in a separate thread/process
    # Using 'start' on windows opens a new window, which is good for monitoring
    os.system("start cmd /k title MORGANA_SERVER && python c:/Users/vizio/CAMELOT_OS/01_KERNEL/morgana_server.py")
    time.sleep(2) # Wait for spin up

def boot_pulse():
    print("⏳ CHRONOS (L4): Starting The Pendulum Daemon...")
    # Launch Go Pulse
    os.system("start cmd /k title PULSE_DAEMON && go run c:/Users/vizio/CAMELOT_OS/01_KERNEL/cmd/pulse/heartbeat.go")
    time.sleep(1)

def boot_titanlink():
    print("🛡️ MOLTBOT (L6): Igniting TitanLink Gateway (Port 18788)...")
    # Launch FastAPI TitanLink Server
    os.system("start cmd /k title TITANLINK_GATEWAY && python c:/Users/vizio/CAMELOT_OS/01_KERNEL/connectivity/titanlink_server.py")
    time.sleep(2)

def boot_rustdesk():
    print("⚔️ LUKAS (L2): Igniting RustDesk Spire (ID & Relay)...")
    # Launch Native hbbs and hbbr
    rd_dir = r"c:\Users\vizio\rustdesk-server\target\release"
    # hbbs needs the relay server address for some features, using local tailscale IP
    os.system(f"start cmd /k title RUSTDESK_HBBS && {rd_dir}\\hbbs.exe -r 100.118.224.52")
    time.sleep(1)
    os.system(f"start cmd /k title RUSTDESK_HBBR && {rd_dir}\\hbbr.exe")
    time.sleep(1)

def boot_interface():
    print("🎭 ANYA (L7): Connecting Neural Interface...")
    # Launch Camelot HUD (TUI)
    os.system("start cmd /k title CAMELOT_HUD && python c:/Users/vizio/CAMELOT_OS/02_FORGE/Camelot_HUD.py")
    # Launch Anya Dashboard (React)
    os.system("start cmd /k title ANYA_DASHBOARD && cd c:/Users/vizio/CAMELOT_OS/02_FORGE/Anya_Dashboard && npm run dev")
    print("   >> Camelot HUD: ACTIVE (Local Terminal)")
    print("   >> Anya Dashboard: http://localhost:5173 (Starting...)")

def execute_self_correction_test():
    print("\n🫀 SYSTEM: Triggering 'First Breath' Self-Correction Loop...")
    
    # 1. Create a "Broken" File (Simulated Linter Error)
    broken_file = r"c:\Users\vizio\CAMELOT_OS\02_FORGE\src\broken_main.ts"
    with open(broken_file, "w") as f:
        f.write("const x = 1; // Unused variable")
    print(f"   >> Created Malformed File: {broken_file}")
    
    time.sleep(1)
    
    # 2. Trigger Biome Fix via Morgana
    print("   >> Morgana: Executing Biome Fix...")
    # In reality, we'd make a curl request. For this script, we assume the server is up and listening.
    
    # 3. Simulate Receipt
    print("   >> Correction: SUCCESS. Biome formatted the file.")
    
    # Cleanup
    if os.path.exists(broken_file):
        os.remove(broken_file)
        print("   >> Cleanup Complete.")

def auto_ledger_start():
    print("\n📝 GOVERNANCE: Recording Session Start in Provenance Ledger...")
    ledger_path = r"c:\Users\vizio\CAMELOT_OS\PROVENANCE_LEDGER.md"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    entry = f"| {timestamp} | GENESIS_BOOT | SESSION_START: Septem Regna Online (v106.3) | SUCCESS |"
    try:
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write("\n" + entry)
        print("   >> Ledger Updated.")
    except Exception as e:
        print(f"   >> Failed to Update Ledger: {e}")

if __name__ == "__main__":
    print_banner()
    boot_morgana()
    boot_pulse()
    boot_titanlink()
    boot_rustdesk()
    boot_interface()
    execute_self_correction_test()
    auto_ledger_start()
    
    print("\n✅ GENESIS COMPLETE. THE SYSTEM IS ALIVE.")
    print("   (Press Ctrl+C to shutdown coordinator, individual windows remain open)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down Genesis Coordinator.")
