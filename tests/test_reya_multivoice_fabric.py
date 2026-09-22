# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Test Suite for Reya Universal Fabric & Multivoice Persona Interchange
=====================================================================
Verifies:
1. Voice interchange trigger detection across diverse conversational utterances.
2. Dynamic Knight persona switching and acoustic/timbre profiles.
3. Reya kinetic fabric action execution under strict cgroups v2 sandbox bounds (<350MB).
4. Runic router dispatch for //REYA_CHANNEL and its aliases.
5. Parity with Multivoice Router TypeScript profile registry.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import pytest

from control_plane.runes.runic_router import route_rune

CAMELOT_HOME = Path(__file__).resolve().parent.parent

# Dynamically import ReyaUniversalFabric
fabric_path = CAMELOT_HOME / "02_FORGE" / "assimilation" / "reya" / "reya_fabric_layer.py"
spec = importlib.util.spec_from_file_location("reya_fabric_layer", str(fabric_path))
assert spec is not None and spec.loader is not None
reya_fabric_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reya_fabric_mod
spec.loader.exec_module(reya_fabric_mod)

ReyaUniversalFabric = reya_fabric_mod.ReyaUniversalFabric
CANONICAL_KNIGHT_PERSONAS = reya_fabric_mod.CANONICAL_KNIGHT_PERSONAS


# ── 1. Voice Interchange Trigger Detection Tests ──────────────────────────────

@pytest.mark.parametrize(
    "utterance,expected_target",
    [
        ("Reya, switch to Merlin please", "merlin_omega"),
        ("switch to Sir Boris now", "sir_boris"),
        ("speak as Codex", "sir_codex"),
        ("channel Sir Lukas Müller", "sir_lukas"),
        ("talk to me as Arthur", "arthur_omega"),
        ("become Helios", "sir_helios"),
        ("switch persona to Anya", "anya_omega"),
        ("channel Lady Apis", "lady_apis"),
        ("speak as Gideon", "sir_gideon"),
        ("talk as Sonus", "sir_sonus"),
        ("reset to default persona", "reya_companion"),
        ("switch back to Reya please", "reya_companion"),
    ],
)
def test_voice_interchange_trigger_detection(utterance: str, expected_target: str):
    """Verify that spoken utterances accurately detect the intended Knight persona."""
    fabric = ReyaUniversalFabric()
    detected = fabric.detect_voice_interchange_trigger(utterance)
    assert detected == expected_target, f"Failed to detect {expected_target} from '{utterance}', got: {detected}"


def test_voice_interchange_ignores_unrelated_utterances():
    """Verify that non-switch utterances return None without false positives."""
    fabric = ReyaUniversalFabric()
    assert fabric.detect_voice_interchange_trigger("What is the current system load?") is None
    assert fabric.detect_voice_interchange_trigger("Click coordinates 540 by 960 on the phone") is None
    assert fabric.detect_voice_interchange_trigger("Hello world, play sound on speaker") is None


# ── 2. Persona Switching & Acoustic Profile Calibration ───────────────────────

def test_switch_knight_updates_persona_and_acoustic_profile():
    """Verify switching knight updates active persona, voice engine, and acoustics."""
    fabric = ReyaUniversalFabric()

    # Initial state is default Reya
    assert fabric.current_persona.knight_id == "reya_companion"

    # Switch to Sir Boris
    res = fabric.switch_knight("sir_boris")
    assert res["status"] == "KNIGHT_CHANNELED"
    assert res["active_knight_id"] == "sir_boris"
    assert res["display_name"] == "Sir Boris"
    assert "brutalist" in res["acoustic_profile"]["timbre"]
    assert res["voice_engine"] == "vibevoice_0.5b"
    assert fabric.current_persona.knight_id == "sir_boris"

    # Switch to Merlin Ω
    res_m = fabric.switch_knight("merlin_omega")
    assert res_m["active_knight_id"] == "merlin_omega"
    assert res_m["display_name"] == "Merlin Ω"
    assert res_m["acoustic_profile"]["pitch_offset"] == -1.5
    assert res_m["voice_engine"] == "kokoro_onnx"

    # Switch to Arthur Ω
    res_a = fabric.switch_knight("arthur_omega")
    assert res_a["active_knight_id"] == "arthur_omega"
    assert res_a["display_name"] == "King Arthur Ω"
    assert res_a["acoustic_profile"]["pitch_offset"] == -2.5

    # Switch back to Reya
    res_r = fabric.switch_knight("reya")
    assert res_r["active_knight_id"] == "reya_companion"
    assert res_r["voice_engine"] == "gemini_live"


def test_switch_knight_invalid_target_raises_value_error():
    """Verify switching to an unknown persona raises ValueError."""
    fabric = ReyaUniversalFabric()
    with pytest.raises(ValueError, match="Unknown Knight target"):
        fabric.switch_knight("lord_voldemort")


