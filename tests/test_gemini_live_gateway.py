# SPDX-License-Identifier: MIT
import asyncio
from unittest.mock import patch
from control_plane.dispatch.gemini_live_gateway import (
    KNIGHT_VOICE_MAP,
    GeminiLiveRelay
)

def test_knight_voice_mapping():
    assert "MERLIN_OMEGA" in KNIGHT_VOICE_MAP
    assert "SIR_BORIS" in KNIGHT_VOICE_MAP
    assert "SIR_HEIMDALL" in KNIGHT_VOICE_MAP
    assert "LADY_LAKISHA" in KNIGHT_VOICE_MAP

    assert KNIGHT_VOICE_MAP["MERLIN_OMEGA"]["voice"] == "Fenrir"
    assert KNIGHT_VOICE_MAP["SIR_BORIS"]["voice"] == "Charon"
    assert KNIGHT_VOICE_MAP["SIR_HEIMDALL"]["voice"] == "Puck"
    assert KNIGHT_VOICE_MAP["LADY_LAKISHA"]["voice"] == "Aoede"

def test_gemini_live_relay_init():
    relay = GeminiLiveRelay("SIR_BORIS")
    assert relay.knight_id == "SIR_BORIS"
    assert relay.knight_config["voice"] == "Charon"

def test_gemini_live_relay_mock_connect():
    relay = GeminiLiveRelay("MERLIN_OMEGA")
    with patch.dict('os.environ', {}, clear=True):
        ws = asyncio.run(relay.connect_gemini_live())
        assert ws is None
