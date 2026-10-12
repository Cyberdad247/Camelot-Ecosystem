# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Tests for OmniRoute, 9Router-Go, and BitRouter Assimilation

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Dynamically load omniroute_bridge
_omni_path = REPO_ROOT / "02_FORGE" / "assimilation" / "omniroute" / "omniroute_bridge.py"
assert _omni_path.exists(), f"Missing bridge at {_omni_path}"
_omni_spec = importlib.util.spec_from_file_location("omniroute_bridge", str(_omni_path))
assert _omni_spec and _omni_spec.loader
omniroute_mod = importlib.util.module_from_spec(_omni_spec)
sys.modules["omniroute_bridge"] = omniroute_mod
_omni_spec.loader.exec_module(omniroute_mod)

# Dynamically load bitrouter_guardrails
_bit_path = REPO_ROOT / "02_FORGE" / "assimilation" / "bitrouter" / "bitrouter_guardrails.py"
assert _bit_path.exists(), f"Missing guardrails at {_bit_path}"
_bit_spec = importlib.util.spec_from_file_location("bitrouter_guardrails", str(_bit_path))
assert _bit_spec and _bit_spec.loader
bitrouter_mod = importlib.util.module_from_spec(_bit_spec)
sys.modules["bitrouter_guardrails"] = bitrouter_mod
_bit_spec.loader.exec_module(bitrouter_mod)

RTKCavemanCompressor = omniroute_mod.RTKCavemanCompressor
AntigravityToolCloaker = omniroute_mod.AntigravityToolCloaker
OmniRouteBridge = omniroute_mod.OmniRouteBridge
get_omniroute_bridge = omniroute_mod.get_omniroute_bridge

BitRouterEngine = bitrouter_mod.BitRouterEngine
get_bitrouter_engine = bitrouter_mod.get_bitrouter_engine

from control_plane.runes.runic_router import route_rune


