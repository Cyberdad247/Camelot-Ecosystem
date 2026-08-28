# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for Excalibur EntireMap & CI/CD Snapshot Versioning Engine.
"""
import json
import unittest

from scripts.forge_excalibur_entiremap import create_cicd_snapshot, WORLDTREE_HOME_ID


class TestExcaliburEntireMapCICD(unittest.TestCase):
    def test_create_cicd_snapshot(self):
        snapshot_id, map_path, snap_meta_path = create_cicd_snapshot("v1000.54-EXCALIBUR-A")
        
        # Verify map file existence and content
        self.assertTrue(map_path.exists())
        content = map_path.read_text(encoding="utf-8")
        self.assertIn("EXCALIBUR COMMAND CENTER · WORLDTREE ENTIRE MAP", content)
        self.assertIn("100.106.246.126", content)
        self.assertIn(WORLDTREE_HOME_ID, content)
        self.assertIn(snapshot_id, content)

        # Verify snapshot metadata
        self.assertTrue(snap_meta_path.exists())
        meta = json.loads(snap_meta_path.read_text(encoding="utf-8"))
        self.assertEqual(meta["snapshot_id"], snapshot_id)
        self.assertEqual(meta["version_tag"], "v1000.54-EXCALIBUR-A")
        self.assertEqual(meta["worldtree_home"], WORLDTREE_HOME_ID)
        self.assertEqual(meta["status"], "RATIFIED_IMMUTABLE")
        self.assertTrue(meta["sha256"])


if __name__ == "__main__":
    unittest.main()
