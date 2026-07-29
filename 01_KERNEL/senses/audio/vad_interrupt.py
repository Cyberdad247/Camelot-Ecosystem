# Copyright (c) 2026 CAMELOT-OS. All rights reserved.
# -*- coding: utf-8 -*-
"""
[S4-03] VAD Interrupt Controller — interruptible TTS pipeline.

When omnivoice-router detects speech (VAD fires) mid-TTS playback, this module:
  1. Sets an asyncio.Event (interrupt signal)
  2. synthesize_interruptible() checks the signal before each yielded chunk
  3. Generator exits early; caller drains the audio buffer and clears it

Usage:
    controller = VadInterruptController()

    # Producer (omnivoice-router on VAD detection):
    controller.interrupt()

    # Consumer (audio playback loop):
    async for chunk in controller.synthesize_interruptible(token_stream, kitten):
        play(chunk)          # interrupted early when user speaks

    # Reset before next turn:
    controller.reset()
"""
from __future__ import annotations

import asyncio
import time
from typing import AsyncGenerator, TYPE_CHECKING

if TYPE_CHECKING:
    from kitten_service import KittenService


class VadInterruptController:
    """asyncio.Event-based interrupt gate for streaming TTS."""

    def __init__(self) -> None:
        self._interrupt = asyncio.Event()
        self._interrupt_count = 0
        self._last_interrupt_ts: float | None = None

    def interrupt(self) -> None:
        """Signal that VAD detected user speech — abort current TTS stream."""
        self._interrupt.set()
        self._interrupt_count += 1
        self._last_interrupt_ts = time.monotonic()

    def reset(self) -> None:
        """Clear interrupt signal — call before starting a new TTS turn."""
        self._interrupt.clear()

    @property
    def is_interrupted(self) -> bool:
        return self._interrupt.is_set()

    async def synthesize_interruptible(
        self,
        token_stream: AsyncGenerator[str, None],
        kitten: "KittenService",
        mode: str = "efficiency",
        drain_on_interrupt: bool = True,
        knight_id: str = "tasha",
    ) -> AsyncGenerator[bytes, None]:
        """Wrap kitten.synthesize_chunked_async() with interrupt support.

        Yields audio chunks until either:
          a) The token_stream is exhausted (normal completion), or
          b) The interrupt event fires (user spoke — abort mid-stream)

        Args:
            drain_on_interrupt: if True, consume remaining tokens from generator
                                 after interrupt (prevents upstream coroutine hang).
            knight_id: the active Knight ID for synthesis
        """
        self.reset()

        async def _guarded_stream() -> AsyncGenerator[bytes, None]:
            async for chunk in kitten.synthesize_chunked_async(token_stream, mode=mode, knight_id=knight_id):
                if self._interrupt.is_set():
                    break
                yield chunk
                # Yield control so interrupt can be set between chunks
                await asyncio.sleep(0)

        async for audio_bytes in _guarded_stream():
            yield audio_bytes
            if self._interrupt.is_set():
                break

        if self._interrupt.is_set():
            # Drain remaining tokens to unblock upstream generator
            if drain_on_interrupt:
                try:
                    async for _ in token_stream:
                        pass
                except Exception:
                    pass

    def stats(self) -> dict:
        return {
            "interrupt_count": self._interrupt_count,
            "last_interrupt_ts": self._last_interrupt_ts,
            "currently_interrupted": self.is_interrupted,
        }


# Module-level singleton — shared between omnivoice-router and kitten pipeline
vad_controller = VadInterruptController()
