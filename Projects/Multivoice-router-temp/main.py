import asyncio
import hashlib
import hmac
import json
import logging
import os
import struct
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from multiprocessing import shared_memory
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import make_asgi_app, Counter, Histogram
import redis.asyncio as aioredis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Merlin_Multivoice")

REQUEST_COUNT = Counter('router_requests_total', 'Total requests', ['endpoint'])
REQUEST_LATENCY = Histogram('router_request_latency_seconds', 'Request latency', ['endpoint'])
RATE_LIMIT_DROPS = Counter('router_rate_limit_drops_total', 'Rate limit drops')

redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)

# ==============================================================================
# Core Audio & Memory Structures
# ==============================================================================

@dataclass
class AudioFrame:
    sequence_num: int
    send_timestamp: float
    recv_timestamp: float
    pcm_bytes: bytes

class ZeroCopySharedMemoryBuffer:
    def __init__(self, name: str = "merlin_pcm_shm", size_bytes: int = 1048576):
        self.name = name
        self.size_bytes = size_bytes
        try:
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.size_bytes)
            struct.pack_into("<I", self.shm.buf, 0, 0)
        except FileExistsError:
            self.shm = shared_memory.SharedMemory(name=self.name)
        self.header_size = 8
        self.data_size = self.size_bytes - self.header_size

    def write_pcm_bytes(self, pcm_bytes: bytes) -> int:
        n = len(pcm_bytes)
        if n + self.header_size > self.size_bytes:
            raise ValueError("Frame exceeds shared memory allocation limit.")
        write_offset = struct.unpack_from("<I", self.shm.buf, 0)[0]
        target_index = self.header_size + write_offset
        self.shm.buf[target_index : target_index + n] = pcm_bytes
        new_offset = (write_offset + n) % self.data_size
        struct.pack_into("<I", self.shm.buf, 0, new_offset)
        return write_offset

    def read_pcm_bytes(self, offset: int, length: int) -> bytes:
        target_index = self.header_size + offset
        return bytes(self.shm.buf[target_index : target_index + length])

    def close(self):
        try:
            self.shm.close()
        except Exception:
            pass

    def unlink(self):
        try:
            self.shm.unlink()
        except Exception:
            pass

class SpectralFormantMorpher:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.knight_formant_deltas = {
            "C1_Strategic": -0.05,
            "C2_Technical": 0.02,
            "C3_Creative": 0.08,
            "C4_Analytical": 0.00,
            "C5_Operational": -0.02
        }

    def morph_pcm_frame(self, pcm_bytes: bytes, blend_weights: Dict[str, float]) -> bytes:
        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        if len(audio) == 0:
            return pcm_bytes
        formant_shift = sum(
            weight * self.knight_formant_deltas.get(knight, 0.0)
            for knight, weight in blend_weights.items()
        )
        alpha_morph = 1.0 + formant_shift
        spectrum = np.fft.rfft(audio)
        warped_indices = np.clip(
            np.round(np.arange(len(spectrum)) * alpha_morph).astype(int),
            0,
            len(spectrum) - 1
        )
        warped_spectrum = spectrum[warped_indices]
        morphed_audio = np.fft.irfft(warped_spectrum, n=len(audio))
        morphed_audio = np.clip(morphed_audio, -32768, 32767).astype(np.int16)
        return morphed_audio.tobytes()

# ==============================================================================
# QoS: Rate Limiting & Jitter Buffer
# ==============================================================================

class TokenBucketRateLimiter:
    def __init__(self, capacity: int = 50, refill_rate_per_sec: float = 30.0, ttl_seconds: float = 3600.0):
        self.capacity = float(capacity)
        self.refill_rate = refill_rate_per_sec
        self.ttl_seconds = ttl_seconds
        self.buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = asyncio.Lock()

    async def allow_request(self, client_id: str, tokens_required: float = 1.0) -> Tuple[bool, float]:
        async with self._lock:
            now = time.time()
            
            # TTL Memory Eviction
            expired_keys = [k for k, v in self.buckets.items() if now - v[1] > self.ttl_seconds]
            for k in expired_keys:
                del self.buckets[k]

            tokens, last_refill = self.buckets.get(client_id, (self.capacity, now))
            elapsed = now - last_refill
            tokens = min(self.capacity, tokens + (elapsed * self.refill_rate))
            if tokens >= tokens_required:
                tokens -= tokens_required
                self.buckets[client_id] = (tokens, now)
                return True, tokens
            self.buckets[client_id] = (tokens, now)
            RATE_LIMIT_DROPS.inc()
            return False, tokens

