# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
[S6-02] SileroVadDetector — ML-based VAD with energy-VAD fallback
==================================================================
Wraps snakers4/silero-vad torch.hub model.  Falls back gracefully to
energy RMS threshold when torch or the model are unavailable.

Usage:
    detector = SileroVadDetector()        # auto-selects Silero or energy
    is_speech = detector.is_speech(pcm_float32_array, sample_rate=16000)
    detector.reset()                       # clear frame buffer

Module-level singleton:
    from silero_vad import silero_detector
"""
from __future__ import annotations

import math
import os
from typing import Sequence

# ── Config ────────────────────────────────────────────────────────────────────

SILERO_REPO    = os.environ.get("SILERO_VAD_REPO", "snakers4/silero-vad")
SILERO_MODEL   = os.environ.get("SILERO_VAD_MODEL", "silero_vad")
ENERGY_THRESH  = float(os.environ.get("VAD_RMS_THRESHOLD", "0.01"))
SILERO_THRESH  = float(os.environ.get("SILERO_THRESHOLD", "0.5"))


def _rms(samples: Sequence[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(v * v for v in samples) / len(samples))


class SileroVadDetector:
    """VAD using Silero model; falls back to energy RMS if torch unavailable."""

    def __init__(self) -> None:
        self._model = None
        self._get_speech_timestamps = None
        self._backend: str = "energy"
        self._load_silero()

    def _load_silero(self) -> None:
        try:
            import torch  # type: ignore
            model, utils = torch.hub.load(
                repo_or_dir=SILERO_REPO,
                model=SILERO_MODEL,
                force_reload=False,
                trust_repo=True,
                verbose=False,
            )
            (
                self._get_speech_timestamps,
                _,
                _,
                _,
                _,
            ) = utils
            self._model = model
            self._model.eval()
            self._backend = "silero"
        except Exception:
            self._backend = "energy"

    def is_speech(self, samples: Sequence[float], sample_rate: int = 16000) -> bool:
        """Return True if the frame contains speech."""
        if self._backend == "silero" and self._model is not None:
            return self._silero_check(samples, sample_rate)
        return _rms(samples) > ENERGY_THRESH

    def _silero_check(self, samples: Sequence[float], sample_rate: int) -> bool:
        try:
            import torch  # type: ignore
            tensor = torch.tensor(list(samples), dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                prob = self._model(tensor, sample_rate).item()
            return prob >= SILERO_THRESH
        except Exception:
            return _rms(samples) > ENERGY_THRESH

    def reset(self) -> None:
        """Reset Silero internal state between utterances."""
        if self._backend == "silero" and self._model is not None:
            try:
                self._model.reset_states()
            except Exception:
                pass

    @property
    def backend(self) -> str:
        return self._backend

    def stats(self) -> dict:
        return {"backend": self._backend, "silero_threshold": SILERO_THRESH, "energy_threshold": ENERGY_THRESH}


# Module-level singleton — used by omnivoice-router and AudioSession
silero_detector = SileroVadDetector()
