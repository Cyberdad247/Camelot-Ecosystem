#!/usr/bin/env python3
"""
NORTHSTAR Phase 1 — Service Launcher

Starts all three S3 services and keeps them alive:
  :3001  edge-router      (WebSocket forge/query gateway)
  :3002  omnivoice-router (WebRTC signaling + energy VAD)
  :8300  kitten_service   (chunked token-to-audio TTS streaming)

Usage:
  python scripts/start_northstar.py           # start all
  python scripts/start_northstar.py --check   # probe ports only
  python scripts/start_northstar.py --stop    # send SIGTERM to saved PIDs
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
ARMORY = HOME / "02_FORGE" / "KINETIC_ARMORY"
PID_FILE = HOME / "logs" / "northstar_pids.json"

SERVICES = [
    {
        "name": "edge-router",
        "port": 3001,
        "dir": ARMORY / "edge-router",
        "cmd": ["npx", "--yes", "ts-node", "edge-router.ts"],
        "log": HOME / "logs" / "edge-router.log",
    },
    {
        "name": "omnivoice-router",
        "port": 3002,
        "dir": ARMORY / "omnivoice-router",
        "cmd": ["npx", "--yes", "ts-node", "omnivoice-router.ts"],
        "log": HOME / "logs" / "omnivoice-router.log",
    },
    {
        "name": "kitten-service",
        "port": 8300,
        "dir": HOME / "01_KERNEL" / "senses" / "audio",
        "cmd": [sys.executable, "-c",
                "import asyncio, sys; sys.path.insert(0,'.'); "
                "from kitten_service import kitten_service; "
                "asyncio.run(kitten_service.run_streaming_server())"],
        "log": HOME / "logs" / "kitten-service.log",
    },
]


def probe(port: int, timeout: float = 0.5) -> bool:
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False


def check_ports() -> None:
    print("\n[NORTHSTAR] Port probe:")
    for svc in SERVICES:
        up = probe(svc["port"])
        status = "UP  ✅" if up else "DOWN ❌"
        print(f"  :{svc['port']}  {svc['name']:<20}  {status}")


def start_all() -> None:
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    pids: dict[str, int] = {}

    print("\n[NORTHSTAR] Starting S3 services...")
    for svc in SERVICES:
        name = svc["name"]
        port = svc["port"]

        if probe(port):
            print(f"  [{name}] :{port} already UP — skipping")
            continue

        log_path: Path = svc["log"]
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_fh = open(log_path, "a", encoding="utf-8")

        env = {**os.environ, "CAMELOT_OS_HOME": str(HOME)}
        proc = subprocess.Popen(
            svc["cmd"],
            cwd=str(svc["dir"]),
            stdout=log_fh,
            stderr=log_fh,
            env=env,
        )
        pids[name] = proc.pid
        print(f"  [{name}] :{port} started  pid={proc.pid}  log={log_path.name}")

    if pids:
        existing = json.loads(PID_FILE.read_text()) if PID_FILE.exists() else {}
        existing.update(pids)
        PID_FILE.write_text(json.dumps(existing, indent=2))

    # Wait for ports to come up
    print("\n[NORTHSTAR] Waiting for ports...")
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        ready = all(probe(s["port"]) for s in SERVICES)
        if ready:
            break
        time.sleep(1)

    check_ports()


def stop_all() -> None:
    if not PID_FILE.exists():
        print("[NORTHSTAR] No PID file found.")
        return
    pids: dict = json.loads(PID_FILE.read_text())
    for name, pid in pids.items():
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"  [{name}] SIGTERM → pid={pid}")
        except (ProcessLookupError, PermissionError) as e:
            print(f"  [{name}] pid={pid} not found ({e})")
    PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NORTHSTAR Phase 1 service launcher")
    parser.add_argument("--check", action="store_true", help="Probe ports only")
    parser.add_argument("--stop", action="store_true", help="Stop running services")
    args = parser.parse_args()

    if args.check:
        check_ports()
    elif args.stop:
        stop_all()
    else:
        start_all()
