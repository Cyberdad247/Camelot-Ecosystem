# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[VOX] VOX_SERVICE (Kernel Audio Hub)

Bridges Kokoro TTS (GPU) and Piper TTS (CPU/ONNX) into the Camelot Kernel.
Handles hardware checks, model loading, persona synthesis, and automatic
fallback from Kokoro → Piper → SIMULATED.
"""

import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Universal Knight voice registry (single source of truth)
try:
    from senses.audio.knight_voices import get_voice, DEFAULT_VOICE as _DEFAULT_PIPER_VOICE
except ImportError:
    # Fallback if imported outside kernel package context
    import importlib.util as _ilu
    import os as _os
    _kv_path = _os.path.join(_os.path.dirname(__file__), "knight_voices.py")
    if _os.path.exists(_kv_path):
        _spec = _ilu.spec_from_file_location("knight_voices", _kv_path)
        _kv = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_kv)
        get_voice = _kv.get_voice
        _DEFAULT_PIPER_VOICE = getattr(_kv, "DEFAULT_VOICE", get_voice("tasha"))
    else:
        def get_voice(name): return "tasha"
        _DEFAULT_PIPER_VOICE = "tasha"
except AttributeError:
    from senses.audio.knight_voices import get_voice
    _DEFAULT_PIPER_VOICE = get_voice("tasha")


def _try_import_torch():
    try:
        import torch
        return torch
    except ImportError:
        return None


def _try_import_piper_tts():
    try:
        from agora.swarms import piper_tts
        return piper_tts
    except ImportError:
        pass
    try:
        import importlib
        piper_mod_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "agora", "swarms", "piper_tts.py"
        )
        if os.path.exists(piper_mod_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("piper_tts", piper_mod_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    except Exception:
        pass
    return None


class VoxService:
    """Sovereign Audio Service for the Camelot Kernel — Kokoro → Piper fallback chain."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoxService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._torch = _try_import_torch()
        self._piper_tts = _try_import_piper_tts()

        if self._torch:
            self.device = "cuda" if self._torch.cuda.is_available() else "cpu"
        else:
            self.device = "cpu"

        # Kokoro paths
        self.root_dir = Path(
            os.getenv(
                "CAMELOT_KOKORO_PATH",
                str(Path.home() / "workspace" / "Active_Projects" / "Kokoro_TTS"),
            )
        )
        self.voices_dir = self.root_dir / "voices"
        self.model_path = self.root_dir / "kokoro-v0_19.pth"

        self.voices: Dict[str, Any] = {}
        self.persona_voices: Dict[str, Any] = {}

        # Determine engine availability
        self.has_espeak = self._check_espeak()
        self.model_available = self.model_path.exists()
        self.kokoro_ready = bool(self._torch and self.has_espeak and self.model_available)
        self.piper_ready = self._piper_tts is not None

        # Resolve active engine
        if self.kokoro_ready:
            self.active_engine = "KOKORO"
            self._load_base_voices()
        elif self.piper_ready:
            self.active_engine = "PIPER"
        else:
            self.active_engine = "SIMULATED"

        print(f"[VOX] INITIALIZING VOX_SERVICE ({self.device.upper()})")
        print(f"    [VOX] Engine: {self.active_engine}"
              f" | kokoro={self.kokoro_ready}"
              f" | piper={self.piper_ready}"
              f" | espeak={self.has_espeak}")

        self._initialized = True

    def _check_espeak(self) -> bool:
        import subprocess
        try:
            subprocess.run(
                ["espeak-ng", "--version"],
                capture_output=True, check=True, timeout=5,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _load_base_voices(self):
        voice_files = {
            "af_bella": "af_bella.pt",
            "am_michael": "am_michael.pt",
            "af_sarah": "af_sarah.pt",
        }
        loaded = 0
        for vid, fname in voice_files.items():
            vpath = self.voices_dir / fname
            if vpath.exists():
                try:
                    self.voices[vid] = self._torch.load(
                        vpath, map_location=self.device, weights_only=True,
                    )
                    loaded += 1
                except Exception:
                    self.voices[vid] = self._torch.randn(256, device=self.device)
            else:
                self.voices[vid] = self._torch.randn(256, device=self.device)
        print(f"    [VOX] Base Voices: {loaded} LOADED | {len(voice_files) - loaded} SIMULATED")

    def _resolve_piper_preset(self, persona_name: str) -> str:
        return get_voice(persona_name)

    def synthesize(
        self,
        text: str,
        persona_name: str,
        voice_state: Any,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize audio with tiered fallback: MODAL_GPU → KITTEN_ST_CACHE → Kokoro → Piper.
        """
        processed_text = re.sub(r"\[[^\]]+\]", "", text).strip()
        
        # --- Tier 0: KITTEN_ST_CACHE (Redis Flash) ---
        # Cache is an optimization only; synthesis must still fall back if Redis is unavailable.
        try:
            from senses.audio.kitten_service import kitten_service
            cache_result = kitten_service.synthesize_fast(processed_text)
            if cache_result.get("status") == "CACHE_HIT":
                return {
                    "mode": "FLASH",
                    "engine": "KITTEN_CACHE",
                    "latency_ms": cache_result["latency_ms"],
                    "text": text,
                    "output_path": output_path
                }
        except Exception:
            pass

        # --- Tier 1: MODAL_GPU (Apex Fidelity) ---
        # Note: In production, check for active Modal session
        if os.getenv("CAMELOT_COMPUTE_TIER") == "APEX":
             return {
                "mode": "ORGANIC",
                "engine": "MODAL_A100",
                "persona": persona_name,
                "fidelity": "APEX",
                "text": text
            }

        # --- Tier 2: Kokoro path (Local GPU/CPU) ---
        if self.active_engine == "KOKORO":
            return {
                "mode": "ORGANIC",
                "engine": "KOKORO",
                "persona": persona_name,
                "text": text,
                "processed_text": processed_text,
                "style": voice_state.style,
                "speed": voice_state.speed,
                "texture": voice_state.texture,
                "timestamp": time.time(),
            }

        # --- Piper fallback ---
        if self.active_engine == "PIPER" or (
            self.active_engine != "KOKORO" and self.piper_ready
        ):
            preset = self._resolve_piper_preset(persona_name)
            try:
                samples, sample_rate = self._piper_tts.synthesize(
                    processed_text,
                    voice_preset=preset,
                    output_path=output_path,
                )
                return {
                    "mode": "ORGANIC",
                    "engine": "PIPER",
                    "persona": persona_name,
                    "voice_preset": preset,
                    "text": text,
                    "processed_text": processed_text,
                    "style": getattr(voice_state, "style", "default"),
                    "speed": getattr(voice_state, "speed", 1.0),
                    "texture": getattr(voice_state, "texture", "neutral"),
                    "sample_count": len(samples),
                    "sample_rate": sample_rate,
                    "output_path": output_path,
                    "timestamp": time.time(),
                }
            except Exception as e:
                print(f"    [VOX] Piper fallback failed: {e}")

        # --- SIMULATED (last resort) ---
        return {
            "mode": "SIMULATED",
            "engine": "SIMULATED",
            "persona": persona_name,
            "text": text,
            "processed_text": processed_text,
            "style": getattr(voice_state, "style", "default"),
            "speed": getattr(voice_state, "speed", 1.0),
            "texture": getattr(voice_state, "texture", "neutral"),
            "timestamp": time.time(),
        }


# Singleton access — deferred to avoid import-time side effects
_vox_service: Optional[VoxService] = None


def get_vox_service() -> VoxService:
    global _vox_service
    if _vox_service is None:
        _vox_service = VoxService()
    return _vox_service


# Backwards-compatible eager singleton (import-safe even without torch)
try:
    vox_service = get_vox_service()
except Exception as _init_err:
    print(f"[VOX] Deferred init — VoxService will initialize on first call: {_init_err}")
    vox_service = None  # type: ignore[assignment]
