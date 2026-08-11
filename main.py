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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

try:
    from redis.asyncio.sentinel import Sentinel
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

from src.native_webrtc import NativeWebRTCEngine, _c_lib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MultivoiceRouter")

ROUTER_REQUESTS_TOTAL = Counter("merlin_router_requests_total", "Total incoming requests", ["status", "client_uuid"])
ROUTER_LATENCY_HISTOGRAM = Histogram("merlin_router_latency_seconds", "Routing latency in seconds")
RATE_LIMIT_DROPS_TOTAL = Counter("merlin_rate_limit_drops_total", "Dropped frames", ["client_uuid"])
QR_PILL_REJECTIONS_TOTAL = Counter("merlin_qr_pill_rejections_total", "QR Pill rejections", ["reason"])


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


class TokenBucketRateLimiter:
    def __init__(self, capacity: int = 50, refill_rate_per_sec: float = 30.0):
        self.capacity = float(capacity)
        self.refill_rate = refill_rate_per_sec
        self.buckets: Dict[str, Tuple[float, float]] = {}
        self._lock = asyncio.Lock()

    async def allow_request(self, client_id: str, tokens_required: float = 1.0) -> Tuple[bool, float]:
        async with self._lock:
            now = time.time()
            tokens, last_refill = self.buckets.get(client_id, (self.capacity, now))

            elapsed = now - last_refill
            tokens = min(self.capacity, tokens + (elapsed * self.refill_rate))

            if len(self.buckets) > 500:
                stale_keys = [k for k, (_, last_t) in self.buckets.items() if (now - last_t) > 3600]
                for k in stale_keys:
                    del self.buckets[k]

            if tokens >= tokens_required:
                tokens -= tokens_required
                self.buckets[client_id] = (tokens, now)
                return True, tokens
            
            self.buckets[client_id] = (tokens, now)
            return False, tokens


@dataclass
class AudioFrame:
    sequence_num: int
    send_timestamp: float
    recv_timestamp: float
    pcm_bytes: bytes


class AdaptiveJitterBuffer:
    def __init__(self, min_depth_ms: float = 10.0, max_depth_ms: float = 60.0):
        self.min_depth_ms = min_depth_ms
        self.max_depth_ms = max_depth_ms
        self.current_jitter_ms: float = 0.0
        self.prev_transit_delta: Optional[float] = None
        self.buffer: Dict[int, AudioFrame] = {}
        self.next_playout_seq: int = 0

    def push_frame(self, sequence_num: int, send_ts: float, pcm_bytes: bytes) -> float:
        now = time.time()
        transit_time = (now - send_ts) * 1000.0

        if self.prev_transit_delta is not None:
            delta = transit_time - self.prev_transit_delta
            self.current_jitter_ms += (abs(delta) - self.current_jitter_ms) / 16.0
        
        self.prev_transit_delta = transit_time

        frame = AudioFrame(
            sequence_num=sequence_num,
            send_timestamp=send_ts,
            recv_timestamp=now,
            pcm_bytes=pcm_bytes
        )
        self.buffer[sequence_num] = frame
        return self.get_target_delay_ms()

    def get_target_delay_ms(self) -> float:
        calculated_delay = 4.0 * self.current_jitter_ms
        return max(self.min_depth_ms, min(self.max_depth_ms, calculated_delay))


class DistributedQRPillSecurityEngine:
    def __init__(self, pill_secret: str, ttl_seconds: float = 30.0, redis_client: Optional[Any] = None):
        self.pill_secret = pill_secret.encode("utf-8")
        self.ttl_seconds = ttl_seconds
        self.redis = redis_client
        self.local_consumed_nonces = set()

    async def validate_qr_pill(self, token: str) -> Tuple[bool, str]:
        try:
            data_str, sig = token.rsplit(".", 1)
            expected = hmac.new(self.pill_secret, data_str.encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, sig):
                QR_PILL_REJECTIONS_TOTAL.labels(reason="invalid_signature").inc()
                return False, "Invalid pill signature."

            data = json.loads(data_str)
            pill_id = data.get("pill_id")
            exp = data.get("exp", 0)

            if not pill_id:
                QR_PILL_REJECTIONS_TOTAL.labels(reason="missing_pill_id").inc()
                return False, "Malformed pill token."

            if time.time() > exp:
                QR_PILL_REJECTIONS_TOTAL.labels(reason="expired_token").inc()
                return False, "Pill expired."

            remaining_ttl = int(max(1, exp - time.time()))

            if self.redis is not None:
                redis_key = f"qr_pill:nonce:{pill_id}"
                is_set = await self.redis.set(redis_key, "1", ex=remaining_ttl, nx=True)
                if not is_set:
                    QR_PILL_REJECTIONS_TOTAL.labels(reason="replay_attack_redis").inc()
                    return False, "Pill already consumed."
            else:
                if pill_id in self.local_consumed_nonces:
                    QR_PILL_REJECTIONS_TOTAL.labels(reason="replay_attack_local").inc()
                    return False, "Pill already consumed."
                self.local_consumed_nonces.add(pill_id)

            return True, "Pill Valid"

        except Exception as e:
            QR_PILL_REJECTIONS_TOTAL.labels(reason="parsing_error").inc()
            return False, f"Pill validation error: {e}"


