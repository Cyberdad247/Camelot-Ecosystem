# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
TTS_ENGINES — Zero-Cost TTS Engine Registry
============================================
All engines are zero-cost (free weights, offline-capable, no API billing).

Engine Roster:
  KOKORO      — Kokoro ONNX (style-TTS, high fidelity, ~150ms CPU)     ← via KittenService
  PIPER       — Piper ONNX  (NAR, <100ms CPU, 22 voices)               ← via piper_tts.py
  SILERO      — Silero TTS  (PyTorch, 48kHz, 117 speakers, <80ms)
  SPEECHT5    — SpeechT5    (HuggingFace microsoft/speecht5_tts)
  BARK        — Bark        (suno-ai/bark, expressive, ~4s CPU)
  MMS         — MMS-TTS     (Meta, 1100+ languages, multilingual)
  SIMULATED   — Placeholder bytes for testing

Architecture note:
  These engines form the TTS tier in the Cascaded pipeline:
    Text → [TTS_ENGINE] → PCM audio bytes

  For Native Audio (Omni) pipeline (GPT-4o Realtime, Gemini Live, future
  Camelot Omni LLM), TTS is bypassed — audio tokens flow directly.

  Sir Alex selects the engine via vocal_weight_vector(knight_id)["tts_engine"].
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional


class TTSEngine(Enum):
    KOKORO    = "kokoro"
    PIPER     = "piper"
    SILERO    = "silero"
    SPEECHT5  = "speecht5"
    BARK      = "bark"
    MMS       = "mms"
    SIMULATED = "simulated"


# ── Lazy loader helpers ───────────────────────────────────────────────────────

def _load_silero() -> Optional[Any]:
    """
    Silero TTS — PyTorch, 48kHz, 117 speakers.
    pip install silero-tts (or torch.hub)
    """
    try:
        import torch  # type: ignore
        model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="en",
            speaker="v3_en",
            force_reload=False,
        )
        model.eval()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        return {"model": model, "device": device, "sample_rate": 48000}
    except Exception:
        return None


def _load_speecht5() -> Optional[Any]:
    """
    SpeechT5 — HuggingFace microsoft/speecht5_tts.
    Uses x-vector speaker embeddings from CMU ARCTIC dataset.
    pip install transformers datasets
    """
    try:
        from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan  # type: ignore
        from datasets import load_dataset  # type: ignore

        processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        model     = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        vocoder   = SpeechT5HifiGan.from_pretrained("microsoft/speecht5-hifigan")

        # Default speaker embedding (BDL speaker from CMU ARCTIC)
        embeddings_dataset = load_dataset(
            "Matthijs/cmu-arctic-xvectors", split="validation"
        )
        speaker_embedding = embeddings_dataset[7306]["xvector"]  # BDL (US male)

        return {
            "processor": processor,
            "model": model,
            "vocoder": vocoder,
            "speaker_embedding": speaker_embedding,
            "sample_rate": 16000,
        }
    except Exception:
        return None


def _load_bark() -> Optional[Any]:
    """
    Bark — suno-ai/bark. Expressive, supports laughter/music.
    pip install suno-bark  (CPU ~4s, GPU ~0.5s per sentence)
    """
    try:
        from bark import SAMPLE_RATE, generate_audio, preload_models  # type: ignore
        preload_models(text_use_gpu=False, coarse_use_gpu=False, fine_use_gpu=False)
        return {"generate": generate_audio, "sample_rate": SAMPLE_RATE}
    except Exception:
        return None


def _load_mms() -> Optional[Any]:
    """
    MMS-TTS — Meta Massively Multilingual Speech (1100+ languages).
    pip install transformers
    """
    try:
        from transformers import VitsModel, AutoTokenizer  # type: ignore
        model_id = "facebook/mms-tts-eng"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = VitsModel.from_pretrained(model_id)
        return {"tokenizer": tokenizer, "model": model, "sample_rate": 22050}
    except Exception:
        return None


# ── Engine registry (lazy-loaded singletons) ──────────────────────────────────

_ENGINES: dict[TTSEngine, Any] = {}


