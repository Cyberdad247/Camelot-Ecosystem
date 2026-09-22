#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""AWAKEN — Universal Camelot-OS Bootstrap Entry Point

One word, one command, any platform, any shell, any IDE.
Runs the 6-phase //BOOT sequence (CLIProxy → Defense → Kinetic Edge → Cloud Brain → HUD → REPL).
"""

import argparse
import json
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add control_plane to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from control_plane.boot_sequence import _C

from control_plane import boot_sequence


BOOT_PROFILES = {
    "razor": {
        "name": "RAZOR SENTINEL (Thin Client)",
        "skip": "titan,local lt,octavian,clawdbot,bio-swarm,symbiotic",
    },
    "citadel": {
        "name": "HEADLESS CITADEL (VPS Apex)",
        "skip": "local lt,titan,octavian,bio-swarm,symbiotic,kitten,clawdbot",
    },
    "airgap": {
        "name": "SOVEREIGN AIR-GAP (Local Autonomous)",
        "skip": "",
    },
}

def _banner(mode: str | None = None):
    mode_label = f" [{BOOT_PROFILES[mode]['name']}]" if mode in BOOT_PROFILES else ""
    print(f"{_C['m']}{_C['B']}")
    print("+------------------------------------------------------------+")
    print(f"|  AWAKEN{mode_label.ljust(52)}|")
    print("|  ANYA_OMEGA - Anya First & Anya Last. Knight at the Helm. |")
    print("|  Global Boot: engines -> OmniRoute -> Hermes -> Cloud ->  |")
    print("|               Vizion Telemetry -> Sovereign Harness       |")
    print("|                (24/7)                                     |")
    print("+------------------------------------------------------------+")
    print(_C["x"])

def main():
    ap = argparse.ArgumentParser(prog="awaken", description="Universal Camelot-OS bootstrap")
    ap.add_argument("mode", nargs="?", default=None,
                    help="Boot profile mode: razor | airgap | citadel (or 'status')")
    ap.add_argument("--mode", choices=["razor", "airgap", "citadel"], default=None,
                    help="Boot profile mode")
    ap.add_argument("--status", action="store_true", help="Run boot phases, print status, exit")
    ap.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    ap.add_argument("--quick", action="store_true", help="Terse single-line summary")
    ap.add_argument("--snapshot", action="store_true",
                    help="Serve fresh boot_snapshot.json when ports still live (<ttl), else full boot")
    ap.add_argument("--snapshot-ttl", type=int, default=900,
                    help="Snapshot freshness in seconds (default 900)")
    ap.add_argument("--skip", default="",
                    help="Comma-separated phase substrings to skip (also AWAKEN_SKIP)")
    ap.add_argument("--no-hud", action="store_true", help="Skip HUD, enter REPL")
    ap.add_argument("--no-venv-bootstrap", action="store_true",
                    help="Don't auto-create venv if missing")
    args = ap.parse_args()

    # Handle mode positional vs flag vs status alias
    active_mode = args.mode if args.mode in BOOT_PROFILES else None
    if args.mode == "status":
        args.status = True
        active_mode = None

    # Bifrost gate
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import bifrost
        bifrost.enforce()
    except Exception as e:
        sys.stderr.write(f"{_C['r']}AWAKEN: bifrost gate refused caller: {e}{_C['x']}\n")
        sys.exit(77)

    home = boot_sequence._detect_home()
    os.environ["CAMELOT_OS_HOME"] = str(home)

    # Apply mode-specific phase skips
    if active_mode:
        mode_skip = BOOT_PROFILES[active_mode]["skip"]
        if mode_skip:
            prior = os.environ.get("AWAKEN_SKIP", "")
            merged = ",".join(t for t in [prior, mode_skip] if t)
            os.environ["AWAKEN_SKIP"] = merged

    if args.skip:
        prior = os.environ.get("AWAKEN_SKIP", "")
        merged = ",".join(t for t in [prior, args.skip] if t)
        os.environ["AWAKEN_SKIP"] = merged

    # Thread and memory bounds for host (caps BLAS thread pool allocations)
    for _k, _v in [
        ("OPENBLAS_NUM_THREADS", "2"),
        ("OMP_NUM_THREADS", "2"),
        ("MKL_NUM_THREADS", "2"),
        ("NUMEXPR_NUM_THREADS", "2"),
        ("VECLIB_MAXIMUM_THREADS", "2"),
    ]:
        os.environ.setdefault(_k, _v)

    # Phase 0: Machine-Actionable VKG Crystal Layer Gate
    crystal_bin = home / "bin" / ("camelot-vkg-crystal.exe" if sys.platform == "win32" else "camelot-vkg-crystal")
    if crystal_bin.exists():
        import subprocess
        res = subprocess.run([str(crystal_bin), "--verify"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0:
            sys.stderr.write(f"{_C['r']}AWAKEN: VKG Crystal gate verification failed:{_C['x']}\n{res.stderr or res.stdout}\n")
            sys.exit(78)
        else:
            if not args.quick and not args.json:
                print(f"{_C['g']}[VKG_CRYSTAL] All 6 machine-actionable layers verified.{_C['x']}")

    if args.snapshot:
        snap = boot_sequence.try_snapshot_boot(home, ttl_s=args.snapshot_ttl)
        if snap is not None:
            if args.json:
                print(json.dumps(snap, indent=2))
            else:
                s = snap.get("_summary", {})
                print(f"{_C['g']}AWAKEN (snapshot {s.get('snapshot_age_s', '?')}s old) "
                      f"{s.get('required_ok', '?')}/{s.get('required_total', '?')} required green{_C['x']}")
            sys.exit(0)

    if args.json:
        results = boot_sequence.run_boot(home, quick=True)
        print(json.dumps(results, indent=2))
        sys.exit(0 if all(v["ok"] for k, v in results.items() if not k.startswith("_")) else 1)

    if args.quick:
        results = boot_sequence.run_boot(home, quick=True)
        green = sum(1 for k, v in results.items() if not k.startswith("_") and v["ok"])
        total = sum(1 for k in results if not k.startswith("_"))
        color = _C["g"] if green == total else _C["y"]
        print(f"{color}AWAKEN {green}/{total} phases in {results['_total_ms']}ms{_C['x']}")
        sys.exit(0 if green == total else 1)

    _banner(mode=active_mode)
    results = boot_sequence.run_boot(home)
    total = sum(1 for k in results if not k.startswith("_"))
    green = sum(1 for k, v in results.items() if not k.startswith("_") and v["ok"])
    print()
    color = _C["g"] if green == total else _C["y"]
    print(f"  {color}{_C['B']}{green}/{total} phases green in {results['_total_ms']}ms{_C['x']}")

    if args.status:
        sys.exit(0 if green == total else 1)

    if not args.no_hud:
        hud_path = home / "03_VAULT" / "training" / "configs" / "hud.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("hud", hud_path)
        hud = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hud)
        try:
            hud.render_hud()
            hud.interactive_loop()
        except KeyboardInterrupt:
            print(f"\n{_C['d']}Awaken: session closed.{_C['x']}")
            sys.exit(0)

if __name__ == "__main__":
    main()
