"""
Fusion Cockpit — Universal Cockpit Fusion (L7 Ethereal)
======================================================
Fuses superior cockpit UI logic into the Omni-Eye Dashboard.
Visualizes the Graph of Thoughts (GoT) and multi-agent Vox HUD.
Copyright (c) 2026 Invisioned Marketing inc. All Rights Reserved.
"""

import sys
import os
import asyncio
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional

# Add CAMELOT_OS to path to import control_plane.st_brain
CAMELOT_ROOT = "C:\\Users\\vizio\\CAMELOT_OS"
if CAMELOT_ROOT not in sys.path:
    sys.path.append(CAMELOT_ROOT)

from rich.text import Text
from rich.panel import Panel
from rich.table import Table

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log, Input, Label, DataTable, Tree, ProgressBar, TabbedContent, TabPane
from textual.containers import Container, Horizontal, Vertical, Grid, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message

# Import Short-Term Brain (ST-Memory)
try:
    from control_plane.st_brain import st_brain
except ImportError:
    st_brain = None

class GraphOfThoughts(Tree):
    """Visualizes the hierarchy of agent reasoning steps."""
    def on_mount(self) -> None:
        self.root.expand()
        self.border_title = "🧠 GRAPH OF THOUGHTS"
        
    def update_thoughts(self, thoughts: List[Dict]):
        self.clear()
        node_map = {}
        for t in thoughts:
            label = f"[{t.get('type', 'INFO')}] {t.get('label', 'Thought')}"
            parent_id = t.get('parent')
            if parent_id and parent_id in node_map:
                node = node_map[parent_id].add(label, expand=True)
            else:
                node = self.root.add(label, expand=True)
            node_map[t.get('id')] = node