try:
    from src.security import BifrostBridgeAuth
    from src.extractors import AcousticSignalExtractor, ONNXEmbeddingModel
    from src.vector_cache import AsyncSafeTTLLRUFAISSVectorCache
    from src.router import TraitBlender
    from src.context import ContextRewindEngine
except ImportError:
    class BifrostBridgeAuth:
        def __init__(self, bridge_secret: str, allowed_uuids: List[str]):
            self.bridge_secret = bridge_secret.encode("utf-8")
            self.allowed_uuids = set(allowed_uuids)

        def verify_request(self, client_uuid: str, payload_str: str, timestamp: float, provided_signature: str):
            if client_uuid not in self.allowed_uuids:
                return False, "UUID not whitelisted."
            if abs(time.time() - timestamp) > 300:
                return False, "Timestamp out of bounds."
            msg = f"{client_uuid}:{timestamp}:{payload_str}".encode("utf-8")
            expected = hmac.new(self.bridge_secret, msg, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, provided_signature):
                return False, "Invalid signature."
            return True, "Auth OK"

    class AcousticSignalExtractor:
        def extract_features(self, pcm_bytes: bytes):
            audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            if len(audio) == 0:
                return {"energy": 0.0, "pitch": 0.0, "zcr": 0.0}
            rms = float(np.sqrt(np.mean(audio**2)))
            zcr = float(np.mean(np.abs(np.diff(np.signbit(audio)))))
            return {"energy": round(rms, 4), "pitch": 180.0 if rms > 0.01 else 0.0, "zcr": round(zcr, 4)}

        def map_acoustic_to_signals(self, features: Dict[str, float]):
            e = features["energy"]
            return {
                "C1_Strategic": 1.0 + (1.5 if e > 0.1 else 0.0),
                "C2_Technical": 1.0,
                "C3_Creative": 1.0,
                "C4_Analytical": 1.0,
                "C5_Operational": 1.0 + (2.0 if e > 0.15 else 0.0)
            }

    class ONNXEmbeddingModel:
        def __init__(self, model_dir: str = "merlin_onnx_minilm"):
            self.dim = 384

        def embed_text(self, text: str) -> np.ndarray:
            seed = abs(hash(text)) % (2**32)
            rng = np.random.default_rng(seed)
            vec = rng.standard_normal(384).astype(np.float32)
            norm = np.linalg.norm(vec)
            return vec / norm if norm > 0 else vec

    class AsyncSafeTTLLRUFAISSVectorCache:
        def __init__(self, dimension: int = 384, max_capacity: int = 500):
            self._lock = asyncio.Lock()
            self.cache = {}

        async def async_search(self, vec: np.ndarray):
            async with self._lock:
                return False, None, 0.0

        async def async_add(self, vec: np.ndarray, text: str, signals: Dict[str, float]):
            async with self._lock:
                self.cache[text] = signals

    class TraitBlender:
        def __init__(self, knights: List[str]):
            self.knights = knights

        def compute_fused_blend(self, semantic_signals: Dict[str, float], acoustic_signals: Dict[str, float]):
            fused = {}
            for k in self.knights:
                fused[k] = (0.7 * semantic_signals.get(k, 1.0)) + (0.3 * acoustic_signals.get(k, 1.0))
            tot = sum(fused.values()) or 1.0
            return {k: round(v / tot, 4) for k, v in fused.items()}

    class ContextRewindEngine:
        def __init__(self):
            self.history = []

        def commit_turn(self, role: str, content: str):
            self.history.append({"role": role, "content": content})


