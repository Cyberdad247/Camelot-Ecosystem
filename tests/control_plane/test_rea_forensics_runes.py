# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""Unit tests for //REA Reverse Engineering Forensics rune and Sir Helios routing."""

from __future__ import annotations

import unittest
from pathlib import Path

import control_plane.runes.runic_router as rr


class TestReaForensicsRunes(unittest.TestCase):
    def test_rea_rune_command_registered(self):
        self.assertIn("//REA", rr.RUNIC_COMMANDS)
        self.assertEqual(rr.RUNIC_COMMANDS["//REA"]["knight"], "sir_helios")
        self.assertEqual(rr.RUNIC_COMMANDS["//REA"]["mode"], "KINETIC")

    def test_rea_handler_asar_classification(self):
        res = rr._handle_rea_forensics_dispatch("demo.asar", {})
        self.assertEqual(res["action"], "rea_forensics_dispatch")
        self.assertEqual(res["cartridge"], "rea-forensics")
        self.assertEqual(res["lead_knight"], "SIR_HELIOS")
        self.assertEqual(res["classification"], "JAVASCRIPT_ELECTRON")
        self.assertEqual(res["status"], "REA_FORENSICS_DISPATCH_ARMED")
        self.assertTrue(res["sandbox_policy"]["global_law_03_compliant"])

    def test_rea_handler_native_binary_classification(self):
        res = rr._handle_rea_forensics_dispatch("kernel_driver.dll", {})
        self.assertEqual(res["classification"], "NATIVE_BINARY")
        self.assertEqual(res["dag_planner"], "MERLIN_Ω")
        self.assertEqual(res["formal_prover"], "SIR_CODEX")

    def test_rea_handler_mobile_package_classification(self):
        res = rr._handle_rea_forensics_dispatch("app_release.apk", {})
        self.assertEqual(res["classification"], "MOBILE_PACKAGE")

    def test_rea_cartridge_manifest_and_skill_exist(self):
        manifest_path = Path("cartridges/rea-forensics/manifest.json")
        self.assertTrue(manifest_path.exists())
        skill_path = Path("cartridges/rea-forensics/skills/SKILL.md")
        self.assertTrue(skill_path.exists())
        content = skill_path.read_text(encoding="utf-8")
        self.assertIn("name: reverse-engineer-anything", content)


if __name__ == "__main__":
    unittest.main()