class VoxHUD(Static):
    """Visual 'Voice Bar' for Knights that pulses during synthesis events."""
    anya_pulse = reactive(0)
    boris_pulse = reactive(0)
    merlin_pulse = reactive(0)

    def render(self) -> Panel:
        def get_bar(val: int, color: str) -> str:
            bar_len = min(20, int(val) // 5)
            return f"[{color}]" + "█" * bar_len + "░" * (20 - bar_len) + f"[/] {val}%"

        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column()
        grid.add_row("ANYA Ω  ", get_bar(self.anya_pulse, "magenta"))
        grid.add_row("BORIS Ω ", get_bar(self.boris_pulse, "cyan"))
        grid.add_row("MERLIN Ω", get_bar(self.merlin_pulse, "yellow"))

        return Panel(grid, title="[bold]Multi-Agent Vox HUD[/]", border_style="blue")

class SystemLattice(Static):
    """System status, RAM, and active cartridges."""
    ram_usage = reactive(0.0)
    status = reactive("RADIANT")

    def render(self) -> Panel:
        status_color = "green" if self.status == "RADIANT" else "yellow"
        usage_color = "green" if self.ram_usage < 70 else "red"
        
        table = Table.grid(padding=(0, 1))
        table.add_row("LATTICE:", f"[{status_color}]{self.status}[/]")
        table.add_row("RAM:", f"[{usage_color}]{self.ram_usage:.1f}%[/]")
        table.add_row("UPTIME:", f"{time.strftime('%H:%M:%S')}")
        
        return Panel(table, title="[bold cyan]Col 1: LATTICE[/]", border_style="cyan")

class KineticFeed(Log):
    """Real-time file diffs and tool execution logs."""
    def on_mount(self) -> None:
        self.border_title = "Col 3: KINETIC"
        self.border_style = "green"

class FusionCockpit(App):
    """The Universal Fusion Cockpit for Camelot-OS."""
    CSS = """
    Screen {
        background: #000510;
    }
    #layout {
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 2fr 1.5fr;
        padding: 1;
    }
    .panel {
        height: 1fr;
        border: solid gray;
    }
    #vox_hud {
        height: 7;
        margin-bottom: 1;
    }
    #intent_box {
        dock: bottom;
        height: 3;
        border: tall magenta;
    }
    """

    BINDINGS = [
        ("q", "quit", "Exit Cockpit"),
        ("r", "refresh", "Force Sync"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="layout"):
            with Vertical():
                yield SystemLattice(id="lattice")
                yield Static(Panel("Active Cartridges:\n- AETHER_ROUTING\n- KINETIC_STACK\n- VOX_SYNTH", title="CARTRIDGES", border_style="yellow"))
                yield VoxHUD(id="vox_hud")
            
            with Vertical():
                yield GraphOfThoughts("ROOT_INTENT: //PLAN upgrade_hud", id="got")
                yield Log(id="heart_log")
            
            yield KineticFeed(id="kinetic")
            
        yield Input(placeholder="Enter Fusion Intent...", id="intent_box")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "OMNI-EYE | FUSION COCKPIT v7.0"
        self.set_interval(1.0, self.update_state)
        self.query_one("#heart_log").write("FUSION_CORE: Active. Ready for Intent.")
        
        # Initial GoT
        got = self.query_one("#got")
        got.root.add("Node 1: Analyze Current Layout").add("Sub 1.1: Identify Overlaps")
        got.root.add("Node 2: Generate Fusion Plan")

        # Load Ledger Entries
        self.load_ledger()

    def load_ledger(self) -> None:
        """Read last 5 entries from PROVENANCE_LEDGER.md"""
        try:
            ledger_path = os.path.join(CAMELOT_ROOT, "PROVENANCE_LEDGER.md")
            if os.path.exists(ledger_path):
                with open(ledger_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    last_entries = [l.strip() for l in lines[-5:] if l.strip().startswith("|")]
                    kinetic = self.query_one("#kinetic")
                    for entry in last_entries:
                        kinetic.write(f"[LEDGER] {entry}")
        except Exception as e:
            self.query_one("#heart_log").write(f"LEDGER_ERROR: {e}")

    async def update_state(self) -> None:
        """Syncs UI state from Redis ST-Memory."""
        lattice = self.query_one("#lattice")
        vox = self.query_one("#vox_hud")
        
        if st_brain and st_brain.ping():
            try:
                # Real sync from ST-Brain
                real_ram = st_brain.retrieve_context("ram_usage")
                if real_ram is not None:
                    lattice.ram_usage = float(real_ram)
                else:
                    lattice.ram_usage = (lattice.ram_usage + random.uniform(0.1, 0.5)) % 100

                vox_pulses = st_brain.retrieve_context("vox_pulses")
                if vox_pulses and isinstance(vox_pulses, dict):
                    vox.anya_pulse = vox_pulses.get("anya", vox.anya_pulse)
                    vox.boris_pulse = vox_pulses.get("boris", vox.boris_pulse)
                    vox.merlin_pulse = vox_pulses.get("merlin", vox.merlin_pulse)
                else:
                    vox.anya_pulse = random.randint(20, 80)
                    vox.boris_pulse = random.randint(10, 60)
                    vox.merlin_pulse = random.randint(5, 40)
                
                # Check for new kinetic events
                recent_ledger = st_brain.retrieve_context("recent_ledger_entries")
                if recent_ledger and isinstance(recent_ledger, list):
                    kinetic = self.query_one("#kinetic")
                    for entry in recent_ledger:
                        kinetic.write(f"[ST-BRAIN] {entry}")
                        
            except Exception as e:
                self.query_one("#heart_log").write(f"SYNC_ERROR: {e}")
        else:
            # Fallback to simulation if Redis is down
            lattice.ram_usage = (lattice.ram_usage + random.uniform(0.1, 0.5)) % 100
            vox.anya_pulse = random.randint(20, 80)
            vox.boris_pulse = random.randint(10, 60)
            vox.merlin_pulse = random.randint(5, 40)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user intent input."""
        intent = event.value
        if intent:
            self.query_one("#heart_log").write(f"INTENT: {intent}")
            self.query_one("#kinetic").write(f"[EXEC] Intent registered: {intent}")
            
            # If st_brain is active, we could push this intent to Redis
            if st_brain and st_brain.ping():
                try:
                    st_brain.store_context("last_intent", {"intent": intent, "ts": time.time()})
                except Exception:
                    pass
                    
            event.input.value = ""

if __name__ == "__main__":
    app = FusionCockpit()
    app.run()
