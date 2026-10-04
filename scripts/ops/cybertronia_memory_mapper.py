#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Cybertronia Memory Mapper & Working Set Reduction Engine
========================================================
Comprehensive memory topology mapping, classification, and surgical
working set trimming for the Cybertronia Windows orchestrator.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import logging
import os
import platform
import subprocess
import sys

if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

LOG = logging.getLogger("CybertroniaMemoryMapper")
logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class ProcessMemoryRecord:
    pid: int
    name: str
    working_set_mb: float
    private_mb: float
    category: str


@dataclass
class MemoryTopologyMap:
    timestamp: str
    total_physical_mb: float
    free_physical_mb: float
    used_physical_mb: float
    utilization_pct: float
    commit_total_mb: float
    commit_limit_mb: float
    categories: Dict[str, float]
    top_processes: List[Dict[str, Any]]
    trimmed_reclaimed_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def categorize_process(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ("agy", "python", "node", "cargo", "rustc", "camelot", "scrcpy")):
        return "CAMELOT_AGENTIC_SUITE"
    if any(k in n for k in ("msmpeng", "security", "defender", "antivirus")):
        return "SECURITY_AV"
    if any(k in n for k in ("chrome", "edge", "duckduckgo", "browser", "webview")):
        return "BROWSERS_WEBVIEW"
    if any(k in n for k in ("nitrosense", "warp", "tailscale", "overlay", "nvidia")):
        return "HARDWARE_OEM_UTILITIES"
    if any(k in n for k in ("explorer", "dwm", "svchost", "audiodg", "system", "compression")):
        return "WINDOWS_CORE_SYSTEM"
    return "OTHER_USER_APPS"


class CybertroniaMemoryMapper:
    def __init__(self, home: Optional[Path] = None) -> None:
        self.home = home or _ROOT
        self.output_file = self.home / "03_VAULT" / "runtime_state" / "cybertronia_memory_map.json"
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def get_system_memory(self) -> Tuple[float, float, float, float]:
        """Returns (total_mb, free_mb, commit_total_mb, commit_limit_mb)."""
        if platform.system() != "Windows":
            return 8192.0, 4096.0, 8192.0, 16384.0

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

        total_phys = stat.ullTotalPhys / (1024 * 1024)
        avail_phys = stat.ullAvailPhys / (1024 * 1024)
        total_page = stat.ullTotalPageFile / (1024 * 1024)
        avail_page = stat.ullAvailPageFile / (1024 * 1024)
        commit_total = total_page - avail_page
        commit_limit = total_page

        return round(total_phys, 2), round(avail_phys, 2), round(commit_total, 2), round(commit_limit, 2)

    def map_processes(self) -> List[ProcessMemoryRecord]:
        """Enumerates running processes and computes working set and private memory."""
        records: List[ProcessMemoryRecord] = []
        ps_cmd = (
            "Get-Process | Where-Object { $_.WorkingSet64 -gt 1MB } | "
            "Select-Object Id, ProcessName, WorkingSet64, PrivateMemorySize64 | "
            "ConvertTo-Json -Compress"
        )
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=10,
            )
            raw = json.loads(res.stdout)
            if isinstance(raw, dict):
                raw = [raw]
            for item in raw:
                ws_mb = round(item.get("WorkingSet64", 0) / (1024 * 1024), 2)
                priv_mb = round(item.get("PrivateMemorySize64", 0) / (1024 * 1024), 2)
                pname = str(item.get("ProcessName", "unknown"))
                pid = int(item.get("Id", 0))
                cat = categorize_process(pname)
                records.append(ProcessMemoryRecord(
                    pid=pid,
                    name=pname,
                    working_set_mb=ws_mb,
                    private_mb=priv_mb,
                    category=cat,
                ))
        except Exception as exc:
            LOG.warning(f"[MAPPER] Process enumeration fallback: {exc}")

        return sorted(records, key=lambda r: r.working_set_mb, reverse=True)

    def trim_working_sets(self) -> float:
        """Invokes PSAPI EmptyWorkingSet on all accessible user processes to purge stale pages."""
        if platform.system() != "Windows":
            return 0.0

        _, before_free, _, _ = self.get_system_memory()
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400

        trimmed_count = 0
        records = self.map_processes()
        for r in records:
            # Skip trimming our own process
            if r.pid == os.getpid():
                continue
            h_proc = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, r.pid)
            if h_proc:
                try:
                    if psapi.EmptyWorkingSet(h_proc):
                        trimmed_count += 1
                finally:
                    kernel32.CloseHandle(h_proc)

        time.sleep(0.5)
        _, after_free, _, _ = self.get_system_memory()
        reclaimed = max(0.0, round(after_free - before_free, 2))
        LOG.info(f"✨ [TRIM] Purged stale memory pages across {trimmed_count} processes (Reclaimed ~{reclaimed} MB physical RAM).")
        return reclaimed

    def generate_map(self, execute_trim: bool = False) -> MemoryTopologyMap:
        reclaimed = 0.0
        if execute_trim:
            reclaimed = self.trim_working_sets()

        total_mb, free_mb, commit_mb, commit_limit_mb = self.get_system_memory()
        used_mb = round(total_mb - free_mb, 2)
        pct = round((used_mb / total_mb) * 100, 1)

        records = self.map_processes()
        categories: Dict[str, float] = {}
        for r in records:
            categories[r.category] = round(categories.get(r.category, 0.0) + r.working_set_mb, 2)

        top_proc = [asdict(r) for r in records[:15]]

        topo = MemoryTopologyMap(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_physical_mb=total_mb,
            free_physical_mb=free_mb,
            used_physical_mb=used_mb,
            utilization_pct=pct,
            commit_total_mb=commit_mb,
            commit_limit_mb=commit_limit_mb,
            categories=categories,
            top_processes=top_proc,
            trimmed_reclaimed_mb=reclaimed,
        )

        try:
            self.output_file.write_text(json.dumps(topo.to_dict(), indent=2), encoding="utf-8")
        except Exception as exc:
            LOG.error(f"[MAPPER] Failed to write map: {exc}")

        return topo