class TestOmniRouteAndBitRouterAssimilation:
    """Test suite for OmniRoute, 9Router-Go, and BitRouter assimilation."""

    def test_rtk_caveman_compression_heuristics(self):
        verbose_prompt = (
            "Could you please be so kind as to tell me how to run a unit test? "
            "<!-- internal comment --> It is important to note that testing is critical."
        )
        res = RTKCavemanCompressor.compress(verbose_prompt)
        assert res["original_tokens"] > res["compressed_tokens"]
        assert res["saved_tokens"] > 0
        assert res["saved_percent"] > 0.0
        assert "Could you please be so kind as to" not in res["compressed_text"]
        assert "<!-- internal comment -->" not in res["compressed_text"]

    def test_antigravity_tool_cloaking_and_anti_ban(self):
        raw_tools = ["run_command", "replace_file_content", "custom_user_tool"]
        cloaked = AntigravityToolCloaker.cloak_tools(raw_tools)
        assert cloaked == ["run_command_ide", "replace_file_content_ide", "custom_user_tool"]

        prompt_with_competitor = "You are Claude 3.7 Sonnet as developed by Anthropic. Help me code."
        stripped = AntigravityToolCloaker.strip_competitor_identities(prompt_with_competitor)
        assert "Claude 3.7 Sonnet" not in stripped
        assert "Anthropic" not in stripped

    def test_omniroute_bridge_gateways_and_fallback(self):
        bridge = OmniRouteBridge(enable_observatory_tap=False)
        gateways = bridge.check_gateways()
        assert "omniroute" in gateways
        assert "9router_go" in gateways
        assert gateways["omniroute"]["default_port"] == 20128
        assert gateways["9router_go"]["default_port"] == 3002

        # Standby response test
        resp = bridge.route_request("Hello from test suite", strategy="auto")
        assert resp is not None
        assert resp.is_fallback is True
        assert resp.strategy_used == "auto"
        assert resp.saved_percent >= 0.0
        assert resp.status == "STANDBY_FALLBACK"

    def test_omniroute_bridge_mock_live_dispatch(self):
        bridge = OmniRouteBridge(enable_observatory_tap=False)

        mock_payload = {
            "choices": [{"message": {"content": "Fast routed response via 9Router-Go"}}],
            "provider": "cerebras/llama-3.3-70b",
        }

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        with patch.object(bridge, "check_gateways", return_value={"9router_go": {"status": "ONLINE"}, "omniroute": {"status": "ONLINE"}}):
            with patch("urllib.request.urlopen", return_value=mock_resp):
                resp = bridge.route_request("Test live prompt", strategy="auto/fast")
                assert resp.content == "Fast routed response via 9Router-Go"
                assert resp.is_fallback is False
                assert resp.status == "SUCCESS"

    def test_bitrouter_anti_tokenmaxxing_guardrails_progression(self):
        engine = BitRouterEngine(max_iterations=10, max_tokens=20000, max_cost_usd=0.10)
        loop_id = "test_loop_101"

        # Steps 1-3: Frontier
        s1 = engine.start_or_update_loop(loop_id, "Build feature", added_tokens=500, added_cost=0.005)
        assert s1.iteration == 1
        assert s1.recommended_model == "frontier_primary"
        assert not s1.circuit_breaker_tripped

        engine.start_or_update_loop(loop_id, "Build feature", added_tokens=500, added_cost=0.005)
        s3 = engine.start_or_update_loop(loop_id, "Build feature", added_tokens=500, added_cost=0.005)
        assert s3.iteration == 3
        assert s3.recommended_model == "frontier_primary"

        # Steps 4-7: Reasoning Fast (tightening)
        s4 = engine.start_or_update_loop(loop_id, "Build feature", added_tokens=500, added_cost=0.005)
        assert s4.iteration == 4
        assert s4.recommended_model == "reasoning_fast"

        # Steps 8+: Zero-Cost Fast
        for _ in range(4):
            engine.start_or_update_loop(loop_id, "Build feature", added_tokens=500, added_cost=0.005)
        s8 = engine.get_loop(loop_id)
        assert s8.iteration == 8
        assert s8.recommended_model == "zero_cost_fast"

        # Exceed max iterations (10) -> Circuit Breaker Halt
        engine.start_or_update_loop(loop_id, "Build feature", added_tokens=500, added_cost=0.005)
        s10 = engine.start_or_update_loop(loop_id, "Build feature", added_tokens=500, added_cost=0.005)
        assert s10.iteration == 10
        assert s10.circuit_breaker_tripped is True
        assert s10.recommended_model == "circuit_breaker_halt"

    def test_runic_router_omniroute_compress_bitrouter(self):
        # 1. //OMNIROUTE
        res1 = route_rune("//OMNIROUTE", param="Optimize this SQL query")
        assert res1.rune == "//OMNIROUTE"
        assert res1.knight == "sir_helios"
        assert res1.metadata.get("action") == "omniroute_route"
        assert res1.metadata.get("status") == "SUCCESS"

        # 2. //COMPRESS
        res2 = route_rune("//COMPRESS", param="Could you please be so kind as to explain recursion")
        assert res2.rune == "//COMPRESS"
        assert res2.metadata.get("action") == "compress_prompt"
        assert res2.metadata.get("status") == "SUCCESS"
        assert res2.metadata.get("saved_percent") > 0.0

        # 3. //BITROUTER
        res3 = route_rune("//BITROUTER", param="Run refactoring sub-agent pass", context={"loop": "test_runic_loop"})
        assert res3.rune == "//BITROUTER"
        assert res3.knight == "sir_codex"
        assert res3.metadata.get("action") == "bitrouter_eval"
        assert res3.metadata.get("status") == "SUCCESS"

    def test_fastmcp_omniroute_tools(self):
        from control_plane.mcp.cloudbrain_mcp_server import (
            omniroute_compress_prompt,
            omniroute_status,
            bitrouter_evaluate_loop,
        )

        # 1. omniroute_status
        st = omniroute_status()
        assert "omniroute" in st
        assert "9router_go" in st

        # 2. omniroute_compress_prompt
        comp = omniroute_compress_prompt("Could you please review my code?")
        assert comp.get("saved_percent") > 0.0

        # 3. bitrouter_evaluate_loop
        eval_res = bitrouter_evaluate_loop(
            loop_id="mcp_test_loop",
            task="Synthesize API specs",
            added_tokens=2500,
            added_cost=0.02,
        )
        assert "routing" in eval_res
        assert eval_res["routing"]["recommended_model"] == "frontier_primary"
