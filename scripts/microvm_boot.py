#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
microvm_boot.py — Unikraft/libkrun MicroVM pill launcher (v9000.14, P5-T02).
============================================================================
Boots a sovereign edge "pill" (a 5 MB unikernel image) inside a KVM MicroVM and
health-checks it. Hypervisor-agnostic: prefers cloud-hypervisor, then
qemu-system-x86_64 (-enable-kvm), then krunvm/libkrun.

Exit codes (so callers can SKIP vs FAIL precisely):
    0  boot + health OK
    2  boot attempted but failed (hard FAIL)
    3  prerequisites missing — /dev/kvm, a hypervisor, or a pill image (SKIP)

Usage:
    python3 scripts/microvm_boot.py --health-check                # real boot
    python3 scripts/microvm_boot.py --health-check --image pill.img --port 8088
    python3 scripts/microvm_boot.py --self-test                   # launcher machinery
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_PORT = 8088
DEFAULT_IMAGE_ENV = "CAMELOT_PILL_IMAGE"
DEFAULT_IMAGE_PATHS = ("build/microvm/pill.img", "03_VAULT/pills/edge_pill.img")
BOOT_BUDGET_MS = 12.0  # blueprint target: 5MB pill boots < 12ms


# ── capability detection ─────────────────────────────────────────────────────

def kvm_ready() -> tuple[bool, str]:
    if not os.path.exists("/dev/kvm"):
        return False, "/dev/kvm absent — enable nested virtualization / WSL2 KVM"
    if not os.access("/dev/kvm", os.R_OK | os.W_OK):
        return False, "/dev/kvm not accessible — add your user to the 'kvm' group"
    return True, "/dev/kvm ready"


def detect_hypervisor() -> Optional[tuple[str, str]]:
    """Return (name, path) of the first available hypervisor, or None."""
    for name in ("cloud-hypervisor", "qemu-system-x86_64", "krunvm"):
        path = shutil.which(name)
        if path:
            return name, path
    return None


def resolve_image(explicit: Optional[str]) -> Optional[Path]:
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    env = os.environ.get(DEFAULT_IMAGE_ENV)
    if env and Path(env).exists():
        return Path(env)
    for cand in DEFAULT_IMAGE_PATHS:
        if Path(cand).exists():
            return Path(cand)
    return None


# ── boot + health ────────────────────────────────────────────────────────────

def _boot_command(hv_name: str, hv_path: str, image: Path, port: int) -> list[str]:
    """Construct a boot command that forwards guest :80 to host :port."""
    if hv_name == "qemu-system-x86_64":
        return [hv_path, "-enable-kvm", "-m", "64", "-nographic", "-kernel", str(image),
                "-netdev", f"user,id=n0,hostfwd=tcp::{port}-:80",
                "-device", "virtio-net,netdev=n0", "-append", "console=ttyS0"]
    if hv_name == "cloud-hypervisor":
        return [hv_path, "--kernel", str(image), "--memory", "size=64M",
                "--net", f"tap=,mac=,ip=,mask=", "--cmdline", "console=ttyS0"]
    # krunvm
    return [hv_path, "start", "--mem", "64", str(image)]


def health_poll(url: str, timeout_s: float) -> tuple[bool, float]:
    """Poll `url` until HTTP 200 or timeout. Returns (ok, elapsed_ms)."""
    t0 = time.perf_counter()
    deadline = t0 + timeout_s
    while time.perf_counter() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as r:
                if r.status == 200:
                    return True, (time.perf_counter() - t0) * 1000
        except Exception:
            time.sleep(0.02)
    return False, (time.perf_counter() - t0) * 1000


