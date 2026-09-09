# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
Unit tests for Harness Emulator & Hermes Autonomous Execution Loop
===================================================================
Tests:
  1. Harness registry and profile configurations
  2. Model family inference & wire API deduction
  3. Tool schema transformations (OpenAI, Anthropic)
  4. Request formatting across harness modes (Codex, Claude-Code, Kimi-Code, DeepSeek-TUI)
  5. ToolRegistry and HermesExecutionLoop trajectory recording & skill evolution
  6. AutoRouterBridge endpoint resolution and multi-agent dispatch
  7. Runic router integration (normalize, parse, route for //HARNESS, //HERMES_LOOP, //EMULATE, aliases)
"""

import pytest

from control_plane import runic_router
from control_plane.runes.harness_emulator import (
    HARNESS_REGISTRY,
    AutoRouterBridge,
    HarnessID,
    HermesExecutionLoop,
    RequestFormatter,
    ToolRegistry,
    ToolTransformer,
    WireAPI,
    infer_harness_from_model,
    infer_wire_api,
)


@pytest.fixture
def router(monkeypatch, tmp_path):
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)
    return runic_router


# ---------------------------------------------------------------------------
# 1. Harness Registry & Profile Tests
# ---------------------------------------------------------------------------


def test_harness_registry_contains_assimilated_profiles():
    assert HarnessID.CODEX.value in HARNESS_REGISTRY
    assert HarnessID.CLAUDE_CODE.value in HARNESS_REGISTRY
    assert HarnessID.KIMI_CODE.value in HARNESS_REGISTRY
    assert HarnessID.DEEPSEEK_TUI.value in HARNESS_REGISTRY
    assert HarnessID.QWEN_CODE.value in HARNESS_REGISTRY
    assert HarnessID.SWE_AGENT.value in HARNESS_REGISTRY
    assert HarnessID.ANTIGRAVITY.value in HARNESS_REGISTRY
    assert HarnessID.HERMES.value in HARNESS_REGISTRY


def test_claude_code_profile_configuration():
    cfg = HARNESS_REGISTRY[HarnessID.CLAUDE_CODE.value]
    assert cfg.wire_api == WireAPI.MESSAGES
    assert cfg.thinking_budget == 4096
    assert cfg.prompt_cache_enabled is True
    assert "anthropic-beta" in cfg.custom_headers


def test_kimi_code_profile_configuration():
    cfg = HARNESS_REGISTRY[HarnessID.KIMI_CODE.value]
    assert cfg.wire_api == WireAPI.CHAT
    assert cfg.reasoning_effort == "high"
    assert cfg.prompt_cache_enabled is True


def test_deepseek_tui_profile_configuration():
    cfg = HARNESS_REGISTRY[HarnessID.DEEPSEEK_TUI.value]
    assert cfg.wire_api == WireAPI.CHAT
    assert "apply_patch" in cfg.supported_tools


# ---------------------------------------------------------------------------
# 2. Model Inference & Wire API Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model,provider,expected_harness",
    [
        ("claude-3-5-sonnet-20241022", None, HarnessID.CLAUDE_CODE.value),
        ("anthropic/claude-opus-4", "anthropic", HarnessID.CLAUDE_CODE.value),
        ("kimi-k3", "moonshot", HarnessID.KIMI_CODE.value),
        ("moonshot-v1-auto", None, HarnessID.KIMI_CODE.value),
        ("deepseek-chat", None, HarnessID.DEEPSEEK_TUI.value),
        ("deepseek-r1-distill", None, HarnessID.DEEPSEEK_TUI.value),
        ("qwen2.5-coder-32b", None, HarnessID.QWEN_CODE.value),
        ("hermes-3-llama-3.1-70b", "nous", HarnessID.HERMES.value),
        ("gpt-4o", "openai", HarnessID.CODEX.value),
        ("codex-davinci", None, HarnessID.CODEX.value),
        ("gemini-2.5-pro", None, HarnessID.ANTIGRAVITY.value),
        ("unknown-custom-model", None, HarnessID.MINIMAL.value),
    ],
)
def test_infer_harness_from_model(model, provider, expected_harness):
    assert infer_harness_from_model(model, provider) == expected_harness


def test_infer_wire_api():
    assert infer_wire_api(HarnessID.CLAUDE_CODE.value) == WireAPI.MESSAGES
    assert infer_wire_api(HarnessID.CODEX.value) == WireAPI.RESPONSES
    assert infer_wire_api(HarnessID.KIMI_CODE.value) == WireAPI.CHAT
    # Override
    assert infer_wire_api(HarnessID.CLAUDE_CODE.value, "chat") == WireAPI.CHAT


# ---------------------------------------------------------------------------
# 3. Tool Schema Transformation Tests
# ---------------------------------------------------------------------------


def test_tool_transformer_openai_and_anthropic():
    tools = [
        {
            "name": "edit_file",
            "description": "Edit file with patch",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        }
    ]

    anthropic_tools = ToolTransformer.transform_tools(tools, WireAPI.MESSAGES)
    assert len(anthropic_tools) == 1
    assert anthropic_tools[0]["name"] == "edit_file"
    assert "input_schema" in anthropic_tools[0]

    openai_tools = ToolTransformer.transform_tools(tools, WireAPI.CHAT)
    assert len(openai_tools) == 1
    assert openai_tools[0]["type"] == "function"
    assert openai_tools[0]["function"]["name"] == "edit_file"


# ---------------------------------------------------------------------------
# 4. Request Formatter Tests
# ---------------------------------------------------------------------------


def test_request_formatter_messages_wire_api():
    messages = [{"role": "user", "content": "Refactor auth handler."}]
    tools = [{"name": "read_file", "description": "read", "parameters": {}}]

    req = RequestFormatter.format_request(
        harness_id=HarnessID.CLAUDE_CODE.value,
        messages=messages,
        tools=tools,
        max_tokens=2048,
    )

    assert "system" in req
    assert "thinking" in req
    assert req["thinking"]["budget_tokens"] == 4096
    assert req["max_tokens"] == 2048
    assert len(req["messages"]) == 1
    assert req["messages"][0]["content"] == "Refactor auth handler."
    assert "tools" in req
    assert "input_schema" in req["tools"][0]


def test_request_formatter_chat_wire_api():
    messages = [{"role": "user", "content": "Analyze memory leaks."}]
    req = RequestFormatter.format_request(
        harness_id=HarnessID.KIMI_CODE.value,
        messages=messages,
    )

    assert "messages" in req
    assert req["messages"][0]["role"] == "system"
    assert req["messages"][1]["role"] == "user"
    assert req["reasoning_effort"] == "high"


# ---------------------------------------------------------------------------
# 5. ToolRegistry & Hermes Execution Loop Tests
# ---------------------------------------------------------------------------


def test_tool_registry_file_ops(tmp_path):
    registry = ToolRegistry(workspace_root=tmp_path)
    write_res = registry.execute("write_file", {"path": "test.txt", "content": "hello camelot"})
    assert "Successfully wrote" in write_res

    read_res = registry.execute("read_file", {"path": "test.txt"})
    assert read_res == "hello camelot"

    skill_res = registry.execute("create_skill", {"skill_name": "auth_flow", "description": "auth logic"})
    assert "[SKILL_PERSISTED]" in skill_res


def test_hermes_execution_loop_multi_turn(tmp_path):
    loop = HermesExecutionLoop(
        harness_id=HarnessID.HERMES.value,
        max_turns=5,
        workspace_root=tmp_path,
    )

    result = loop.run(objective="Inspect system configuration and report.")
    assert result.success is True
    assert result.turns_executed >= 2
    assert len(result.trajectory) >= 2
    assert result.trajectory[0].state == "ACT"
    assert result.trajectory[0].tool_name == "read_file"
    assert result.trajectory[-1].state == "CONCLUDE"


# ---------------------------------------------------------------------------
# 6. AutoRouterBridge Tests
# ---------------------------------------------------------------------------


def test_auto_router_bridge_routing():
    bridge = AutoRouterBridge()
    route = bridge.route_command(
        command_text="Execute autonomous scan",
        target_model="claude-3-5-sonnet",
        endpoint="ollama",
    )

    assert route["target_harness"] == HarnessID.CLAUDE_CODE.value
    assert route["wire_api"] == "messages"
    assert route["endpoint"] == "http://localhost:11434/v1"
    assert route["status"] == "READY_FOR_DISPATCH"


# ---------------------------------------------------------------------------
# 7. Runic Router Integration Tests
# ---------------------------------------------------------------------------


def test_normalize_harness_runes(router):
    assert router.normalize_rune("//harness") == "//HARNESS"
    assert router.normalize_rune("//hermes_loop") == "//HERMES_LOOP"
    assert router.normalize_rune("//emulate") == "//EMULATE"
    assert router.normalize_rune("$harness") == "//HARNESS"
    assert router.normalize_rune("$emulate") == "//EMULATE"
    assert router.normalize_rune("$hermes") == "//HERMES_LOOP"


def test_parse_harness_runes(router):
    assert router.parse_rune("//HARNESS --model=qwen2.5 task") == ("//HARNESS", "--model=qwen2.5 task")
    assert router.parse_rune("$hermes run audit") == ("//HERMES_LOOP", "run audit")
    assert router.parse_rune("//EMULATE claude-code") == ("//EMULATE", "claude-code")


def test_route_harness_rune(router):
    res = router.route_rune("//HARNESS", "--harness=kimi-code optimize query")
    assert res.rune == "//HARNESS"
    assert res.knight == "sir_codex"
    assert res.queued is True
    assert res.metadata["harness_id"] == "kimi-code"
    assert res.metadata["route_info"]["target_harness"] == "kimi-code"


def test_route_hermes_loop_rune(router):
    res = router.route_rune("//HERMES_LOOP", "--turns=3 verify build")
    assert res.rune == "//HERMES_LOOP"
    assert res.knight == "hermes_prime"
    assert res.queued is True
    assert "execution_result" in res.metadata
    assert res.metadata["execution_result"]["success"] is True
