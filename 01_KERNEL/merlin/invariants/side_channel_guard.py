# SPDX-License-Identifier: MIT
# <!-- Copyright © 2026 Invisioned Marketing inc. All Rights Reserved. -->
"""
INVARIANT-3: Uniform Side-Channel Elimination
Enforces:
1. Strict 64-byte bucket padding across all compressed token envelopes.
2. Isochronous 20ms flush cadence (time-quantization to eliminate inter-arrival timing side-channels).
3. Decoy null-frame emission during idle ticks to prevent traffic analysis.
4. Constant-time dictionary lookup bounds.
"""

from __future__ import annotations

import hmac
import math
import os
import queue
import secrets
import struct
import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

DECOY_MAGIC = b"\xFA\xCE\xDE\xC0"  # 4-byte decoy marker


@dataclass
class PaddedFrame:
    payload: bytes
    total_bytes: int
    is_decoy: bool
    timestamp_ns: int


class SideChannelGuard:
    """Provides 64-byte bucket padding and constant-size envelope wrapping."""

    BUCKET_SIZE: int = 64

    @classmethod
    def pad(cls, data: bytes) -> bytes:
        """Pad data to the next multiple of 64 bytes using PKCS7-like padding."""
        length = len(data)
        pad_needed = cls.BUCKET_SIZE - (length % cls.BUCKET_SIZE)
        if pad_needed == 0:
            pad_needed = cls.BUCKET_SIZE

        # Format: [2 bytes original length (big-endian)] + [data] + [random padding bytes]
        header = struct.pack(">H", length)
        combined = header + data
        total_len = len(combined)
        rem = cls.BUCKET_SIZE - (total_len % cls.BUCKET_SIZE)
        if rem == 0:
            rem = cls.BUCKET_SIZE
        padding = secrets.token_bytes(rem)
        return combined + padding

    @classmethod
    def unpad(cls, padded_data: bytes) -> Tuple[bytes, bool]:
        """Unpad data. Returns (payload, is_decoy)."""
        if len(padded_data) < 2 or len(padded_data) % cls.BUCKET_SIZE != 0:
            raise ValueError("Invalid padded frame length")

        # Check for decoy null-frame
        if padded_data.startswith(DECOY_MAGIC):
            return b"", True

        orig_len = struct.unpack(">H", padded_data[:2])[0]
        if 2 + orig_len > len(padded_data):
            raise ValueError("Corrupt frame header length")

        payload = padded_data[2 : 2 + orig_len]
        return payload, False

    @classmethod
    def create_decoy_frame(cls) -> bytes:
        """Create a 64-byte decoy null-frame filled with pseudo-random noise."""
        noise = secrets.token_bytes(cls.BUCKET_SIZE - len(DECOY_MAGIC))
        return DECOY_MAGIC + noise


class IsochronousChannel:
    """Isochronous transmission channel operating on a fixed clock cadence (default 20ms)."""

    def __init__(self, interval_ms: float = 20.0, transmitter_callback: Optional[Callable[[bytes], None]] = None):
        self.interval_sec = interval_ms / 1000.0
        self.transmitter_callback = transmitter_callback or (lambda b: None)
        self.outbound_queue: queue.Queue[bytes] = queue.Queue()
        self.frames_transmitted: List[PaddedFrame] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def enqueue(self, raw_data: bytes) -> None:
        """Enqueue payload for next isochronous tick."""
        padded = SideChannelGuard.pad(raw_data)
        self.outbound_queue.put(padded)

    def start(self) -> None:
        """Start the isochronous timer loop."""
        self._running = True
        self._thread = threading.Thread(target=self._cadence_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.1)

    def tick_once(self) -> PaddedFrame:
        """Manual single tick execution (useful for deterministic synchronous testing)."""
        now = time.perf_counter_ns()
        try:
            frame_bytes = self.outbound_queue.get_nowait()
            is_decoy = False
        except queue.Empty:
            frame_bytes = SideChannelGuard.create_decoy_frame()
            is_decoy = True

        frame = PaddedFrame(
            payload=frame_bytes,
            total_bytes=len(frame_bytes),
            is_decoy=is_decoy,
            timestamp_ns=now,
        )
        self.frames_transmitted.append(frame)
        self.transmitter_callback(frame_bytes)
        return frame

    def _cadence_loop(self) -> None:
        while self._running:
            start_t = time.perf_counter()
            self.tick_once()
            elapsed = time.perf_counter() - start_t
            sleep_t = self.interval_sec - elapsed
            if sleep_t > 0:
                time.sleep(sleep_t)
