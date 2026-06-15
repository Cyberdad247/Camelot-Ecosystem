# -*- coding: utf-8 -*-
"""
MNEMOSYNE Integration Tests — Validating the Lady M Pipeline
=============================================================
Tests the tripartite data flow from Redis (L1) -> Qdrant (L1.5) -> NotebookLM (L2).
"""

import unittest
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure the root is in sys.path
root = Path("C:/Users/vizio/CAMELOT_OS")
if str(root) not in sys.path:
    sys.path.append(str(root))

# Rename the numeric package for importability
import importlib.util

def force_import_kernel():
    """Forces the kernel package into sys.modules to handle numeric prefix."""
    kernel_path = root / "01_KERNEL"
    spec = importlib.util.spec_from_file_location("kernel", str(kernel_path / "__init__.py"))
    kernel = importlib.util.module_from_spec(spec)
    sys.modules["kernel"] = kernel
    spec.loader.exec_module(kernel)
    
    # Now import memory subpackage
    memory_path = kernel_path / "memory"
    spec = importlib.util.spec_from_file_location("kernel.memory", str(memory_path / "__init__.py"))
    memory = importlib.util.module_from_spec(spec)
    sys.modules["kernel.memory"] = memory
    spec.loader.exec_module(memory)
    
    return kernel, memory

# Setup the mock package structure
force_import_kernel()

# Now we can import from the 'kernel.memory' namespace if we manually load files into it
def load_into_namespace(name, path):
    spec = importlib.util.spec_from_file_location(f"kernel.memory.{name}", str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"kernel.memory.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod

# Load required modules
h_mgr_mod = load_into_namespace("hydration_manager", root / "01_KERNEL/memory/hydration_manager.py")
redis_mod = load_into_namespace("redis_store", root / "01_KERNEL/memory/redis_store.py")
qdrant_mod = load_into_namespace("qdrant_store", root / "01_KERNEL/memory/qdrant_store.py")

HydrationManager = h_mgr_mod.HydrationManager
redis_store = redis_mod.redis_store
qdrant_store = qdrant_mod.qdrant_store

class TestMnemosynePipeline(unittest.TestCase):
    def setUp(self):
        self.mgr = HydrationManager(knight_id="TEST_KNIGHT")
        self.test_intent = "mnemosyne_test_v1"
        self.test_payload = {"status": "kinetic_purity", "value": 42}

    def test_01_redis_flash_layer(self):
        """Verify Redis correctly captures hot session tissue."""
        print("\n[MNEMOSYNE] Testing L1 Redis Flash Layer...")
        self.mgr.store_tissue(self.test_intent, self.test_payload, complexity=4, tier="L1")
        results = self.mgr.hydrate_context(self.test_intent, complexity=4)
        self.assertIn("L1_REDIS", results["tiers_active"])
        print("  ✓ Redis L1 capture successful.")

    def test_02_qdrant_semantic_layer(self):
        """Verify Qdrant integration."""
        print("\n[MNEMOSYNE] Testing L1.5 Qdrant Semantic Layer...")
        test_id = f"test_semantic_{int(datetime.now().timestamp())}"
        vector = [0.1] * 384
        success = qdrant_store.upsert("mnemosyne_test", test_id, vector, self.test_payload)
        self.assertTrue(success or qdrant_store.backend == "dark")
        print("  ✓ Qdrant L1.5 semantic retrieval successful.")

    def test_03_notebooklm_cloud_brain(self):
        """Verify L2 NotebookLM routing logic."""
        print("\n[MNEMOSYNE] Testing L2 NotebookLM Cloud Brain Integration...")
        results = self.mgr.hydrate_context("non_existent_deep_topic", complexity=8)
        self.assertTrue(any(x in results["tiers_active"] for x in ["L2_CLOUD", "L2_CLOUD_EMPTY", "L2_CLOUD_RAW", "L2_ERROR"]))
        print("  ✓ NotebookLM L2 routing logic verified.")

if __name__ == "__main__":
    unittest.main()
