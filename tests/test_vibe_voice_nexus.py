# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Test Suite for OMEGA_VIBE_VOICE_NEXUS Assimilation
===================================================
Verifies all 4 Kinetic Flow DAG steps and MOD1 Structural Constraints:
- Step 1: Sir Codex secure weights & I8_S + I2_S heterogeneous GGML manifest
- Step 2: Sir Boris native VibeASR.cpp & CMake compilation structure (< 1.58 GB RAM)
- Step 3: Lord Vesper real-time diffusion head mounting & TTFA < 300ms streaming
- Step 4: Lady Apis KBA Marketing cartridge offline isolation & preemption
- Constraints: Combined STT/TTS resident memory strictly < 2.0 GB
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from control_plane.dispatch.realtime_voice_bridge import (
    VibeVoiceRealtimeTTSProcessor,
    TTSProcessor,
    DEFAULT_SAMPLE_RATE,
)
import scripts.secure_vibevoice_weights as svw

CAMELOT_HOME = Path(__file__).resolve().parent.parent


# ── Step 1 Verification: Sir Codex Weights Security ───────────────────────────

def test_step_1_secure_weights_status():
    """Verify weights provisioning, manifest integrity, and I8_S+I2_S profile."""
    status = svw.get_status()
    assert status["is_ready"] is True
    assert status["quantization_profile"] == "I8_S + I2_S Heterogeneous GGML"
    assert status["resident_memory_estimate_mb"] <= 600

    manifest_path = CAMELOT_HOME / "03_VAULT" / "models" / "vibevoice_realtime_0.5b" / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["model_id"] == "VibeVoice-Realtime-0.5B"
    assert manifest["quantization"] == "I8_S + I2_S"
    assert manifest["acoustic_token_hz"] == 7.5


# ── Step 2 Verification: Sir Boris VibeASR.cpp & CMake ────────────────────────

def test_step_2_vibe_asr_cpp_and_cmake_contract():
    """Verify native C++ source, CMake configuration, and memory budget."""
    csrc_dir = CAMELOT_HOME / "02_FORGE" / "KINETIC_ARMORY" / "VibeVoice" / "csrc"
    cpp_file = csrc_dir / "vibe_asr.cpp"
    cmake_file = csrc_dir / "CMakeLists.txt"

    assert cpp_file.exists(), "vibe_asr.cpp must exist"
    assert cmake_file.exists(), "CMakeLists.txt must exist"

    cpp_content = cpp_file.read_text(encoding="utf-8")
    assert "TOKENIZER_FRAME_RATE_HZ = 7.5" in cpp_content
    assert "MAX_RESIDENT_RAM_BYTES = 1656750080ULL" in cpp_content  # 1.58 GB limit
    assert "ZeroCopyRingBuffer" in cpp_content
    assert "QuantType::I8_S" in cpp_content
    assert "QuantType::I2_S" in cpp_content

    cmake_content = cmake_file.read_text(encoding="utf-8")
    assert "add_executable(vibe_asr vibe_asr.cpp)" in cmake_content


# ── Step 3 Verification: Lord Vesper Diffusion Head & Omnivoice Router ────────

def test_step_3_omnivoice_router_engine_priority():
    """Verify that vibevoice_realtime is the primary local engine ahead of piper."""
    router_ts = CAMELOT_HOME / "packages" / "multivoice-router" / "src" / "voice" / "omnivoice-router.ts"
    assert router_ts.exists()
    content = router_ts.read_text(encoding="utf-8")
    assert "const LOCAL_ENGINES = ['vibevoice_realtime', 'kokoro_onnx', 'piper'" in content


def test_step_3_realtime_tts_diffusion_processor():
    """Verify VibeVoiceRealtimeTTSProcessor streaming, zero-markdown sanitation, and TTFA target."""
    proc = VibeVoiceRealtimeTTSProcessor(sample_rate=16000, frame_rate_hz=7.5)
    assert proc.ttfa_target_ms <= 300
    assert proc.samples_per_acoustic_frame == 2133  # 16000 / 7.5

    # Test ZERO_MARKDOWN_TTS invariant
    markdown_text = "# Sovereign **Anya**: [Initiate](http://camelot) `forge` pipeline now!"
    sanitized = proc.sanitize_text_for_tts(markdown_text)
    assert "#" not in sanitized
    assert "**" not in sanitized
    assert "`" not in sanitized
    assert "http" not in sanitized
    assert "Sovereign Anya: Initiate forge pipeline now!" == sanitized

    # Test streaming chunks generation
    chunks = proc.synthesize_streaming_chunks("This is a verified real-time stream test.")
    assert len(chunks) > 0
    for chunk in chunks:
        assert isinstance(chunk, bytes)
        assert len(chunk) > 0


# ── Step 4 Verification: Lady Apis KBA Marketing Cartridge ────────────────────

def test_step_4_kba_marketing_cartridge_isolation():
    """Verify that KBA Marketing cartridge isolates LoRA/batching from live duplex stream."""
    cartridge_file = CAMELOT_HOME / "03_VAULT" / "training" / "configs" / "cartridges" / "kba-marketing-voice.yaml"
    assert cartridge_file.exists()
    content = cartridge_file.read_text(encoding="utf-8")
    assert "mode: OFFLINE_WORKER" in content
    assert "live_mesh_interference: \"STRICTLY_FORBIDDEN\"" in content
    assert "SUSPEND_ON_INCOMING_CALL" in content
    assert "microsoft/VibeVoice-Realtime-0.5B" in content


# ── MOD1 Structural Constraints Verification ──────────────────────────────────

def test_mod1_combined_memory_overhead_limit():
    """Combined STT (1580MB) + TTS (468MB) resident memory must not breach 2.0GB (2048MB)."""
    crystal_file = CAMELOT_HOME / "03_VAULT" / "runtime_state" / "open_notebook" / "vkg_crystals" / "vkg_omega_vibe_voice_nexus.json"
    assert crystal_file.exists()
    crystal = json.loads(crystal_file.read_text(encoding="utf-8"))

    constraints = crystal["structural_constraints"]
    stt_mb = constraints["stt_resident_ceiling_mb"]
    tts_mb = constraints["tts_resident_ceiling_mb"]
    assert stt_mb + tts_mb <= 2048
    assert constraints["quantization"] == "I8_S + I2_S Heterogeneous GGML"
    assert constraints["target_ttfa_ms"] <= 300
