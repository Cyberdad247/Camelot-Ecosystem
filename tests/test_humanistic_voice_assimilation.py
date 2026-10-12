# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit Test Suite for Humanistic Voice Nexus Assimilation Protocol
================================================================
Verifies:
1. νKG crystal integrity for OMEGA_HUMANISTIC_VOICE_NEXUS (6-repo assimilation).
2. VocalPatternAnalyzer F0 pitch contour, intonation slope, and RMS energy dynamics.
3. Conversational backchannel recognition vs. true user turn completion.
4. Adaptive turn-taking silence thresholding (rising inflection vs. falling inflection).
5. Speakeasy dynamic slider calibration & LiveTalking 25 FPS viseme alignment.
6. LiveKit WebRTC transport metrics.
7. Runic router dispatch for //HUMANISTIC_VOICE and aliases (//humanistic, //vocal_prosody, //live_speech).
"""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
import pytest

from control_plane.runes.runic_router import route_rune

CAMELOT_HOME = Path(__file__).resolve().parent.parent

# Dynamically import VocalPatternAnalyzer & HumanisticConversationalLoop
hv_dir = CAMELOT_HOME / "02_FORGE" / "assimilation" / "humanistic_voice"
if str(hv_dir) not in sys.path:
    sys.path.insert(0, str(hv_dir))

import vocal_pattern_analyzer
import humanistic_conversational_loop

VocalPatternAnalyzer = vocal_pattern_analyzer.VocalPatternAnalyzer
PitchInflection = vocal_pattern_analyzer.PitchInflection
EnergyTier = vocal_pattern_analyzer.EnergyTier
HumanisticConversationalLoop = humanistic_conversational_loop.HumanisticConversationalLoop
VISEMES_16 = humanistic_conversational_loop.VISEMES_16


# ── 1. νKG Crystal Integrity Test ─────────────────────────────────────────────

def test_vkg_crystal_presence_and_structure():
    """Verify vkg_humanistic_voice_nexus.json exists, lists 6 repos, and has kinetic flow DAG."""
    crystal_path = (
        CAMELOT_HOME
        / "03_VAULT"
        / "runtime_state"
        / "open_notebook"
        / "vkg_crystals"
        / "vkg_humanistic_voice_nexus.json"
    )
    assert crystal_path.exists(), "vkg_humanistic_voice_nexus.json must exist"

    data = json.loads(crystal_path.read_text(encoding="utf-8"))
    assert data["system_identity"] == "OMEGA_HUMANISTIC_VOICE_NEXUS"
    assert len(data["assimilated_repositories"]) == 6

    repo_urls = [r["repo"] for r in data["assimilated_repositories"]]
    assert "https://github.com/nhunzaker/speakeasy.git" in repo_urls
    assert "https://github.com/livnoni/continuousSpeechRecognition" in repo_urls
    assert "https://github.com/danships/genie-ai.git" in repo_urls
    assert "https://github.com/viniciuspereiras/OpenAIChat.git" in repo_urls
    assert "https://github.com/Cyberdad247/LiveTalking.git" in repo_urls
    assert "https://github.com/Cyberdad247/livekit.git" in repo_urls


# ── 2. Vocal Pattern Analyzer: Pitch, Inflection & Energy Tests ───────────────

def _generate_sine_pcm(freq_start: float, freq_end: float, duration_sec: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generates synthetic 16-bit linear PCM audio with linear frequency modulation."""
    num_samples = int(duration_sec * sample_rate)
    samples = []
    phase = 0.0
    for i in range(num_samples):
        # Linear frequency interpolation
        t = i / num_samples
        f = freq_start + t * (freq_end - freq_start)
        phase += 2.0 * math.pi * f / sample_rate
        sample = int(3000 * math.sin(phase))
        samples.append(sample)
    return struct.pack(f"<{len(samples)}h", *samples)