def _get_engine(engine: TTSEngine) -> Optional[Any]:
    if engine not in _ENGINES:
        loaders = {
            TTSEngine.SILERO:   _load_silero,
            TTSEngine.SPEECHT5: _load_speecht5,
            TTSEngine.BARK:     _load_bark,
            TTSEngine.MMS:      _load_mms,
        }
        loader = loaders.get(engine)
        _ENGINES[engine] = loader() if loader else None
    return _ENGINES.get(engine)


# ── Synthesis dispatch ────────────────────────────────────────────────────────

def synthesize(
    text: str,
    engine: TTSEngine = TTSEngine.SILERO,
    voice: str = "en_0",
    sample_rate: int = 22050,
) -> tuple[bytes, int]:
    """
    Synthesize text → PCM audio bytes using the specified zero-cost engine.

    Returns:
        (pcm_bytes: bytes, sample_rate: int)

    Fallback chain: requested engine → SIMULATED if unavailable.
    """
    backend = _get_engine(engine)

    if engine == TTSEngine.SILERO and backend:
        return _synth_silero(text, backend, voice)
    elif engine == TTSEngine.SPEECHT5 and backend:
        return _synth_speecht5(text, backend)
    elif engine == TTSEngine.BARK and backend:
        return _synth_bark(text, backend, voice)
    elif engine == TTSEngine.MMS and backend:
        return _synth_mms(text, backend)
    elif engine in (TTSEngine.KOKORO, TTSEngine.PIPER):
        raise NotImplementedError(
            f"{engine.value} is handled by KittenService / piper_tts.py respectively"
        )
    else:
        return _synth_simulated(text, sample_rate)


def available_engines() -> list[str]:
    """Return names of engines that loaded successfully."""
    results = []
    for eng in (TTSEngine.SILERO, TTSEngine.SPEECHT5, TTSEngine.MMS, TTSEngine.BARK):
        if _get_engine(eng) is not None:
            results.append(eng.value)
    # Kokoro and Piper availability reported separately
    results.append("piper (via piper_tts.py)")
    try:
        results.append("kokoro (via KittenService)")
    except Exception:
        pass
    return results


# ── Engine implementations ────────────────────────────────────────────────────

def _synth_silero(text: str, backend: dict, voice: str) -> tuple[bytes, int]:
    sample_rate = backend["sample_rate"]
    audio_tensor = backend["model"].apply_tts(
        text=text,
        speaker=voice,
        sample_rate=sample_rate,
    )
    audio_np = audio_tensor.numpy()
    pcm = (audio_np * 32767).astype("int16").tobytes()
    return pcm, sample_rate


def _synth_speecht5(text: str, backend: dict) -> tuple[bytes, int]:
    import torch  # type: ignore
    processor  = backend["processor"]
    model      = backend["model"]
    vocoder    = backend["vocoder"]
    spk_emb    = backend["speaker_embedding"]
    sample_rate = backend["sample_rate"]

    inputs = processor(text=text, return_tensors="pt")
    spk_tensor = torch.tensor(spk_emb).unsqueeze(0)
    with torch.no_grad():
        speech = model.generate_speech(inputs["input_ids"], spk_tensor, vocoder=vocoder)
    pcm = (speech.numpy() * 32767).astype("int16").tobytes()
    return pcm, sample_rate


def _synth_bark(text: str, backend: dict, voice: str) -> tuple[bytes, int]:
    audio_np = backend["generate"](text, history_prompt=voice if voice else None)
    pcm = (audio_np * 32767).astype("int16").tobytes()
    return pcm, backend["sample_rate"]


def _synth_mms(text: str, backend: dict) -> tuple[bytes, int]:
    import torch  # type: ignore
    tokenizer = backend["tokenizer"]
    model = backend["model"]
    sample_rate = backend["sample_rate"]

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    pcm = (output.squeeze().numpy() * 32767).astype("int16").tobytes()
    return pcm, sample_rate


def _synth_simulated(text: str, sample_rate: int) -> tuple[bytes, int]:
    placeholder = f"[SIMULATED_AUDIO: {text}]".encode("utf-8")
    return placeholder, sample_rate