# ── 3. Fabric Kinetic Action Execution & Sandbox Boundaries ───────────────────

def test_fabric_action_execution_mobile_tap():
    """Verify phone coordinate injection action executes through Reya's kinetic fabric."""
    fabric = ReyaUniversalFabric()
    res = fabric.execute_fabric_action(
        "mobile_adb_tap",
        {"x": 480, "y": 800, "device_id": "vashawns-s26-ultra"},
    )
    assert res["status"] == "SUCCESS"
    assert res["action"] == "mobile_adb_tap"
    assert res["channeled_knight"] == "reya_companion"
    assert res["result"]["x"] == 480
    assert res["result"]["y"] == 800
    assert res["sandbox"]["cgroups_memory_max"] == "350M"
    assert res["sandbox"]["memory_ceiling_mb"] <= 350.0


def test_fabric_action_execution_under_channeled_knight():
    """Verify fabric action execution attributes to currently channeled knight."""
    fabric = ReyaUniversalFabric()
    fabric.switch_knight("sir_codex")

    res = fabric.execute_fabric_action(
        "speech_synthesize",
        {"text": "Refactoring module in Rust; proof verified."},
    )
    assert res["status"] == "SUCCESS"
    assert res["channeled_knight"] == "sir_codex"
    assert res["result"]["voice_engine"] == "kokoro_onnx"
    assert res["result"]["text_length"] > 0


def test_fabric_action_invalid_type_raises_value_error():
    """Verify unknown action type raises ValueError."""
    fabric = ReyaUniversalFabric()
    with pytest.raises(ValueError, match="Unsupported fabric action"):
        fabric.execute_fabric_action("unauthorized_nuke", {})


# ── 4. Runic Router Dispatch Tests ────────────────────────────────────────────

def test_runic_dispatch_reya_channel_direct_switch():
    """Verify //REYA_CHANNEL parses intent and switches knight persona."""
    result = route_rune("//REYA_CHANNEL switch to Sir Boris please", {})
    assert result.rune == "//REYA_CHANNEL"
    assert result.metadata["status"] == "REYA_CHANNEL_DISPATCHED"
    assert result.metadata["detected_trigger"] == "sir_boris"
    assert result.metadata["switch_result"]["active_knight_id"] == "sir_boris"


def test_runic_dispatch_reya_channel_aliases():
    """Verify //channel, //voice_interchange, and //reya_voice aliases work."""
    # 1. //channel
    res1 = route_rune("//channel channel Sir Lukas now", {})
    assert res1.rune == "//channel"
    assert res1.metadata["detected_trigger"] == "sir_lukas"
    assert res1.metadata["switch_result"]["active_knight_id"] == "sir_lukas"

    # 2. //voice_interchange
    res2 = route_rune("//voice_interchange speak as Arthur", {})
    assert res2.rune == "//voice_interchange"
    assert res2.metadata["detected_trigger"] == "arthur_omega"
    assert res2.metadata["switch_result"]["active_knight_id"] == "arthur_omega"

    # 3. //reya_voice
    res3 = route_rune("//reya_voice switch back to Reya", {})
    assert res3.rune == "//reya_voice"
    assert res3.metadata["detected_trigger"] == "reya_companion"
    assert res3.metadata["switch_result"]["active_knight_id"] == "reya_companion"


def test_runic_dispatch_with_action_context():
    """Verify //REYA_CHANNEL executes an underlying kinetic action when passed in context."""
    context = {
        "action": "nostr_event",
        "payload": {"kind": 1, "content": "Sovereign beacon emitted"},
    }
    result = route_rune("//REYA_CHANNEL become Helios", context)
    assert result.metadata["detected_trigger"] == "sir_helios"
    assert result.metadata["action_result"] is not None
    assert result.metadata["action_result"]["action"] == "nostr_event"
    assert result.metadata["action_result"]["channeled_knight"] == "sir_helios"


# ── 5. TypeScript Profile Registry Parity Test ────────────────────────────────

def test_multivoice_registry_typescript_parity():
    """Verify packages/multivoice-router/src/voice/voice-profile-registry.ts contains channeled profiles."""
    registry_ts = CAMELOT_HOME / "packages" / "multivoice-router" / "src" / "voice" / "voice-profile-registry.ts"
    assert registry_ts.exists(), "voice-profile-registry.ts must exist"
    content = registry_ts.read_text(encoding="utf-8")

    expected_tokens = [
        "reya_companion",
        "boris_architect",
        "codex_implementer",
        "helio_sentinel",
        "lukas_telemetry",
        "arthur_sovereign",
        "getReyaChanneledProfile",
        "listAllChanneledKnights",
    ]
    for token in expected_tokens:
        assert token in content, f"Missing token '{token}' in voice-profile-registry.ts"
