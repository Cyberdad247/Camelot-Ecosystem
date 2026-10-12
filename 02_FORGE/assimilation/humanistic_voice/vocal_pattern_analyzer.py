# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Vocal Pattern & Acoustic Aspect Analyzer for Humanistic AI Conversation.
==========================================================================
Domain: CAMELOT-OS Humanistic Voice Nexus
Forged by: SIR_SONUS (Multivoice Audio Director) & SIR_HELIO (Bifrost Guardian)

Analyzes human speech in real-time to achieve empathetic, natural turn-taking:
1. F0 Pitch Contour: Rising (+ΔF0) vs. Falling (-ΔF0) intonation tracking.
2. Speech Cadence: Words/syllables per minute and cadence dynamics.
3. Energy/Intensity: RMS dBFS loudness and dynamic range.
4. Backchannel Filter: Recognizes short affirmations ("mhm", "yeah") to prevent false barge-in.
5. Adaptive Turn-Taking: Dynamically adjusts silence threshold (180ms - 650ms).
6. Prosody Mirroring: Calculates optimal TTS vocal parameters to build rapport.
"""

from __future__ import annotations

import audioop
import math
import re
import struct
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Dict, List, Optional, Tuple


class PitchInflection(StrEnum):
    RISING = "rising"      # Question, continuation cue, mid-thought hesitation
    FALLING = "falling"    # Definitive terminal statement, completed command
    FLAT = "flat"          # Neutral, declarative, or reading cadence
    UNKNOWN = "unknown"


class EnergyTier(StrEnum):
    WHISPER = "whisper"      # < -35 dBFS
    QUIET = "quiet"          # -35 to -26 dBFS
    NORMAL = "normal"        # -26 to -16 dBFS
    ASSERTIVE = "assertive"  # > -16 dBFS


@dataclass(frozen=True)
class AcousticProsodyReport:
    # Pitch features
    mean_f0_hz: float
    f0_inflection: PitchInflection
    f0_delta_hz: float
    
    # Energy features
    rms_dbfs: float
    energy_tier: EnergyTier
    
    # Cadence features
    estimated_wpm: float
    duration_ms: float
    is_urgent: bool
    is_hesitant: bool
    
    # Conversational turn-taking
    is_backchannel: bool
    is_turn_complete: bool
    recommended_silence_wait_ms: int
    
    # Mirroring recommendations for TTS
    recommended_tts_pitch_offset: float  # Semitones (-2.0 to +2.0)
    recommended_tts_speech_rate: float   # Multiplier (0.85 to 1.25)
    recommended_tts_warmth: float        # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Common human affirmative backchannels that should NOT trigger full playback cancellation
COMMON_BACKCHANNELS = {
    "mhm", "uh-huh", "yeah", "yep", "right", "ok", "okay",
    "sure", "ah", "got it", "i see", "mm", "yup", "cool"
}


class VocalPatternAnalyzer:
    """Real-time vocal pattern and conversational prosody extraction engine."""

    def __init__(self, sample_rate: int = 16000, base_silence_threshold_ms: int = 350):
        self.sample_rate = sample_rate
        self.base_silence_threshold_ms = base_silence_threshold_ms

    def analyze_audio_chunk(
        self,
        pcm_bytes: bytes,
        transcript_hint: Optional[str] = None,
    ) -> AcousticProsodyReport:
        """Analyzes a PCM16 audio segment along with optional transcript tokens."""
        duration_ms = (len(pcm_bytes) / (2 * self.sample_rate)) * 1000.0 if self.sample_rate > 0 else 0.0

        # 1. Energy Analysis (RMS dBFS)
        rms_dbfs, energy_tier = self._calculate_rms_energy(pcm_bytes)

        # 2. F0 Pitch Contour Analysis
        mean_f0, inflection, delta_f0 = self._estimate_pitch_contour(pcm_bytes)

        # 3. Speech Cadence & Rate
        wpm, is_urgent, is_hesitant = self._calculate_cadence(duration_ms, transcript_hint)

        # 4. Conversational Backchannel Detection
        is_backchannel = self._detect_backchannel(duration_ms, rms_dbfs, transcript_hint)

        # 5. Adaptive Turn-Taking Silence Calculation
        recommended_silence_ms, is_turn_complete = self._calculate_adaptive_turn_taking(
            inflection=inflection,
            is_backchannel=is_backchannel,
            is_urgent=is_urgent,
            is_hesitant=is_hesitant,
            duration_ms=duration_ms,
        )

        # 6. Dynamic Prosody Mirroring Recommendations
        pitch_offset, speech_rate, warmth = self._compute_prosody_mirroring(
            energy_tier=energy_tier,
            is_urgent=is_urgent,
            is_hesitant=is_hesitant,
            mean_f0=mean_f0,
        )

        return AcousticProsodyReport(
            mean_f0_hz=round(mean_f0, 1),
            f0_inflection=inflection,
            f0_delta_hz=round(delta_f0, 1),
            rms_dbfs=round(rms_dbfs, 1),
            energy_tier=energy_tier,
            estimated_wpm=round(wpm, 1),
            duration_ms=round(duration_ms, 1),
            is_urgent=is_urgent,
            is_hesitant=is_hesitant,
            is_backchannel=is_backchannel,
            is_turn_complete=is_turn_complete,
            recommended_silence_wait_ms=recommended_silence_ms,
            recommended_tts_pitch_offset=round(pitch_offset, 2),
            recommended_tts_speech_rate=round(speech_rate, 2),
            recommended_tts_warmth=round(warmth, 2),
        )

    def _calculate_rms_energy(self, pcm_bytes: bytes) -> Tuple[float, EnergyTier]:
        """Calculates RMS energy in dBFS from 16-bit linear PCM audio."""
        if len(pcm_bytes) < 2:
            return -96.0, EnergyTier.WHISPER

        try:
            rms = audioop.rms(pcm_bytes, 2)
        except Exception:
            rms = 0

        if rms <= 0:
            return -96.0, EnergyTier.WHISPER

        # Full scale for 16-bit is 32767
        dbfs = 20.0 * math.log10(rms / 32767.0)

        if dbfs < -35.0:
            tier = EnergyTier.WHISPER
        elif dbfs < -26.0:
            tier = EnergyTier.QUIET
        elif dbfs < -16.0:
            tier = EnergyTier.NORMAL
        else:
            tier = EnergyTier.ASSERTIVE

        return dbfs, tier

    def _estimate_pitch_contour(self, pcm_bytes: bytes) -> Tuple[float, PitchInflection, float]:
        """Estimates pitch contour (F0) using autocorrelation across temporal windows."""
        sample_count = len(pcm_bytes) // 2
        if sample_count < 320:  # Less than 20ms at 16kHz
            return 0.0, PitchInflection.UNKNOWN, 0.0

        # Unpack 16-bit PCM samples
        samples = struct.unpack(f"<{sample_count}h", pcm_bytes[: sample_count * 2])

        # Divide into temporal slices to evaluate pitch contour over time
        slice_size = max(sample_count // 3, 160)
        slices = [
            samples[:slice_size],
            samples[slice_size : slice_size * 2],
            samples[-slice_size:],
        ]

        f0_estimates: List[float] = []
        for s in slices:
            f0 = self._autocorrelate_f0(s)
            if f0 > 0:
                f0_estimates.append(f0)

        if not f0_estimates:
            return 0.0, PitchInflection.UNKNOWN, 0.0

        mean_f0 = sum(f0_estimates) / len(f0_estimates)

        # Delta between onset and terminal pitch
        if len(f0_estimates) >= 2:
            delta_f0 = f0_estimates[-1] - f0_estimates[0]
        else:
            delta_f0 = 0.0

        # Inflection classification threshold (15 Hz delta)
        if delta_f0 > 15.0:
            inflection = PitchInflection.RISING
        elif delta_f0 < -15.0:
            inflection = PitchInflection.FALLING
        else:
            inflection = PitchInflection.FLAT

        return mean_f0, inflection, delta_f0

    def _autocorrelate_f0(self, samples: Tuple[int, ...] | List[int]) -> float:
        """Autocorrelation-based pitch estimator within typical human vocal range (75 - 450 Hz)."""
        n = len(samples)
        if n < 160:
            return 0.0

        min_lag = int(self.sample_rate / 450)  # ~450 Hz upper limit
        max_lag = int(self.sample_rate / 75)   # ~75 Hz lower limit
        max_lag = min(max_lag, n // 2)

        best_corr = -1.0
        best_lag = 0

        # Normalized autocorrelation at lag
        for lag in range(min_lag, max_lag):
            corr = 0
            energy = 0
            for i in range(n - lag):
                corr += samples[i] * samples[i + lag]
                energy += samples[i] * samples[i]

            if energy > 0:
                norm_corr = corr / energy
                if norm_corr > best_corr and norm_corr > 0.35:
                    best_corr = norm_corr
                    best_lag = lag

        if best_lag > 0:
            return self.sample_rate / best_lag
        return 0.0

    def _calculate_cadence(
        self, duration_ms: float, transcript_hint: Optional[str]
    ) -> Tuple[float, bool, bool]:
        """Estimates speaking rate in words-per-minute and flags urgency/hesitation."""
        if not transcript_hint or duration_ms <= 0:
            return 130.0, False, False

        words = re.findall(r"\w+", transcript_hint.strip())
        word_count = len(words)
        if word_count == 0:
            return 130.0, False, False

        # WPM calculation: (words / duration_ms) * 60,000
        wpm = (word_count / duration_ms) * 60000.0

        is_hesitant = (
            wpm < 110.0
            or "..." in transcript_hint
            or "um" in transcript_hint.lower()
            or "uh" in transcript_hint.lower()
        )
        is_urgent = (wpm > 165.0) and not is_hesitant

        return wpm, is_urgent, is_hesitant

    def _detect_backchannel(
        self, duration_ms: float, rms_dbfs: float, transcript_hint: Optional[str]
    ) -> bool:
        """Determines if the speech chunk is an affirmative backchannel cue rather than a barge-in."""
        if transcript_hint:
            clean_text = transcript_hint.strip().lower().rstrip(".,!?")
            if clean_text in COMMON_BACKCHANNELS:
                return True

        # Acoustic heuristic: very short bursts (<420ms) with moderate/low intensity
        if 80.0 <= duration_ms <= 420.0 and rms_dbfs < -22.0:
            return True

        return False

    def _calculate_adaptive_turn_taking(
        self,
        inflection: PitchInflection,
        is_backchannel: bool,
        is_urgent: bool,
        is_hesitant: bool,
        duration_ms: float,
    ) -> Tuple[int, bool]:
        """Calculates dynamic silence wait time before triggering AI conversational turn."""
        if is_backchannel:
            # Backchannel does not complete the user's turn (user is just acknowledging)
            return 0, False

        wait_ms = self.base_silence_threshold_ms

        if inflection == PitchInflection.RISING:
            # Question or mid-sentence hesitation -> give human more breathing room
            wait_ms += 250  # e.g., 350 + 250 = 600ms
        elif inflection == PitchInflection.FALLING:
            # Definitive completion -> answer swiftly
            wait_ms = max(180, wait_ms - 150)  # e.g., 200ms

        if is_urgent:
            wait_ms = max(160, wait_ms - 80)
        elif is_hesitant:
            wait_ms += 150

        is_turn_complete = duration_ms >= 300.0

        return int(wait_ms), is_turn_complete

    def _compute_prosody_mirroring(
        self,
        energy_tier: EnergyTier,
        is_urgent: bool,
        is_hesitant: bool,
        mean_f0: float,
    ) -> Tuple[float, float, float]:
        """Computes empathetic TTS mirroring parameters (pitch offset, speech rate, warmth)."""
        pitch_offset = 0.0
        speech_rate = 1.0
        warmth = 0.7

        # Pacing alignment
        if is_hesitant:
            speech_rate = 0.92
            warmth = 0.95
            pitch_offset = -0.3
        elif is_urgent:
            speech_rate = 1.18
            warmth = 0.5

        # Energy alignment
        if energy_tier == EnergyTier.WHISPER:
            warmth = 1.0
            speech_rate = min(speech_rate, 0.9)
            pitch_offset -= 0.5
        elif energy_tier == EnergyTier.ASSERTIVE:
            speech_rate = max(speech_rate, 1.05)
            warmth = 0.6
            pitch_offset += 0.2

        return pitch_offset, speech_rate, warmth
