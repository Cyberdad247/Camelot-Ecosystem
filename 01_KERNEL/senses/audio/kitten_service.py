# -*- coding: utf-8 -*-
"""
[KITTEN] KITTEN_SERVICE (L2 Kinetic)
=====================================
High-velocity phonetic synthesis node.
Refactored for Token-to-Audio chunk streaming.
Utilizes Redis Sonic Cache for <15ms response hits.
HTTP streaming endpoint at :8300 for edge-router consumers.
"""

import asyncio
import socket
import time
import redis
import hashlib
from typing import Any, AsyncGenerator, Dict, Optional, Generator

# Optional Kokoro TTS — graceful fallback to placeholder if unavailable
try:
    from kokoro import KPipeline  # type: ignore
    _KOKORO_PIPELINE: Optional[Any] = KPipeline(lang_code="a")
except Exception:
    _KOKORO_PIPELINE = None

class KittenService:
    """Standalone high-velocity phonetic synthesis node."""
    
    def __init__(self):
        self.engine_id = "KITTEN_VOX_V1"
        self.cache_prefix = "vox:engine:"
        redis_host, redis_port = 'localhost', 6379
        redis_status = self._probe_port(redis_host, redis_port)
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=0,
            socket_connect_timeout=0.5, socket_timeout=0.5,
        ) if redis_status else None
        print(f"[KITTEN] KITTEN_SERVICE ONLINE. (Redis Link: {redis_status})")

    @staticmethod
    def _probe_port(host: str, port: int, timeout: float = 0.3) -> bool:
        """Fast TCP probe — avoids blocking redis-py retries when Redis is offline."""
        try:
            s = socket.create_connection((host, port), timeout=timeout)
            s.close()
            return True
        except OSError:
            return False

    def get_cached_chunk(self, chunk_hash: str) -> Optional[bytes]:
        """Sub-10ms retrieval of audio chunks from Redis."""
        if self.redis_client is None:
            return None
        try:
            cached = self.redis_client.get(f"{self.cache_prefix}chunk:{chunk_hash}")
            return cached if cached else None
        except redis.RedisError:
            return None

    def cache_chunk(self, chunk_hash: str, audio_data: bytes, ttl: int = 1800):
        """Store audio fragments (chunks) with 30min TTL (omnivox.yaml spec)."""
        if self.redis_client is None:
            return
        try:
            self.redis_client.setex(f"{self.cache_prefix}chunk:{chunk_hash}", ttl, audio_data)
        except redis.RedisError as e:
            print(f"[KITTEN] Redis Cache fallback: {e}")

    def synthesize_fast(self, text: str, persona: str = "tasha") -> Dict[str, Any]:
        """Cache-only synthesis probe — returns CACHE_HIT or CACHE_MISS dict.

        Called by VoxService as Tier-0 (KITTEN_CACHE) before any GPU/CPU synthesis.
        """
        t0 = time.monotonic()
        chunk_hash = hashlib.sha256(text.encode()).hexdigest()[:12]
        cached = self.get_cached_chunk(chunk_hash)
        latency_ms = (time.monotonic() - t0) * 1000
        if cached:
            return {"status": "CACHE_HIT", "latency_ms": latency_ms, "audio_data": cached}
        return {"status": "CACHE_MISS", "latency_ms": latency_ms}

    def synthesize_stream(self, token_stream: Generator[str, None, None], mode: str = "efficiency") -> Generator[bytes, None, None]:
        """Token-to-Audio streaming synthesis."""
        buffer = ""
        for token in token_stream:
            buffer += token
            # Yield audio chunk when we hit punctuation or a natural break
            if any(punc in token for punc in ['.', '!', '?', '\n', ',']):
                chunk_text = buffer.strip()
                if not chunk_text: continue
                
                chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()[:12]
                cached = self.get_cached_chunk(chunk_hash)
                
                if cached:
                    yield cached
                else:
                    # Placeholder for real TTS chunk generation
                    synthetic_audio = f"[AUDIO CHUNK FOR: {chunk_text}]".encode('utf-8')
                    self.cache_chunk(chunk_hash, synthetic_audio)
                    yield synthetic_audio
                
                buffer = ""

    async def synthesize_chunked_async(
        self,
        token_stream: AsyncGenerator[str, None],
        mode: str = "efficiency",
    ) -> AsyncGenerator[bytes, None]:
        """Async Token-to-Audio streaming synthesis with Kokoro TTS support.

        Buffers tokens until a sentence boundary, then yields audio bytes.
        Uses Redis cache; falls back to Kokoro pipeline if cache misses,
        or placeholder bytes if Kokoro is unavailable.
        """
        buffer = ""
        async for token in token_stream:
            buffer += token
            if any(punc in token for punc in [".", "!", "?", "\n", ","]):
                chunk_text = buffer.strip()
                buffer = ""
                if not chunk_text:
                    continue

                chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()[:12]
                cached = self.get_cached_chunk(chunk_hash)
                if cached:
                    yield cached
                    continue

                audio_data = await asyncio.to_thread(
                    self._synthesize_chunk_sync, chunk_text, chunk_hash
                )
                yield audio_data

        # Flush remainder
        if buffer.strip():
            chunk_text = buffer.strip()
            chunk_hash = hashlib.sha256(chunk_text.encode()).hexdigest()[:12]
            cached = self.get_cached_chunk(chunk_hash)
            if cached:
                yield cached
            else:
                yield await asyncio.to_thread(self._synthesize_chunk_sync, chunk_text, chunk_hash)

    def _synthesize_chunk_sync(self, chunk_text: str, chunk_hash: str) -> bytes:
        """Blocking TTS call — run via asyncio.to_thread."""
        if _KOKORO_PIPELINE is not None:
            try:
                # KPipeline returns (gs, ps, audio_np) tuples; concat all segments
                import numpy as np  # type: ignore
                segments = list(_KOKORO_PIPELINE(chunk_text, voice="af_heart"))
                if segments:
                    audio_np = np.concatenate([seg[2] for seg in segments])
                    # Convert float32 → int16 PCM bytes
                    audio_data = (audio_np * 32767).astype("int16").tobytes()
                    self.cache_chunk(chunk_hash, audio_data)
                    return audio_data
            except Exception as e:
                print(f"[KITTEN] Kokoro synthesis failed ({e}) — using placeholder")

        # Fallback placeholder
        audio_data = f"[AUDIO CHUNK: {chunk_text}]".encode("utf-8")
        self.cache_chunk(chunk_hash, audio_data)
        return audio_data

    async def run_streaming_server(self, host: str = "0.0.0.0", port: int = 8300) -> None:
        """HTTP streaming server — POST /synthesize with JSON body {text: str}."""
        from aiohttp import web  # type: ignore

        async def handle_synthesize(request: web.Request) -> web.StreamResponse:
            body = await request.json()
            text: str = body.get("text", "")
            if not text:
                return web.Response(status=400, text="missing text")

            response = web.StreamResponse(
                status=200,
                headers={"Content-Type": "application/octet-stream", "X-Engine": self.engine_id},
            )
            await response.prepare(request)

            async def _token_stream() -> AsyncGenerator[str, None]:
                # Treat whole text as one token stream for now
                for word in text.split():
                    yield word + " "
                    await asyncio.sleep(0)

            async for chunk in self.synthesize_chunked_async(_token_stream()):
                await response.write(chunk)

            await response.write_eof()
            return response

        app = web.Application()
        app.router.add_post("/synthesize", handle_synthesize)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        print(f"[KITTEN] HTTP streaming server ::{port} ONLINE")
        await asyncio.Event().wait()  # block forever


kitten_service = KittenService()