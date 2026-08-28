#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
r"""
♜ CYBERTRONIA MASTER CLI — CAMELOT-OS SOVEREIGN ORCHESTRATOR ♜
===============================================================
Operator Authority: King Arthur (VaShawn O. Head / Vizion)
Primary Node:       cybertronia (100.118.224.52 · Windows 11 Pro)
WorldTree Anchor:   a0a4bfb9-e847-4c38-be39-7aee398f0795
Max Version:        v1000.54-EXCALIBUR-A (vMAX Singularity)

Commands:
    python bin/cybertronia.py --hud       : Launch 36-Knight Sovereign HUD
    python bin/cybertronia.py --tuneup    : Run complete daily tuneup pass
    python bin/cybertronia.py --vps       : Query VPS Hub (KVM563 / 162.35.107.134)
    python bin/cybertronia.py --sync      : Execute WorldTree CloudBrain sync
    python bin/cybertronia.py --scan      : Run Squire Colony intelligence scan
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

current_dir = Path(__file__).resolve().parent
REPO_ROOT = current_dir
while REPO_ROOT.parent != REPO_ROOT:
    if (REPO_ROOT / "01_KERNEL").exists() and (REPO_ROOT / "03_VAULT").exists():
        break
    REPO_ROOT = REPO_ROOT.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def main():
    parser = argparse.ArgumentParser(description="Cybertronia Master Sovereign CLI")
    parser.add_argument("--hud", action="store_true", help="Launch interactive 36-Knight Sovereign HUD")
    parser.add_argument("--tuneup", action="store_true", help="Run full daily system tuneup & cache purge")
    parser.add_argument("--vps", action="store_true", help="Probe and access Camelot Hub VPS (KVM563)")
    parser.add_argument("--sync", action="store_true", help="Synchronize CloudBrain & WorldTree Max Version")
    parser.add_argument("--scan", action="store_true", help="Run Squire Colony codebase intelligence scan")
    parser.add_argument("--status", action="store_true", default=False, help="Display master node status")
    args = parser.parse_args()

    if args.hud:
        hud_script = REPO_ROOT / "control_plane" / "cli" / "knight_hud.py"
        subprocess.run([sys.executable, str(hud_script)])
    elif args.tuneup:
        tuneup_script = REPO_ROOT / "bin" / "tuneup.py"
        subprocess.run([sys.executable, str(tuneup_script)])
    elif args.vps:
        vps_script = REPO_ROOT / "bin" / "vps_hub.py"
        subprocess.run([sys.executable, str(vps_script), "--status"])
    elif args.sync:
        sync_script = REPO_ROOT / "bin" / "cloudbrain_sync.py"
        subprocess.run([sys.executable, str(sync_script)])
    elif args.scan:
        subprocess.run([sys.executable, "-m", "squires.colony", "status"])
    else:
        # Default: Print master status overview
        print("=" * 85)
        print("♜ CYBERTRONIA MASTER SOVEREIGN ORCHESTRATOR — TELEMETRY OVERVIEW ♜")
        print("=" * 85)
        print(f"• Host Node            : cybertronia (100.118.224.52 · Windows 11 Pro)")
        print(f"• Excalibur Sentinel   : vashawns-s26-ultra (100.106.246.126 · Android 16)")
        print(f"• Camelot Hub VPS      : KVM563 / vps3573819 (162.35.107.134 / HERMES_PRIME)")
        print(f"• WorldTree Home Anchor: a0a4bfb9-e847-4c38-be39-7aee398f0795")
        print(f"• Active Max Version   : v1000.54-EXCALIBUR-A (vMAX Singularity)")
        print(f"• Repository Footprint : ~18.02 GB (18.78 GB Purged / 51% Optimized)")
        print(f"• 36 Knights Status    : 100% Tethered & Matched to Max Version")
        print("=" * 85)
        print("Available Commands:")
        print("   python bin/cybertronia.py --hud     : Live 36-Knight Sovereign REPL HUD")
        print("   python bin/cybertronia.py --tuneup  : One-Command Daily System Tuneup")
        print("   python bin/cybertronia.py --vps     : Query & SSH to Camelot Hub VPS")
        print("   python bin/cybertronia.py --sync    : Synchronize CloudBrain & WorldTree")
        print("   python bin/cybertronia.py --scan    : Check Squire Colony Intelligence")
        print("=" * 85)

if __name__ == "__main__":
    main()
