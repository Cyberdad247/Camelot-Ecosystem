# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
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
from typing import AsyncGenerator

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
QUEUE_PATH = HOME / "logs" / "harness_queue.jsonl"


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
        """Run one full voice turn: classify → enqueue → poll response → TTS stream.

        Yields audio bytes. Stops early if VAD interrupt fires.
        """
        self._turn_count += 1
        turn_id = f"turn-{self._turn_count}-{datetime.now(timezone.utc).strftime('%H%M%S')}"

        # Step 1: classify intent
        terminal, category, confidence = await self._classify(transcript)
        terminal_id = terminal.id if terminal else "unknown"

        # Step 2: enqueue directive to harness queue
        enqueue_ok = await self._enqueue_task(transcript, terminal_id, turn_id, category.value)

        # Step 3: stream real response from harness worker (falls back to error token on queue fail)
        if enqueue_ok:
            text_stream = self._response_stream_from_harness(turn_id)
        else:
            async def _err_stream():
                yield "[queue error — cannot dispatch]"
            text_stream = _err_stream()

        # Step 4: synthesize with interrupt support
        async for audio_chunk in self.vad.synthesize_interruptible(
            token_stream=text_stream,
            kitten=self.kitten,
            mode=mode,
            knight_id=terminal_id,
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
        from senses.audio.lyricus_v4 import VocalMode, VocalSegment, lyricus

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
        import re

        from control_plane.intent_router import IntentCategory, route_by_intent

        if self.board is None:
            from control_plane.switchboard import get_board
            self.board = get_board()

        # Dynamic Knight swapping keywords/triggers
        text_lower = text.lower()
        triggers = {
            "sir_sentinel": ["sentinel", "sir sentinel", "security"],
            "sir_forge": ["forge", "sir forge", "execute"],
            "sir_boris": ["boris", "sir boris", "architect"],
            "sir_alex": ["alex", "sir alex", "planner"],
            "sir_ghost": ["ghost", "sir ghost", "privacy"],
            "sir_gideon": ["gideon", "sir gideon", "forensic"],
            "sir_octavian": ["octavian", "sir octavian", "ops"],
            "sir_mnemo": ["mnemo", "sir mnemo", "memory"],
            "sir_link": ["link", "sir link"],
            "lady_apis": ["apis", "lady apis", "research"],
            "sir_sonus": ["sonus", "sir sonus", "voice", "speech"],
            "sir_gravity": ["gravity", "antigravity", "sir gravity"],
            "sir_kimi": ["kimi", "sir kimi"],
            "sir_hermes": ["hermes", "sir hermes"],
        }
        for knight_id, keywords in triggers.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    term = await self.board.probe_one(knight_id)
                    if term and term.status in ("live", "assumed_live"):
                        # Map to appropriate category
                        cat_map = {
                            "sir_sentinel": IntentCategory.SECURITY,
                            "sir_forge": IntentCategory.CODE,
                            "sir_boris": IntentCategory.FORGE,
                            "sir_alex": IntentCategory.GENERAL,
                            "sir_ghost": IntentCategory.SECURITY,
                            "sir_gideon": IntentCategory.SECURITY,
                            "sir_octavian": IntentCategory.OPS,
                            "sir_mnemo": IntentCategory.MEMORY,
                            "lady_apis": IntentCategory.RESEARCH,
                        }
                        category = cat_map.get(knight_id, IntentCategory.GENERAL)
                        return term, category, 1.0

        return await route_by_intent(text, self.board)

    async def _enqueue_task(
        self,
        directive: str,
        terminal_id: str,
        turn_id: str,
        intent: str,
    ) -> bool:
        """Write directive to harness_queue.jsonl. Returns True on success."""
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
            return True
        except Exception:
            return False

    async def _response_stream_from_harness(
        self,
        turn_id: str,
        timeout: float = 30.0,
    ) -> AsyncGenerator[str, None]:
        """Stream response: tries Redis pub/sub first, falls back to file polling."""
        # ── Redis path (low-latency) ──────────────────────────────────────────
        raw = await asyncio.to_thread(self._redis_subscribe, turn_id, timeout)
        if raw is not None:
            try:
                text = json.loads(raw).get("text", raw)
            except Exception:
                text = raw
            for word in text.split():
                yield word + " "
                await asyncio.sleep(0)
            return

        # ── File-polling fallback ─────────────────────────────────────────────
        response_path = HOME / "logs" / "harness_responses" / f"{turn_id}.json"
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if response_path.exists():
                try:
                    data = json.loads(response_path.read_text(encoding="utf-8"))
                    text = data.get("text", "")
                except Exception:
                    text = response_path.read_text(encoding="utf-8")
                for word in text.split():
                    yield word + " "
                    await asyncio.sleep(0)
                return
            await asyncio.sleep(0.5)
        yield "[timeout waiting for harness response]"

    def _redis_subscribe(self, turn_id: str, timeout: float) -> str | None:
        """Blocking Redis subscribe — runs in thread pool via asyncio.to_thread."""
        try:
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location(
                "local_store", HOME / "01_KERNEL" / "memory" / "local_store.py"
            )
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
            return _mod.local_store.subscribe_one(turn_id, timeout)
        except Exception:
            return None


# Module-level singleton
audio_session = AudioSession()
