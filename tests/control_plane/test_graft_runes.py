# SPDX-License-Identifier: MIT
#-*- coding: utf-8 -*-
"""Unit tests for the //CONTEXT rune (graft repo context graph dispatch)."""
import unittest

import control_plane.runes.runic_router as rr


class TestContextRune(unittest.TestCase):
    def test_rune_registered(self):
        self.assertIn('//CONTEXT', rr.RUNIC_COMMANDS)
        cfg = rr.RUNIC_COMMANDS['//CONTEXT']
        self.assertEqual(cfg['knight'], 'squire_colony')
        self.assertEqual(cfg['mode'], 'ORACLE')
        self.assertEqual(cfg['handler'], '_handle_context')
        self.assertIn('_handle_context', rr._HANDLERS)

    def test_rune_normalize(self):
        self.assertEqual(rr.normalize_rune('//context'), '//CONTEXT')

    def test_default_is_ask_with_source(self):
        res = rr._handle_context('how does auth work', {})
        self.assertEqual(res['action'], 'graft_context_query')
        self.assertEqual(res['knight'], 'squire_colony')
        self.assertTrue(res['read_only'])
        self.assertEqual(
            res['canonical_command'],
            "graft ask 'how does auth work' --source",
        )

    def test_empty_param_orients_repo(self):
        res = rr._handle_context('', {})
        self.assertTrue(res['canonical_command'].startswith('graft ask '))
        self.assertIn('--source', res['canonical_command'])

    def test_flagless_subverbs(self):
        self.assertEqual(rr._handle_context('map', {})['canonical_command'], 'graft map')
        self.assertEqual(rr._handle_context('check', {})['canonical_command'], 'graft check')
        self.assertEqual(
            rr._handle_context('map --max-dirs 20', {})['canonical_command'],
            'graft map --max-dirs 20',
        )

    def test_grep_quotes_pattern(self):
        self.assertEqual(
            rr._handle_context('grep route_rune', {})['canonical_command'],
            'graft grep route_rune',
        )
        self.assertEqual(
            rr._handle_context('grep foo bar', {})['canonical_command'],
            "graft grep 'foo bar'",
        )

    def test_callers_passes_flags(self):
        self.assertEqual(
            rr._handle_context('callers route_rune --depth 2', {})['canonical_command'],
            'graft callers route_rune --depth 2',
        )

    def test_skeleton_quotes_path(self):
        self.assertEqual(
            rr._handle_context('squires/colony.py', {})['canonical_command'],
            'graft ask squires/colony.py --source',
        )
        self.assertEqual(
            rr._handle_context('skeleton squires/colony.py', {})['canonical_command'],
            'graft skeleton squires/colony.py',
        )

    def test_detail_echoes_command(self):
        res = rr._handle_context('map', {})
        self.assertEqual(res['detail'], f"run: {res['canonical_command']}")


if __name__ == '__main__':
    unittest.main()
