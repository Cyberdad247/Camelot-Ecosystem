# -*- coding: utf-8 -*-
"""
[S5-03] AudioSession — Full-Duplex Audio Session Orchestrator
==============================================================
Wires: VAD → interrupt_controller → intent_router → knight dispatch → kitten TTS

Turn structure (one complete exchange):
  1. Listen  : wait for wake_event (fired by omnivoice-router VAD on utterance end)
  2. Classify: intent_router classifies transcript text → terminal selection
  3. Dispatch: push directive to harness_queue.jsonl, await knight text stream
  4. Speak   : kitten.synthesize_chunked_async() → yield audio chunks downstream
  5. Interrupt: if VAD fires mid-TTS → vad_controller.interrupt() → abort early

Usage:
    session = AudioSession()
    async for audio_chunk in session.run_turn(transcript_text):
        send_to_speaker(audio_chunk)

    # When omnivoice-router VAD detects user speaking mid-TTS:
    session.on_vad_interrupt()
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator, Optional

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
QUEUE_PATH = HOME / "control_plane" / "harness_queue.jsonl"


class AudioSession:
    """Full-duplex audio session: VAD → intent → knight → TTS with interrupt support."""

    def __init__(
        self,
        kitten=None,
        board=None,
        vad_controller=None,
    ) -> None:
        # Lazy imports to avoid circular deps at module level
        if kitten is None:
            from kitten_service import kitten_service as _ks
            kitten = _ks
        if vad_controller is None:
            from vad_interrupt import vad_controller as _vc
            vad_controller = _vc

        self.kitten = kitten
        self.board = board  # Switchboard — set lazily if None
        self.vad = vad_controller
        self._turn_count = 0
        self._session_start = time.monotonic()

    # ── Public API ────────────────────────────────────────────────────────────

    def on_vad_interrupt(self) -> None:
        """Call from omnivoice-router when VAD detects user speech mid-TTS."""
        self.vad.interrupt()

    async def run_turn(
        self,
        transcript: str,
        mode: str = "efficiency",
    ) -> AsyncGenerator[bytes, None]:
        """Run one full voice turn: classify → dispatch → TTS stream.

        Yields audio bytes. Stops early if VAD interrupt fires.
        """
        self._turn_count += 1
        turn_id = f"turn-{self._turn_count}-{datetime.now(timezone.utc).strftime('%H%M%S')}"

        # Step 1: classify intent
        terminal, category, confidence = await self._classify(transcript)
        terminal_id = terminal.id if terminal else "unknown"

        # Step 2: dispatch to knight via harness queue; get text stream back
        text_stream = self._dispatch_to_knight(transcript, terminal_id, turn_id, category.value)

        # Step 3: synthesize with interrupt support
        async for audio_chunk in self.vad.synthesize_interruptible(
            token_stream=text_stream,
            kitten=self.kitten,
            mode=mode,
        ):
            yield audio_chunk

        if self.vad.is_interrupted:
            pass  # caller handles flush; reset on next turn_start

    async def wait_for_vad(self, timeout: float = 30.0) -> bool:
        """Block until VAD fires (user finishes speaking) or timeout."""
        try:
            await asyncio.wait_for(self.vad._interrupt.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    def start_listening(self) -> None:
        """Reset interrupt and begin listening phase."""
        self.vad.reset()

    async def run_swarm_turn(
        self,
        segments: list,
        mode: str = "simultaneous",
    ) -> AsyncGenerator[tuple, None]:
        """
        Multi-knight swarm turn via LYRICUS_v4.

        Accepts a list of (knight_id, text) tuples and runs them through the
        vocal synthesis engine in the specified mode.

        mode: "sequential" | "simultaneous" | "debate"

        Yields (knight_id, pcm_bytes, sample_rate) tuples.

        Example — parallel Foundry Council audit report:
            async for kid, pcm, sr in session.run_swarm_turn([
                ("sir_sentinel", "Security: no vulnerabilities found."),
                ("sir_boris",    "Architecture: clean, one refactor suggested."),
                ("sir_gideon",   "Forensics: zero leaked secrets."),
            ], mode="simultaneous"):
                play_audio(kid, pcm, sr)
        """
        from senses.audio.lyricus_v4 import lyricus, VocalMode, VocalSegment

        mode_map = {
            "sequential":   VocalMode.SEQUENTIAL,
            "simultaneous": VocalMode.SIMULTANEOUS,
            "debate":       VocalMode.DEBATE,
        }
        vocal_mode = mode_map.get(mode.lower(), VocalMode.SEQUENTIAL)

        vocal_segments = [
            VocalSegment(knight_id=kid, text=txt, position=i)
            for i, (kid, txt) in enumerate(segments)
        ]

        async for chunk in lyricus.synthesize(vocal_segments, vocal_mode):
            yield chunk

    def stats(self) -> dict:
        return {
            "turns": self._turn_count,
            "uptime_s": round(time.monotonic() - self._session_start, 1),
            "vad": self.vad.stats(),
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _classify(self, text: str):
        """Classify intent, lazy-loading switchboard if not injected."""
        from control_plane.intent_router import route_by_intent, IntentCategory

        if self.board is None:
            from control_plane.switchboard import get_board
            self.board = get_board()

        return await route_by_intent(text, self.board)

    async def _dispatch_to_knight(
        self,
        directive: str,
        terminal_id: str,
        turn_id: str,
        intent: str,
    ) -> AsyncGenerator[str, None]:
        """Enqueue directive and yield text tokens.

        Current implementation: enqueue to harness_queue and yield a
        placeholder stream. Full async streaming from harness requires
        a response channel (e.g., Redis pub/sub or asyncio.Queue returned
        by the harness worker). Wired as a TODO boundary.
        """
        task = {
            "id": turn_id,
            "type": "forge",
            "directive": directive,
            "terminal": terminal_id,
            "intent": intent,
            "source": "audio_session",
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "priority": 1,
        }
        try:
            with QUEUE_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(task) + "\n")
        except Exception as e:
            yield f"[AudioSession] queue error: {e}"
            return

        # TODO: replace with real async harness response stream
        # For now: acknowledgement token so TTS has something to synthesize
        yield f"Processing directive via {terminal_id}. "
        yield f"Intent classified as {intent}. "
        yield "Response will follow."
        await asyncio.sleep(0)  # yield control

    async def _response_stream_from_harness(
        self,
        turn_id: str,
        timeout: float = 30.0,
    ) -> AsyncGenerator[str, None]:
        """Placeholder: poll logs/harness_responses/ for turn_id result.

        Replace with Redis SUBSCRIBE or asyncio.Queue once harness worker
        implements response channels.
        """
        response_path = HOME / "logs" / "harness_responses" / f"{turn_id}.txt"
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if response_path.exists():
                text = response_path.read_text(encoding="utf-8")
                for word in text.split():
                    yield word + " "
                    await asyncio.sleep(0)
                return
            await asyncio.sleep(0.5)
        yield "[timeout waiting for harness response]"


# Module-level singleton
audio_session = AudioSession()
