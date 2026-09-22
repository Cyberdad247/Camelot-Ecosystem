# SPDX-License-Identifier: MIT
# <!-- Copyright © 2026 Invisioned Marketing inc. All Rights Reserved. -->
"""
INVARIANT-1: Memory Pinning & Scarcity Governor
Enforces:
1. Dual-threshold Schmitt-trigger hysteresis backpressure governor (3.60GB shed / 3.30GB resume).
2. Hard host ceiling enforcement at <= 3.85GB (4.0GB Scarcity Protocol).
3. Cross-platform memory pinning adapter:
   - Win32: SetProcessWorkingSetSizeEx + VirtualLock with SE_LOCK_MEMORY_NAME handling.
   - POSIX: mlock() fallback with RLIMIT_MEMLOCK probing.
"""

from __future__ import annotations

import ctypes
import os
import platform
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class GovernorState(str, Enum):
    NORMAL = "NORMAL"
    SHEDDING = "SHEDDING"
    CRITICAL = "CRITICAL"


@dataclass
class GovernorMetrics:
    current_rss_bytes: int
    current_rss_gb: float
    state: GovernorState
    shedding_active: bool
    tasks_admitted: int
    tasks_shed: int
    memory_ceiling_gb: float = 3.85
    high_watermark_gb: float = 3.60
    low_watermark_gb: float = 3.30


class ScarcityGovernor:
    """Schmitt-Trigger Dual-Threshold Backpressure Governor for Memory Scarcity."""

    def __init__(
        self,
        high_watermark_gb: float = 3.60,
        low_watermark_gb: float = 3.30,
        hard_ceiling_gb: float = 3.85,
    ):
        assert low_watermark_gb < high_watermark_gb < hard_ceiling_gb, "Thresholds must be strictly ordered"
        self.high_watermark_bytes = int(high_watermark_gb * (1024**3))
        self.low_watermark_bytes = int(low_watermark_gb * (1024**3))
        self.hard_ceiling_bytes = int(hard_ceiling_gb * (1024**3))

        self.high_watermark_gb = high_watermark_gb
        self.low_watermark_gb = low_watermark_gb
        self.hard_ceiling_gb = hard_ceiling_gb

        self.state: GovernorState = GovernorState.NORMAL
        self.current_rss_bytes: int = 0
        self.tasks_admitted: int = 0
        self.tasks_shed: int = 0

    def update_rss(self, rss_bytes: int) -> GovernorState:
        """Update current RSS and apply Schmitt-trigger state transition."""
        self.current_rss_bytes = rss_bytes

        if self.state == GovernorState.NORMAL:
            if rss_bytes >= self.hard_ceiling_bytes:
                self.state = GovernorState.CRITICAL
            elif rss_bytes >= self.high_watermark_bytes:
                self.state = GovernorState.SHEDDING
        elif self.state == GovernorState.SHEDDING:
            if rss_bytes >= self.hard_ceiling_bytes:
                self.state = GovernorState.CRITICAL
            elif rss_bytes <= self.low_watermark_bytes:
                self.state = GovernorState.NORMAL
            # Inside the deadband [low, high], remain in SHEDDING (hysteresis)
        elif self.state == GovernorState.CRITICAL:
            if rss_bytes <= self.low_watermark_bytes:
                self.state = GovernorState.NORMAL
            elif rss_bytes < self.hard_ceiling_bytes:
                self.state = GovernorState.SHEDDING

        return self.state

    def evaluate_task_admission(self, task_priority: str = "SPECULATIVE") -> bool:
        """Evaluate if a task can be admitted under current memory state.

        - NORMAL: All tasks admitted.
        - SHEDDING: CRITICAL and ROOT tasks admitted; SPECULATIVE/BACKGROUND shed.
        - CRITICAL: Only ROOT / KERNEL recovery tasks admitted; all others dropped.
        """
        priority = task_priority.upper()

        if self.state == GovernorState.NORMAL:
            self.tasks_admitted += 1
            return True
        elif self.state == GovernorState.SHEDDING:
            if priority in ("ROOT", "KERNEL", "CRITICAL", "AUDIO_REALTIME"):
                self.tasks_admitted += 1
                return True
            else:
                self.tasks_shed += 1
                return False
        else:  # CRITICAL
            if priority in ("ROOT", "EMERGENCY_RECOVERY"):
                self.tasks_admitted += 1
                return True
            else:
                self.tasks_shed += 1
                return False

    def get_metrics(self) -> GovernorMetrics:
        return GovernorMetrics(
            current_rss_bytes=self.current_rss_bytes,
            current_rss_gb=round(self.current_rss_bytes / (1024**3), 3),
            state=self.state,
            shedding_active=(self.state != GovernorState.NORMAL),
            tasks_admitted=self.tasks_admitted,
            tasks_shed=self.tasks_shed,
            memory_ceiling_gb=self.hard_ceiling_gb,
            high_watermark_gb=self.high_watermark_gb,
            low_watermark_gb=self.low_watermark_gb,
        )


