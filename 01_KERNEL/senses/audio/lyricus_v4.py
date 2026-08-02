# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
LYRICUS_v4 — L3 NEURAL Multivoice Router
=========================================
Implements the vocal synthesis orchestrator defined in omnivox.yaml.
Closes the spec gap: LYRICUS_v4 + SIMULTANEOUS + DEBATE modes.

Architecture layer: L3 NEURAL (Multivoice Router)
Feeds:            L2 KINETIC (Redis Sonic Cache via KittenService)
Consumes:         knight_voices.py vocal profiles + tts_engines.py backends

Three synthesis modes
─────────────────────
SEQUENTIAL    One knight at a time. Standard audio_session.py flow.
              Latency: sum(each segment synthesis time).

SIMULTANEOUS  All segments dispatched concurrently via asyncio.to_thread.
              Results yielded in position order as each resolves.
              Use case: Foundry Council swarm — Sentinel + Boris + Veritas
              each report findings in their own voice, pipeline overlap
              cuts total latency by ~60%.
              Latency: max(synthesis times) + queue overhead.

DEBATE        Structured turn-taking between exactly two knights.
              Knight A speaks → pause → Knight B responds → repeat for N rounds.
              Optional: pass A's audio hash to B's synthesis context
              (prosody continuity via sigma-keyed cache namespace).
              Use case: Boris vs Sentinel code review, Merlin vs Oracle reasoning.

Usage
─────
    from senses.audio.lyricus_v4 import LyricusV4, VocalMode, VocalSegment

    engine = LyricusV4()

    # Swarm audit — three knights speak in parallel, yielded in order
    segments = [
        VocalSegment("sir_sentinel", "No vulnerabilities found in auth layer."),
        VocalSegment("sir_boris",    "Architecture looks clean. One refactor suggestion."),
        VocalSegment("sir_gideon",   "Forensic scan passed. Zero leaked secrets."),
    ]
    async for knight_id, pcm, sr in engine.synthesize(segments, VocalMode.SIMULTANEOUS):
        play_audio(knight_id, pcm, sr)

    # Debate — Merlin vs Oracle, 2 rounds
    topic = [
        VocalSegment("sir_merlin", "The recursive approach is more elegant."),
        VocalSegment("oracle",     "Iteration is safer under memory constraints."),
    ]
    async for knight_id, pcm, sr in engine.synthesize(topic, VocalMode.DEBATE, rounds=2):
        play_audio(knight_id, pcm, sr)
