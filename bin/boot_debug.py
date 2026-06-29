#!/usr/bin/env python3
"""Debug boot hang — runs all phases with live timestamps."""
import os
import sys
import time
from pathlib import Path

os.environ["CAMELOT_BRIDGE_PRELOAD_TIMEOUT"] = "0"
os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from control_plane import boot_sequence

home = boot_sequence._detect_home()
os.environ["CAMELOT_OS_HOME"] = str(home)

import importlib.util

hud_path = home / "03_VAULT" / "training" / "configs" / "hud.py"
spec = importlib.util.spec_from_file_location("hud", hud_path)
hud_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hud_mod)

phases = [
    {"name": "CLIProxyAPI   :8080", "fn": hud_mod._boot_cliproxy},
    {"name": "Defense Grid",        "fn": hud_mod._boot_defense_grid},
    {"name": "Kinetic Edge  :3001", "fn": hud_mod._boot_kinetic_edge},
    {"name": "OmniVoice     :3002", "fn": lambda: boot_sequence.boot_omnivoice_router(home)},
    {"name": "Kitten TTS    :8300", "fn": lambda: boot_sequence.boot_kitten_tts(home)},
    {"name": "Sir Octavian  :8400", "fn": lambda: boot_sequence.boot_sir_octavian(home)},
    {"name": "Morgana Bridge :8001", "fn": lambda: boot_sequence.boot_morgana_bridge(home)},
    {"name": "Local LT Mem  :8200", "fn": lambda: boot_sequence.start_local_lt_memory(home)},
    {"name": "Cloud Brain Auth",    "fn": lambda: boot_sequence.boot_cloud_brain_auth(home)},
    {"name": "Cloud Brain   (RPC)", "fn": lambda: boot_sequence.boot_cloud_brain(home)},
    {"name": "Warp Workflow Sync",  "fn": lambda: boot_sequence.sync_warp_workflows(home)},
    {"name": "Symbiotic Maint.",    "fn": lambda: boot_sequence.boot_symbiotic_maintenance(home, quick=True)},
    {"name": "Codex Integration",   "fn": lambda: boot_sequence.boot_codex_integration(home)},
    {"name": "Clawdbot  :18789",    "fn": lambda: boot_sequence.boot_clawdbot_gateway(home)},
    {"name": "Sir Pi   [PI]",       "fn": lambda: boot_sequence.boot_sir_pi(home)},
    {"name": "Warp Terminal",       "fn": boot_sequence.launch_warp},
    {"name": "Knight Config Sync",  "fn": lambda: boot_sequence.sync_knight_configuration(home)},
    {"name": "Vizion Telemetry",    "fn": lambda: boot_sequence.boot_telemetry(home)},
    {"name": "Sovereign Harness",   "fn": lambda: boot_sequence.boot_harness(home)},
    {"name": "Bio-Swarm (Nano)",    "fn": lambda: boot_sequence.boot_bioswarm(home)},
    {"name": "Edge PWA      :3000", "fn": lambda: boot_sequence.boot_edge_interface(home)},
]

t_total = time.perf_counter()
for phase in phases:
    label = phase["name"]
    print(f"  START {label}", flush=True)
    t0 = time.perf_counter()
    try:
        ok, msg = phase["fn"]()
        dt = round((time.perf_counter() - t0) * 1000)
        glyph = "OK  " if ok else "WARN"
        print(f"  {glyph} {label}  {msg}  ({dt}ms)", flush=True)
    except Exception as exc:
        dt = round((time.perf_counter() - t0) * 1000)
        print(f"  ERR  {label}  {type(exc).__name__}: {exc}  ({dt}ms)", flush=True)

total_ms = round((time.perf_counter() - t_total) * 1000)
print(f"\nAll phases complete in {total_ms}ms", flush=True)