def cmd_health_check(args) -> int:
    ok, detail = kvm_ready()
    if not ok:
        print(f"[P5-T02] PREREQ MISSING: {detail}")
        return 3
    hv = detect_hypervisor()
    if hv is None:
        print("[P5-T02] PREREQ MISSING: no hypervisor "
              "(install cloud-hypervisor, qemu-system-x86_64, or krunvm)")
        return 3
    image = resolve_image(args.image)
    if image is None:
        print(f"[P5-T02] PREREQ MISSING: no pill image "
              f"(build one, set ${DEFAULT_IMAGE_ENV}, or pass --image)")
        return 3

    hv_name, hv_path = hv
    url = f"http://127.0.0.1:{args.port}/health"
    print(f"[P5-T02] booting {image} via {hv_name} (health: {url})")
    cmd = _boot_command(hv_name, hv_path, image, args.port)
    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        print(f"[P5-T02] FAIL: hypervisor launch error: {exc}")
        return 2
    try:
        healthy, ms = health_poll(url, args.timeout)
        boot_ms = (time.perf_counter() - t0) * 1000
        if healthy:
            budget = "✓ under" if boot_ms <= args.boot_budget_ms else "⚠ over"
            print(f"[P5-T02] PASS: health 200 in {ms:.1f}ms "
                  f"(boot {boot_ms:.1f}ms; budget {budget} {args.boot_budget_ms}ms)")
            return 0
        print(f"[P5-T02] FAIL: no health 200 within {args.timeout}s")
        return 2
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def cmd_self_test(args) -> int:
    """Validate the launcher machinery (detection + health-poll + process mgmt)
    against a local mock 'VM' — a tiny HTTP server that answers /health 200.
    Cross-platform; needs no KVM. Proves the boot/health pipeline works."""
    failures = 0

    def check(name: str, cond: bool) -> None:
        nonlocal failures
        if not cond:
            failures += 1
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("microvm_boot self-test (P5-T02 launcher machinery)")

    # detection helpers never raise and return sane shapes
    kok, kdetail = kvm_ready()
    check("kvm_ready returns (bool, str)", isinstance(kok, bool) and isinstance(kdetail, str))
    hv = detect_hypervisor()
    check("detect_hypervisor returns None or (name,path)", hv is None or (len(hv) == 2))
    check("resolve_image(None) is path-or-None", resolve_image(None) is None or isinstance(resolve_image(None), Path))

    # mock VM: a stdlib HTTP server answering /health 200, launched as a subprocess
    port = args.port
    mock_src = (
        "import sys\n"
        "from http.server import BaseHTTPRequestHandler, HTTPServer\n"
        "class H(BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        ok = self.path == '/health'\n"
        "        self.send_response(200 if ok else 404)\n"
        "        self.end_headers(); self.wfile.write(b'CAMELOT-EDGE PILL OK')\n"
        "    def log_message(self, *a): pass\n"
        f"HTTPServer(('127.0.0.1', {port}), H).serve_forever()\n"
    )
    proc = subprocess.Popen([sys.executable, "-c", mock_src],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ok, ms = health_poll(f"http://127.0.0.1:{port}/health", timeout_s=5.0)
        check(f"health_poll reaches mock VM 200 ({ms:.0f}ms)", ok)
        bad, _ = health_poll(f"http://127.0.0.1:{port}/nope", timeout_s=0.5)
        check("health_poll fails on non-200 path", not bad)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    print(f"\n{'ALL PASS' if failures == 0 else f'{failures} FAILURE(S)'} — microvm_boot")
    return 1 if failures else 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="CAMELOT MicroVM pill launcher (P5-T02)")
    ap.add_argument("--health-check", action="store_true", help="boot a pill and health-check it")
    ap.add_argument("--self-test", action="store_true", help="test the launcher machinery (no KVM)")
    ap.add_argument("--image", default=None, help="pill image path")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--timeout", type=float, default=20.0, help="health poll timeout (s)")
    ap.add_argument("--boot-budget-ms", type=float, default=BOOT_BUDGET_MS)
    args = ap.parse_args(argv)

    if args.self_test:
        return cmd_self_test(args)
    if args.health_check:
        return cmd_health_check(args)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
