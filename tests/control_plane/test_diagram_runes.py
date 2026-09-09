# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""Unit tests for Diagram Design runes and Sir Boris / Lady Guinevere routing."""
import unittest
from pathlib import Path
import control_plane.runes.runic_router as rr

class TestDiagramRunes(unittest.TestCase):
    def test_diagram_rune_commands_registered(self):
        self.assertIn('//DIAGRAM', rr.RUNIC_COMMANDS)
        self.assertIn('//DRAW', rr.RUNIC_COMMANDS)
        self.assertIn('//DIAGRAM_DESIGN', rr.RUNIC_COMMANDS)
        self.assertEqual(rr.RUNIC_COMMANDS['//DIAGRAM']['knight'], 'sir_boris')
        self.assertEqual(rr.RUNIC_COMMANDS['//DRAW']['knight'], 'lady_guinevere')

    def test_diagram_rune_aliases(self):
        self.assertEqual(rr.normalize_rune('$diagram'), '//DIAGRAM')
        self.assertEqual(rr.normalize_rune('$draw'), '//DRAW')
        self.assertEqual(rr.normalize_rune('$diagram-design'), '//DIAGRAM')
        self.assertEqual(rr.normalize_rune('//diagram-design'), '//DIAGRAM')
        self.assertEqual(rr.normalize_rune('/diagram'), '//DIAGRAM')
        self.assertEqual(rr.normalize_rune('/draw'), '//DRAW')

    def test_diagram_handler_execution(self):
        res = rr._handle_diagram('sequence', {})
        self.assertEqual(res['action'], 'diagram_design')
        self.assertEqual(res['knight'], 'sir_boris')
        self.assertEqual(res['aesthetic_partner'], 'lady_guinevere')
        self.assertEqual(res['type'], 'sequence')
        self.assertEqual(res['status'], 'ARMED')
        self.assertEqual(res['brand_palette']['luxora_gold'], '#D4AF37')

    def test_skill_file_exists(self):
        skill_file = Path('.agents/skills/diagram-design/SKILL.md')
        self.assertTrue(skill_file.exists())
        content = skill_file.read_text(encoding='utf-8')
        self.assertIn('name: diagram-design', content)
        self.assertIn('# Diagram Design', content)

if __name__ == '__main__':
    unittest.main()
