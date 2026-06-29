#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
[S6-04] factory_status — One-shot factory health dashboard
===========================================================
Probes all CAMELOT-OS services, reads queue depth, ledger entry
count, and optionally fetches Sir Octavian metrics.

Usage:
    python bin/factory_status.py
    python bin/factory_status.py --json
    python bin/factory_status.py --watch 10   # refresh every 10s
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
QUEUE_FILE  = HOME / "logs" / "harness_queue.jsonl"
DONE_FILE   = HOME / "logs" / "worker_done.txt"
LEDGER_FILE = HOME / "PROVENANCE_LEDGER.md"
METRICS_FILE = HOME / "logs" / "metrics.json"

PROBES: list[tuple[str, str, int]] = [
    ("CLIProxy",    "127.0.0.1", 8080),
    ("KineticEdge", "127.0.0.1", 3001),
    ("OmniVoice",   "127.0.0.1", 3002),
    ("Redis",       "127.0.0.1", 6379),
    ("Saltare",     "127.0.0.1", 8085),
    ("Holotable",   "127.0.0.1", 3000),
    ("KittenTTS",   "127.0.0.1", 8300),
    ("SirOctavian", "127.0.0.1", 8400),
]


def _probe(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _queue_stats() -> dict:
    total, done_count = 0, 0
    if QUEUE_FILE.exists():
        try:
            lines = [l for l in QUEUE_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
            total = len(lines)
        except Exception:
            pass
    if DONE_FILE.exists():
        try:
            done_count = len([l for l in DONE_FILE.read_text(encoding="utf-8").splitlines() if l.strip()])
        except Exception:
            pass
    pending = max(0, total - done_count)
    return {"total": total, "done": done_count, "pending": pending}


def _ledger_count() -> int:
    if not LEDGER_FILE.exists():
        return 0
    try:
        import re
        text = LEDGER_FILE.read_text(encoding="utf-8")
        return len(re.findall(r"^\| *\d+ *\|", text, re.MULTILINE))
    except Exception:
        return 0


def _octavian_metrics() -> dict | None:
    if not METRICS_FILE.exists():
        return None
    try:
        return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def collect() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    probes = {name: _probe(host, port) for name, host, port in PROBES}
    green = sum(1 for ok in probes.values() if ok)
    queue = _queue_stats()
    ledger = _ledger_count()
    oct_metrics = _octavian_metrics()
    return {
        "ts": ts,
        "probes": probes,
        "probes_green": green,
        "probes_total": len(PROBES),
        "queue": queue,
        "ledger_entries": ledger,
        "octavian_metrics": oct_metrics,
    }


def _render(data: dict) -> str:
    lines = []
    ts = data["ts"]
    lines.append(f"\n{'═' * 56}")
    lines.append(f"  CAMELOT-OS FACTORY STATUS  {ts[:19]}Z")
    lines.append(f"{'═' * 56}")

    lines.append(f"\n  SERVICES  ({data['probes_green']}/{data['probes_total']} green)")
    for name, ok in data["probes"].items():
        icon = "✅" if ok else "🔴"
        lines.append(f"    {icon}  {name}")

    q = data["queue"]
    lines.append(f"\n  QUEUE     pending={q['pending']}  done={q['done']}  total={q['total']}")
    lines.append(f"  LEDGER    {data['ledger_entries']} entries")

    oct = data.get("octavian_metrics")
    if oct:
        tph = oct.get("throughput_tasks_per_hour", "?")
        cells = oct.get("terminals", {})
        lines.append(f"  OCTAVIAN  throughput={tph} tph  terminals={len(cells)}")

    lines.append(f"{'─' * 56}\n")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="CAMELOT-OS factory health dashboard")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of table")
    parser.add_argument("--watch", type=int, metavar="SECS", help="Refresh every N seconds")
    args = parser.parse_args()

    while True:
        data = collect()
        if args.json:
            print(json.dumps(data, indent=2, default=str))
        else:
            print(_render(data))
        if args.watch:
            time.sleep(args.watch)
        else:
            break


if __name__ == "__main__":
    main()
