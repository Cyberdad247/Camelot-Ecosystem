# SPDX-License-Identifier: MIT
"""
Test battery for Redis L1 Hot Cache Persistence & Auto-Snapshotting.
"""

from pathlib import Path
from control_plane.infra.redis_persistence import RedisPersistenceManager

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_redis_persistence_local_mirror(tmp_path):
    manager = RedisPersistenceManager(snapshot_dir=tmp_path)
    manager.set_key("session_context_01", {"tokens": 1200, "knight": "SIR_HELIOS"})
    
    val = manager.get_key("session_context_01")
    assert val is not None
    assert val["knight"] == "SIR_HELIOS"
    assert val["tokens"] == 1200


def test_redis_snapshot_creation(tmp_path):
    manager = RedisPersistenceManager(snapshot_dir=tmp_path)
    manager.set_key("crystal_anchor_01", "0xAB8AA3592B3B")
    
    meta = manager.create_snapshot(trigger_reason="test_snapshot")
    assert meta.status == "VERIFIED_SEALED"
    assert meta.key_count >= 1
    
    snapshots = list(tmp_path.glob("redis_snap_*.json"))
    assert len(snapshots) >= 1


def test_redis_windows_conf_persistence_directives():
    conf_path = REPO_ROOT / "bin" / "redis" / "redis.windows.conf"
    assert conf_path.exists(), "redis.windows.conf must exist"
    
    content = conf_path.read_text(encoding="utf-8")
    assert "appendonly yes" in content, "AOF must be enabled"
    assert "save 60 1" in content, "Aggressive 60-second snapshotting must be configured"
