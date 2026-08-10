#!/usr/bin/env python3
"""AWAKEN — Universal Camelot-OS Bootstrap Entry Point

One word, one command, any platform, any shell, any IDE.
Runs the 6-phase //BOOT sequence (CLIProxy → Defense → Kinetic Edge → Cloud Brain → HUD → REPL).
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add control_plane to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from control_plane.boot_sequence import _C

from control_plane import boot_sequence


def _banner():
    print(f"{_C['m']}{_C['B']}")
    print("+------------------------------------------------------------+")
    print("|  AWAKEN - Camelot Apex OS v.999.3 (Sovereign Lattice)     |")
    print("|  SIR_BORIS v3.0 - One word. Any shell. Any platform.      |")
    print("|  Global Boot: engines -> OmniRoute -> Hermes -> Cloud ->  |")
    print("|               Vizion Telemetry -> Sovereign Harness       |")
    print("|                (24/7)                                     |")
    print("+------------------------------------------------------------+")
    print(_C["x"])

def main():
    ap = argparse.ArgumentParser(prog="awaken", description="Universal Camelot-OS bootstrap")
    ap.add_argument("--status", action="store_true", help="Run boot phases, print status, exit")
    ap.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    ap.add_argument("--quick", action="store_true", help="Terse single-line summary")
    ap.add_argument("--no-hud", action="store_true", help="Skip HUD, enter REPL")
    ap.add_argument("--no-venv-bootstrap", action="store_true",
                    help="Don't auto-create venv if missing")
    args = ap.parse_args()

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

    _banner()
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