def test_pitch_and_inflection_flat_tone():
    """Verify constant 220Hz sine wave yields flat inflection and ~220Hz mean F0."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000)
    pcm = _generate_sine_pcm(220.0, 220.0, duration_sec=0.5)
    report = analyzer.analyze_audio_chunk(pcm)

    assert 200.0 <= report.mean_f0_hz <= 240.0
    assert report.f0_inflection == PitchInflection.FLAT
    assert abs(report.f0_delta_hz) < 15.0


def test_pitch_inflection_rising_sweep():
    """Verify rising sweep (150Hz -> 250Hz) triggers RISING inflection."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000)
    pcm = _generate_sine_pcm(150.0, 260.0, duration_sec=0.5)
    report = analyzer.analyze_audio_chunk(pcm)

    assert report.f0_inflection == PitchInflection.RISING
    assert report.f0_delta_hz > 15.0


def test_pitch_inflection_falling_sweep():
    """Verify falling sweep (260Hz -> 150Hz) triggers FALLING inflection."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000)
    pcm = _generate_sine_pcm(260.0, 150.0, duration_sec=0.5)
    report = analyzer.analyze_audio_chunk(pcm)

    assert report.f0_inflection == PitchInflection.FALLING
    assert report.f0_delta_hz < -15.0


def test_energy_tier_classification():
    """Verify low amplitude is classified as whisper/quiet and high amplitude as normal/assertive."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000)

    # Low amplitude
    samples_low = [int(150 * math.sin(2 * math.pi * 200 * i / 16000)) for i in range(4000)]
    pcm_low = struct.pack(f"<{len(samples_low)}h", *samples_low)
    rep_low = analyzer.analyze_audio_chunk(pcm_low)
    assert rep_low.energy_tier in (EnergyTier.WHISPER, EnergyTier.QUIET)

    # High amplitude
    samples_high = [int(18000 * math.sin(2 * math.pi * 200 * i / 16000)) for i in range(4000)]
    pcm_high = struct.pack(f"<{len(samples_high)}h", *samples_high)
    rep_high = analyzer.analyze_audio_chunk(pcm_high)
    assert rep_high.energy_tier in (EnergyTier.NORMAL, EnergyTier.ASSERTIVE)


# ── 3. Backchannel Filter & Turn Boundary Tests ───────────────────────────────

@pytest.mark.parametrize("backchannel_token", ["mhm", "yeah", "uh-huh", "right", "ok", "sure"])
def test_backchannel_detection_filters_false_barge_in(backchannel_token: str):
    """Verify common human conversational affirmations are flagged as backchannels."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000)
    pcm = _generate_sine_pcm(200.0, 200.0, duration_sec=0.25)
    report = analyzer.analyze_audio_chunk(pcm, transcript_hint=backchannel_token)

    assert report.is_backchannel is True
    assert report.recommended_silence_wait_ms == 0
    assert report.is_turn_complete is False


def test_substantive_utterance_not_flagged_as_backchannel():
    """Verify substantive sentences are recognized as true human turns."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000)
    pcm = _generate_sine_pcm(200.0, 180.0, duration_sec=1.5)
    report = analyzer.analyze_audio_chunk(pcm, transcript_hint="Deploy the container to production.")

    assert report.is_backchannel is False
    assert report.is_turn_complete is True
    assert report.recommended_silence_wait_ms > 0


# ── 4. Adaptive Turn-Taking Silence Threshold Tests ───────────────────────────

