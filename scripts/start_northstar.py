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
import asyncio
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
            shell=(sys.platform == "win32"),
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


async def run_test_suite_async() -> bool:
    import websockets
    import aiohttp

    print("\n[NORTHSTAR TEST] Beginning system verification test suite...")

    # 1. Probe ports first to make sure they are active
    all_up = True
    for svc in SERVICES:
        if not probe(svc["port"]):
            print(f"  [ERROR] Port {svc['port']} for {svc['name']} is DOWN. Cannot run tests.")
            all_up = False
    if not all_up:
        return False

    passed = True

    # ── Test 1: WebSocket connection handshake completing under 200ms (Edge Router) ──
    print("\n[NORTHSTAR TEST] Test 1: WebSocket Edge Router Handshake (<200ms)")
    try:
        t0 = time.perf_counter()
        async with websockets.connect("ws://127.0.0.1:3001") as ws:
            handshake_time = (time.perf_counter() - t0) * 1000
            print(f"  [OK] Connected to Edge Router in {handshake_time:.2f}ms")

            # Send a ping
            await ws.send(json.dumps({"type": "ping"}))
            response = await ws.recv()
            resp_data = json.loads(response)
            if resp_data.get("status") == "pong":
                print("  [OK] Ping/Pong response received successfully")
            else:
                print(f"  [FAIL] Unexpected response: {response}")
                passed = False

            if handshake_time < 200:
                print("  [PASS] Handshake latency meets requirement of <200ms")
            else:
                print(f"  [FAIL] Handshake latency exceeds 200ms limit: {handshake_time:.2f}ms")
                passed = False
    except Exception as e:
        print(f"  [FAIL] WebSocket Edge Router test failed: {e}")
        passed = False

    # ── Test 2: VAD Interruption halts playback under 150ms ──
    print("\n[NORTHSTAR TEST] Test 2: VAD Interruption Halts Playback (<150ms)")
    try:
        # Connect client to omnivoice-router on port 3002
        async with websockets.connect("ws://127.0.0.1:3002") as ws:
            # We should receive welcome message
            welcome_raw = await ws.recv()
            welcome = json.loads(welcome_raw)
            peer_id = welcome.get("peer_id", "peer-test")
            print(f"  [OK] Connected to OmniVoice Router as peer {peer_id}")

            # Send some speech samples (high energy) to trigger speech detection
            # RMS threshold is 0.01. So if we send samples of 0.05, energy is 0.05 > 0.01.
            high_energy_samples = [0.05] * 2000

            # Record time right before sending speech frame
            t_send = time.perf_counter()
            await ws.send(json.dumps({
                "type": "data_frame",
                "samples": high_energy_samples
            }))

            # Now wait for the clear-signal broadcast from OmniVoice router
            # We expect a clear signal message like {"type": "clear"}
            # Set a timeout of 1 second
            response = await asyncio.wait_for(ws.recv(), timeout=1.0)
            interruption_latency = (time.perf_counter() - t_send) * 1000
            resp_data = json.loads(response)

            if resp_data.get("type") == "clear":
                print(f"  [OK] Received socket 'clear' signal in {interruption_latency:.2f}ms")
                if interruption_latency < 150:
                    print("  [PASS] Interruption latency meets requirement of <150ms")
                else:
                    print(f"  [FAIL] Interruption latency exceeds 150ms limit: {interruption_latency:.2f}ms")
                    passed = False
            else:
                print(f"  [FAIL] Did not receive 'clear' signal. Got: {response}")
                passed = False

    except Exception as e:
        print(f"  [FAIL] VAD Interruption test failed: {e}")
        passed = False

    return passed


def run_test_suite() -> None:
    any_down = any(not probe(svc["port"]) for svc in SERVICES)
    if any_down:
        print("[NORTHSTAR TEST] Some services are down. Starting all services first...")
        start_all()

    success = asyncio.run(run_test_suite_async())
    if success:
        print("\n🎉 ALL SYSTEM VERIFICATION TESTS PASSED SUCCESSFULLY! 🎉\n")
        sys.exit(0)
    else:
        print("\n❌ SYSTEM VERIFICATION TESTS FAILED! ❌\n")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NORTHSTAR Phase 1 service launcher")
    parser.add_argument("--check", action="store_true", help="Probe ports only")
    parser.add_argument("--stop", action="store_true", help="Stop running services")
    parser.add_argument("--test", action="store_true", help="Run E2E system integration tests")
    args = parser.parse_args()

    if args.check:
        check_ports()
    elif args.stop:
        stop_all()
    elif args.test:
        run_test_suite()
    else:
        start_all()