class AdaptiveJitterBuffer:
    def __init__(self, min_depth_ms: float = 10.0, max_depth_ms: float = 60.0):
        self.min_depth_ms = min_depth_ms / 1000.0
        self.max_depth_ms = max_depth_ms / 1000.0
        self.current_jitter = self.min_depth_ms

    def adjust(self, latency_ms: float) -> float:
        latency = latency_ms / 1000.0
        self.current_jitter = min(self.max_depth_ms, max(self.min_depth_ms, latency * 1.2))
        return self.current_jitter

# ==============================================================================
# Setup Application State
# ==============================================================================

limiter = TokenBucketRateLimiter(capacity=100, refill_rate_per_sec=10.0)
jitter_buffer = AdaptiveJitterBuffer()
audio_buffer = ZeroCopySharedMemoryBuffer()
morpher = SpectralFormantMorpher()

SHARED_SECRET = b"BIFROST_HMAC_SECRET_KEY_2026"
used_nonces = set()

def verify_hmac(payload: bytes, signature: str) -> bool:
    expected = hmac.new(SHARED_SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

async def verify_qr_nonce(nonce: str) -> bool:
    try:
        is_new = await redis_client.set(f"qr_nonce:{nonce}", "1", nx=True, ex=3600)
        return bool(is_new)
    except Exception as e:
        logger.error(f"Redis error: {e}")
        if nonce in used_nonces:
            return False
        used_nonces.add(nonce)
        return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Merlin Multivoice Router Phase 1-7 Production Engine...")
    yield
    logger.info("Tearing down resources...")
    audio_buffer.close()
    audio_buffer.unlink()

app = FastAPI(title="Merlin Multivoice Router v2.0 (Phase 7 Production)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/metrics", make_asgi_app())

# ==============================================================================
# API Endpoints
# ==============================================================================

class IngressPayload(BaseModel):
    text: str
    nonce: str
    timestamp: float

@app.post("/api/v1/route")
async def route_intent(payload: IngressPayload, request: Request, signature: str = Header(...)):
    REQUEST_COUNT.labels(endpoint='/api/v1/route').inc()
    with REQUEST_LATENCY.labels(endpoint='/api/v1/route').time():
        allowed, _ = await limiter.allow_request("global_router")
        if not allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        body = await request.body()
        if not verify_hmac(body, signature):
            raise HTTPException(status_code=401, detail="Signature invalid")

        if not await verify_qr_nonce(payload.nonce):
            raise HTTPException(status_code=403, detail="Nonce invalid or exhausted")

        return {"status": "ROUTED", "intent": "GENERIC_EXECUTE", "latency_ms": (time.time() - payload.timestamp) * 1000}

class InferPayload(BaseModel):
    intent: str
    state_dim: int

@app.post("/api/infer")
async def infer_intent(payload: InferPayload):
    t0 = time.perf_counter()
    ast_data = {
        "tag": "OxiBonsai_v2_Ternary_AST",
        "intent": payload.intent,
        "nodes": [{"id": 1, "action": "STDP_ROUTE"}]
    }
    time.sleep(0.01) # Simulated jitter
    return {
        "error": False,
        "ast_json": json.dumps(ast_data),
        "latency_ms": (time.perf_counter() - t0) * 1000.0
    }

@app.websocket("/api/v1/stream")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to audio stream.")
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    try:
        while True:
            data = await websocket.receive_bytes()
            
            allowed, _ = await limiter.allow_request(client_ip)
            if not allowed:
                await websocket.send_json({"error": "Rate limit exceeded for audio frames"})
                continue
            
            # Morph the audio based on dynamic knight weights
            morphed_data = morpher.morph_pcm_frame(data, {"C1_Strategic": 0.5, "C3_Creative": 0.5})
            
            # Write to zero-copy shared memory
            offset = audio_buffer.write_pcm_bytes(morphed_data)
            
            await websocket.send_json({
                "status": "processed", 
                "shm_offset": offset, 
                "bytes_written": len(morphed_data)
            })
            
    except WebSocketDisconnect:
        logger.info("Client disconnected from audio stream.")
    except Exception as e:
        logger.error(f"Stream error: {e}")
        try:
            await websocket.close()
        except:
            pass

@app.get("/health")
async def health_check():
    return {"status": "OK", "uptime": time.monotonic(), "phase": 7}
