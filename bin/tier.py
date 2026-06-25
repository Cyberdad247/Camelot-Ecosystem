#!/usr/bin/env python3
"""
Camelot-OS Universal Tier Controller.
Single CLI invoked by Claude Code, Gemini CLI, and Codex.

Usage:
    python tier.py <edge|local|cloud|all> <up|down|status>
"""
from __future__ import annotations

import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n")
    sys.exit(2)

REPO = Path(__file__).resolve().parent
CONFIG = REPO / "config" / "tiers.yaml"


def _load() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def _resolve(p: str) -> Path:
    return (REPO / p) if not Path(p).is_absolute() else Path(p)


def _tcp_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_ok(url: str, timeout: float = 5.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def status(name: str, t: dict) -> str:
    host = t.get("host", "127.0.0.1")
    port = t.get("port")
    if name == "cloud":
        url = t["endpoints"]["health"]
        return "UP" if _http_ok(url) else "DOWN (on-demand)"
    if port and _tcp_open(host, port):
        if t.get("health"):
            return "UP" if _http_ok(f"http://{host}:{port}{t['health']}") else "PORT-OPEN"
        return "UP"
    return "DOWN"


def up(name: str, t: dict) -> int:
    if name == "edge":
        exe = _resolve(t["binary"])
        if not exe.exists():
            exe = _resolve(t["source"])
        if not exe.exists():
            print(f"[edge] binary missing: {exe}"); return 1
        subprocess.Popen([str(exe)], cwd=str(REPO))
        print(f"[edge] launched {exe.name} on :{t['port']}"); return 0
    if name == "local":
        py = _resolve(t["python"])
        entry = _resolve(t["entry"])
        subprocess.Popen([str(py), str(entry)], cwd=str(REPO))
        print(f"[local] launched {entry.name} on :{t['port']}"); return 0
    if name == "cloud":
        cli = _resolve(t["modal_cli"])
        df = _resolve(t["deploy_file"])
        env = {"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", **__import__("os").environ}
        r = subprocess.run([str(cli), "deploy", str(df)], cwd=str(REPO), env=env)
        return r.returncode


def down(name: str, t: dict) -> int:
    if name == "cloud":
        cli = _resolve(t["modal_cli"])
        r = subprocess.run([str(cli), "app", "stop", t["modal_app"]], cwd=str(REPO))
        return r.returncode
    print(f"[{name}] down: use Ctrl+C or taskkill on the local process"); return 0


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__); return 2
    target, action = sys.argv[1], sys.argv[2]
    cfg = _load()
    tiers = cfg["tiers"]
    names = list(tiers.keys()) if target == "all" else [target]
    for n in names:
        if n not in tiers:
            print(f"unknown tier: {n}"); return 2
        t = tiers[n]
        if action == "status":
            print(f"{n:<6} {status(n, t)}")
        elif action == "up":
            up(n, t)
        elif action == "down":
            down(n, t)
        else:
            print(f"unknown action: {action}"); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