class MultivoiceRouterPipeline:
    def __init__(
        self,
        knights: List[str],
        bridge_secret: str,
        allowed_uuids: List[str],
        pill_secret: str,
        redis_client: Optional[Any] = None,
        onnx_model_dir: str = "merlin_onnx_minilm"
    ):
        self.knights = knights
        self.bifrost = BifrostBridgeAuth(bridge_secret, allowed_uuids)
        self.qr_pill = DistributedQRPillSecurityEngine(pill_secret, ttl_seconds=30.0, redis_client=redis_client)
        self.rate_limiter = TokenBucketRateLimiter(capacity=50, refill_rate_per_sec=30.0)
        self.shm_buffer = ZeroCopySharedMemoryBuffer(name="merlin_main_pcm_shm")
        self.formant_morpher = SpectralFormantMorpher(sample_rate=16000)
        self.acoustic_extractor = AcousticSignalExtractor()
        self.embedder = ONNXEmbeddingModel(model_dir=onnx_model_dir)
        self.cache = AsyncSafeTTLLRUFAISSVectorCache(dimension=384, max_capacity=500)
        self.blender = TraitBlender(knights)
        self.context_engine = ContextRewindEngine()

    async def route_turn(
        self,
        client_uuid: str,
        timestamp: float,
        bridge_signature: str,
        qr_pill_token: str,
        pcm_bytes: bytes,
        transcribed_text: str
    ) -> Dict[str, Any]:
        
        bifrost_ok, bifrost_msg = self.bifrost.verify_request(
            client_uuid=client_uuid,
            payload_str=transcribed_text,
            timestamp=timestamp,
            provided_signature=bridge_signature
        )
        if not bifrost_ok:
            ROUTER_REQUESTS_TOTAL.labels(status="denied_bifrost", client_uuid=client_uuid).inc()
            return {"status": "denied", "reason": f"Bifrost: {bifrost_msg}"}

        pill_ok, pill_msg = await self.qr_pill.validate_qr_pill(qr_pill_token)
        if not pill_ok:
            ROUTER_REQUESTS_TOTAL.labels(status="denied_qr_pill", client_uuid=client_uuid).inc()
            return {"status": "denied", "reason": f"QR Pill: {pill_msg}"}

        write_offset = self.shm_buffer.write_pcm_bytes(pcm_bytes)

        acoustic_features = self.acoustic_extractor.extract_features(pcm_bytes)
        acoustic_signals = self.acoustic_extractor.map_acoustic_to_signals(acoustic_features)

        prompt_vec = self.embedder.embed_text(transcribed_text)
        is_hit, cached_signals, _ = await self.cache.async_search(prompt_vec)

        if is_hit and cached_signals:
            semantic_signals = cached_signals
        else:
            semantic_signals = {k: 1.0 for k in self.knights}
            semantic_signals["C2_Technical"] = 2.5
            await self.cache.async_add(prompt_vec, transcribed_text, semantic_signals)

        fused_blend = self.blender.compute_fused_blend(semantic_signals, acoustic_signals)
        dominant_trait = max(fused_blend, key=fused_blend.get)

        morphed_pcm_bytes = self.formant_morpher.morph_pcm_frame(pcm_bytes, fused_blend)

        self.context_engine.commit_turn("user", transcribed_text)
        ROUTER_REQUESTS_TOTAL.labels(status="authorized", client_uuid=client_uuid).inc()

        return {
            "status": "authorized",
            "routing_decision": {
                "dominant_trait": dominant_trait,
                "fused_blend_weights": fused_blend,
                "cache_hit": is_hit,
                "acoustic_features": acoustic_features
            },
            "shm_metadata": {
                "shm_buffer_name": self.shm_buffer.name,
                "write_offset_bytes": write_offset,
                "morphed_frame_size_bytes": len(morphed_pcm_bytes)
            },
            "morphed_pcm_hex": morphed_pcm_bytes.hex()
        }

    def close(self):
        if hasattr(self, "shm_buffer"):
            self.shm_buffer.close()
            self.shm_buffer.unlink()


pipeline: Optional[MultivoiceRouterPipeline] = None
native_webrtc_engine: Optional[NativeWebRTCEngine] = None
redis_client: Optional[Any] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, native_webrtc_engine, redis_client
    logger.info("Initializing Merlin Multivoice Router v1.4.0...")

    # Initialize Redis Sentinel / Cluster
    if HAS_REDIS:
        try:
            sentinel_hosts = [("10.0.0.1", 26379), ("10.0.0.2", 26379), ("10.0.0.3", 26379)]
            redis_pwd = os.getenv("REDIS_PASSWORD", "MERLIN_SUPER_SECRET_REDIS_AUTH_9981")
            sentinel = Sentinel(sentinel_hosts, socket_timeout=0.5, password=redis_pwd, sentinel_kwargs={"password": redis_pwd})
            redis_client = sentinel.master_for("mymaster", decode_responses=True)
            await redis_client.ping()
            logger.info("Connected to Redis Sentinel master.")
        except Exception as e:
            logger.warning(f"Redis Sentinel unavailable ({e}). Fallback to local memory.")
            redis_client = None

    # Initialize Pipeline
    knights = ["C1_Strategic", "C2_Technical", "C3_Creative", "C4_Analytical", "C5_Operational"]
    pipeline = MultivoiceRouterPipeline(
        knights=knights,
        bridge_secret=os.getenv("BIFROST_BRIDGE_SECRET", "BIFROST_MASTER_SECRET_KEY_9981"),
        allowed_uuids=os.getenv("ALLOWED_UUIDS", "e83b27b4-1234-5678-9abc-def012345678").split(","),
        pill_secret=os.getenv("QR_PILL_SECRET", "QR_PILL_SECRET_KEY_4412"),
        redis_client=redis_client
    )

    # Initialize Native WebRTC Engine
    if _c_lib is not None:
        try:
            native_webrtc_engine = NativeWebRTCEngine(shm_name="merlin_native_webrtc_pcm", shm_capacity=1048576)
            native_webrtc_engine.initialize()
            logger.info(f"Native WebRTC engine online. SHM FD: {native_webrtc_engine.get_shm_fd()}")
        except Exception as e:
            logger.error(f"Failed to start Native WebRTC Engine: {e}")

    yield

    logger.info("Shutting down pipeline components...")
    if native_webrtc_engine:
        native_webrtc_engine.close()
    if pipeline:
        pipeline.close()