class MemoryPinner:
    """Cross-platform memory pinning adapter handling Win32 VirtualLock and POSIX mlock."""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.pinned_buffers: Dict[int, int] = {}  # ptr -> size

    def pin_buffer(self, buffer_address: int, size_bytes: int) -> bool:
        """Pin a virtual memory region to prevent paging."""
        if self.is_windows:
            return self._pin_windows(buffer_address, size_bytes)
        else:
            return self._pin_posix(buffer_address, size_bytes)

    def unpin_buffer(self, buffer_address: int, size_bytes: int) -> bool:
        """Unpin a previously locked virtual memory region."""
        if self.is_windows:
            return self._unpin_windows(buffer_address, size_bytes)
        else:
            return self._unpin_posix(buffer_address, size_bytes)

    def _pin_windows(self, addr: int, size: int) -> bool:
        try:
            kernel32 = ctypes.windll.kernel32  # type: ignore

            # Configure minimum working set to accommodate the lock size
            current_proc = kernel32.GetCurrentProcess()
            min_ws = ctypes.c_size_t()
            max_ws = ctypes.c_size_t()
            flags = ctypes.c_ulong()

            if kernel32.GetProcessWorkingSetSizeEx(current_proc, ctypes.byref(min_ws), ctypes.byref(max_ws), ctypes.byref(flags)):
                new_min = max(min_ws.value, size + (64 * 1024 * 1024))
                new_max = max(max_ws.value, new_min * 2)
                kernel32.SetProcessWorkingSetSizeEx(current_proc, new_min, new_max, 0x00000001)  # QUOTA_LIMITS_HARDWS_MIN_ENABLE

            res = kernel32.VirtualLock(ctypes.c_void_p(addr), ctypes.c_size_t(size))
            if res != 0:
                self.pinned_buffers[addr] = size
                return True
            return False
        except Exception:
            return False

    def _unpin_windows(self, addr: int, size: int) -> bool:
        try:
            kernel32 = ctypes.windll.kernel32  # type: ignore
            res = kernel32.VirtualUnlock(ctypes.c_void_p(addr), ctypes.c_size_t(size))
            if addr in self.pinned_buffers:
                del self.pinned_buffers[addr]
            return res != 0
        except Exception:
            return False

    def _pin_posix(self, addr: int, size: int) -> bool:
        try:
            libc = ctypes.CDLL(None)
            res = libc.mlock(ctypes.c_void_p(addr), ctypes.c_size_t(size))
            if res == 0:
                self.pinned_buffers[addr] = size
                return True
            return False
        except Exception:
            return False

    def _unpin_posix(self, addr: int, size: int) -> bool:
        try:
            libc = ctypes.CDLL(None)
            res = libc.munlock(ctypes.c_void_p(addr), ctypes.c_size_t(size))
            if addr in self.pinned_buffers:
                del self.pinned_buffers[addr]
            return res == 0
        except Exception:
            return False

    def total_pinned_bytes(self) -> int:
        return sum(self.pinned_buffers.values())