def main() -> None:
    parser = argparse.ArgumentParser(description="Cybertronia Memory Mapper & Reducer")
    parser.add_argument("--trim", action="store_true", help="Execute surgical working set trim")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    mapper = CybertroniaMemoryMapper()
    topo = mapper.generate_map(execute_trim=args.trim)

    if args.json:
        print(json.dumps(topo.to_dict(), indent=2))
        return

    print("==========================================================================")
    print("🗺️  CYBERTRONIA MEMORY TOPOLOGY MAP & REDUCTION AUDIT")
    print(f"Timestamp: {topo.timestamp}")
    print("==========================================================================")
    print(f"Physical Memory: {topo.used_physical_mb} MB used / {topo.total_physical_mb} MB total ({topo.utilization_pct}% utilized)")
    print(f"Free Headroom:   {topo.free_physical_mb} MB free physical RAM")
    print(f"Commit Pool:     {topo.commit_total_mb} MB / {topo.commit_limit_mb} MB limit")
    if args.trim:
        print(f"Trim Reclaimed:  +{topo.trimmed_reclaimed_mb} MB physical RAM freed")
    print("--------------------------------------------------------------------------")
    print("Memory by Functional Category:")
    for cat, mb in sorted(topo.categories.items(), key=lambda x: x[1], reverse=True):
        pct_cat = round((mb / topo.total_physical_mb) * 100, 1)
        print(f"  - {cat:<26}: {mb:>8.2f} MB ({pct_cat}%)")
    print("--------------------------------------------------------------------------")
    print("Top 10 Resident Processes:")
    for p in topo.top_processes[:10]:
        print(f"  - PID {p['pid']:<6} {p['name']:<22} {p['working_set_mb']:>8.2f} MB ({p['category']})")
    print("==========================================================================")


if __name__ == "__main__":
    main()
