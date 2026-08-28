# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for NineRouter Engine & RTK Compressor in Camelot-OS.
Tests token compression, protocol translation, quota tracking, multi-account round robin,
and VoiceProAdapter orchestration. Zero external dependencies outside Python standard library.
"""
import unittest

from control_plane.dispatch.nine_router_engine import (
    NineRouterEngine,
    ProtocolTranslator,
    UpstreamAccount,
    filter_git_diff,
    filter_git_log,
    filter_dedup_log,
    filter_smart_truncate,
)
from control_plane.infra.voice_pro_adapter import VoiceProAdapter, VoiceProJobConfig
from control_plane.multivoice_bridge import MultivoiceBridge, render_panel


class TestRTKFilters(unittest.TestCase):
    def test_git_diff_compression(self):
        sample_diff = "diff --git a/src/app.py b/src/app.py\n@@ -1,5 +1,5 @@\n-old line\n+new line\n" + (" context line\n" * 150)
        compressed = filter_git_diff(sample_diff)
        self.assertTrue(len(compressed) < len(sample_diff))
        self.assertIn("src/app.py", compressed)
        self.assertIn("lines truncated", compressed)

    def test_git_log_compression(self):
        sample_log = (
            "commit 0123456789abcdef0123456789abcdef01234567\n"
            "Author: Boris <boris@camelot.os>\n"
            "Date:   Mon Jan 1 00:00:00 2026\n\n"
            "    Assimilate NineRouter and Voice-Pro\n\n"
            + ("    extra body line with tons of detail\n" * 20)
        )
        compressed = filter_git_log(sample_log)
        self.assertTrue(len(compressed) < len(sample_log))
        self.assertIn("Subject: Assimilate NineRouter", compressed)

    def test_dedup_log(self):
        repeated = "\n".join(["[INFO] Polling endpoint..."] * 50)
        compressed = filter_dedup_log(repeated)
        self.assertTrue(len(compressed) < len(repeated))
        self.assertIn("repeated 49 more times", compressed)

    def test_smart_truncate(self):
        huge_text = "A" * 10000
        truncated = filter_smart_truncate(huge_text, max_chars=1000)
        self.assertTrue(len(truncated) < 2000)
        self.assertIn("characters compressed", truncated)


class TestNineRouterEngine(unittest.TestCase):
    def setUp(self):
        self.engine = NineRouterEngine(rtk_enabled=True)

    def test_openai_tool_compression(self):
        sample_git_diff = "diff --git a/file.py b/file.py\n@@ -1,5 +1,5 @@\n" + ("+change\n" * 200)
        body = {
            "model": "gpt-4o",
            "messages": [
                {"role": "user", "content": "Run git diff"},
                {"role": "assistant", "content": None, "tool_calls": [{"id": "call_1", "type": "function", "function": {"name": "run_command"}}]},
                {"role": "tool", "tool_call_id": "call_1", "content": sample_git_diff}
            ]
        }
        stats = self.engine.rtk.compress_messages(body)
        self.assertIsNotNone(stats)
        self.assertGreater(stats.bytes_saved, 0)
        self.assertGreater(stats.savings_pct, 20.0)
        self.assertIn("lines truncated", body["messages"][2]["content"])

    def test_claude_tool_result_compression(self):
        sample_git_diff = "diff --git a/file.py b/file.py\n@@ -1,5 +1,5 @@\n" + ("+change\n" * 200)
        body = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": "Check diff"},
                {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": "call_1", "content": sample_git_diff, "is_error": False}
                    ]
                }
            ]
        }
        stats = self.engine.rtk.compress_messages(body)
        self.assertIsNotNone(stats)
        self.assertGreater(stats.bytes_saved, 0)

    def test_error_traces_preserved(self):
        error_content = "diff --git a/bad.py b/bad.py\n" + ("+err\n" * 200)
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": "call_err", "content": error_content, "is_error": True}
                    ]
                }
            ]
        }
        stats = self.engine.rtk.compress_messages(body)
        self.assertEqual(body["messages"][0]["content"][0]["content"], error_content)

    def test_protocol_translation_openai_to_claude(self):
        openai_req = {
            "model": "gpt-4o",
            "max_tokens": 2048,
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": "You are Sir Codex."},
                {"role": "user", "content": "Build bridge"},
                {"role": "assistant", "content": "Calling tool", "tool_calls": [{"id": "call_99", "type": "function", "function": {"name": "build", "arguments": "{\"target\": \"bridge\"}"}}]},
                {"role": "tool", "tool_call_id": "call_99", "content": "Built successfully."}
            ],
            "tools": [
                {"type": "function", "function": {"name": "build", "description": "Build component", "parameters": {"type": "object", "properties": {"target": {"type": "string"}}}}}
            ]
        }
        claude_req = ProtocolTranslator.openai_to_claude_request(openai_req)
        self.assertEqual(claude_req["system"], "You are Sir Codex.")
        self.assertEqual(claude_req["max_tokens"], 2048)
        self.assertEqual(len(claude_req["tools"]), 1)
        self.assertEqual(claude_req["tools"][0]["name"], "build")
        
        # Verify tool use block
        asst_msg = [m for m in claude_req["messages"] if m["role"] == "assistant"][0]
        self.assertEqual(asst_msg["content"][1]["type"], "tool_use")
        self.assertEqual(asst_msg["content"][1]["name"], "build")

        # Verify tool result block
        user_tool_msg = claude_req["messages"][-1]
        self.assertEqual(user_tool_msg["content"][0]["type"], "tool_result")
        self.assertEqual(user_tool_msg["content"][0]["tool_use_id"], "call_99")

    def test_protocol_translation_claude_to_openai(self):
        claude_req = {
            "model": "claude-3-5-sonnet-20241022",
            "system": "You are Merlin.",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": "Analyze system"},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Let me check"},
                        {"type": "tool_use", "id": "t1", "name": "scan", "input": {"depth": 3}}
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": "t1", "content": "Clean scan"}
                    ]
                }
            ],
            "tools": [
                {"name": "scan", "description": "Scan codebase", "input_schema": {"type": "object"}}
            ]
        }
        openai_req = ProtocolTranslator.claude_to_openai_request(claude_req)
        self.assertEqual(openai_req["messages"][0]["role"], "system")
        self.assertEqual(openai_req["messages"][0]["content"], "You are Merlin.")
        self.assertEqual(openai_req["tools"][0]["function"]["name"], "scan")
        self.assertEqual(openai_req["messages"][2]["tool_calls"][0]["id"], "t1")
        self.assertEqual(openai_req["messages"][3]["role"], "tool")
        self.assertEqual(openai_req["messages"][3]["tool_call_id"], "t1")

    def test_multi_account_round_robin_and_quota(self):
        acc1 = UpstreamAccount(account_id="acc1", provider="anthropic", api_key="sk-1", quota_limit_tokens=1000, used_tokens=900)
        acc2 = UpstreamAccount(account_id="acc2", provider="anthropic", api_key="sk-2", quota_limit_tokens=1000, used_tokens=200)
        
        self.engine.register_account(acc1)
        self.engine.register_account(acc2)

        selected1 = self.engine.select_account("anthropic")
        self.assertEqual(selected1.account_id, "acc1")

        selected2 = self.engine.select_account("anthropic")
        self.assertEqual(selected2.account_id, "acc2")

        # Exhaust acc1
        acc1.record_usage(200) # used = 1100 >= 1000 limit
        self.assertFalse(acc1.is_available())

        # Next selections should skip exhausted acc1 and return acc2
        self.assertEqual(self.engine.select_account("anthropic").account_id, "acc2")
        self.assertEqual(self.engine.select_account("anthropic").account_id, "acc2")

    def test_account_rate_limit_cooldown(self):
        acc = UpstreamAccount(account_id="rate_limited", provider="openai", api_key="sk-openai")
        self.engine.register_account(acc)
        self.assertTrue(acc.is_available())

        acc.record_error(is_rate_limit=True)
        self.assertFalse(acc.is_available())
        self.assertIsNone(self.engine.select_account("openai"))


class TestVoiceProAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = VoiceProAdapter()

    def test_srt_parsing(self):
        srt_data = (
            "1\n00:00:01,000 --> 00:00:04,500\n{Lakisha} Welcome to Camelot-OS.\n\n"
            "2\n00:00:05,000 --> 00:00:08,200\n{Merlin} Systems are nominal.\n"
        )
        segments = VoiceProAdapter.parse_srt(srt_data)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].speaker, "Lakisha")
        self.assertEqual(segments[0].start_ms, 1000)
        self.assertEqual(segments[0].end_ms, 4500)
        self.assertEqual(segments[0].text, "Welcome to Camelot-OS.")
        self.assertEqual(segments[1].speaker, "Merlin")

    def test_dubbing_job_execution(self):
        cfg = VoiceProJobConfig(
            job_id="job_001",
            engine="cosyvoice",
            text="Testing audio dubbing pipeline across Camelot.",
            voice_name="LakishaHUD",
            speed_factor=1.0
        )
        res = self.adapter.run_dubbing_job(cfg)
        self.assertEqual(res["job_id"], "job_001")
        self.assertEqual(res["voice"], "LakishaHUD")
        self.assertGreater(res["estimated_duration_s"], 0)
        
        telemetry = self.adapter.get_telemetry()
        self.assertEqual(telemetry["completed_jobs"], 1)
        self.assertGreater(telemetry["total_audio_seconds"], 0)


class TestMultivoiceBridgeIntegration(unittest.TestCase):
    def test_nine_router_and_voice_pro_attachment(self):
        bridge = MultivoiceBridge()
        engine = NineRouterEngine()
        voice_pro = VoiceProAdapter()

        # Run a simulated job on voice_pro
        voice_pro.run_dubbing_job(VoiceProJobConfig(
            job_id="test_job",
            engine="rvc",
            text="Dubbing test",
            voice_name="Anya"
        ))

        bridge.attach_nine_router(engine)
        bridge.attach_voice_pro(voice_pro)

        stats = bridge.fetch_affinity()
        self.assertTrue(stats.connected)
        self.assertEqual(stats.voice_pro_jobs, 1)

        panel = render_panel(stats)
        self.assertIn("OMNIROUTE AFFINITY", panel)
        self.assertIn("Voice-Pro: 1 dubs", panel)


if __name__ == "__main__":
    unittest.main()
