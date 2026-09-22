# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Honcho L4 metamemory embedded in every Round Table knight (offline-safe).

Covers: per-knight user+session embedding across the KNIGHT_NOTEBOOKS
registry, the L4_HONCHO hydration tier, and honcho_memory_engine tissue
entries (the hermes_prime tissue assertion that guards the whole lane).
"""
import json
import unittest
from pathlib import Path

from control_plane.infra.honcho_bridge import (
    HonchoBridge,
    honcho_bridge,
    knight_session_id,
    knight_user_id,
    normalize_knight_id,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OPEN_NOTEBOOK_DIR = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook"


class TestHonchoKnightIdentity(unittest.TestCase):
    def test_normalization_mirrors_hydration(self):
        self.assertEqual(normalize_knight_id("sir_helios"), "SIR_HELIO")
        self.assertEqual(normalize_knight_id(" hermes_prime "), "HERMES_PRIME")

    def test_user_and_session_naming(self):
        self.assertEqual(knight_user_id("SIR_FORGE"), "knight_sir_forge")
        self.assertEqual(knight_session_id("SIR_FORGE"), "sess_knight_sir_forge")


class TestHonchoAllKnights(unittest.TestCase):
    def test_sync_all_knights_embeds_registry(self):
        from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS

        result = honcho_bridge.sync_all_knights()
        self.assertEqual(result["status"], "COMPLETE")
        self.assertGreater(result["total"], 30)
        self.assertEqual(result["embedded"], result["total"], "errors: %s" % [
            (k, v.get("error")) for k, v in result["knights"].items() if v.get("status") != "EMBEDDED"
        ])
        expected = {normalize_knight_id(k) for k in KNIGHT_NOTEBOOKS}
        self.assertEqual(set(result["knights"]), expected)

    def test_embedded_check_is_read_only(self):
        bridge = HonchoBridge()
        self.assertTrue(bridge.is_knight_embedded("HERMES_PRIME"))
        self.assertFalse(bridge.is_knight_embedded("KNIGHT_THAT_DOES_NOT_EXIST_XYZ"))

    def test_worldtree_tissue_has_subsystem_tether(self):
        honcho_bridge.sync_all_knights()
        tissue = OPEN_NOTEBOOK_DIR / "world_tree_tissue.json"
        self.assertTrue(tissue.exists())
        data = json.loads(tissue.read_text(encoding="utf-8"))
        tethers = [e for e in data if e.get("artifact_type") == "subsystem_tether"]
        self.assertTrue(tethers, "world_tree tissue lacks subsystem_tether entry")
        self.assertEqual(tethers[0].get("title"), "Honcho L4 subsystem tether")

    def test_hermes_tissue_has_engine_entry(self):
        honcho_bridge.ensure_knight("HERMES_PRIME")
        tissue = OPEN_NOTEBOOK_DIR / "hermes_prime_tissue.json"
        self.assertTrue(tissue.exists())
        data = json.loads(tissue.read_text(encoding="utf-8"))
        self.assertTrue(
            any(entry.get("artifact_type") == "honcho_memory_engine" for entry in data),
            "hermes_prime tissue lacks honcho_memory_engine entry",
        )


class TestHonchoHydrationTier(unittest.TestCase):
    def test_l4_honcho_tier_active(self):
        from memory.hydration_manager import HydrationManager

        mgr = HydrationManager(knight_id="SIR_FORGE")
        self.assertEqual(mgr.honcho_user_id, "knight_sir_forge")
        hydration = mgr.hydrate_context("honcho embed probe", 7)
        self.assertIn("L4_HONCHO", hydration["tiers_active"])
        self.assertIn("user_id", hydration["L4_HONCHO"])


if __name__ == "__main__":
    unittest.main()
