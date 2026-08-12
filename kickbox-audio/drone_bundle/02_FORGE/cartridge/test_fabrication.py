# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite for Cartridge Fabrication Engine
"""

import os
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cartridge.fabrication_engine import CartridgeFabricator

def test_cartridge_fabrication():
    print("\n=== Testing Cartridge Fabrication ===")
    
    # Use custom output dir for testing
    output_dir = "test_packages"
    fab = CartridgeFabricator(output_dir=output_dir)
    
    spec = {
        "cartridge_id": "TEST_FAB_CARTRIDGE",
        "type": "engineering",
        "agents": ["Sir_Tester"],
        "capabilities": ["unit_testing"],
        "governance": {
            "HITL_required": True,
            "allowed_tools": ["ls", "cat"]
        }
    }
    
    manifest = fab.fabricate(spec)
    
    print(f"✅ Fabricated: {manifest.cartridge_id}")
    print(f"✅ Agents: {manifest.agents}")
    print(f"✅ Governance: {manifest.governance.HITL_required}")
    print(f"✅ Signature: {manifest.signature}")
    
    assert manifest.cartridge_id == "TEST_FAB_CARTRIDGE"
    assert "Sir_Tester" in manifest.agents
    assert manifest.governance.HITL_required == True
    
    # Verify persistence
    package_path = os.path.join(fab.output_dir, manifest.cartridge_id)
    assert os.path.exists(package_path), "Package directory should exist"
    assert os.path.exists(os.path.join(package_path, "manifest.json")), "Manifest file should exist"
    assert os.path.exists(os.path.join(package_path, "persona.py")), "Persona file should exist"
    
    # Cleanup
    shutil.rmtree(fab.output_dir)
    print(f"✅ Cleanup successful")

def test_jit_tool_compilation():
    print("\n=== Testing JIT Tool Compilation ===")
    
    fab = CartridgeFabricator()
    
    tool_spec = {
        "adapter_id": "shopify_inventory_jit",
        "endpoint": "https://api.shopify.com/v1",
        "auth": "env:SHOPIFY_API_KEY",
        "methods": {
            "get_stock": {
                "method": "GET",
                "params": ["product_id"],
                "response_map": {"stock": "$.inventory_quantity"}
            }
        },
        "rate_limit": 100
    }
    
    adapter = fab.compile_jit_tool(tool_spec)
    
    print(f"✅ Compiled JIT Adapter: {adapter.adapter_id}")
    print(f"✅ Auth: {adapter.auth}")
    print(f"✅ Method 'get_stock': {adapter.methods['get_stock'].method}")
    print(f"✅ Rate Limit: {adapter.sandbox_constraints.max_calls_per_minute}")
    
    assert adapter.adapter_id == "shopify_inventory_jit"
    assert adapter.auth == "env:SHOPIFY_API_KEY"
    assert adapter.sandbox_constraints.max_calls_per_minute == 100

def test_template_inheritance():
    print("\n=== Testing Template Inheritance ===")
    
    fab = CartridgeFabricator(output_dir="temp_templates")
    
    # Custom strategy spec (should inherit Lord_Nexus)
    spec = {
        "cartridge_id": "CUSTOM_STRATEGY",
        "type": "strategy",
        "agents": ["Sir_Extra"]
    }
    
    manifest = fab.fabricate(spec)
    
    print(f"✅ Agents in Custom Strategy: {manifest.agents}")
    assert "Lord_Nexus" in manifest.agents
    assert "Sir_Extra" in manifest.agents
    
    shutil.rmtree(fab.output_dir)

if __name__ == "__main__":
    print("🧪 Starting Cartridge Fabrication Test Suite...")
    try:
        test_cartridge_fabrication()
        test_jit_tool_compilation()
        test_template_inheritance()
        print("\n🏆 ALL FABRICATION TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()