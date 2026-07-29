# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch
import sys
from pathlib import Path

import shutil
from pathlib import Path

# Add project root to sys.path for relative imports to work
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import importlib
hydration_mgr_mod = importlib.import_module("01_KERNEL.memory.hydration_manager")
HydrationManager = hydration_mgr_mod.HydrationManager

class TestHydrationManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for tests
        self.test_dir = Path("C:/Users/vizio/CAMELOT_OS/01_KERNEL/memory/test_tissue")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.mgr = HydrationManager(storage_dir=self.test_dir)

    def tearDown(self):
        import gc
        # Ensure SQLite connections are fully closed by deleting the manager and forcing GC
        del self.mgr
        gc.collect()
        
        # Cleanup test files using rmtree
        if self.test_dir.exists():
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                pass # Windows can sometimes hold file locks a bit longer

    def test_l1_hydration(self):
        """Verify that L1 tissue is correctly stored and retrieved."""
        intent = "test_l1"
        content = {"key": "l1_value"}
        self.mgr.store_tissue(intent, content, complexity=5, tier="L1")
        
        # Hydrate with high enough complexity
        result = self.mgr.hydrate_context(intent, complexity=5)
        self.assertIn("L1", result)
        self.assertEqual(result["L1"]["data"]["key"], "l1_value")
        self.assertIn("L1_LOCAL", result["tiers_active"])

    @patch("psutil.virtual_memory")
    @patch.object(hydration_mgr_mod.CloudBrainConnector, "query_notebook")
    def test_l2_hydration_success(self, mock_query, mock_mem):
        """Verify L2 hydration when RAM Law is respected."""
        # Mock 4GB used (below 8GB limit)
        mock_mem.return_value.used = 4 * (1024**3)
        mock_query.return_value = "Mocked Burst Data"
        
        intent = "test_l2_pass"
        result = self.mgr.hydrate_context(intent, complexity=9)
        self.assertIn("L2", result)
        self.assertIn("L2_CLOUD", result["tiers_active"])

    @patch("psutil.virtual_memory")
    def test_l2_hydration_rejection(self, mock_mem):
        """Verify L2 hydration rejection when RAM Law is violated."""
        # Mock 10GB used (above 8GB limit)
        mock_mem.return_value.used = 10 * (1024**3)
        
        intent = "test_l2_fail"
        result = self.mgr.hydrate_context(intent, complexity=9)
        self.assertNotIn("L2", result)
        self.assertIn("L2_ERROR", result)
        self.assertTrue("8GB RAM Law Violation" in result["L2_ERROR"])

    def test_complexity_filtering(self):
        """Verify that low complexity tasks don't trigger high-tier hydration."""
        intent = "test_low_complexity"
        content = {"key": "value"}
        self.mgr.store_tissue(intent, content, complexity=5, tier="L1")
        
        # Complexity 2 should not pull L1 (which requires complexity 4)
        result = self.mgr.hydrate_context(intent, complexity=2)
        self.assertNotIn("L1", result)
        self.assertIn("L0_LOCAL", result["tiers_active"])
        self.assertNotIn("L1_LOCAL", result["tiers_active"])

if __name__ == "__main__":
    unittest.main()
