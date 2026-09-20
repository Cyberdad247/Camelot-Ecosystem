# SPDX-License-Identifier: MIT
"""
Tests for Honcho Self-Hosted L4 Memory & Hermes Integration:
- HonchoBridge client & resilient local cache
- HermesBus event publication on honcho channels
- //HONCHO_SYNC and //HONCHO_QUERY runic dispatch
- VFS tissue and deployment manifest integrity
"""

import json
from pathlib import Path
import pytest

from control_plane.infra.hermes_bridge import HermesBus, CHANNELS
from control_plane.infra.honcho_bridge import HonchoBridge, honcho_bridge
from control_plane.runes.runic_router import normalize_rune, route_rune, RUNIC_COMMANDS


def test_honcho_runes_present_in_table():
    assert "//HONCHO_SYNC" in RUNIC_COMMANDS
    assert "//HONCHO_QUERY" in RUNIC_COMMANDS
    assert RUNIC_COMMANDS["//HONCHO_SYNC"]["knight"] == "hermes_prime"
    assert RUNIC_COMMANDS["//HONCHO_QUERY"]["knight"] == "hermes_prime"


def test_honcho_runes_normalization():
    assert normalize_rune("//honcho-sync") == "//HONCHO_SYNC"
    assert normalize_rune("$honcho-sync") == "//HONCHO_SYNC"
    assert normalize_rune("/honcho-sync") == "//HONCHO_SYNC"
    assert normalize_rune("//honcho-query") == "//HONCHO_QUERY"
    assert normalize_rune("$honcho-query") == "//HONCHO_QUERY"
    assert normalize_rune("/honcho-query") == "//HONCHO_QUERY"


def test_hermes_bus_channels_contain_honcho():
    assert "honcho.memory" in CHANNELS
    assert "honcho.dialectic" in CHANNELS


def test_honcho_bridge_user_and_session_lifecycle():
    bridge = HonchoBridge()
    user = bridge.get_or_create_user("test_user_arthur", {"role": "Sovereign Operator"})
    assert user["id"] == "test_user_arthur"

    session = bridge.get_or_create_session("sess_001", "test_user_arthur")
    assert session["id"] == "sess_001"

    msg = bridge.add_message("sess_001", "test_user_arthur", "user", "Deploy Honcho memory to WorldTree")
    assert msg["role"] == "user"
    assert "Deploy Honcho" in msg["content"]

    ctx = bridge.query_context("sess_001", "Honcho deployment")
    assert "retrieved_context" in ctx

    meta = bridge.get_metamemory("test_user_arthur")
    assert "core_identity" in meta or "user_id" in meta


def test_honcho_sync_dispatch():
    res = route_rune("//HONCHO_SYNC king_arthur_vizion", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "SYNCED"
    assert res.metadata.get("action") == "honcho_sync"
    assert res.metadata.get("knight") == "HERMES_PRIME"
    assert res.metadata.get("subsystem") == "Honcho Self-Hosted L4 Memory"


def test_honcho_query_dispatch():
    res = route_rune("//HONCHO_QUERY directives", context={"session_id": "sess_001"})
    assert res.queued is True
    assert res.metadata.get("status") == "QUERY_COMPLETE"
    assert res.metadata.get("action") == "honcho_query"
    assert res.metadata.get("knight") == "HERMES_PRIME"


def test_honcho_deployment_artifacts_exist():
    repo_root = Path(__file__).resolve().parent.parent.parent
    deploy_dir = repo_root / "deploy" / "honcho-self-hosted"
    assert (deploy_dir / "docker-compose.yml").exists()
    assert (deploy_dir / "config.toml").exists()
    assert (deploy_dir / "env.example").exists()
    assert (deploy_dir / "setup.sh").exists()
    assert (deploy_dir / "README.md").exists()


def test_hermes_and_worldtree_tissue_integrity():
    repo_root = Path(__file__).resolve().parent.parent.parent
    hermes_tissue = repo_root / "03_VAULT" / "runtime_state" / "open_notebook" / "hermes_prime_tissue.json"
    worldtree_tissue = repo_root / "03_VAULT" / "runtime_state" / "open_notebook" / "world_tree_tissue.json"

    assert hermes_tissue.exists()
    assert worldtree_tissue.exists()

    hermes_data = json.load(open(hermes_tissue, encoding="utf-8"))
    assert any(entry.get("artifact_type") == "honcho_memory_engine" for entry in hermes_data)

    worldtree_data = json.load(open(worldtree_tissue, encoding="utf-8"))
    assert any(entry.get("artifact_type") == "subsystem_tether" for entry in worldtree_data)
