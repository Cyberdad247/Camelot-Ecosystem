# SPDX-License-Identifier: MIT
from control_plane.dispatch.knight_engine_router import (
    KNIGHT_ENGINE_MAP,
    get_knight_engine,
    dispatch_knight_inference
)

def test_knight_engine_mappings():
    assert "MERLIN_OMEGA" in KNIGHT_ENGINE_MAP
    assert "SIR_HEIMDALL" in KNIGHT_ENGINE_MAP
    assert "SIR_BORIS" in KNIGHT_ENGINE_MAP
    assert "SIR_FORGE" in KNIGHT_ENGINE_MAP
    assert "HERMES_PRIME" in KNIGHT_ENGINE_MAP
    assert "LADY_LAKISHA" in KNIGHT_ENGINE_MAP

    merlin = get_knight_engine("MERLIN_OMEGA")
    assert merlin["grade"] == "FRONTIER_TIER_1"
    assert merlin["llm"]["route_policy"] == "FREE_FRONTIER_FIRST"
    assert merlin["tts"]["voice_id"] == "merlin-arcane-sage"

    lakisha = get_knight_engine("LADY_LAKISHA")
    assert lakisha["grade"] == "REALTIME_S2S_ENGINE"
    assert lakisha["tts"]["voice_id"] == "lakisha-luxury-brutalism"

def test_dispatch_knight_inference():
    res = dispatch_knight_inference("SIR_BORIS")
    assert res["knight"] == "SIR_BORIS"
    assert res["status"] == "ROUTED_TO_FRONTIER_MODEL"
    assert res["tts_voice"] == "boris-command-direct"
