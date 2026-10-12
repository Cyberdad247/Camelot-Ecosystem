#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Measure real memory pressure on Windows and diff two snapshots.

Windows Task Manager and psutil's ``percent`` both count standby cache as
"in use", so a machine with 5 GB of instantly-reclaimable cache still reports
95%. That number is not pressure. Two figures are:

  commit charge / commit limit
      Virtual memory the OS has promised to back with RAM + pagefile. This is
      what actually runs out, and what causes paging thrash.

  available physical (ullAvailPhys)
      RAM that can be handed to a new allocation right now, *including*
      standby cache that is reclaimable without a pagefile hit.

A host is in genuine pressure when available is low AND commit charge is
high. High ``percent`` with a low commit charge is a cache illusion.

Usage:
    python scripts/ram_probe.py --label before --out logs/ram/before.json
    python scripts/ram_probe.py --label after  --out logs/ram/after.json \\
        --compare logs/ram/before.json

Reading, not asserting: every claim about whether a change helped should come
from a pair of these snapshots.
"""

from __future__ import annotations

import argparse
import ctypes
import json
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

import psutil

GIB = 1024**3
MIB = 1024**2


class _PERFORMANCE_INFORMATION(ctypes.Structure):
    """Win32 PERFOMANCE_INFORMATION -- see psapi.GetPerformanceInfo."""

    _fields_ = [
        ("cb", wintypes.DWORD),
        ("CommitTotal", ctypes.c_size_t),
        ("CommitLimit", ctypes.c_size_t),
        ("CommitPeak", ctypes.c_size_t),
        ("PhysicalTotal", ctypes.c_size_t),
        ("PhysicalAvailable", ctypes.c_size_t),
        ("SystemCache", ctypes.c_size_t),
        ("KernelTotal", ctypes.c_size_t),
        ("KernelPaged", ctypes.c_size_t),
        ("KernelNonpaged", ctypes.c_size_t),
        ("PageSize", ctypes.c_size_t),
        ("HandleCount", wintypes.DWORD),
        ("ProcessCount", wintypes.DWORD),
        ("ThreadCount", wintypes.DWORD),
    ]


def _get_perf_info() -> tuple[dict[str, int], dict[str, int]] | None:
    """Return (memory, system) counters from PERFOMANCE_INFORMATION.

    Every SIZE_T field in this struct is denominated in PAGES, not bytes, so
    each is scaled by PageSize on the way out. Verified against psutil:
    PhysicalTotal * PageSize equals psutil.virtual_memory().total exactly.
    Reading these as bytes understates every figure by 4096x, which made a
    14 GiB commit charge display as "4 MiB".
    """
    info = _PERFORMANCE_INFORMATION()
    info.cb = ctypes.sizeof(info)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    if not psapi.GetPerformanceInfo(ctypes.byref(info), info.cb):
        return None

    page = info.PageSize or 4096
    mem = {
        "commit_total_bytes": info.CommitTotal * page,
        "commit_limit_bytes": info.CommitLimit * page,
        "commit_peak_bytes": info.CommitPeak * page,
        "physical_total_bytes": info.PhysicalTotal * page,
        "physical_available_bytes": info.PhysicalAvailable * page,
        "system_cache_bytes": info.SystemCache * page,
        "kernel_paged_bytes": info.KernelPaged * page,
        "kernel_nonpaged_bytes": info.KernelNonpaged * page,
        "page_size": page,
    }
    system = {
        "handles": info.HandleCount,
        "processes": info.ProcessCount,
        "threads": info.ThreadCount,
    }
    return mem, system


def _top_processes(limit: int) -> list[dict[str, object]]:
    """Top processes by resident set size, with a trimmed command line.

    Aggregating per name (rather than per pid) matters: an app that spawned
    twelve workers shows up as twelve rows and hides the real consumer.

    Both RSS and private bytes are recorded. RSS is what is physically resident;
    private bytes are what the process has *committed* (RAM + pagefile
    promised). A process can commit far more than it holds resident, and commit
    is what runs out, so sorting by RSS alone hides the largest contributor.
    """
    rows: dict[str, dict[str, object]] = {}
    for proc in psutil.process_iter(["name", "memory_info"]):
        try:
            info = proc.info
            if not info["memory_info"]:
                continue
            name = info["name"] or "<unknown>"
            cmd = ""
            try:
                cmd = (proc.cmdline() or [""])[0][:70]
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            mi = info["memory_info"]
            entry = rows.setdefault(
                name,
                {
                    "name": name,
                    "rss_bytes": 0,
                    "private_bytes": 0,
                    "instances": 0,
                    "cmdline": cmd,
                },
            )
            entry["rss_bytes"] = int(entry["rss_bytes"]) + mi.rss
            entry["private_bytes"] = int(entry["private_bytes"]) + getattr(mi, "private", 0)
            entry["instances"] = int(entry["instances"]) + 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    ordered = sorted(rows.values(), key=lambda r: int(r["rss_bytes"]), reverse=True)
    return ordered[:limit]


def _top_committers(limit: int) -> tuple[list[dict[str, object]], int]:
    """Return (top N by committed private bytes, total across ALL processes).

    The total must span every process, not just the reported rows, or the
    commit reconciliation attributes the untruncated tail to "unaccounted".
    """
    rows: dict[str, dict[str, object]] = {}
    total = 0
    for proc in psutil.process_iter(["name", "memory_info"]):
        try:
            info = proc.info
            if not info["memory_info"]:
                continue
            priv = getattr(info["memory_info"], "private", 0)
            if not priv:
                continue
            total += priv
            name = info["name"] or "<unknown>"
            entry = rows.setdefault(
                name,
                {
                    "name": name,
                    "private_bytes": 0,
                    "rss_bytes": 0,
                    "instances": 0,
                    "cmdline": "",
                },
            )
            entry["private_bytes"] = int(entry["private_bytes"]) + priv
            entry["rss_bytes"] = int(entry["rss_bytes"]) + info["memory_info"].rss
            entry["instances"] = int(entry["instances"]) + 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    ordered = sorted(rows.values(), key=lambda r: int(r["private_bytes"]), reverse=True)
    return ordered[:limit], total


def snapshot(limit: int = 12) -> dict[str, object]:
    """Capture one point-in-time memory measurement."""
    virt = psutil.virtual_memory()
    snap: dict[str, object] = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "physical": {
            "total_bytes": virt.total,
            "available_bytes": virt.available,
            "used_bytes": virt.used,
            "percent_used": virt.percent,
        },
    }

    perf = _get_perf_info()
    if perf is None:
        snap["commit"] = {"error": "GetPerformanceInfo unavailable"}
        snap["pressure"] = "unknown (psapi unavailable)"
    else:
        mem, counts = perf
        commit_pct = 100.0 * mem["commit_total_bytes"] / mem["commit_limit_bytes"] if mem["commit_limit_bytes"] else 0.0
        snap["commit"] = {
            "charge_bytes": mem["commit_total_bytes"],
            "limit_bytes": mem["commit_limit_bytes"],
            "peak_bytes": mem["commit_peak_bytes"],
            "percent": round(commit_pct, 1),
        }
        snap["kernel"] = {
            "paged_bytes": mem["kernel_paged_bytes"],
            "nonpaged_bytes": mem["kernel_nonpaged_bytes"],
        }
        snap["counts"] = counts
        snap["cache"] = {
            "system_cache_bytes": mem["system_cache_bytes"],
            "note": (
                "standby/modified cache is reclaimable on demand; it inflates "
                "'percent used' without being real pressure"
            ),
        }
        snap["pressure"] = _verdict(
            virt.available,
            commit_pct,
            mem["system_cache_bytes"],
            mem["commit_total_bytes"],
        )

    snap["top_processes"] = _top_processes(limit)
    committers, private_total = _top_committers(limit)
    snap["top_committers"] = committers
    snap["process_rss_total_bytes"] = sum(
        int(p["rss_bytes"])
        for p in snap["top_processes"]  # type: ignore[index]
    )
    snap["process_private_total_bytes"] = private_total
    return snap


def _verdict(avail_bytes: int, commit_pct: float, cache_bytes: int, commit_bytes: int) -> str:
    """Classify pressure from the numbers that matter, not from 'percent used'."""
    avail_mib = avail_bytes / MIB
    parts: list[str] = []
    if commit_pct >= 90.0:
        parts.append(
            f"REAL PRESSURE: commit at {commit_pct:.0f}% of limit "
            f"({commit_bytes / GIB:.1f} GiB charged) with {avail_mib:.0f} MiB "
            "available. New allocations will page."
        )
    elif avail_mib < 512 and commit_pct >= 70.0:
        parts.append(
            f"TIGHT: {avail_mib:.0f} MiB available, commit {commit_pct:.0f}%. Large new allocations will page."
        )
    elif avail_mib < 512:
        parts.append(
            f"MODERATE: {avail_mib:.0f} MiB available, commit {commit_pct:.0f}%. "
            "Standby cache is being reclaimed to meet demand."
        )
    else:
        parts.append(
            f"HEALTHY: {avail_mib:.0f} MiB available, commit {commit_pct:.0f}%. "
            f"{cache_bytes / GIB:.1f} GiB of cache is standby, not pressure."
        )
    return " ".join(parts)


def _fmt_bytes(n: float) -> str:
    if n >= GIB:
        return f"{n / GIB:.2f} GiB"
    return f"{n / MIB:.0f} MiB"


def report(snap: dict[str, object]) -> str:
    """Render a snapshot as a human-readable report."""
    phys = snap["physical"]  # type: ignore[index]
    lines = [
        "=" * 72,
        f"  MEMORY SNAPSHOT  {snap['captured_utc']}",
        "=" * 72,
        "",
        "PHYSICAL",
        f"  total            {_fmt_bytes(phys['total_bytes'])}",  # type: ignore[index]
        f"  available        {_fmt_bytes(phys['available_bytes'])}",  # type: ignore[index]
        f"  percent used     {phys['percent_used']}%",  # type: ignore[index]
    ]

    commit = snap.get("commit") or {}
    if "error" not in commit:
        lines += [
            "",
            "COMMIT (RAM + pagefile promises)",
            f"  charge           {_fmt_bytes(commit['charge_bytes'])}",  # type: ignore[index]
            f"  limit            {_fmt_bytes(commit['limit_bytes'])}",  # type: ignore[index]
            f"  percent          {commit['percent']}%",  # type: ignore[index]
        ]
    kern = snap.get("kernel") or {}
    if kern:
        lines += [
            "",
            "KERNEL POOLS (leak-prone, nonpaged cannot be paged out)",
            f"  paged            {_fmt_bytes(kern['paged_bytes'])}",  # type: ignore[index]
            f"  nonpaged         {_fmt_bytes(kern['nonpaged_bytes'])}",  # type: ignore[index]
        ]

    lines += ["", f"VERDICT: {snap['pressure']}", "", "TOP PROCESSES (RSS, aggregated by name)"]
    for row in snap["top_processes"]:  # type: ignore[union-attr]
        inst = f" x{row['instances']}" if int(row["instances"]) > 1 else ""
        lines.append(f"  {_fmt_bytes(int(row['rss_bytes'])):>10}  {row['name']}{inst}")
        if row["cmdline"]:
            lines.append(f"              {row['cmdline']}")

    lines += [
        "",
        "TOP COMMITTERS (private bytes = RAM + pagefile promised)",
    ]
    for row in snap.get("top_committers", []):  # type: ignore[union-attr]
        inst = f" x{row['instances']}" if int(row["instances"]) > 1 else ""
        lines.append(f"  {_fmt_bytes(int(row['private_bytes'])):>10}  {row['name']}{inst}")

    commit = snap.get("commit") or {}
    if "error" not in commit:
        charge = commit["charge_bytes"]  # type: ignore[index]
        proc_priv = snap.get("process_private_total_bytes", 0)
        kernel = snap.get("kernel") or {}
        unaccounted = charge - int(proc_priv) - int(kernel.get("paged_bytes", 0)) - int(kernel.get("nonpaged_bytes", 0))
        lines += [
            "",
            "COMMIT RECONCILIATION (what is charged but not resident)",
            f"  process private      {_fmt_bytes(proc_priv)}",
            f"  kernel pools         {_fmt_bytes(int(kernel.get('paged_bytes', 0)) + int(kernel.get('nonpaged_bytes', 0)))}",
            f"  unaccounted          {_fmt_bytes(unaccounted)}",
        ]
        if unaccounted > 2 * GIB:
            lines.append(
                "  -> most of the commit limit is neither process private memory"
                " nor kernel pool:"
                " mapped files, pagefile-backed heaps, or driver mappings."
            )
    lines.append("")
    return "\n".join(lines)


def compare(before: dict[str, object], after: dict[str, object]) -> str:
    """Diff two snapshots and attribute the change to processes where possible."""
    lines = ["=" * 72, "  BEFORE / AFTER", "=" * 72, ""]
    b_phys, a_phys = before["physical"], after["physical"]  # type: ignore[index]
    b_commit, a_commit = before.get("commit") or {}, after.get("commit") or {}  # type: ignore[index]

    def delta(label: str, b: float, a: float, lower_is_better: bool = True) -> None:
        d = a - b
        if not d:
            lines.append(f"  {label:<22} unchanged")
            return
        arrow = ""
        if (d < 0 and lower_is_better) or (d > 0 and not lower_is_better):
            arrow = "  (better)"
        lines.append(f"  {label:<22} {_fmt_bytes(abs(b))} -> {_fmt_bytes(abs(a))}   {d / MIB:+.0f} MiB{arrow}")

    lines.append("SYSTEM")
    delta("available", b_phys["available_bytes"], a_phys["available_bytes"])  # type: ignore[index]
    delta("physical used", b_phys["used_bytes"], a_phys["used_bytes"])  # type: ignore[index]
    if "error" not in b_commit and "error" not in a_commit:
        delta("commit charge", b_commit["charge_bytes"], a_commit["charge_bytes"])  # type: ignore[index]
        delta(
            "nonpaged pool",
            (before.get("kernel") or {}).get("nonpaged_bytes", 0),  # type: ignore[union-attr]
            (after.get("kernel") or {}).get("nonpaged_bytes", 0),  # type: ignore[union-attr]
        )

    b_map = {r["name"]: int(r["rss_bytes"]) for r in before["top_processes"]}  # type: ignore[union-attr]
    a_map = {r["name"]: int(r["rss_bytes"]) for r in after["top_processes"]}  # type: ignore[union-attr]
    movers = sorted(
        ((n, a_map.get(n, 0) - b_map.get(n, 0)) for n in set(a_map) | set(b_map)),
        key=lambda kv: abs(kv[1]),
        reverse=True,
    )
    lines += ["", "PER-PROCESS RSS DELTA"]
    for name, d in movers[:10]:
        if abs(d) < 4 * MIB:
            continue
        lines.append(f"  {name:<34} {d / MIB:+.0f} MiB")
    lines.append("")
    lines.append(f"BEFORE: {before['pressure']}")  # type: ignore[index]
    lines.append(f"AFTER:  {after['pressure']}")  # type: ignore[index]
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--label", default="", help="tag stored with the snapshot")
    parser.add_argument("--out", type=Path, help="write JSON snapshot here")
    parser.add_argument("--compare", type=Path, help="diff against a prior JSON snapshot")
    parser.add_argument("--top", type=int, default=12, help="processes to report")
    args = parser.parse_args(argv)

    snap = snapshot(limit=args.top)
    snap["label"] = args.label

    print(report(snap))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(snap, indent=2), encoding="utf-8")
        print(f"  snapshot written: {args.out}")

    if args.compare:
        prior = json.loads(args.compare.read_text(encoding="utf-8"))
        print(compare(prior, snap))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
