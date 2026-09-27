# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot-OS — Test Suite for TypeSafe AI Jev (System 1) Integration
r"""
Tests for TypeSafe AI Jev (System 1) Non-Autoregressive Decision & Router Integration.
Enforces:
1. Environment Key Resolution & Masking (Sir Ghost Airgap Invariant)
2. Fast Structured Decision & Parallel Question Sampling
3. Low-Latency Route Classification & Candidate Selection
4. High-Integrity Risk Triage & HITL Escalation Rules
5. OmniRouteBridge System 1 Strategy Dispatch
6. Omniroute Policies Lane Selection & Provider Failover Chain
7. Knight Engine Router System 1 Grade Configuration
8. Runic Router //SYSTEM1 and //JEV Dispatch
9. Air-Gap Secret Sanitization Invariant
"""

import importlib
import json
import os
import pytest


@pytest.fixture
def jev_module():
    return importlib.import_module("02_FORGE.assimilation.omniroute.typesafe_jev_client")


@pytest.fixture
def omniroute_module():
    return importlib.import_module("02_FORGE.assimilation.omniroute.omniroute_bridge")


@pytest.fixture
def bitrouter_module():
    return importlib.import_module("02_FORGE.assimilation.bitrouter.bitrouter_guardrails")


class TestTypeSafeJevSystem1:
    """Core verification test suite for TypeSafe Jev System 1 model."""

    def test_env_key_resolution_and_masking(self, jev_module):
        client = jev_module.TypeSafeJevClient()
        assert client.has_api_key is True, "TypeSafe Jev client should resolve API key from environment"
        masked = client.mask_key()
        assert masked.startswith("apikey") or masked.startswith("***")
        # Ensure full key is masked, not exposed in plain text
        raw_key = client._api_key
        assert masked != raw_key
        assert "..." in masked

    def test_decide_parallel_questions(self, jev_module):
        client = jev_module.TypeSafeJevClient()
        state = "Scaffold a new Rust hyper server module with high performance"
        questions = {
            "target_language": {"type": "choice", "options": ["rust", "python", "typescript", "go"]},
            "complexity_score": {"type": "score", "min": 0, "max": 100},
            "requires_hitl": {"type": "boolean"},
        }
        res = client.decide(state, questions)
        assert res.model is not None
        assert "target_language" in res.decisions
        assert res.decisions["target_language"] == "rust"
        assert "complexity_score" in res.decisions
        assert isinstance(res.decisions["complexity_score"], (int, float))
        assert "requires_hitl" in res.decisions
        assert res.decisions["requires_hitl"] is False
        assert res.status in ("SUCCESS", "FALLBACK_HEURISTIC")
        assert res.latency_ms >= 0.0

    def test_classify_route(self, jev_module):
        client = jev_module.TypeSafeJevClient()
        prompt = "Scaffold code templates for digital factory"
        candidates = ["forge", "codex", "sentinel", "oracle"]
        result = client.classify_route(prompt, candidates)
        assert result["selected_route"] in candidates
        assert "confidence" in result
        assert result["status"] in ("SUCCESS", "FALLBACK_HEURISTIC")

    def test_triage_risk_readonly_vs_destructive(self, jev_module):
        client = jev_module.TypeSafeJevClient()

        # Read-only task
        ro_task = "List active directories and inspect system logs"
        ro_res = client.triage_risk(ro_task)
        assert ro_res["risk_level"] in ("R0_TRIVIAL", "R1_READONLY")
        assert ro_res["requires_hitl"] is False

        # Destructive task
        crit_task = "rm -rf / --no-preserve-root and wipe disk partitions"
        crit_res = client.triage_risk(crit_task)
        assert crit_res["risk_level"] in ("R3_PRIVILEGED", "R4_CRITICAL")
        assert crit_res["requires_hitl"] is True

    def test_omniroute_bridge_system1_strategy(self, omniroute_module):
        bridge = omniroute_module.get_omniroute_bridge()
        prompt = "Reflexive intent check: analyze incoming payload"
        resp = bridge.route_request(prompt, strategy="system1/jev")
        assert resp.strategy_used == "system1/jev"
        assert "typesafe" in resp.provider.lower()
        assert resp.status in ("SUCCESS", "FALLBACK_HEURISTIC")
        parsed = json.loads(resp.content)
        assert "decisions" in parsed
        assert "system1_model" in parsed

    def test_omniroute_bridge_route_system1_decision(self, omniroute_module):
        bridge = omniroute_module.get_omniroute_bridge()
        state = "Compile kernel binary"
        questions = {
            "lane": {"type": "choice", "options": ["kinetic_forge", "system2_dag", "airgap"]},
        }
        res = bridge.route_system1_decision(state, questions)
        assert "decisions" in res
        assert "lane" in res["decisions"]

    def test_omniroute_policies_lane_selection(self):
        from control_plane.dispatch.omniroute_policies import (
            LANE_TYPESAFE_JEV_SYSTEM1,
            select_lane,
            resolve_fcc_failover_chain,
            get_fcc_provider_policy,
        )

        test_inputs = [
            "Execute fast triage using typesafe model",
            "Route prompt to jev-latest for non-autoregressive decision",
            "Evaluate s1_reflex action loop",
            "Perform system1 fast decision",
        ]
        for text in test_inputs:
            signal = select_lane(text)
            assert signal.lane == LANE_TYPESAFE_JEV_SYSTEM1, f"Failed for text: {text}"
            assert signal.matched_keyword != ""

        # Failover chain includes typesafe_jev
        chain = resolve_fcc_failover_chain("typesafe system1 decision")
        assert chain[0] == "typesafe_jev"

        # Provider policy includes zero downtime
        policy = get_fcc_provider_policy("typesafe jev fast routing")
        assert policy["lane"] == LANE_TYPESAFE_JEV_SYSTEM1
        assert policy["zero_downtime_enabled"] is True

    def test_knight_engine_router_system1_config(self):
        from control_plane.dispatch.knight_engine_router import (
            get_knight_engine,
            dispatch_knight_inference,
            dispatch_system1_decision,
        )

        # Knights have system1 config
        for knight in ["SIR_GHOST", "SIR_SENTINEL", "SIR_HELIOS", "MERLIN_OMEGA"]:
            cfg = get_knight_engine(knight)
            assert "system1" in cfg
            assert "typesafe" in cfg["system1"]["primary"]

        inference = dispatch_knight_inference("SIR_GHOST")
        assert "system1_model" in inference
        assert "typesafe" in inference["system1_model"]

        # Test dispatch_system1_decision
        s1_res = dispatch_system1_decision(
            "SIR_GHOST",
            "inspect privacy buffer",
            {"safe": {"type": "boolean"}},
        )
        assert s1_res["knight"] == "SIR_GHOST"
        assert "decisions" in s1_res

    def test_runic_router_system1_command(self):
        from control_plane.runes.runic_router import route_rune, RUNIC_COMMANDS, _handle_system1

        assert "//SYSTEM1" in RUNIC_COMMANDS
        assert "//JEV" in RUNIC_COMMANDS
        assert RUNIC_COMMANDS["//SYSTEM1"]["knight"] == "sir_ghost"

        # Route rune dispatch
        rune_res = route_rune("//SYSTEM1 rapid security scan", {})
        assert rune_res.rune == "//SYSTEM1"
        assert rune_res.knight == "sir_ghost"

        # Direct handler execution
        handler_res = _handle_system1("fast triage check", {})
        assert handler_res["action"] == "system1_decision"
        assert handler_res["status"] in ("SUCCESS", "FALLBACK_HEURISTIC")
        assert "decisions" in handler_res

    def test_bitrouter_guardrails_reflex_step(self, bitrouter_module):
        engine = bitrouter_module.get_bitrouter_engine()
        res = engine.evaluate_reflex_step("loop-test-1", "read local source file")
        assert res["loop_id"] == "loop-test-1"
        assert "decisions" in res
        assert "can_execute_reflexively" in res["decisions"]

    def test_airgap_secret_isolation_invariant(self):
        """SIR_GHOST Invariant: Ensure the actual raw key is NEVER present in tracked template files."""
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        example_path = os.path.join(root_dir, ".env.example")
        template_path = os.path.join(root_dir, ".env.template")

        # Check .env.example
        if os.path.exists(example_path):
            with open(example_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "apikey_231cd309ea776e14cb2af814d1e986686ea" not in content
                assert "TYPESAFE_API_KEY=" in content

        # Check .env.template
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "apikey_231cd309ea776e14cb2af814d1e986686ea" not in content
                assert "TYPESAFE_API_KEY=" in content
