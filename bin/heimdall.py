#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""
🛡️ SIR HEIMDALL — Guardian of the Bifrost Bridge
CAMELOT Apex OS v400 | Universal Network Dashboard

Usage:
    uv run --with rich --with psutil --with requests python heimdall.py
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil

# Try importing Rich components
try:
    from rich import box
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("Rich library required: pip install rich")
    sys.exit(1)

# Paths and Constants
CAMELOT_HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
BIFROST_PY = CAMELOT_HOME / "bin" / "bifrost.py"
MANIFEST_PATH = CAMELOT_HOME / "logs" / "switchboard_manifest.json"
console = Console()

# --- 🏹 HEIMDALL LOGIC ---

def get_bifrost_identity():
    """Query the bifrost.py gate for local identity status."""
    try:
        # Use uv run to ensure dependencies of bifrost.py are met if needed
        result = subprocess.run(
            ["uv", "run", "python", str(BIFROST_PY)],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # First line is usually the JSON status report
            return json.loads(result.stdout.splitlines()[0])
    except Exception:
        pass
    return {"token_present": False, "owner": "Unknown", "hostname": "Unknown"}

def get_relay_status():
    """Check for active Rust relay processes (hbbs, hbbr)."""
    status = {"hbbs": "OFFLINE", "hbbr": "OFFLINE", "rustdesk": "OFFLINE"}
    for proc in psutil.process_iter(['name']):
        name = proc.info['name'].lower()
        if "hbbs" in name: status["hbbs"] = "ONLINE"
        if "hbbr" in name: status["hbbr"] = "ONLINE"
        if "rustdesk" in name: status["rustdesk"] = "ONLINE"
    return status

def get_tailscale_peers():
    """Fetch live peer status from Tailscale."""
    try:
        result = subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            peers = []
            for _, peer in data.get("Peer", {}).items():
                peers.append({
                    "name": peer.get("HostName", "Unknown"),
                    "ip": peer.get("TailscaleIPs", [""])[0],
                    "status": "ONLINE" if peer.get("Online", False) else "OFFLINE",
                    "os": peer.get("OS", "Unknown")
                })
            return peers
    except Exception:
        pass
    return []

def get_switchboard():
    """Read the active LLM terminals from the Switchboard."""
    try:
        if MANIFEST_PATH.exists():
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("terminals", {})
    except Exception:
        pass
    return {}

# --- 🖼️ UI COMPONENTS ---

def build_header():
    """The radiant header of Sir Heimdall."""
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right")
    
    title = Text.from_markup("[bold bright_yellow]🛡️ SIR HEIMDALL[/] [dim]|[/] [cyan]GUARDIAN OF THE BIFROST BRIDGE[/]")
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    grid.add_row(title, f"[dim]{time_str}[/]")
    return Panel(grid, style="bright_yellow", box=box.ROUNDED)

def build_identity_panel(ident):
    """Local identity status."""
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold cyan")
    table.add_column()
    
    status_color = "green" if ident.get("token_present") else "red"
    token_status = f"[{status_color}]PRESENT[/]" if ident.get("token_present") else "[red]MISSING[/]"
    
    table.add_row("Identity:", ident.get("owner", "N/A"))
    table.add_row("Host:", ident.get("hostname", "N/A"))
    table.add_row("Token:", token_status)
    
    return Panel(table, title="[bold]Sovereign Identity[/]", border_style="cyan")

def build_relay_panel(relay):
    """Rust relay status."""
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold magenta")
    table.add_column()
    
    def color(s): return "green" if s == "ONLINE" else "red"
    
    table.add_row("HBBS (ID):", f"[{color(relay['hbbs'])}]{relay['hbbs']}[/]")
    table.add_row("HBBR (Relay):", f"[{color(relay['hbbr'])}]{relay['hbbr']}[/]")
    table.add_row("RustDesk:", f"[{color(relay['rustdesk'])}]{relay['rustdesk']}[/]")
    
    return Panel(table, title="[bold]Rust Bifrost Relay[/]", border_style="magenta")

def build_peer_table(peers):
    """Live Tailnet nodes."""
    table = Table(box=box.SIMPLE, expand=True)
    table.add_column("Node Name", style="bold white")
    table.add_column("Tailnet IP", style="dim")
    table.add_column("OS", style="dim")
    table.add_column("Status", justify="right")
    
    for p in peers:
        status_style = "bold green" if p["status"] == "ONLINE" else "dim red"
        table.add_row(p["name"], p["ip"], p["os"], f"[{status_style}]{p['status']}[/]")
        
    return Panel(table, title="[bold]Tailnet Peer Grid[/]", border_style="blue")

def build_terminal_table(terminals):
    """Switchboard terminals."""
    table = Table(box=box.SIMPLE, expand=True)
    table.add_column("Terminal", style="bold cyan")
    table.add_column("Engine", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Capability", style="italic grey50")
    
    for tid, data in terminals.items():
        status = data.get("status", "unknown")
        style = "green" if status in ("live", "assumed_live") else "red"
        caps = ", ".join(data.get("capability", [])[:2])
        table.add_row(tid.replace("sir_", ""), data.get("engine", "?"), f"[{style}]{status.upper()}[/]", caps)
        
    return Panel(table, title="[bold]LLM Terminal Switchboard[/]", border_style="bright_blue")

# --- 🚀 MAIN LOOP ---

def main():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2)
    )
    
    layout["left"].split_column(
        Layout(name="identity", size=7),
        Layout(name="relay", size=7)
    )
    
    layout["right"].split_column(
        Layout(name="peers", ratio=1),
        Layout(name="terminals", ratio=1)
    )

    with Live(layout, refresh_per_second=1, screen=True):
        while True:
            # Gather Data
            ident = get_bifrost_identity()
            relay = get_relay_status()
            peers = get_tailscale_peers()
            terminals = get_switchboard()
            
            # Update UI
            layout["header"].update(build_header())
            layout["identity"].update(build_identity_panel(ident))
            layout["relay"].update(build_relay_panel(relay))
            layout["peers"].update(build_peer_table(peers))
            layout["terminals"].update(build_terminal_table(terminals))
            
            layout["footer"].update(Panel(
                Text.from_markup("[bold cyan]COMMANDS:[/] [white]Q: Quit | R: Re-probe | B: Open Bridge[/]"),
                box=box.ROUNDED, style="dim"
            ))
            
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
