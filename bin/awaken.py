#!/usr/bin/env python3
"""AWAKEN — Universal Camelot-OS Bootstrap Entry Point

One word, one command, any platform, any shell, any IDE.
Runs the 6-phase //BOOT sequence (CLIProxy → Defense → Kinetic Edge → Cloud Brain → HUD → REPL).

Usage:
    awaken              # full boot + interactive HUD
    awaken --status     # boot phases only, print status, exit
    awaken --json       # machine-readable status, exit
    awaken --no-hud     # skip HUD, enter REPL directly
    awaken --quick      # status-line only (single row, idempotent probes)

Environment:
    CAMELOT_OS_HOME     override auto-detected CAMELOT_OS root
    CAMELOT_VENV        override auto-detected venv python path
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

# ANSI escape (works on Win10+, Linux, macOS, VS Code, Cursor, JetBrains, etc.)
_C = {"g": "\033[92m", "y": "\033[93m", "r": "\033[91m", "c": "\033[96m",
      "m": "\033[95m", "b": "\033[94m", "w": "\033[97m", "d": "\033[2m",
      "x": "\033[0m", "B": "\033[1m"}

if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


def _detect_home() -> Path:
    env = os.environ.get("CAMELOT_OS_HOME")
    if env and Path(env).is_dir():
        return Path(env)
    candidates = [
        Path.home() / "CAMELOT_OS",
        Path("C:/Users/vizio/CAMELOT_OS"),
        Path(__file__).resolve().parent.parent,
    ]
    for c in candidates:
        if (c / "03_VAULT" / "training" / "configs" / "hud.py").exists():
            return c
    sys.stderr.write(f"{_C['r']}AWAKEN: Cannot locate CAMELOT_OS root.{_C['x']}\n"
                     "Set CAMELOT_OS_HOME env var or place Camelot at ~/CAMELOT_OS\n")
    sys.exit(2)


def _detect_venv_python(home: Path) -> Path:
    env = os.environ.get("CAMELOT_VENV")
    if env and Path(env).exists():
        return Path(env)
    system = platform.system()
    if system == "Windows":
        venv_py = home / ".venv_camelot" / "Scripts" / "python.exe"
    else:
        venv_py = home / ".venv_camelot" / "bin" / "python"
    if venv_py.exists():
        return venv_py
    # Fallback: current interpreter
    return Path(sys.executable)


def _ensure_venv(home: Path) -> Path:
    venv_py = _detect_venv_python(home)
    if venv_py.exists() and venv_py != Path(sys.executable):
        return venv_py
    sys.stderr.write(f"{_C['y']}AWAKEN: venv missing, bootstrapping…{_C['x']}\n")
    try:
        subprocess.run(["uv", "venv", str(home / ".venv_camelot"),
                        "--python", "3.13"], check=True, cwd=home)
        subprocess.run(["uv", "pip", "install", "--python", str(venv_py),
                        "notebooklm-py @ git+https://github.com/Cyberdad247/notebooklm-py.git@main",
                        "rich", "requests", "httpx"], check=True, cwd=home)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        sys.stderr.write(f"{_C['r']}AWAKEN: venv bootstrap failed: {e}{_C['x']}\n")
        return Path(sys.executable)
    return venv_py


def _load_hud(home: Path):
    hud_path = home / "03_VAULT" / "training" / "configs" / "hud.py"
    configs_dir = str(hud_path.parent)
    if configs_dir not in sys.path:
        sys.path.insert(0, configs_dir)
    spec = importlib.util.spec_from_file_location("hud", hud_path)
    hud = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hud)
    return hud


_STRIP_RICH = re.compile(r"\[/?[a-zA-Z_ ]*\]")


def _strip(msg: str) -> str:
    return _STRIP_RICH.sub("", msg).strip()


def _banner():
    print(f"{_C['m']}{_C['B']}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  AWAKEN — Camelot Apex OS v300.5 (Universal Singularity)    ║")
    print("║  SIR_BORIS v2.1 — One word. Any shell. Any platform.         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(_C["x"])


def _run_boot(home: Path, quick: bool = False) -> dict:
    hud = _load_hud(home)
    phases = [
        ("CLIProxyAPI   :8080", hud._boot_cliproxy),
        ("Defense Grid       ", hud._boot_defense_grid),
        ("Kinetic Edge  :3001", hud._boot_kinetic_edge),
        ("Cloud Brain   (RPC)", hud._boot_cloud_brain),
    ]
    results = {}
    t_total = time.perf_counter()
    for label, fn in phases:
        t0 = time.perf_counter()
        try:
            _, msg = fn()
            ok = not any(k in msg for k in ("[red]", "failed", "unreachable", "[yellow]"))
            clean = _strip(msg)
        except Exception as e:
            ok, clean = False, f"exception: {type(e).__name__}: {e}"
        dt = (time.perf_counter() - t0) * 1000
        results[label.strip()] = {"ok": ok, "msg": clean, "ms": round(dt)}
        if not quick:
            glyph = f"{_C['g']}✅{_C['x']}" if ok else f"{_C['y']}⚠ {_C['x']}"
            print(f"  {glyph} {_C['B']}{label}{_C['x']}  {clean}  {_C['d']}({dt:.0f}ms){_C['x']}")
    results["_total_ms"] = round((time.perf_counter() - t_total) * 1000)
    return results


def main():
    ap = argparse.ArgumentParser(prog="awaken", description="Universal Camelot-OS bootstrap")
    ap.add_argument("--status", action="store_true", help="Run boot phases, print status, exit")
    ap.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    ap.add_argument("--quick", action="store_true", help="Terse single-line summary")
    ap.add_argument("--no-hud", action="store_true", help="Skip HUD, enter REPL")
    ap.add_argument("--no-venv-bootstrap", action="store_true",
                    help="Don't auto-create venv if missing")
    args = ap.parse_args()

    # Bifrost gate — refuse unauthorized callers before touching anything.
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import bifrost
        reason = bifrost.enforce()
        if os.environ.get("AWAKEN_DEBUG"):
            sys.stderr.write(f"{_C['d']}bifrost: {reason}{_C['x']}\n")
    except Exception as e:
        sys.stderr.write(f"{_C['r']}AWAKEN: bifrost gate refused caller: {e}{_C['x']}\n")
        sys.exit(77)

    home = _detect_home()
    os.environ["CAMELOT_OS_HOME"] = str(home)
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    # Short-lived launcher modes detach spawned children so Kinetic Edge
    # outlives this process. Interactive mode keeps atexit cleanup.
    if args.status or args.json or args.quick or args.no_hud:
        os.environ["AWAKEN_DETACH_CHILDREN"] = "1"

    venv_py = _detect_venv_python(home)
    if (venv_py == Path(sys.executable).resolve()
            or str(venv_py) == sys.executable):
        pass
    elif venv_py.exists():
        os.execv(str(venv_py), [str(venv_py), str(Path(__file__).resolve()), *sys.argv[1:]])
    elif not args.no_venv_bootstrap:
        _ensure_venv(home)

    if args.json:
        results = _run_boot(home, quick=True)
        print(json.dumps(results, indent=2))
        all_ok = all(v["ok"] for k, v in results.items() if not k.startswith("_"))
        sys.exit(0 if all_ok else 1)

    if args.quick:
        results = _run_boot(home, quick=True)
        green = sum(1 for k, v in results.items() if not k.startswith("_") and v["ok"])
        total = sum(1 for k in results if not k.startswith("_"))
        total_ms = results["_total_ms"]
        color = _C["g"] if green == total else _C["y"]
        print(f"{color}AWAKEN {green}/{total} phases in {total_ms}ms{_C['x']}")
        sys.exit(0 if green == total else 1)

    _banner()
    results = _run_boot(home)
    total = sum(1 for k in results if not k.startswith("_"))
    green = sum(1 for k, v in results.items() if not k.startswith("_") and v["ok"])
    print()
    color = _C["g"] if green == total else _C["y"]
    print(f"  {color}{_C['B']}{green}/{total} phases green in {results['_total_ms']}ms{_C['x']}")

    if args.status:
        sys.exit(0 if green == total else 1)

    if not args.no_hud:
        hud = _load_hud(home)
        try:
            hud.render_hud()
            hud.interactive_loop()
        except KeyboardInterrupt:
            print(f"\n{_C['d']}Awaken: session closed.{_C['x']}")
            sys.exit(0)


if __name__ == "__main__":
    main()