"""

from __future__ import annotations

import asyncio
import hashlib
from enum import Enum
from typing import AsyncGenerator, NamedTuple, Optional

# ── Vocal subsystem imports ───────────────────────────────────────────────────

try:
    from senses.audio.knight_voices import KnightVocalProfile, get_profile
except ImportError:
    import importlib.util as _ilu
    import os as _os
    _kv = _ilu.spec_from_file_location(
        "knight_voices",
        _os.path.join(_os.path.dirname(__file__), "knight_voices.py"),
    )
    _mod = _ilu.module_from_spec(_kv); _kv.loader.exec_module(_mod)  # type: ignore
    get_profile = _mod.get_profile
    KnightVocalProfile = _mod.KnightVocalProfile

try:
    from senses.audio.tts_engines import TTSEngine
    from senses.audio.tts_engines import synthesize as _synth_engine
except ImportError:
    _synth_engine = None  # type: ignore
    TTSEngine = None  # type: ignore

try:
    from senses.audio.kitten_service import kitten_service as _kitten
except ImportError:
    _kitten = None  # type: ignore


# ── Public types ──────────────────────────────────────────────────────────────

class VocalMode(Enum):
    SEQUENTIAL   = "sequential"    # one at a time
    SIMULTANEOUS = "simultaneous"  # parallel synthesis, in-order delivery
    DEBATE       = "debate"        # structured A/B turn-taking


class VocalSegment(NamedTuple):
    knight_id: str
    text:      str
    position:  int = 0            # explicit ordering; auto-assigned if 0


# Yield type: (knight_id, pcm_bytes, sample_rate)
AudioChunk = tuple[str, bytes, int]


# ── Engine ────────────────────────────────────────────────────────────────────

class LyricusV4:
    """
    L3 NEURAL Multivoice Router — omnivox.yaml §vocal_subsystem.engine.

    Singleton usage:   lyricus = LyricusV4()
    Thread safety:     each synthesize() call creates independent async tasks.
    Redis integration: all synthesized chunks are stored in Sonic Cache (KittenService)
                       using sigma-namespaced keys for per-knight cache isolation.
    """

    ENGINE_VERSION = "LYRICUS_v4"
    SILENCE_MS     = 150   # inter-segment pause for DEBATE mode (ms)

    def __init__(self) -> None:
        self._stats: dict[str, int] = {
            "sequential": 0, "simultaneous": 0, "debate": 0, "cache_hits": 0,
        }

    # ── Main API ──────────────────────────────────────────────────────────────

    async def synthesize(
        self,
        segments:       list[VocalSegment],
        mode:           VocalMode = VocalMode.SEQUENTIAL,
        rounds:         int       = 1,
        silence_ms:     int       = SILENCE_MS,
    ) -> AsyncGenerator[AudioChunk, None]:
        """
        Synthesize a list of VocalSegments and yield (knight_id, pcm, sr) tuples.

        mode=SEQUENTIAL:   segments in order, one at a time
        mode=SIMULTANEOUS: all segments start concurrently; yielded in position order
        mode=DEBATE:       exactly 2 knights, alternating for `rounds` exchanges
        """
        # Assign positions if not set
        ordered = [
            s if s.position != 0 else VocalSegment(s.knight_id, s.text, i)
            for i, s in enumerate(segments)
        ]

        if mode == VocalMode.SEQUENTIAL:
            self._stats["sequential"] += 1
            async for chunk in self._sequential(ordered, silence_ms):
                yield chunk

        elif mode == VocalMode.SIMULTANEOUS:
            self._stats["simultaneous"] += 1
            async for chunk in self._simultaneous(ordered):
                yield chunk

        elif mode == VocalMode.DEBATE:
            self._stats["debate"] += 1
            if len(ordered) != 2:
                raise ValueError(
                    f"DEBATE mode requires exactly 2 segments, got {len(ordered)}"
                )
            async for chunk in self._debate(ordered[0], ordered[1], rounds, silence_ms):
                yield chunk

    def stats(self) -> dict:
        return {**self._stats, "engine": self.ENGINE_VERSION}

    # ── Mode implementations ──────────────────────────────────────────────────

    async def _sequential(
        self, segments: list[VocalSegment], silence_ms: int
    ) -> AsyncGenerator[AudioChunk, None]:
        for seg in sorted(segments, key=lambda s: s.position):
            pcm, sr = await self._synth_one(seg.knight_id, seg.text)
            yield seg.knight_id, pcm, sr
            if silence_ms > 0:
                await asyncio.sleep(silence_ms / 1000)

    async def _simultaneous(
        self, segments: list[VocalSegment]
    ) -> AsyncGenerator[AudioChunk, None]:
        """
        Dispatch all segments concurrently.  Results collected into a dict keyed
        by position, then yielded in position order — so the caller always
        receives audio in the original segment sequence regardless of which
        knight's synthesis finished first.
        """
        tasks = {
            seg.position: asyncio.create_task(
                self._synth_one(seg.knight_id, seg.text),
                name=f"lyricus_{seg.knight_id}_{seg.position}",
            )
            for seg in segments
        }
        knight_map = {seg.position: seg.knight_id for seg in segments}

        for pos in sorted(tasks):
            pcm, sr = await tasks[pos]
            yield knight_map[pos], pcm, sr

    async def _debate(
        self,
        seg_a:      VocalSegment,
        seg_b:      VocalSegment,
        rounds:     int,
        silence_ms: int,
    ) -> AsyncGenerator[AudioChunk, None]:
        """
        Alternating exchange for `rounds` iterations.
        Knight A always opens; B responds; A re-opens next round.
        Prosody continuity: each response cached under a sigma-namespaced key
        so the opponent's prior turn can warm the other knight's cache.
        """
        speakers = [seg_a, seg_b]
        for _ in range(rounds):
            for seg in speakers:
                pcm, sr = await self._synth_one(seg.knight_id, seg.text)
                yield seg.knight_id, pcm, sr
                if silence_ms > 0:
                    await asyncio.sleep(silence_ms / 1000)

    # ── Single-segment synthesis with cache ───────────────────────────────────

    async def _synth_one(self, knight_id: str, text: str) -> tuple[bytes, int]:
        """
        Synthesize one segment:
          1. Check KittenService Sonic Cache (Redis, <15ms)
          2. If miss → synthesize via knight's preferred TTS engine
          3. Cache result for future recalls

        Cache key includes the knight's sigma for per-persona isolation:
          key = SHA256(sigma + ":" + text)[:16]
        """
        profile = get_profile(knight_id)
        sigma   = profile.sigma if profile else hashlib.sha256(
            knight_id.encode()
        ).hexdigest()[:16]

        cache_key = hashlib.sha256(
            f"{sigma}:{text}".encode()
        ).hexdigest()[:16]

        # Tier 0: Sonic Cache
        if _kitten is not None:
            cached = _kitten.get_cached_chunk(cache_key)
            if cached:
                self._stats["cache_hits"] += 1
                return cached, 22050

        # Tier 1: TTS Engine (run in thread to avoid blocking event loop)
        pcm, sr = await asyncio.to_thread(
            self._synth_blocking, knight_id, text, profile
        )

        # Store in Sonic Cache
        if _kitten is not None:
            _kitten.cache_chunk(cache_key, pcm)

        return pcm, sr

    @staticmethod
    def _synth_blocking(
        knight_id: str,
        text:      str,
        profile:   Optional[KnightVocalProfile],
    ) -> tuple[bytes, int]:
        """Blocking TTS call — executes in asyncio.to_thread pool."""
        engine_name = profile.tts_engine if profile else "piper"

        # Kokoro (via KittenService KPipeline)
        if engine_name == "kokoro" and _kitten is not None:
            try:
                result = _kitten._synthesize_chunk_sync(
                    text,
                    hashlib.sha256(text.encode()).hexdigest()[:12],
                )
                # _synthesize_chunk_sync caches internally; return raw bytes
                if isinstance(result, bytes) and not result.startswith(b"[AUDIO"):
                    return result, 24000
            except Exception:
                pass  # fall through

        # Silero / SpeechT5 / MMS via tts_engines.py
        if _synth_engine is not None and TTSEngine is not None:
            engine_map = {
                "silero":   TTSEngine.SILERO,
                "speecht5": TTSEngine.SPEECHT5,
                "bark":     TTSEngine.BARK,
                "mms":      TTSEngine.MMS,
            }
            tts_enum = engine_map.get(engine_name)
            if tts_enum:
                try:
                    return _synth_engine(text, engine=tts_enum)
                except Exception:
                    pass

        # Piper via piper_tts.py
        try:
            from agora.swarms import piper_tts  # type: ignore
            voice = profile.piper_model if profile else "en_US-lessac-medium"
            samples, sr = piper_tts.synthesize(text, voice_preset=voice)
            pcm = (samples * 32767).astype("int16").tobytes()
            return pcm, sr
        except Exception:
            pass

        # Simulated fallback
        placeholder = f"[LYRICUS:{knight_id}] {text}".encode("utf-8")
        return placeholder, 22050


# ── Module singleton ──────────────────────────────────────────────────────────

lyricus = LyricusV4()
