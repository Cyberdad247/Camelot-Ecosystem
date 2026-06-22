#!/usr/bin/env python3
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
run_observability.py — bring up the CAMELOT-OS observability stack natively.

No Docker (Microcubic VM Law). This launches a native Prometheus pointed at the
local metrics endpoint, and tells you how to start the metrics daemon. Grafana,
if installed natively, can point at Prometheus on :9090.

Prometheus binary resolution order:
  1. $PROMETHEUS_BIN
  2. `prometheus` on PATH (e.g. `scoop install prometheus`, `brew install
     prometheus`, or the official binary release)

Usage:
  python observability/run_observability.py            # launch Prometheus
  python observability/run_observability.py --check     # print status, don't run
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "prometheus.yml"
METRICS_PORT = int(os.environ.get("CAMELOT_METRICS_PORT", "8000"))


def find_prometheus() -> str | None:
    return os.environ.get("PROMETHEUS_BIN") or shutil.which("prometheus")


def _install_hint() -> str:
    return (
        "Prometheus binary not found. Install natively (no Docker):\n"
        "  • Windows : scoop install prometheus\n"
        "  • macOS   : brew install prometheus\n"
        "  • Linux   : download from https://prometheus.io/download/ and add to PATH\n"
        "Then re-run, or set PROMETHEUS_BIN=/path/to/prometheus."
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bring up CAMELOT-OS observability (no Docker)")
    ap.add_argument("--check", action="store_true", help="Report status without launching")
    args = ap.parse_args(argv)

    prom = find_prometheus()
    alertmgr = os.environ.get("ALERTMANAGER_BIN") or shutil.which("alertmanager")
    grafana = os.environ.get("GRAFANA_BIN") or shutil.which("grafana-server") or shutil.which("grafana")
    print("CAMELOT-OS Observability (native / no-Docker)")
    print(f"  config          : {CONFIG}")
    print(f"  metrics target  : http://127.0.0.1:{METRICS_PORT}/metrics")
    print(f"  prometheus bin  : {prom or 'NOT FOUND'}")
    print(f"  alertmanager bin: {alertmgr or 'not found (optional)'}")
    print(f"  grafana bin     : {grafana or 'not found (optional)'}")
    if alertmgr:
        print(f"  alertmanager    : {alertmgr} --config.file={HERE / 'alertmanager.yml'}")
    if grafana:
        print(f"  grafana         : set GF_PATHS_PROVISIONING={HERE / 'grafana' / 'provisioning'}")
    print()
    print("Start the metrics daemon first (separate terminal):")
    print(f"  python -m control_plane.cluster.metrics_daemon --port {METRICS_PORT} \\")
    print('      --nodes "node_1=http://127.0.0.1:8443,node_2=http://127.0.0.1:8444,node_3=http://127.0.0.1:8445"')
    print()

    if not CONFIG.is_file():
        print(f"[ERROR] missing config: {CONFIG}", file=sys.stderr)
        return 1

    if args.check:
        print("Prometheus UI (once running): http://127.0.0.1:9090")
        return 0 if prom else 1

    if not prom:
        print(_install_hint(), file=sys.stderr)
        return 1

    # cwd = observability/ so the relative rule_files path resolves.
    cmd = [prom, f"--config.file={CONFIG.name}"]
    print(f"[launch] {' '.join(cmd)}  (cwd={HERE})")
    try:
        return subprocess.call(cmd, cwd=str(HERE))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
