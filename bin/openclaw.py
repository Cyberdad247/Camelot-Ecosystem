#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""OpenClaw CLI — CAMELOT-OS Dynamic Health Triage
===================================================
Usage:
    python bin/openclaw.py             # one-shot triage, colored table
    python bin/openclaw.py --status    # check-only, no auto-triage
    python bin/openclaw.py --watch     # loop every 60s, print deltas
    python bin/openclaw.py --json      # machine-readable one-shot
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "control_plane"))
sys.path.insert(0, str(ROOT / "03_VAULT" / "training" / "configs"))

from control_plane.openclaw import _classify, _run_checks, run_openclaw_triage

_C = {
    "g": "\033[92m", "y": "\033[93m", "r": "\033[91m", "c": "\033[96m",
    "m": "\033[95m", "x": "\033[0m", "B": "\033[1m", "d": "\033[2m",
}


def _print_table(report: dict) -> None:
    status = report["status"]
    color = _C["g"] if status == "ALL_GREEN" else (_C["y"] if status == "DEGRADED" else _C["r"])
    print(f"\n{_C['c']}{_C['B']}-- OpenClaw Triage Report --{_C['x']}")
    print(f"  Status : {color}{_C['B']}{status}{_C['x']}")
    print(f"  Checks : {report['checks_ok']}/{report['checks_total']} OK | "
          f"{report['checks_warn']} warn | {report['checks_critical']} critical")
    print(f"  Healed : {report['auto_healed']} auto-actions taken")
    if report["hitl_required"]:
        print(f"  {_C['r']}{_C['B']}HITL REQUIRED — see logs/openclaw_hitl_required.md{_C['x']}")
    if report["critical_items"]:
        print(f"  {_C['r']}CRITICAL: {', '.join(report['critical_items'])}{_C['x']}")
    if report["warn_items"]:
        print(f"  {_C['y']}WARN: {', '.join(report['warn_items'])}{_C['x']}")
    if report["actions_taken"]:
        print(f"  {_C['d']}Actions: {'; '.join(report['actions_taken'])}{_C['x']}")
    print(f"  {_C['d']}({report['duration_ms']}ms){_C['x']}")


def _print_status_only() -> None:
    checks = _run_checks()
    critical, warn, ok_list = _classify(checks)
    print(f"\n{_C['c']}{_C['B']}-- OpenClaw Status (no triage) --{_C['x']}")
    for r in checks:
        if r.ok:
            sym = f"{_C['g']}OK  {_C['x']}"
        elif r.critical:
            sym = f"{_C['r']}FAIL{_C['x']}"
        else:
            sym = f"{_C['y']}WARN{_C['x']}"
        print(f"  [{sym}] {_C['B']}{r.key:<30}{_C['x']} {_C['d']}{r.detail}{_C['x']}")
    print(f"\n  {len(ok_list)} OK | {len(warn)} WARN | {len(critical)} CRITICAL")


def main() -> None:
    args = sys.argv[1:]

    if "--json" in args:
        report = run_openclaw_triage()
        print(json.dumps(report))
        sys.exit(0 if report["status"] != "CRITICAL" else 1)

    if "--status" in args:
        _print_status_only()
        sys.exit(0)

    if "--watch" in args:
        interval = 60
        prev_status = None
        while True:
            report = run_openclaw_triage()
            if report["status"] != prev_status:
                _print_table(report)
                prev_status = report["status"]
            else:
                ts = report["timestamp"][:19]
                print(f"  [{ts}] {report['status']} — {report['checks_ok']}/{report['checks_total']} OK")
            try:
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[OpenClaw] Watch stopped.")
                break
        return

    # Default: one-shot triage
    report = run_openclaw_triage()
    _print_table(report)
    sys.exit(0 if report["status"] != "CRITICAL" else 1)


if __name__ == "__main__":
    main()
