"""
tests.control_plane.test_agent_slab_sync
========================================
Pytest suite for ZeroClaw Shared Memory & File-Lock Manager under Cybertronia 4GB edge constraints.
"""

import os
import pytest
from pathlib import Path

from control_plane.infra.agent_slab_sync import (
    CYBERTRONIA_IS_EDGE_NODE,
    NODE_RAM_CEILING_MB,
    ACTIVE_ALLOCATION_FLOOR_MB,
    CANONICAL_SLABS,
    SlabLockManager,
    SlabLockError,
    MemoryMappedSlab,
    audit_memory,
    render_htmx_status_fragment,
)


def test_edge_node_ram_constants():
    """Verifies that Cybertronia is treated strictly as an Edge Node with 4GB ceiling."""
    assert CYBERTRONIA_IS_EDGE_NODE is True
    assert NODE_RAM_CEILING_MB == 4096.0
    assert ACTIVE_ALLOCATION_FLOOR_MB == 480.0


def test_audit_memory_within_bounds():
    """Ensures current process RSS is within the 4GB edge node ceiling."""
    mem = audit_memory()
    assert mem.process_rss_mb < NODE_RAM_CEILING_MB
    assert mem.edge_ceiling_exceeded is False
    assert isinstance(mem.to_dict(), dict)


def test_canonical_slabs_exist():
    """Ensures all 6 canonical slabs exist in .agent/ directory."""
    mgr = SlabLockManager()
    statuses = mgr.get_all_lock_statuses()
    for slab_name in CANONICAL_SLABS:
        assert slab_name in statuses
        assert statuses[slab_name]["exists"] is True


def test_atomic_exclusive_lock(tmp_path: Path):
    """Tests atomic exclusive lock acquisition, collision handling, and release."""
    agent_dir = tmp_path / ".agent"
    lock_dir = agent_dir / ".locks"
    agent_dir.mkdir(parents=True)
    
    test_slab = "Agents.md"
    (agent_dir / test_slab).write_text("# Agents\n", encoding="utf-8")
    
    mgr = SlabLockManager(agent_dir=agent_dir, lock_dir=lock_dir)
    
    # 1. Acquire
    lock_info = mgr.acquire_exclusive(test_slab, timeout_sec=1.0)
    assert lock_info["mode"] == "EXCLUSIVE"
    assert lock_info["pid"] == os.getpid()
    
    # 2. Collision detection
    with pytest.raises(SlabLockError):
        mgr.acquire_exclusive(test_slab, timeout_sec=0.1)
        
    # 3. Release
    released = mgr.release_exclusive(test_slab)
    assert released is True
    assert mgr._inspect_lock(test_slab) is None


def test_write_slab_context_manager(tmp_path: Path):
    """Tests write_slab context manager safely acquires and auto-releases locks."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir(parents=True)
    test_slab = "workflows.md"
    (agent_dir / test_slab).write_text("# Workflows\n", encoding="utf-8")
    
    mgr = SlabLockManager(agent_dir=agent_dir, lock_dir=agent_dir / ".locks")
    
    with mgr.write_slab(test_slab) as path:
        assert path.exists()
        assert mgr._inspect_lock(test_slab) is not None
        
    # After context exit, lock must be released
    assert mgr._inspect_lock(test_slab) is None


def test_memory_mapped_slab(tmp_path: Path):
    """Tests zero-copy memory mapping on slab file."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir(parents=True)
    test_slab = "Skills.md"
    test_file = agent_dir / test_slab
    test_file.write_text("# Skills Slab Data\n", encoding="utf-8")
    
    with MemoryMappedSlab(test_slab, agent_dir=agent_dir) as mm:
        data = mm.read(18)
        assert data == b"# Skills Slab Data"


def test_htmx_status_fragment():
    """Verifies HTMX 2-strand fragment conforms to canonical specification."""
    fragment = render_htmx_status_fragment()
    assert "Cybertronia Edge Node" in fragment
    assert "4096 MB" in fragment
    assert "Cinzel" in fragment
    assert "Shared Memory Slabs" in fragment
