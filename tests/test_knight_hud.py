# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for Camelot-OS Sovereign Knight HUD CLI console.
Verifies knight verification, router probes, LLM config, XP progression,
quick protocols, quick rune symbollect workflows, and cartridge assignments.
"""
import unittest

from control_plane.cli.knight_hud import (
    KNIGHT_REGISTRY,
    ROUTER_PROBES,
    award_knight_xp,
    get_hud_json,
    get_router_status_summary,
    load_xp_ledger,
    render_knight_hud,
    render_progress_bar,
)


class TestKnightHUD(unittest.TestCase):
    def test_knight_registry_completeness(self):
        required_knights = [
            "MERLIN_OMEGA",
            "SIR_BORIS",
            "SIR_CODEX",
            "SIR_FORGE",
            "HERMES_PRIME",
            "LADY_LAKISHA",
            "SIR_HEIMDALL",
            "SIR_SENTINEL",
            "SIR_GHOST",
        ]
        for kid in required_knights:
            self.assertIn(kid, KNIGHT_REGISTRY, f"Missing knight {kid} in KNIGHT_REGISTRY")
            data = KNIGHT_REGISTRY[kid]
            self.assertTrue(data.get("name"))
            self.assertTrue(data.get("title"))
            self.assertTrue(data.get("spark_id"))
            self.assertTrue(data.get("visage"))
            self.assertTrue(data.get("llm", {}).get("primary"))
            self.assertTrue(data.get("audio", {}).get("tts_voice"))
            self.assertTrue(data.get("cartridge", {}).get("id"))
            self.assertGreater(len(data.get("protocols", [])), 0)
            self.assertGreater(len(data.get("runes", [])), 0)

    def test_render_knight_hud_all_knights(self):
        for kid in KNIGHT_REGISTRY:
            hud_text = render_knight_hud(kid, use_color=False)
            self.assertIn("CAMELOT-OS SOVEREIGN OPERATOR HUD", hud_text)
            self.assertIn("KNIGHT PROFILE & PROGRESSION", hud_text)
            self.assertIn("SOVEREIGN ROUTER FLEET", hud_text)
            self.assertIn("INFERENCE & AUDIO MATRIX", hud_text)
            self.assertIn("ASSIGNED CARTRIDGE", hud_text)
            self.assertIn("ACTIVE OPERATIONAL PROTOCOLS", hud_text)
            self.assertIn("QUICK RUNE SYMBOLLECT WORKFLOWS", hud_text)
            self.assertIn(KNIGHT_REGISTRY[kid]["name"], hud_text)
            self.assertIn(KNIGHT_REGISTRY[kid]["cartridge"]["id"], hud_text)

    def test_get_hud_json(self):
        data = get_hud_json("SIR_CODEX")
        self.assertEqual(data["knight_id"], "SIR_CODEX")
        self.assertEqual(data["knight_name"], "Sir Codex")
        self.assertEqual(data["cartridge"]["id"], "openinterpreter-codex")
        self.assertIn("progression", data)
        self.assertIn("routers", data)
        self.assertIn("llm_configuration", data)
        self.assertIn("audio_configuration", data)
        self.assertIn("active_protocols", data)
        self.assertIn("quick_runes", data)

    def test_progress_bar_rendering(self):
        bar_50 = render_progress_bar(50, 0, 100, width=10)
        self.assertIn("50%", bar_50)
        bar_100 = render_progress_bar(100, 0, 100, width=10)
        self.assertIn("100%", bar_100)

    def test_xp_ledger_load_and_award(self):
        ledger = load_xp_ledger()
        self.assertIn("knights", ledger)
        self.assertIn("MERLIN_OMEGA", ledger["knights"])

        total_xp, new_lvl, leveled_up = award_knight_xp("MERLIN_OMEGA", 500)
        self.assertGreater(total_xp, 14500)
        self.assertGreaterEqual(new_lvl, 4)

    def test_router_probes_structure(self):
        summary = get_router_status_summary()
        self.assertEqual(len(summary), len(ROUTER_PROBES))
        for item in summary:
            self.assertIn("name", item)
            self.assertIn("endpoint", item)
            self.assertIn("online", item)
            self.assertIn("role", item)


if __name__ == "__main__":
    unittest.main()
