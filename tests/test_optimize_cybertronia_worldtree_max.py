# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for Cybertronia Scaffolding Optimizer & WorldTree Max Version Matcher.
"""
import unittest

from scripts.optimize_cybertronia_worldtree_max import (
    CybertroniaScaffoldingOptimizer,
    SOULS_DIR,
    SPARKS_DIR,
    OPEN_NOTEBOOK_DIR,
)


class TestCybertroniaScaffoldingOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = CybertroniaScaffoldingOptimizer()

    def test_scaffolding_optimization(self):
        res = self.optimizer.optimize_scaffolding()
        self.assertEqual(res["status"], "SCAFFOLDING_OPTIMIZED")
        self.assertGreater(res["essential_directories_verified"], 10)

    def test_match_worldtree_knights(self):
        res = self.optimizer.match_worldtree_knights()
        self.assertEqual(res["status"], "ALL_KNIGHTS_ALIGNED_TO_MAX_VERSION")
        self.assertEqual(res["total_registered_knights"], res["synced_knights_count"])

        # Check core knight files
        self.assertTrue((SOULS_DIR / "sir_boris_soul.md").exists())
        self.assertTrue((SPARKS_DIR / "sir_boris_spark.md").exists())
        self.assertTrue((OPEN_NOTEBOOK_DIR / "sir_boris_tissue.json").exists())

    def test_refresh_entiremaps(self):
        res = self.optimizer.refresh_entiremaps()
        self.assertEqual(res["status"], "ENTIREMAPS_REFRESHED")
        self.assertEqual(res["entiremap_mirrors_updated"], 3)


if __name__ == "__main__":
    unittest.main()
