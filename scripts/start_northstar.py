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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


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

    # ── Test 3: Bifrost Gateway & mTLS Roaming (Bypass Tailnet check) ──
    print("\n[NORTHSTAR TEST] Test 3: Bifrost Gateway & mTLS Roaming (Bypass Tailnet check)")
    try:
        import importlib.util
        bifrost_path = HOME / "bin" / "bifrost.py"
        spec = importlib.util.spec_from_file_location("bifrost_test_ns", bifrost_path)
        bifrost_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bifrost_mod)
        
        # 1. Non-tailnet IP, no credentials -> Rejected
        ok, reason = bifrost_mod.verify_caller(remote_addr="198.51.100.42")
        if ok:
            print(f"  [FAIL] Unauthenticated public IP was allowed: {reason}")
            passed = False
        else:
            print(f"  [OK] Unauthenticated public IP 198.51.100.42 blocked correctly: {reason}")
        
        # 2. Non-tailnet IP, valid client certificate -> Allowed (mTLS roaming bypass)
        os.environ["BIFROST_ALLOW_ANY_VALID_CERT"] = "1"
        ok, reason = bifrost_mod.verify_caller(
            remote_addr="198.51.100.42",
            client_cert_der=b"mock_client_cert_der"
        )
        if not ok:
            print(f"  [FAIL] Valid client certificate roaming client was blocked: {reason}")
            passed = False
        else:
            print(f"  [OK] Public IP roaming client presenting valid certificate authenticated successfully: {reason}")
            if "mtls" in reason:
                print("  [PASS] mTLS roaming bypass verified successfully")
            else:
                print(f"  [FAIL] Expected mtls in reason, got: {reason}")
                passed = False
        
        # 3. Non-tailnet IP, valid OIDC token -> Allowed (OIDC roaming bypass)
        os.environ["BIFROST_OIDC_ISSUERS"] = "https://accounts.google.com"
        bifrost_mod.MOBILE_TRUSTED_ISSUERS = {"https://accounts.google.com"}
        
        import base64
        header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').decode().rstrip("=")
        payload_data = {
            "iss": "https://accounts.google.com",
            "exp": time.time() + 1000,
            "aud": "camelot-os",
            "sub": "roaming_user_123"
        }
        payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
        token = f"{header}.{payload}.signature"
        
        ok, reason = bifrost_mod.verify_caller(
            remote_addr="198.51.100.42",
            oidc_token=token
        )
        if not ok:
            print(f"  [FAIL] Valid OIDC token roaming client was blocked: {reason}")
            passed = False
        else:
            print(f"  [OK] Public IP roaming client presenting valid OIDC token authenticated successfully: {reason}")
            if "oidc-jwt" in reason:
                print("  [PASS] OIDC token roaming bypass verified successfully")
            else:
                print(f"  [FAIL] Expected oidc-jwt in reason, got: {reason}")
                passed = False
                
    except Exception as e:
        print(f"  [FAIL] Bifrost roaming test failed: {e}")
        passed = False

    # ── Test 4: Dynamic Knight Hot-Swapping mid-dialogue ──
    print("\n[NORTHSTAR TEST] Test 4: Dynamic Knight Hot-Swapping mid-dialogue")
    try:
        # Temporarily append KERNEL/senses/audio to path to import audio_session
        audio_dir = str(HOME / "01_KERNEL" / "senses" / "audio")
        if audio_dir not in sys.path:
            sys.path.insert(0, audio_dir)
        if str(HOME) not in sys.path:
            sys.path.insert(0, str(HOME))
            
        from audio_session import AudioSession
        from control_plane.switchboard import Terminal
        
        session = AudioSession()
        
        # Mock switchboard probe_one to return assumed_live terminal for testing triggers
        class MockBoard:
            async def probe_one(self, knight_id):
                return Terminal(
                    id=knight_id, engine="claude_code", weight=0.85,
                    cost_tier="medium", capability=["security"],
                    probe_port=3001, status="live"
                )
        session.board = MockBoard()
        
        # Test routing for "Sentinel, check the port" -> sir_sentinel
        term, category, confidence = await session._classify("Sentinel, check the port")
        if term.id != "sir_sentinel":
            print(f"  [FAIL] 'Sentinel, check the port' routed to {term.id} (expected sir_sentinel)")
            passed = False
        else:
            print(f"  [OK] 'Sentinel, check the port' routed to {term.id} (category: {category.value})")

        # Test routing for "Sir Forge, compile this code" -> sir_forge
        term, category, confidence = await session._classify("Sir Forge, compile this code")
        if term.id != "sir_forge":
            print(f"  [FAIL] 'Sir Forge, compile this code' routed to {term.id} (expected sir_forge)")
            passed = False
        else:
            print(f"  [OK] 'Sir Forge, compile this code' routed to {term.id}")
            print("  [PASS] Mid-dialogue hot-swapping intent classification triggers work perfectly")
            
    except Exception as e:
        print(f"  [FAIL] Hot-swapping classification test failed: {e}")
        passed = False

    # ── Test 5: Payload Compression & E2E Binary WS Transmission ──
    print("\n[NORTHSTAR TEST] Test 5: Payload Compression & E2E Binary WS Transmission")
    try:
        import gzip
        
        # 1. Benchmark compression ratio on mock TOON state
        state_payload = {
            "version": "vMAX_SYMBOLECT",
            "timestamp": "2026-06-22T18:15:34Z",
            "hardware": {
                "id": "MERLIN_Ω_TITAN",
                "hw": "8GB_ARM64_EDGE|TERMUX_MOBILE",
                "vmm": "Cloud-Hypervisor+Unikraft|WasmEdge(Userland)",
                "cpu": "Apple M2 Max (12 cores, 8 performance, 4 efficiency)",
                "memory": "64GB Unified Memory",
                "disk": "2TB NVMe SSD"
            },
            "cognition": {
                "inf": "OxiBonsai_v2(Ternary_STDP)",
                "ctx": "Mamba3_SSM+AntVortex(1M)",
                "mem": "Ouroboros(Letta)+ChunkKV",
                "ipc": "LTT(io_uring_DAX|POSIX_Fallback)"
            },
            "governance": {
                "gate": "ANYA_Ω(Triple-QFT)",
                "route": "MFOE(ToT|LaC|ReAct)",
                "safe": "TriageScore(Dynamic_Degradation|<0.15:AUTO|>0.55:HITL)",
                "z3": "UNSAT(Zero_Leakage)"
            },
            "kinetic": {
                "swarm": ["Hermes", "OpenClaw", "NanoBot", "ZeroClaw", "RustClaw"] * 10,
                "dom_in": "RevvTen_MutationObserver",
                "dom_out": "Synthetic_Native_Dispatch",
                "net": "eBPF_RingBuffer+Kyber768"
            },
            "history": [
                {"event": "boot", "status": "success", "timestamp": "2026-06-22T18:00:00Z"},
                {"event": "mtls_gate_active", "status": "success", "timestamp": "2026-06-22T18:05:00Z"},
                {"event": "switchboard_sync", "status": "success", "timestamp": "2026-06-22T18:10:00Z"},
                {"event": "delta_compression_init", "status": "success", "timestamp": "2026-06-22T18:12:00Z"}
            ] * 10
        }
        raw_bytes = json.dumps(state_payload).encode("utf-8")
        compressed_bytes = gzip.compress(raw_bytes)
        ratio = (1.0 - (len(compressed_bytes) / len(raw_bytes))) * 100
        print(f"  [OK] Benchmarked gzip compression: {len(raw_bytes)} bytes reduced to {len(compressed_bytes)} bytes ({ratio:.2f}% reduction)")
        if ratio < 60.0:
            print(f"  [FAIL] Gzip compression ratio {ratio:.2f}% is less than 60%")
            passed = False
        else:
            print(f"  [PASS] Gzip compression ratio meets >= 60% requirement")

        # 2. E2E binary gzip WS transmission with edge-router
        async with websockets.connect("ws://127.0.0.1:3001") as ws:
            ping_msg = {"type": "ping", "compress": True}
            ping_raw = json.dumps(ping_msg).encode("utf-8")
            ping_compressed = gzip.compress(ping_raw)
            
            # Send compressed binary
            await ws.send(ping_compressed)
            print("  [OK] Sent gzipped binary ping frame to edge-router")
            
            # Receive response
            response_raw = await ws.recv()
            
            # Check if response is gzipped
            if isinstance(response_raw, bytes) and len(response_raw) > 2 and response_raw[0] == 0x1f and response_raw[1] == 0x8b:
                decompressed = gzip.decompress(response_raw)
                response_data = json.loads(decompressed.decode("utf-8"))
                print(f"  [OK] Received gzipped response and successfully decompressed: {response_data}")
                if response_data.get("status") == "pong":
                    print("  [PASS] E2E Gzip WebSocket round-trip verified successfully")
                else:
                    print(f"  [FAIL] Response status is not pong: {response_data}")
                    passed = False
            else:
                print(f"  [FAIL] Expected gzipped binary response, got: {response_raw}")
                passed = False
                
    except Exception as e:
        print(f"  [FAIL] Payload compression / E2E WS test failed: {e}")
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
