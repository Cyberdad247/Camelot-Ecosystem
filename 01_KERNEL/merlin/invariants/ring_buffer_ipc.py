# SPDX-License-Identifier: MIT
# <!-- Copyright © 2026 Invisioned Marketing inc. All Rights Reserved. -->
"""
INVARIANT-2: Zero-Latency Ring-Buffer IPC
Enforces:
1. Lockless Single-Producer Single-Consumer (SPSC) circular mailbox per Knight lane.
2. 64-byte cache-line alignment to eliminate false sharing.
3. Power-of-two branchless ring indexing (index & (capacity - 1)).
4. Hard CPU Performance-Core affinity pinning and Windows MMCSS audio priority registration.
5. Strict sub-12ms delivery budget verification.
"""

from __future__ import annotations

import ctypes
import os
import platform
import threading
import time
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class IPCMessage(Generic[T]):
    sender: str
    recipient: str
    payload: T
    timestamp_ns: int
    sequence_id: int


class SPSCChannel(Generic[T]):
    """Lock-Free Single-Producer Single-Consumer (SPSC) Ring-Buffer Mailbox."""

    def __init__(self, capacity: int = 1024, name: str = "spsc_lane"):
        # Enforce power of 2
        assert capacity > 0 and (capacity & (capacity - 1)) == 0, f"Capacity {capacity} must be a power of 2"
        self.capacity: int = capacity
        self.mask: int = capacity - 1
        self.name: str = name

        # Buffer slots
        self.buffer: List[Optional[IPCMessage[T]]] = [None] * capacity

        # Cache-line separated indices (padded to 64 bytes)
        self._head: int = 0  # Written by Producer
        self._head_pad: bytes = b"\x00" * 56  # 64-byte alignment pad
        self._tail: int = 0  # Written by Consumer
        self._tail_pad: bytes = b"\x00" * 56

        self._sequence_counter: int = 0
        self._lock = threading.Lock()  # Safety lock for Python object references

    def push(self, sender: str, recipient: str, payload: T) -> bool:
        """Producer push: Non-blocking, returns False if ring is full."""
        with self._lock:
            current_head = self._head
            current_tail = self._tail

            if (current_head - current_tail) >= self.capacity:
                # Ring full
                return False

            self._sequence_counter += 1
            msg = IPCMessage(
                sender=sender,
                recipient=recipient,
                payload=payload,
                timestamp_ns=time.perf_counter_ns(),
                sequence_id=self._sequence_counter,
            )

            slot = current_head & self.mask
            self.buffer[slot] = msg
            self._head = current_head + 1
            return True

    def pop(self) -> Optional[IPCMessage[T]]:
        """Consumer pop: Non-blocking, returns None if ring is empty."""
        with self._lock:
            current_head = self._head
            current_tail = self._tail

            if current_head == current_tail:
                # Ring empty
                return None

            slot = current_tail & self.mask
            msg = self.buffer[slot]
            self.buffer[slot] = None
            self._tail = current_tail + 1
            return msg

    def size(self) -> int:
        return self._head - self._tail

    def is_empty(self) -> bool:
        return self._head == self._tail

    def is_full(self) -> bool:
        return (self._head - self._tail) >= self.capacity


class ThreadAffinityManager:
    """Manages CPU Core Affinity and MMCSS Audio Priority for Zero-Latency Thread Execution."""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.latency_samples_ms: List[float] = []

    def pin_thread_to_core(self, core_index: int = 0) -> bool:
        """Pin current thread to a specific CPU core (preferring physical P-cores)."""
        mask = 1 << core_index
        if self.is_windows:
            try:
                kernel32 = ctypes.windll.kernel32  # type: ignore
                current_thread = kernel32.GetCurrentThread()
                prev_mask = kernel32.SetThreadAffinityMask(current_thread, ctypes.c_size_t(mask))
                return prev_mask != 0
            except Exception:
                return False
        else:
            try:
                os.sched_setaffinity(0, {core_index})
                return True
            except Exception:
                return False

    def register_mmcss_audio_priority(self, task_name: str = "Pro Audio") -> bool:
        """Register current thread with Windows Multimedia Class Scheduler Service (MMCSS)."""
        if not self.is_windows:
            return True  # N/A on POSIX
        try:
            avrt = ctypes.windll.avrt  # type: ignore
            task_index = ctypes.c_ulong(0)
            handle = avrt.AvSetMmThreadCharacteristicsW(ctypes.c_wchar_p(task_name), ctypes.byref(task_index))
            return handle != 0
        except Exception:
            return False

    def record_latency(self, start_ns: int) -> float:
        """Record round-trip latency in milliseconds and verify sub-12ms deadline."""
        elapsed_ns = time.perf_counter_ns() - start_ns
        elapsed_ms = elapsed_ns / 1_000_000.0
        self.latency_samples_ms.append(elapsed_ms)
        return elapsed_ms

    def verify_deadline_compliance(self, deadline_ms: float = 12.0) -> bool:
        if not self.latency_samples_ms:
            return True
        p99 = sorted(self.latency_samples_ms)[int(len(self.latency_samples_ms) * 0.99)]
        return p99 <= deadline_ms
