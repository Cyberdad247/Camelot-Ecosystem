# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
STT_SERVICE — Zero-Cost Speech-to-Text Tier
============================================
Cascaded pipeline: Audio → [STT] → Text → LLM → Text → [TTS] → Audio

Engine tier (all zero cost, offline-capable):
  Tier 0 — FASTER_WHISPER   (CTranslate2, <200ms, CPU/GPU)
  Tier 1 — WHISPER_HF       (HuggingFace transformers, CPU fallback)
  Tier 2 — WAV2VEC2         (Meta wav2vec 2.0, transformer-based)
  Tier 3 — SIMULATED        (echo-back for testing)

Pre-processing: Silero-VAD (voice activity detection, zero cost)

Knight routing: STT engine selection follows knight_voices.py stt_engine field.
  - "faster_whisper" → Tier 0
  - "wav2vec2"       → Tier 2 (privacy-conscious, no cloud)
  - "silero_only"    → VAD + Silero (SIR_GHOST air-gapped mode)
"""

from __future__ import annotations

import os
import time
from enum import Enum
from typing import Any, Optional


class STTEngine(Enum):
    FASTER_WHISPER = "faster_whisper"
    WHISPER_HF     = "whisper_hf"
    WAV2VEC2       = "wav2vec2"
    SILERO_ONLY    = "silero_only"
    SIMULATED      = "simulated"


_MODEL_SIZES = {
    "tiny":   {"params": "39M",  "latency_ms": 30,  "wer": 0.12},
    "base":   {"params": "74M",  "latency_ms": 60,  "wer": 0.08},
    "small":  {"params": "244M", "latency_ms": 120, "wer": 0.05},
    "medium": {"params": "769M", "latency_ms": 300, "wer": 0.03},
    "large":  {"params": "1.5B", "latency_ms": 800, "wer": 0.02},
}


def _try_load_faster_whisper(model_size: str = "base") -> Optional[Any]:
    try:
        from faster_whisper import WhisperModel  # type: ignore
        device = "cuda" if _cuda_available() else "cpu"
        compute = "float16" if device == "cuda" else "int8"
        return WhisperModel(model_size, device=device, compute_type=compute)
    except Exception:
        return None


def _try_load_whisper_hf(model_size: str = "base") -> Optional[Any]:
    try:
        from transformers import pipeline as hf_pipeline  # type: ignore
        model_id = f"openai/whisper-{model_size}"
        return hf_pipeline("automatic-speech-recognition", model=model_id)
    except Exception:
        return None


def _try_load_wav2vec2() -> Optional[Any]:
    try:
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor  # type: ignore
        model_id = "facebook/wav2vec2-base-960h"
        processor = Wav2Vec2Processor.from_pretrained(model_id)
        model = Wav2Vec2ForCTC.from_pretrained(model_id)
        return {"processor": processor, "model": model}
    except Exception:
        return None


def _try_load_silero_vad() -> Optional[Any]:
    try:
        import torch  # type: ignore
        model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
        )
        return {"model": model, "utils": utils}
    except Exception:
        return None


def _cuda_available() -> bool:
    try:
        import torch  # type: ignore
        return torch.cuda.is_available()
    except Exception:
        return False


class STTService:
    """
    Zero-cost Speech-to-Text service with automatic engine fallback.

    Architecture (Cascaded pipeline — Tier 0–3):
      Audio bytes → VAD filter → Whisper/wav2vec2 → transcript str

    Native Audio (Omni) pipeline bypasses this service entirely and passes
    raw audio tokens directly to the Omni LLM (GPT-4o Realtime / Gemini Live).
    """

    _instance: Optional["STTService"] = None

    def __new__(cls) -> "STTService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        model_size = os.getenv("CAMELOT_WHISPER_SIZE", "base")

        self._vad       = _try_load_silero_vad()
        self._fw        = _try_load_faster_whisper(model_size)
        self._whisper   = None  # lazy load on first miss
        self._wav2vec2  = None  # lazy load on first miss

        if self._fw:
            self.active_engine = STTEngine.FASTER_WHISPER
        else:
            self.active_engine = STTEngine.SIMULATED

        self.model_size = model_size
        self._initialized = True

        print(
            f"[STT] STT_SERVICE ONLINE  engine={self.active_engine.value}"
            f"  vad={'ON' if self._vad else 'OFF'}"
            f"  whisper_size={model_size}"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def transcribe(
        self,
        audio: bytes,
        engine: Optional[STTEngine] = None,
        language: str = "en",
    ) -> dict:
        """
        Transcribe audio bytes to text.

        Returns:
            {"text": str, "engine": str, "latency_ms": float,
             "language": str, "confidence": float}
        """
        t0 = time.monotonic()
        target = engine or self.active_engine

        try:
            if target == STTEngine.FASTER_WHISPER and self._fw:
                text, lang, conf = self._transcribe_fw(audio, language)
            elif target == STTEngine.WAV2VEC2:
                if self._wav2vec2 is None:
                    self._wav2vec2 = _try_load_wav2vec2()
                if self._wav2vec2:
                    text, lang, conf = self._transcribe_wav2vec2(audio)
                else:
                    text, lang, conf = self._transcribe_simulated(audio)
            elif target == STTEngine.WHISPER_HF:
                if self._whisper is None:
                    self._whisper = _try_load_whisper_hf(self.model_size)
                if self._whisper:
                    text, lang, conf = self._transcribe_hf(audio)
                else:
                    text, lang, conf = self._transcribe_simulated(audio)
            else:
                text, lang, conf = self._transcribe_simulated(audio)
        except Exception as e:
            text, lang, conf = f"[STT_ERROR: {e}]", language, 0.0

        return {
            "text":       text,
            "engine":     target.value,
            "latency_ms": round((time.monotonic() - t0) * 1000, 1),
            "language":   lang,
            "confidence": conf,
        }

    def is_speech(self, audio: bytes, sample_rate: int = 16000) -> bool:
        """Silero-VAD gate — returns True if audio contains speech."""
        if self._vad is None:
            return True  # assume speech if VAD unavailable
        try:
            import torch  # type: ignore
            import numpy as np  # type: ignore
            audio_np = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
            audio_t = torch.from_numpy(audio_np)
            prob = self._vad["model"](audio_t, sample_rate).item()
            return prob > 0.5
        except Exception:
            return True

    def engine_info(self) -> dict:
        return {
            "active":       self.active_engine.value,
            "vad_online":   self._vad is not None,
            "fw_online":    self._fw is not None,
            "model_size":   self.model_size,
            "model_params": _MODEL_SIZES.get(self.model_size, {}).get("params", "?"),
            "est_latency":  _MODEL_SIZES.get(self.model_size, {}).get("latency_ms", "?"),
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _transcribe_fw(self, audio: bytes, language: str) -> tuple[str, str, float]:
        import numpy as np  # type: ignore
        audio_np = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
        segments, info = self._fw.transcribe(audio_np, language=language, beam_size=5)
        text = " ".join(s.text for s in segments).strip()
        return text, info.language, getattr(info, "language_probability", 0.9)

    def _transcribe_hf(self, audio: bytes) -> tuple[str, str, float]:
        import numpy as np  # type: ignore
        audio_np = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
        result = self._whisper({"raw": audio_np, "sampling_rate": 16000})
        return result["text"].strip(), "en", 0.85

    def _transcribe_wav2vec2(self, audio: bytes) -> tuple[str, str, float]:
        import torch, numpy as np  # type: ignore
        audio_np = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
        proc = self._wav2vec2["processor"]
        model = self._wav2vec2["model"]
        inputs = proc(audio_np, sampling_rate=16000, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
        ids = torch.argmax(logits, dim=-1)
        text = proc.batch_decode(ids)[0].lower()
        return text, "en", 0.80

    @staticmethod
    def _transcribe_simulated(audio: bytes) -> tuple[str, str, float]:
        return f"[SIMULATED_TRANSCRIPT len={len(audio)}B]", "en", 0.0


# ── Module Singleton ──────────────────────────────────────────────────────────

try:
    stt_service = STTService()
except Exception as _e:
    print(f"[STT] Deferred init — STTService will initialize on first call: {_e}")
    stt_service = None  # type: ignore[assignment]
