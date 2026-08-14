# SPDX-License-Identifier: MIT

import importlib.util
from pathlib import Path

import pytest


def test_cache_salting_collision_resistance(tmp_path):
    """
    Verify that two tenants with identical content but different IDs 
    produce distinct internal IDs (salting verification).
    """
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "01_KERNEL" / "memory" / "mempalace_l2.py"
    spec = importlib.util.spec_from_file_location("mempalace_l2", module_path)
    mempalace = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mempalace)
    
    l2 = mempalace.MemPalaceL2(storage_path=tmp_path)
    
    wing = "security"
    room = "test"
    content = "Sensitive content that should be salted"
    
    # Store for tenant_a
    l2.store(wing, room, content, tenant_id="tenant_a")
    results_a = l2.search(content, wing, room, tenant_id="tenant_a")
    id_a = results_a[0]["id"]
    
    # Store for tenant_b
    l2.store(wing, room, content, tenant_id="tenant_b")
    results_b = l2.search(content, wing, room, tenant_id="tenant_b")
    id_b = results_b[0]["id"]
    
    # Assert distinct IDs
    assert id_a != id_b, f"Collision detected! Both tenants produced ID: {id_a}"

if __name__ == "__main__":
    pytest.main([__file__])
