# SPDX-License-Identifier: MIT

"""tests/test_aurora_adapter.py — Unit tests for Aurora Token Pooling and Tool-Call Emulation.

Verifies:
1. Aurora Token Pooling & Round-Robin Rotation across Account Types (noauth, free, puid).
2. Session Health Checks & Automatic Token Renewal of Expired Accounts.
3. Temporary Bearer Token Registration & Fingerprint Profile Generation.
4. JWT Claims Extraction (ChatGPT Account ID, User ID, Plan Type).
5. Simulated <tool_call> Instruction and Prompt Generation with Schema Rendering.
6. Streaming <tool_call> Parser with Tag Normalization, Markdown Fence Stripping, and Delta Emission.
7. Robust JSON Repair (Windows Backslash & Balanced Braces).
8. Text Recovery and Historical Tool-Call Serialization for Round-Trip Multi-Turn Conversation.
"""

from __future__ import annotations

import json

from control_plane.core.ocx_bridge import (
    AuroraAccount,
    AuroraAccountStatus,
    AuroraAccountType,
    AuroraPool,
    AuroraToolCallParser,
    build_aurora_final_nudge,
    build_aurora_tool_instructions,
    extract_chatgpt_account_id,
    extract_chatgpt_plan_type,
    extract_chatgpt_user_id,
    fix_aurora_backslashes,
    recover_aurora_tool_calls_from_text,
    robust_aurora_json,
    serialize_aurora_tool_calls_for_history,
)


# ── 1. Aurora Account Pool & Rotation ────────────────────────────────────────

def test_aurora_account_pool_round_robin():
    """Verify round-robin acquisition across accounts of the same type."""
    a1 = AuroraAccount(id="acct-1", type=AuroraAccountType.FREE, token="token-1", status=AuroraAccountStatus.ACTIVE)
    a2 = AuroraAccount(id="acct-2", type=AuroraAccountType.FREE, token="token-2", status=AuroraAccountStatus.ACTIVE)
    a3 = AuroraAccount(id="acct-3", type=AuroraAccountType.PUID, token="token-3", status=AuroraAccountStatus.ACTIVE)

    pool = AuroraPool([a1, a2, a3])

    # First acquire -> acct-1
    res1 = pool.acquire(AuroraAccountType.FREE)
    assert res1 is not None
    assert res1.id == "acct-1"
    assert res1.total_calls == 1

    # Second acquire -> acct-2
    res2 = pool.acquire(AuroraAccountType.FREE)
    assert res2 is not None
    assert res2.id == "acct-2"
    assert res2.total_calls == 1

    # Third acquire -> wrap around to acct-1
    res3 = pool.acquire(AuroraAccountType.FREE)
    assert res3 is not None
    assert res3.id == "acct-1"
    assert res3.total_calls == 2

    # PUID pool is separate
    puid_res = pool.acquire(AuroraAccountType.PUID)
    assert puid_res is not None
    assert puid_res.id == "acct-3"


def test_aurora_pool_health_check_and_renewal():
    """Verify failed accounts are marked expired and renewed via health check callback."""
    a1 = AuroraAccount(id="acct-1", type=AuroraAccountType.FREE, token="token-1", status=AuroraAccountStatus.ACTIVE)
    pool = AuroraPool([a1])

    # Report failure
    assert pool.report_failure(a1) is True
    assert a1.status == AuroraAccountStatus.EXPIRED
    assert a1.failed_calls == 1

    # Pool acquire should now return None
    assert pool.acquire(AuroraAccountType.FREE) is None

    # Health check renewal callback
    def renew_fn(acct: AuroraAccount) -> bool:
        return acct.id == "acct-1"

    renewed_count = pool.run_health_check(renew_fn)
    assert renewed_count == 1
    assert a1.status == AuroraAccountStatus.ACTIVE

    # Acquire should succeed now
    assert pool.acquire(AuroraAccountType.FREE) is not None


