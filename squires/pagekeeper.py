# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
CLARITY_CORE v1.0.0 — SQUIRE PAGEKEEPER
=======================================
Autonomous Working Set Balancer and Memory Governor for Camelot-OS nodes.
Enforces Global Law 03:
  - Camelot-OS Node RAM Ceiling: 4,096 MB max (4 GB)
  - Sovereign Server Allowance: 8,192 MB max (8 GB)
  - Autonomous working set trimming via Win32 psapi.EmptyWorkingSet / Linux malloc_trim.
"""

from __future__ import annotations

import ctypes
import gc
import json
import logging
import os
import platform
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("SquirePageKeeper")

NODE_MAX_RAM_MB: float = 4096.0
SERVER_MAX_RAM_MB: float = 8192.0
DEFAULT_PRESSURE_THRESHOLD_PCT: float = 80.0


@dataclass
class MemoryAuditStatus:
    timestamp: str
    total_physical_mb: float
    free_physical_mb: float
    used_physical_mb: float
    utilization_pct: float
    process_working_set_mb: float
    node_ceiling_mb: float
    node_compliant: bool
    pressure_detected: bool
    action_taken: str
    reclaimed_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SquirePageKeeper:
    """Autonomous squire responsible for memory governance and working set trimming."""

    def __init__(
        self,
        node_ceiling_mb: float = NODE_MAX_RAM_MB,
        pressure_threshold_pct: float = DEFAULT_PRESSURE_THRESHOLD_PCT,
    ) -> None:
        self.node_ceiling_mb = node_ceiling_mb
        self.pressure_threshold_pct = pressure_threshold_pct

    @staticmethod
    def get_system_memory() -> Tuple[float, float, float, float]:
        """Returns (total_physical_mb, free_physical_mb, used_physical_mb, utilization_pct)."""
        if platform.system() == "Windows":
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
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                total_mb = round(stat.ullTotalPhys / (1024 * 1024), 2)
                avail_mb = round(stat.ullAvailPhys / (1024 * 1024), 2)
                used_mb = round(total_mb - avail_mb, 2)
                pct = round(float(stat.dwMemoryLoad), 1)
                return total_mb, avail_mb, used_mb, pct

        elif platform.system() == "Linux":
            try:
                meminfo = Path("/proc/meminfo").read_text(encoding="utf-8")
                data: Dict[str, float] = {}
                for line in meminfo.splitlines():
                    parts = line.split(":")
                    if len(parts) == 2:
                        k = parts[0].strip()
                        v = parts[1].strip().split()[0]
                        data[k] = float(v)
                total_mb = round(data.get("MemTotal", 0.0) / 1024.0, 2)
                avail_mb = round(data.get("MemAvailable", data.get("MemFree", 0.0)) / 1024.0, 2)
                used_mb = round(total_mb - avail_mb, 2)
                pct = round((used_mb / total_mb) * 100.0, 1) if total_mb > 0 else 0.0
                return total_mb, avail_mb, used_mb, pct
            except Exception:
                pass

        # Fallback simulation
        return 8192.0, 2048.0, 6144.0, 75.0

    @staticmethod
    def get_process_memory(pid: Optional[int] = None) -> float:
        """Returns process working set in MB."""
        target_pid = pid or os.getpid()
        if platform.system() == "Windows":
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", ctypes.c_ulong),
                    ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            PROCESS_QUERY_INFORMATION = 0x0400
            h_proc = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, target_pid)
            if h_proc:
                try:
                    counters = PROCESS_MEMORY_COUNTERS()
                    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
                    if ctypes.windll.psapi.GetProcessMemoryInfo(
                        h_proc, ctypes.byref(counters), counters.cb
                    ):
                        return round(counters.WorkingSetSize / (1024 * 1024), 2)
                finally:
                    ctypes.windll.kernel32.CloseHandle(h_proc)

        elif platform.system() == "Linux":
            try:
                statm = Path(f"/proc/{target_pid}/statm").read_text().split()
                # Page size is usually 4KB
                pages = int(statm[1])
                return round((pages * 4096) / (1024 * 1024), 2)
            except Exception:
                pass

        return 50.0

    def trim_self(self) -> float:
        """Flushes GC and trims the current process working set."""
        before = self.get_process_memory()
        gc.collect()

        if platform.system() == "Windows":
            try:
                h_current = ctypes.windll.kernel32.GetCurrentProcess()
                ctypes.windll.psapi.EmptyWorkingSet(h_current)
            except Exception as exc:
                LOG.debug(f"[PageKeeper] Self-trim error: {exc}")
        elif platform.system() == "Linux":
            try:
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            except Exception:
                pass

        time.sleep(0.05)
        after = self.get_process_memory()
        reclaimed = max(0.0, round(before - after, 2))
        return reclaimed

    def trim_system_working_sets(self, max_procs: int = 150) -> Tuple[int, float]:
        """Iterates accessible user processes and empties stale working sets."""
        if platform.system() != "Windows":
            return 0, 0.0

        _, before_free, _, _ = self.get_system_memory()
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400

        # Enumerate PIDs
        a_pids = (ctypes.c_ulong * 1024)()
        cb_needed = ctypes.c_ulong()
        trimmed_count = 0
        current_pid = os.getpid()

        if psapi.EnumProcesses(ctypes.byref(a_pids), ctypes.sizeof(a_pids), ctypes.byref(cb_needed)):
            n_pids = cb_needed.value // ctypes.sizeof(ctypes.c_ulong)
            for i in range(min(n_pids, max_procs)):
                pid = a_pids[i]
                if pid in (0, 4, current_pid):
                    continue
                h_proc = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
                if h_proc:
                    try:
                        if psapi.EmptyWorkingSet(h_proc):
                            trimmed_count += 1
                    except Exception:
                        pass
                    finally:
                        kernel32.CloseHandle(h_proc)

        time.sleep(0.2)
        _, after_free, _, _ = self.get_system_memory()
        reclaimed = max(0.0, round(after_free - before_free, 2))
        return trimmed_count, reclaimed

    def audit(self) -> MemoryAuditStatus:
        """Takes a point-in-time audit of system and process memory against Global Law 03."""
        total_mb, free_mb, used_mb, pct = self.get_system_memory()
        proc_mb = self.get_process_memory()

        node_compliant = proc_mb <= self.node_ceiling_mb
        pressure = pct >= self.pressure_threshold_pct

        return MemoryAuditStatus(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_physical_mb=total_mb,
            free_physical_mb=free_mb,
            used_physical_mb=used_mb,
            utilization_pct=pct,
            process_working_set_mb=proc_mb,
            node_ceiling_mb=self.node_ceiling_mb,
            node_compliant=node_compliant,
            pressure_detected=pressure,
            action_taken="AUDIT_ONLY",
            reclaimed_mb=0.0,
        )

    def govern(self, force_trim: bool = False) -> MemoryAuditStatus:
        """Evaluates memory state and executes surgical trims if under pressure or non-compliant."""
        status = self.audit()

        action = "NO_ACTION_REQUIRED"
        reclaimed = 0.0

        if force_trim or status.pressure_detected or not status.node_compliant:
            # 1. Trim own process
            reclaimed_self = self.trim_self()

            # 2. Trim system working sets if system is under pressure or force requested
            trimmed_procs, reclaimed_sys = self.trim_system_working_sets()
            reclaimed = round(reclaimed_self + reclaimed_sys, 2)

            action = f"TRIM_EXECUTED (self: {reclaimed_self}MB, {trimmed_procs} procs: {reclaimed_sys}MB)"

        # Re-evaluate
        final_status = self.audit()
        final_status.action_taken = action
        final_status.reclaimed_mb = reclaimed
        return final_status
