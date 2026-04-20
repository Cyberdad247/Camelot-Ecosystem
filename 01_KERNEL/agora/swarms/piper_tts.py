# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Piper TTS Engine — Local neural text-to-speech via HuggingFace ONNX models.

Integrates with:
  - Voice Swarm (agent_echo alternative)
  - TTS Engine Selector (podcast pipeline)
  - SIR_SONUS (Voice Knight)

Piper voices are downloaded from rhasspy/piper-voices on HuggingFace.
Zero API cost, sub-200ms latency, 8GB RAM safe.
"""

import io
import os
import wave
from typing import Any, List, Optional

import numpy as np

PIPER_MODELS_DIR = os.path.join(
    os.path.expanduser("~"), "CAMELOT_OS", "docs", "EXTERNAL", "piper", "models"
)

# Import universal voice registry (single source of truth)
try:
    from senses.audio.knight_voices import VOICE_PRESETS, get_voice, get_model
except ImportError:
    try:
        import importlib.util as _ilu
        _kv_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "senses", "audio", "knight_voices.py"
        )
        if os.path.exists(_kv_path):
            _spec = _ilu.spec_from_file_location("knight_voices", _kv_path)
            _kv = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_kv)
            VOICE_PRESETS = _kv.VOICE_PRESETS
            get_voice = _kv.get_voice
            get_model = _kv.get_model
        else:
            raise ImportError("knight_voices.py not found")
    except Exception:
        # Inline fallback if registry is unreachable
        VOICE_PRESETS = {
            "tasha": "en_GB-jenny_dioco-medium",
            "tasha_british": "en_GB-cori-medium",
            "tasha_scottish": "en_GB-alba-medium",
            "merlin": "en_US-ryan-medium",
            "narrator": "en_US-lessac-medium",
            "narrator_hq": "en_US-lessac-high",
            "joe": "en_US-joe-medium",
        }
        def get_voice(name): return "tasha"
        def get_model(name): return VOICE_PRESETS.get("tasha")


def _resolve_voice(voice_preset: str) -> str:
    """Resolve a preset name or knight name to a Piper model name."""
    # Direct preset match first
    if voice_preset in VOICE_PRESETS:
        return VOICE_PRESETS[voice_preset]
    # Try as knight name -> preset -> model
    knight_preset = get_voice(voice_preset)
    if knight_preset in VOICE_PRESETS:
        return VOICE_PRESETS[knight_preset]
    # Assume it's already a model name
    return voice_preset


def _get_model_path(voice_name: str) -> tuple[str, str]:
    """Return (onnx_path, config_path) for a voice, auto-downloading if missing."""
    voice_dir = os.path.join(PIPER_MODELS_DIR, voice_name)
    onnx_path = os.path.join(voice_dir, f"{voice_name}.onnx")
    config_path = os.path.join(voice_dir, f"{voice_name}.onnx.json")

    if not os.path.exists(onnx_path):
        # Auto-download on first use
        from forge.scripts.setup_piper import download_voice
        download_voice(voice_name)

    if not os.path.exists(onnx_path):
        raise FileNotFoundError(
            f"Piper voice model not found: {onnx_path}\n"
            f"Run: python -m forge.scripts.setup_piper --voice {voice_name}"
        )

    return onnx_path, config_path


def synthesize(
    text: str,
    voice_preset: str = "tasha",
    output_path: Optional[str] = None,
    length_scale: Optional[float] = None,
) -> tuple[np.ndarray, int]:
    """
    Synthesize text to speech using Piper.

    Returns (samples, sample_rate). Optionally writes to output_path.
    """
    from piper import PiperVoice
    from piper.config import SynthesisConfig

    voice_name = _resolve_voice(voice_preset)
    onnx_path, config_path = _get_model_path(voice_name)

    voice = PiperVoice.load(
        onnx_path,
        config_path=config_path if os.path.exists(config_path) else None,
    )

    syn_config = SynthesisConfig(length_scale=length_scale) if length_scale else None

    # Collect audio chunks from the generator
    all_samples = []
    sample_rate = voice.config.sample_rate
    for chunk in voice.synthesize(text, syn_config=syn_config):
        audio_array = np.frombuffer(
            chunk.audio_int16_bytes, dtype=np.int16
        ).astype(np.float32) / 32768.0
        all_samples.append(audio_array)

    samples = np.concatenate(all_samples) if all_samples else np.array([], dtype=np.float32)

    # Write to disk if requested
    if output_path:
        import soundfile as sf
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sf.write(output_path, samples, sample_rate, subtype="PCM_16")

    return samples, sample_rate


def synthesize_stream(
    text: str,
    voice_preset: str = "tasha",
    length_scale: Optional[float] = None,
):
    """
    Stream audio chunks for real-time playback.
    Yields (audio_int16_bytes, sample_rate) per chunk.
    """
    from piper import PiperVoice
    from piper.config import SynthesisConfig

    voice_name = _resolve_voice(voice_preset)
    onnx_path, config_path = _get_model_path(voice_name)

    voice = PiperVoice.load(
        onnx_path,
        config_path=config_path if os.path.exists(config_path) else None,
    )

    syn_config = SynthesisConfig(length_scale=length_scale) if length_scale else None

    for chunk in voice.synthesize(text, syn_config=syn_config):
        yield chunk.audio_int16_bytes, voice.config.sample_rate


# ---------------------------------------------------------------------------
# Podcast / Multi-Speaker Integration (matches Kokoro engine interface)
# ---------------------------------------------------------------------------

def create_silence(duration: float, sample_rate: int) -> np.ndarray:
    return np.zeros(int(sample_rate * duration), dtype=np.float32)


def create_podcast(
    script: Any,
    output_path: str,
    silence_duration: float = 0.7,
    sampling_rate: int = 22050,
    voice_map: Optional[dict] = None,
) -> str:
    """
    Generate podcast audio from a script using Piper TTS.
    Compatible with tts_engine_selector interface.

    voice_map: {speaker_id: voice_preset}, e.g., {1: "tasha", 2: "merlin"}
    """
    import soundfile as sf

    if voice_map is None:
        voice_map = {1: "tasha", 2: "merlin"}

    entries = script if isinstance(script, list) else script.entries
    audio_segments: List[np.ndarray] = []
    silence = create_silence(silence_duration, sampling_rate)
    actual_rate = sampling_rate

    for entry in entries:
        text = entry["text"] if isinstance(entry, dict) else entry.text
        speaker = entry["speaker"] if isinstance(entry, dict) else entry.speaker
        preset = voice_map.get(speaker, "narrator")

        try:
            samples, actual_rate = synthesize(text, voice_preset=preset)
            # Normalize
            max_amp = np.max(np.abs(samples))
            if max_amp > 0:
                samples = samples / max_amp * 0.9
            audio_segments.append(samples)
        except Exception as e:
            print(f"[PIPER] Synthesis failed for segment: {e}")
            fallback = create_silence(len(text) * 0.05, actual_rate)
            audio_segments.append(fallback)

        audio_segments.append(create_silence(silence_duration, actual_rate))

    if not audio_segments:
        audio_segments = [create_silence(1.0, actual_rate)]

    full_audio = np.concatenate(audio_segments)
    max_amp = np.max(np.abs(full_audio))
    if max_amp > 0:
        full_audio = full_audio / max_amp * 0.9

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, full_audio, actual_rate, subtype="PCM_16")

    return output_path


if __name__ == "__main__":
    # Quick test
    samples, sr = synthesize(
        "Hello, darlin'. Welcome to Camelot. I'm Tasha, your voice guide.",
        voice_preset="tasha",
        output_path=os.path.join(
            os.path.expanduser("~"),
            "CAMELOT_OS", "docs", "ARTIFACTS", "test_piper.wav",
        ),
    )
    print(f"[PIPER] Synthesized {len(samples)} samples at {sr}Hz")
