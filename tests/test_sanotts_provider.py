# SPDX-License-Identifier: MIT
"""
tests/test_sanotts_provider.py — Unit tests for SanoTTS Local Voice Engine Provider.
Verifies audio synthesis, 24kHz mono PCM WAV generation, streaming, telemetry,
and MultivoiceBridge integration.
"""

from __future__ import annotations

import io
import wave
from pathlib import Path
import pytest

from control_plane.multivoice_bridge import MultivoiceBridge, parse_metrics, render_panel
from control_plane.voice.sanotts_provider import SanoTTSProvider, SanoVoiceTelemetry


def test_sanotts_provider_initialization_and_metadata():
    """Verify SanoTTS provider initialization and metadata report."""
    provider = SanoTTSProvider()
    meta = provider.get_metadata()

    assert meta["provider"] == "sanotts"
    assert meta["model_identifier"] == "ampixa/sanoTTS"
    assert meta["sample_rate_hz"] == 24000
    assert meta["channels"] == 1
    assert meta["bit_depth"] == 16
    assert meta["memory_footprint_mb"] == 5.1
    assert "ZERO" in meta["cloud_egress"]


def test_sanotts_synthesize_wav_header_and_payload(tmp_path: Path):
    """Verify generated WAV bytes adhere to 16-bit mono 24kHz PCM standard."""
    provider = SanoTTSProvider()
    test_text = "Welcome to Camelot-OS. System telemetry nominal."
    wav_bytes = provider.synthesize_to_wav(test_text)

    assert len(wav_bytes) > 44
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"

    # Verify with standard wave library
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2  # 16-bit
        assert wf.getframerate() == 24000
        n_frames = wf.getnframes()
        assert n_frames > 0

    # Test file saving
    out_file = tmp_path / "test_voice.wav"
    saved_path = provider.synthesize_to_file(test_text, out_file)
    assert Path(saved_path).exists()
    assert Path(saved_path).stat().st_size == len(wav_bytes)


def test_sanotts_synthesize_stream():
    """Verify chunked streaming generator for real-time low-latency playback."""
    provider = SanoTTSProvider()
    test_text = "Testing real-time chunked streaming."
    chunk_size = 2048

    chunks = list(provider.synthesize_stream(test_text, chunk_size=chunk_size))
    assert len(chunks) > 0

    # Ensure all chunks except possibly the last are exactly chunk_size
    for chunk in chunks[:-1]:
        assert len(chunk) == chunk_size
    assert len(chunks[-1]) <= chunk_size


def test_sanotts_telemetry_accumulation():
    """Verify synthesis telemetry counters and latency tracking."""
    provider = SanoTTSProvider()
    p1 = "First synthesis alert."
    p2 = "Second synthesis warning."

    provider.synthesize_to_wav(p1)
    provider.synthesize_to_wav(p2)

    tel = provider.export_telemetry()
    assert tel["sanotts_syntheses"] >= 2
    assert tel["sanotts_chars"] >= len(p1) + len(p2)
    assert tel["sanotts_audio_s"] > 0.0
    assert tel["sanotts_avg_latency_ms"] >= 0.0


def test_sanotts_multivoice_bridge_integration():
    """Verify seamless attachment to MultivoiceBridge and HUD panel rendering."""
    bridge = MultivoiceBridge(timeout_s=0.1)
    provider = SanoTTSProvider()
    provider.synthesize_to_wav("HUD audio active.")

    bridge.attach_sanotts(provider)
    stats = bridge.fetch_affinity()

    assert stats.connected is True
    assert stats.sanotts_syntheses >= 1

    panel_html = render_panel(stats)
    assert "sanoTTS Local:" in panel_html
    assert "synths" in panel_html
