# SPDX-License-Identifier: MIT
#-*- coding: utf-8 -*-
"""Unit tests for ADHD cognitive shaping runes and Sir Codex routing."""
import unittest
from pathlib import Path
import control_plane.runes.runic_router as rr

class TestADHDRunes(unittest.TestCase):
    def test_adhd_rune_commands_registered(self):
        self.assertIn('//ADHD', rr.RUNIC_COMMANDS)
        self.assertIn('//I_HAVE_ADHD', rr.RUNIC_COMMANDS)
        self.assertEqual(rr.RUNIC_COMMANDS['//ADHD']['knight'], 'sir_codex')
        self.assertEqual(rr.RUNIC_COMMANDS['//ADHD']['mode'], 'KINETIC')

    def test_adhd_rune_aliases(self):
        self.assertEqual(rr.normalize_rune('$adhd'), '//ADHD')
        self.assertEqual(rr.normalize_rune('$i-have-adhd'), '//ADHD')
        self.assertEqual(rr.normalize_rune('//i-have-adhd'), '//ADHD')
        self.assertEqual(rr.normalize_rune('/adhd'), '//ADHD')
        self.assertEqual(rr.normalize_rune('/i-have-adhd'), '//ADHD')

    def test_adhd_handler_activation(self):
        res = rr._handle_adhd('', {})
        self.assertEqual(res['action'], 'adhd_cognitive_shaping')
        self.assertEqual(res['knight'], 'sir_codex')
        self.assertEqual(res['status'], 'ARMED')
        self.assertTrue(res['active'])
        self.assertEqual(len(res['rules']), 10)

    def test_adhd_handler_deactivation(self):
        res = rr._handle_adhd('stop adhd mode', {})
        self.assertEqual(res['status'], 'DISARMED')
        self.assertFalse(res['active'])

    def test_skill_file_exists(self):
        skill_file = Path('.agents/skills/i-have-adhd/SKILL.md')
        self.assertTrue(skill_file.exists())
        content = skill_file.read_text(encoding='utf-8')
        self.assertIn('name: i-have-adhd', content)
        self.assertIn('Lead with the next action', content)

if __name__ == '__main__':
    unittest.main()
