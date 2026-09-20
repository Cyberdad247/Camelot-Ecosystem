# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
Tests for JCode Zero-Overhead Memory Compaction & Memory Guard
=============================================================
Verifies:
- Sub-50ms initialization and instant telemetry boot.
- Safe tool use/result boundary cutoff.
- UTF-8 safe boundary truncation.
- Bounded image token charging without raw base64 inflation.
- HTTP 413 payload recovery & oldest-first image stripping.
- Effective token calculation split vs subset accounting.
- Process PSS memory telemetry extraction.
"""

from control_plane.infra.jcode_memory_guard import (
    JCodeMemoryGuard,
    Message,
    ContentBlock,
    Role,
    CompactionActionType,
    DEFAULT_TOKEN_BUDGET,
    IMAGE_TOKEN_COST,
    CHARS_PER_TOKEN,
    SYSTEM_OVERHEAD_TOKENS,
    safe_compaction_cutoff,
    truncate_str_boundary,
    tail_str_boundary,
    message_char_count,
    estimate_compaction_tokens,
    effective_context_tokens_from_usage,
    emergency_truncated_tool_result,
    emergency_truncate_large_payloads,
    emergency_strip_large_images,
    is_request_payload_too_large_error,
)


def test_sub_50ms_boot_and_pss_telemetry():
    """Verify sub-50ms boot speed and stdlib PSS telemetry capability."""
    guard = JCodeMemoryGuard()
    assert guard.boot_time_ms < 50.0

    mem = JCodeMemoryGuard.get_process_memory_mb()
    assert "pss_mb" in mem
    assert "rss_mb" in mem
    assert "vms_mb" in mem
    assert mem["rss_mb"] >= 0.0


def test_utf8_safe_truncation():
    """Verify UTF-8 boundaries are respected and not sliced in between codepoints."""
    s = "éabc"
    assert truncate_str_boundary(s, 1) == ""
    assert truncate_str_boundary(s, 2) == "é"
    assert truncate_str_boundary(s, 3) == "éa"

    tail = tail_str_boundary("helloé", 2)
    assert tail == "é"


def test_effective_context_tokens_accounting():
    """Test split accounting (Anthropic) vs subset accounting (OpenAI)."""
    # Anthropic split accounting
    anthropic_tokens = effective_context_tokens_from_usage(
        "anthropic", input_tokens=10_000, cache_read_input_tokens=300_000, cache_creation_input_tokens=5_000
    )
    assert anthropic_tokens == 315_000

    # OpenAI subset accounting (does not double count cached)
    openai_tokens = effective_context_tokens_from_usage(
        "openai", input_tokens=400_000, cache_read_input_tokens=390_000, cache_creation_input_tokens=None
    )
    assert openai_tokens == 400_000

    # Zero input
    assert effective_context_tokens_from_usage("anthropic", 0, cache_read_input_tokens=100) == 0


def test_image_token_cost_bounded():
    """Verify large base64 image strings do NOT inflate token count 100x."""
    huge_base64 = "A" * 1_400_000
    msg = Message.user("")
    msg.content = [ContentBlock(type="image", media_type="image/png", data=huge_base64)]

    chars = message_char_count(msg)
    # Charged as flat IMAGE_TOKEN_COST * CHARS_PER_TOKEN
    assert chars == IMAGE_TOKEN_COST * CHARS_PER_TOKEN
    assert chars < len(huge_base64) // 10

    tokens = estimate_compaction_tokens(None, chars * 4, DEFAULT_TOKEN_BUDGET)
    assert tokens < SYSTEM_OVERHEAD_TOKENS + 4 * IMAGE_TOKEN_COST + 10


def test_safe_compaction_cutoff_preserves_tool_pairs():
    """Verify safe_compaction_cutoff never leaves orphaned ToolResult blocks."""
    tool_use = Message(
        role=Role.ASSISTANT,
        content=[ContentBlock(type="tool_use", id="call_1", name="read", input={"file": "test.py"})],
    )
    tool_res = Message(
        role=Role.USER,
        content=[ContentBlock(type="tool_result", tool_use_id="call_1", content="file contents")],
    )

    messages = [
        Message.user("turn 0"),
        tool_use,
        tool_res,
        Message.user("turn 3"),
    ]

    # If raw cutoff attempts index 2 (between tool_use and tool_res), it must pull back to index 1
    safe_idx = safe_compaction_cutoff(messages, 2)
    assert safe_idx == 1


def test_emergency_truncated_tool_result():
    """Verify tool result truncation preserves head and tail."""
    original = "START" + ("x" * 5000) + "END"
    truncated = emergency_truncated_tool_result(original, max_chars=1000)
    assert truncated.startswith("START")
    assert truncated.endswith("END")
    assert "chars truncated for context recovery" in truncated


def test_emergency_truncate_large_payloads():
    """Verify emergency_truncate_large_payloads replaces large images with markers."""
    msg = Message(
        role=Role.USER,
        content=[
            ContentBlock(type="tool_result", tool_use_id="1", content="a" * 10_000),
            ContentBlock(type="image", media_type="image/png", data="b" * 5000),
        ],
    )
    count = emergency_truncate_large_payloads([msg], max_tool_result_chars=2000, max_image_chars=1000)
    assert count == 2
    assert msg.content[1].type == "text"
    assert "Image omitted during emergency context recovery" in (msg.content[1].text or "")


def test_payload_too_large_and_image_stripping():
    """Verify HTTP 413 error detection and oldest-first image stripping."""
    err1 = "413 Request Entity Too Large"
    err2 = "Anthropic error: request_too_large"
    assert is_request_payload_too_large_error(err1)
    assert is_request_payload_too_large_error(err2)
    assert not is_request_payload_too_large_error("Rate limit exceeded 429")

    # Strip oldest image first
    img1 = ContentBlock(type="image", media_type="image/png", data="old_img" * 1000)
    img2 = ContentBlock(type="image", media_type="image/png", data="new_img" * 1000)
    m1 = Message(role=Role.USER, content=[img1])
    m2 = Message(role=Role.USER, content=[img2])

    stripped = emergency_strip_large_images([m1, m2], target_total_chars=7000)
    assert stripped == 1
    assert m1.content[0].type == "text"
    assert m2.content[0].type == "image"  # Kept newer image


def test_guard_compaction_lifecycle():
    """Verify end-to-end compaction lifecycle under memory pressure."""
    guard = JCodeMemoryGuard(token_budget=1000)

    # Populate turns
    for i in range(15):
        guard.add_message(Message.user(f"Message {i} discussing src/main.py and tests/test_core.py"))
        guard.add_message(Message.assistant(f"Response {i} executing tool read"))

    stats = guard.get_stats()
    assert stats.active_messages == 30

    action, dropped = guard.compact_if_needed(observed_input_tokens=960)  # >95% critical
    assert action == CompactionActionType.HARD_COMPACTED
    assert dropped > 0
    assert guard.summary is not None
    assert "Emergency compaction" in guard.summary.text
    assert "src/main.py" in guard.summary.text
