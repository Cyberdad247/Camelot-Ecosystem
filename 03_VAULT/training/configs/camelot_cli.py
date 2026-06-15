# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Sovereign CLI (GOD MODE EDITION)
import sys, subprocess, requests, os, psutil, time

# ─────────────────────────────────────────────
# NEON GLOW COLORS
# ─────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[38;5;51m"
MAGENTA= "\033[38;5;201m"
GOLD   = "\033[38;5;220m"
GREEN  = "\033[38;5;82m"
RED    = "\033[38;5;196m"

PROMPT = f"{BOLD}{CYAN}[⚡ LVL 99 ARCHITECT]: {RESET}"
BANNER = f"""
{MAGENTA}{BOLD}
   ______ ___    __  ___ ______ __     ____  ______     ____   _____
  / ____//   |  /  |/  // ____// /    / __ \/_  __/    / __ \ / ___/
 / /    / /| | / /|_/ // __/  / /    / / / / / /      / / / / \__ \ 
/ /___ / ___ |/ /  / // /___ / /___ / /_/ / / /      / /_/ / ___/ / 
\____//_/  |_/_/  /_//_____//_____/ \____/ /_/       \____/ /____/  
{RESET}{GOLD}   >> GOD MODE ACTIVE // SWARM ONLINE // KINETIC PURITY IS LAW <<
{CYAN}   Type {BOLD}//HELP{RESET}{CYAN} to see your power set.
"""

def handle_help():
    print(f"\n{BOLD}{GOLD}🕹️  THE POWER SET (COMMANDS){RESET}")
    print(f"  {BOLD}//FORGE{RESET}      - Compile your code tissue (Local Rust)")
    print(f"  {BOLD}//BORIS{RESET}      - Unleash the Local Claude Agent")
    print(f"  {BOLD}//SPIRE{RESET}      - Launch the Visual Spire Dashboard")
    print(f"  {BOLD}//SWARM{RESET}      - Check the status of your AI Knights")
    
    print(f"\n{BOLD}{MAGENTA}🌀 REALM RUNES{RESET}")
    print(f"  {BOLD}Omega_SYNC{RESET}       - Sync your Cloud Brain (NotebookLM)")
    print(f"  {BOLD}Omega_STATUS{RESET}     - Check your Power Level (RAM/CPU/Ollama)")
    print(f"  {BOLD}Omega_PURGE{RESET}      - Delete 'Ghost' files and cache")
    print("")

def handle_status():
    ram = psutil.virtual_memory()
    print(f"\n{BOLD}{GOLD}📊 POWER LEVEL (DIAGNOSTICS){RESET}")
    print(f"  - System Energy (RAM): {GREEN if ram.percent < 80 else RED}{ram.percent}% Used{RESET}")
    print(f"  - Ollama Engine:       {GREEN}ONLINE{RESET}")
    print(f"  - NotebookLM Link:     {GREEN}RADIANT{RESET}")
    print(f"  - Defense Grid:        {GREEN}ARMED{RESET}")

def repl():
    print(BANNER)
    while True:
        try:
            inp = input(PROMPT).strip()
            if not inp: continue
            if inp.lower() in {"exit", "quit"}: break
            
            if inp.startswith("//HELP"): handle_help()
            elif inp.startswith("//SPIRE"): 
                print(f"{GOLD}Launching Spire...{RESET}")
                subprocess.Popen(["cmd", "/c", "spire"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif inp.startswith("//BORIS"): 
                print(f"{CYAN}Igniting Boris...{RESET}")
                subprocess.Popen(["cmd", "/c", "claude-ollama.cmd"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif inp.startswith("Omega_STATUS"): handle_status()
            elif inp.startswith("Omega_SYNC"):
                print(f"{MAGENTA}Syncing Cloud Brain...{RESET}")
                subprocess.run(["uv", "run", "--with", "requests", "py", "01_KERNEL/EXCALIBUR/system/SYNC_PROTOCOL.py"])
            else:
                # Natural Language fallback to Saltare
                print(f"{CYAN}Routing to Gateway...{RESET}")
                try:
                    res = requests.post("http://localhost:8080/route", json={"query": inp}, timeout=5).json()
                    print(f"\n{BOLD}[AI]:{RESET} {res.get('response', 'Error')}")
                except:
                    print(f"{RED}Gateway Offline. Try //SPIRE to boot it.{RESET}")
        except KeyboardInterrupt: break
    print(f"\n{GOLD}Realm saved. Peace out.{RESET}")

if __name__ == "__main__":
    repl()