def test_aurora_temp_account_registration():
    """Verify temporary bearer tokens get registered with browser fingerprints."""
    pool = AuroraPool()
    temp_token = "eyJhbGciOiJSUzI1NiJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsiY2hhdGdwdF9hY2NvdW50X2lkIjoiYWNjdF85OTkifSwiY2hhdGdwdF9wbGFuX3R5cGUiOiJwcm8ifQ.sig"

    temp_acct = pool.get_or_create_temp_account(
        token=temp_token,
        user_agent="CustomAgent/1.0",
        proxy_url="http://127.0.0.1:8080",
    )
    assert temp_acct.is_temporary is True
    assert temp_acct.chatgpt_account_id == "acct_999"
    assert temp_acct.proxy == "http://127.0.0.1:8080"
    assert temp_acct.fingerprint.user_agent == "CustomAgent/1.0"
    assert temp_acct.fingerprint.tls_profile_name == "chrome_146"

    # Re-requesting same token returns existing instance
    cached_acct = pool.get_or_create_temp_account(token=temp_token)
    assert cached_acct.id == temp_acct.id


# ── 2. JWT Claims Extraction ─────────────────────────────────────────────────

def test_jwt_claims_extraction():
    """Verify parsing and claims extraction without signature verification."""
    # Header: {"alg":"RS256"}, Payload: {"https://api.openai.com/auth":{"chatgpt_account_id":"acc_123","chatgpt_user_id":"user_456"},"chatgpt_plan_type":"team"}
    dummy_jwt = (
        "eyJhbGciOiJSUzI1NiJ9."
        "eyJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsiY2hhdGdwdF9hY2NvdW50X2lkIjoiYWNjXzEyMyIsImNoYXRncHRfdXNlcl9pZCI6InVzZXJfNDU2In0sImNoYXRncHRfcGxhbl90eXBlIjoidGVhbSJ9."
        "dummy_signature"
    )
    assert extract_chatgpt_account_id(dummy_jwt) == "acc_123"
    assert extract_chatgpt_user_id(dummy_jwt) == "user_456"
    assert extract_chatgpt_plan_type(dummy_jwt) == "team"

    # Invalid token handling
    assert extract_chatgpt_account_id("not-a-jwt") == ""
    assert extract_chatgpt_plan_type("invalid.token") == ""


# ── 3. Tool-Call Instruction and Prompt Generation ───────────────────────────

def test_build_aurora_tool_instructions():
    """Verify instruction prompt construction from OpenAPI tool schemas."""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": "Run shell command on host",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "CLI command"},
                        "cwd": {"type": "string", "description": "Working directory"},
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read file contents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                    },
                    "required": ["path"],
                },
            },
        },
    ]

    # Free tool choice
    instructions = build_aurora_tool_instructions(tools)
    assert "# TOOLS AVAILABLE" in instructions
    assert "- execute_command: Run shell command on host" in instructions
    assert "* command (string, required): CLI command" in instructions
    assert "* cwd (string, optional): Working directory" in instructions
    assert "- read_file: Read file contents" in instructions
    assert "<tool_call>" in instructions
    assert "</tool_call>" in instructions

    # Forced tool choice
    forced_choice = {"type": "function", "function": {"name": "execute_command"}}
    forced_instructions = build_aurora_tool_instructions(tools, tool_choice=forced_choice)
    assert 'CRITICAL: You MUST call the tool "execute_command"' in forced_instructions

    # Disabled tool choice
    disabled_instructions = build_aurora_tool_instructions(tools, tool_choice="none")
    assert "CRITICAL: The user has DISABLED tool calling" in disabled_instructions


def test_build_aurora_final_nudge():
    """Verify final nudge prompts generated based on preceding message role."""
    tools = [{"type": "function", "function": {"name": "test_tool"}}]

    # After user message
    user_nudge = build_aurora_final_nudge(tools, [{"role": "user", "content": "hello"}])
    assert "You are an autonomous coding agent" in user_nudge
    assert "Begin your response immediately with '<tool_call>'" in user_nudge

    # After tool result
    tool_nudge = build_aurora_final_nudge(
        tools, [{"role": "user", "content": "run"}, {"role": "tool", "content": "output"}]
    )
    assert "The 'Tool (...)' block above is the REAL output" in tool_nudge


# ── 4. Streaming Tool-Call Parser & Tag Normalization ─────────────────────────