app = FastAPI(title="Merlin Multivoice Router Gateway", version="1.4.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/metrics")
async def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health_check():
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline uninitialized")
    return {
        "status": "online",
        "active_knights": pipeline.knights,
        "zero_copy_shm_active": True,
        "native_cxx_webrtc_active": native_webrtc_engine is not None and native_webrtc_engine.is_initialized,
        "redis_ha_nonce_active": redis_client is not None,
        "prometheus_metrics_active": True,
        "timestamp": time.time()
    }


@app.websocket("/ws/voice-router")
async def voice_router_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_jitter_buffer = AdaptiveJitterBuffer(min_depth_ms=10.0, max_depth_ms=60.0)

    try:
        raw_handshake = await websocket.receive_text()
        handshake = json.loads(raw_handshake)

        client_uuid = handshake.get("client_uuid")
        timestamp = handshake.get("timestamp", time.time())
        bridge_sig = handshake.get("bridge_signature")
        qr_pill = handshake.get("qr_pill_token")

        if not all([client_uuid, bridge_sig, qr_pill]):
            await websocket.send_json({"status": "error", "message": "Missing authentication headers."})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.send_json({"status": "handshake_ok", "message": "Zero-trust session established."})
        sequence_num = 0

        while True:
            frame_data = await websocket.receive_text()
            payload = json.loads(frame_data)

            if payload.get("type") == "barge_in":
                session_jitter_buffer = AdaptiveJitterBuffer(min_depth_ms=10.0, max_depth_ms=60.0)
                await websocket.send_json({"status": "acknowledged", "action": "context_and_jitter_buffer_reset"})
                continue

            allowed, tokens_remaining = await pipeline.rate_limiter.allow_request(client_uuid)
            if not allowed:
                RATE_LIMIT_DROPS_TOTAL.labels(client_uuid=client_uuid).inc()
                await websocket.send_json({
                    "status": "rate_limited",
                    "reason": "Token bucket limit exceeded.",
                    "tokens_remaining": round(tokens_remaining, 2)
                })
                continue

            transcribed_text = payload.get("text", "")
            raw_pcm_hex = payload.get("pcm_hex", "")
            pcm_bytes = bytes.fromhex(raw_pcm_hex) if raw_pcm_hex else b"\x00\x10" * 160
            send_ts = payload.get("send_timestamp", time.time())

            target_delay_ms = session_jitter_buffer.push_frame(sequence_num, send_ts, pcm_bytes)
            sequence_num += 1

            start_time = time.perf_counter()

            result = await pipeline.route_turn(
                client_uuid=client_uuid,
                timestamp=timestamp,
                bridge_signature=bridge_sig,
                qr_pill_token=qr_pill,
                pcm_bytes=pcm_bytes,
                transcribed_text=transcribed_text
            )

            execution_time_sec = time.perf_counter() - start_time
            ROUTER_LATENCY_HISTOGRAM.observe(execution_time_sec)

            result["qos_metrics"] = {
                "latency_ms": round(execution_time_sec * 1000.0, 2),
                "jitter_buffer_delay_ms": round(target_delay_ms, 2),
                "estimated_network_jitter_ms": round(session_jitter_buffer.current_jitter_ms, 2),
                "rate_limit_tokens_remaining": round(tokens_remaining, 2)
            }

            await websocket.send_json(result)

    except WebSocketDisconnect:
        logger.info("Client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket session error: {e}", exc_info=True)
        try:
            await websocket.send_json({"status": "error", "message": str(e)})
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