def test_adaptive_turn_taking_gives_breathing_room_on_rising_pitch():
    """Verify rising inflection expands silence wait threshold to prevent cutting human off."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000, base_silence_threshold_ms=350)
    pcm_rising = _generate_sine_pcm(150.0, 250.0, duration_sec=2.5)
    report = analyzer.analyze_audio_chunk(pcm_rising, transcript_hint="Could you check the server logs?")

    # Rising pitch should add at least +200ms over base 350ms (>= 550ms)
    assert report.f0_inflection == PitchInflection.RISING
    assert report.recommended_silence_wait_ms >= 550


def test_adaptive_turn_taking_responds_snappily_on_falling_pitch():
    """Verify falling inflection contracts silence wait threshold for crisp turn handover."""
    analyzer = VocalPatternAnalyzer(sample_rate=16000, base_silence_threshold_ms=350)
    pcm_falling = _generate_sine_pcm(260.0, 160.0, duration_sec=0.6)
    report = analyzer.analyze_audio_chunk(pcm_falling, transcript_hint="System is ready.")

    # Falling pitch should subtract from base 350ms (<= 250ms)
    assert report.f0_inflection == PitchInflection.FALLING
    assert report.recommended_silence_wait_ms <= 250


# ── 5. Speakeasy Calibration & LiveTalking Viseme Sync Tests ───────────────────

def test_speakeasy_slider_calibration_from_prosody():
    """Verify Speakeasy adapter dynamically tunes rate and pitch based on human urgency."""
    loop = HumanisticConversationalLoop()
    
    # Urgent report
    pcm_fast = _generate_sine_pcm(200.0, 200.0, duration_sec=0.5)
    urgent_turn = loop.process_incoming_human_turn(
        pcm_fast, "Quick, we have a critical incident on cluster two!"
    )
    assert urgent_turn["calibrated_sliders"]["rate"] > 1.1

    # Hesitant report
    pcm_slow = _generate_sine_pcm(180.0, 180.0, duration_sec=2.5)
    hesitant_turn = loop.process_incoming_human_turn(
        pcm_slow, "Um... I was wondering... if maybe we could review this?"
    )
    assert hesitant_turn["calibrated_sliders"]["rate"] <= 1.0


def test_livetalking_viseme_generation():
    """Verify LiveTalking adapter generates standard 16 visemes at 25 FPS."""
    loop = HumanisticConversationalLoop()
    visemes = loop.viseme_sync.extract_viseme_sequence(
        "Camelot OS Sovereign Voice Intelligence Online", duration_sec=1.0, fps=25
    )
    assert len(visemes) == 25
    assert visemes[0]["viseme"] == "viseme_sil"
    assert visemes[0]["weight"] == 0.0

    # Ensure all generated visemes belong to the standard set
    for v in visemes:
        assert v["viseme"] in VISEMES_16


def test_livekit_transport_metrics():
    """Verify LiveKit transport returns expected WebRTC metrics."""
    loop = HumanisticConversationalLoop()
    metrics = loop.livekit.get_transport_metrics()
    assert metrics["rtt_ms"] < 25.0
    assert metrics["jitter_ms"] < 10.0
    assert metrics["audio_codec"] == "OPUS_48KHZ_STEREO"


# ── 6. Runic Dispatch Tests ───────────────────────────────────────────────────

def test_runic_dispatch_humanistic_voice():
    """Verify //HUMANISTIC_VOICE routes and executes conversational synthesis."""
    res = route_rune("//HUMANISTIC_VOICE Can you hear me clearly?", {})
    assert res.rune == "//HUMANISTIC_VOICE"
    assert res.metadata["status"] == "HUMANISTIC_CONVERSATION_ACTIVE"
    assert res.metadata["turn_result"]["status"] == "HUMANISTIC_TURN_SYNTHESIZED"
    assert res.metadata["turn_result"]["active_knight"] == "reya_companion"


def test_runic_dispatch_humanistic_voice_aliases():
    """Verify //humanistic, //vocal_prosody, and //live_speech aliases dispatch correctly."""
    # 1. //humanistic
    res1 = route_rune("//humanistic What is the status of the fortress?", {})
    assert res1.rune == "//humanistic"
    assert res1.metadata["status"] == "HUMANISTIC_CONVERSATION_ACTIVE"

    # 2. //vocal_prosody
    res2 = route_rune("//vocal_prosody Analyze my vocal cadence", {})
    assert res2.rune == "//vocal_prosody"
    assert res2.metadata["status"] == "HUMANISTIC_CONVERSATION_ACTIVE"

    # 3. //live_speech
    res3 = route_rune("//live_speech Full duplex channel check", {})
    assert res3.rune == "//live_speech"
    assert res3.metadata["status"] == "HUMANISTIC_CONVERSATION_ACTIVE"