def test_aurora_tool_call_parser_streaming():
    """Verify streaming tag detection, tag normalization, and delta text separation."""
    parser = AuroraToolCallParser()

    # Feed chunk 1: text preceding tool call + start tag
    text1, calls1 = parser.feed("Analyzing system status...\n<tool_call>\n{\"name\": \"run_command\"")
    assert text1 == "Analyzing system status...\n"
    assert len(calls1) == 0

    # Feed chunk 2: JSON arguments + closing tag + post text
    text2, calls2 = parser.feed(', "arguments": {"command": "git status"}}\n</tool_call>\nAnalysis complete.')
    assert len(calls2) == 1
    assert calls2[0]["function"]["name"] == "run_command"
    assert json.loads(calls2[0]["function"]["arguments"]) == {"command": "git status"}
    assert "Analysis complete." in text2

    # Flush should return empty
    text_flush, calls_flush = parser.flush()
    assert text_flush == ""
    assert len(calls_flush) == 0


def test_aurora_tool_call_parser_tag_variations_and_markdown_fences():
    """Verify parser handles <tool_calls>, <tool call>, and markdown code fences."""
    parser = AuroraToolCallParser()
    raw = (
        "<tool_calls>\n"
        "```json\n"
        '{"name": "fetch_data", "arguments": {"url": "https://api.example.com"}}\n'
        "```\n"
        "</tool_calls>"
    )
    text, calls = parser.feed(raw)
    assert text == ""
    assert len(calls) == 1
    assert calls[0]["function"]["name"] == "fetch_data"
    assert json.loads(calls[0]["function"]["arguments"]) == {"url": "https://api.example.com"}


def test_aurora_tool_call_parser_unclosed_flush():
    """Verify parser recovers unclosed tool call at the end of the stream during flush()."""
    parser = AuroraToolCallParser()
    text, calls = parser.feed('<tool_call>{"name": "list_files", "arguments": {"dir": "src"}}')
    assert len(calls) == 0

    flush_text, flush_calls = parser.flush()
    assert len(flush_calls) == 1
    assert flush_calls[0]["function"]["name"] == "list_files"
    assert json.loads(flush_calls[0]["function"]["arguments"]) == {"dir": "src"}


# ── 5. Robust JSON Repair & Windows Path Handling ────────────────────────────

def test_fix_aurora_backslashes_and_robust_json():
    """Verify Windows paths with unescaped backslashes are repaired."""
    raw_path_json = '{"name": "read_file", "arguments": {"path": "C:\\Users\\vizio\\CAMELOT_OS\\file.txt"}}'
    fixed = fix_aurora_backslashes(raw_path_json)
    assert "\\\\" in fixed

    obj, ok = robust_aurora_json(raw_path_json)
    assert ok is True
    assert obj["name"] == "read_file"
    assert "C:\\Users\\vizio" in obj["arguments"]["path"]


# ── 6. Text Recovery and Historical Serialization ────────────────────────────

def test_recover_aurora_tool_calls_from_text():
    """Verify recovering tool calls from plain text with embedded JSON or sandbox cmd dicts."""
    # Embedded name + arguments JSON
    text_with_json = 'I am running this action: {"name": "read_log", "arguments": {"file": "app.log"}}'
    recovered = recover_aurora_tool_calls_from_text(text_with_json)
    assert len(recovered) == 1
    assert recovered[0]["function"]["name"] == "read_log"
    assert json.loads(recovered[0]["function"]["arguments"]) == {"file": "app.log"}

    # Sandbox cmd format: {"cmd": ["git", "diff"]}
    sandbox_text = 'Executing command: {"cmd": ["git", "diff"]}'
    recovered_cmd = recover_aurora_tool_calls_from_text(sandbox_text, shell_tool_name="bash", shell_param_name="command")
    assert len(recovered_cmd) == 1
    assert recovered_cmd[0]["function"]["name"] == "bash"
    assert json.loads(recovered_cmd[0]["function"]["arguments"]) == {"command": "git diff"}


def test_serialize_aurora_tool_calls_for_history():
    """Verify round-trip serialization of tool calls into prompt history."""
    calls = [
        {
            "function": {
                "name": "search_code",
                "arguments": json.dumps({"query": "AuroraPool"}),
            }
        },
        {
            "function": {
                "name": "edit_file",
                "arguments": json.dumps({"target": "main.go"}),
            }
        },
    ]
    serialized = serialize_aurora_tool_calls_for_history(calls)
    assert "<tool_call>" in serialized
    assert "</tool_call>" in serialized
    assert '{"name": "search_code", "arguments": {"query": "AuroraPool"}}' in serialized
    assert '{"name": "edit_file", "arguments": {"target": "main.go"}}' in serialized
