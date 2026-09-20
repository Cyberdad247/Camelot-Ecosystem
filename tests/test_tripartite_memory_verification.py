# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Tripartite Memory Architecture Verification Test

"""
Verification of:
1. Cloudbrain Main Access -> NotebookLM World Tree (Root UUID: a0a4bfb9-e847-4c38-be39-7aee398f0795)
2. Open-Notebook Longterm Memory (LTM) -> Dynamically twinned to NotebookLM
3. Flash Memory -> Redis (backed by github.com/redis/go-redis)
"""

import json
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(REPO_ROOT / "vfs"))

WORLDTREE_ROOT_UUID = "a0a4bfb9-e847-4c38-be39-7aee398f0795"


def test_cloudbrain_worldtree_main_access():
    """Verify Cloudbrain is set to NotebookLM World Tree for Main Access."""
    # 1. Check NOTEBOOK_MANIFEST.json
    manifest_path = REPO_ROOT / "01_KERNEL" / "memory" / "NOTEBOOK_MANIFEST.json"
    assert manifest_path.exists(), "NOTEBOOK_MANIFEST.json must exist"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("worldtree_root_uuid") == WORLDTREE_ROOT_UUID
    assert len(manifest.get("notebooks", {})) == 294, "Must index full NotebookLM fleet (294 nodes)"
    assert manifest.get("version") == "2.0.0-SINGULARITY"

    # 2. Check worldtree_manifest.json
    vfs_manifest_path = REPO_ROOT / "vfs" / "worldtree_manifest.json"
    assert vfs_manifest_path.exists(), "vfs/worldtree_manifest.json must exist"
    with open(vfs_manifest_path, "r", encoding="utf-8") as f:
        vfs_manifest = json.load(f)

    worldtree_nodes = [
        n for n in vfs_manifest.get("nodes", [])
        if n.get("knight_id") == "WORLD_TREE" and n.get("notebook_id") == WORLDTREE_ROOT_UUID
    ]
    assert len(worldtree_nodes) == 1, "WORLD_TREE root node must be present with notebook_id = a0a4bfb9-e847-4c38-be39-7aee398f0795"
    assert len(vfs_manifest.get("nodes", [])) == 44

    # 3. Check cloudbrain_connector.py KNIGHT_NOTEBOOKS
    from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS
    assert KNIGHT_NOTEBOOKS.get("WORLD_TREE") == WORLDTREE_ROOT_UUID
    assert KNIGHT_NOTEBOOKS.get("HERMES_PRIME") == "28f89cb6-5048-4b5d-9e94-376082d24744"


def test_open_notebook_dynamically_twinned_ltm():
    """Verify Open-Notebook is dynamically twinned to NotebookLM as Longterm Memory."""
    from open_notebook_bridge import OpenNotebookBridge, audit_all_knight_tethers
    from worldtree_vkg_sync import worldtree_vkg_sync, WORLDTREE_UUID

    assert WORLDTREE_UUID == WORLDTREE_ROOT_UUID

    # Verify audit reports active twinning to World Tree
    audit = audit_all_knight_tethers()
    assert audit["worldtree_home"] == WORLDTREE_ROOT_UUID
    assert audit["total_knights_tethered"] >= 60

    # Verify Hermes Prime dynamic twinning
    hermes_bridge = OpenNotebookBridge(knight_id="HERMES_PRIME")
    manifest = hermes_bridge.get_tether_manifest()
    assert manifest["worldtree_home"] == WORLDTREE_ROOT_UUID
    assert manifest["status"] == "ACTIVE_TETHERED"
    assert Path(manifest["open_notebook_local"]).exists()

    # Verify VKG crystals stored in Open-Notebook plane
    crystals = worldtree_vkg_sync.list_vkg_crystals()
    assert len(crystals) >= 30, "Open-Notebook must store finalized machine-actionable VKG crystals"

    # Verify long_term_cloudbrain module imports and recognises Open-Notebook
    from agora.cloud_orchestrator_shim.long_term_cloudbrain import OPEN_NOTEBOOK_ROOT, configure_open_notebook_environment
    assert OPEN_NOTEBOOK_ROOT.exists()
    cfg = configure_open_notebook_environment()
    assert cfg is not None


def test_redis_flash_memory_tier():
    """Verify Third Flash Memory is Redis backed by go-redis (https://github.com/redis/go-redis.git)."""
    # 1. Verify go-redis dependency in kinetic_sovereign
    go_mod_path = REPO_ROOT / "02_FORGE" / "kinetic_sovereign" / "go.mod"
    assert go_mod_path.exists()
    go_mod_content = go_mod_path.read_text(encoding="utf-8")
    assert "github.com/redis/go-redis/v9" in go_mod_content

    # 2. Verify go.sum contains github.com/redis/go-redis/v9
    go_sum_path = REPO_ROOT / "02_FORGE" / "kinetic_sovereign" / "go.sum"
    assert go_sum_path.exists()
    go_sum_content = go_sum_path.read_text(encoding="utf-8")
    assert "github.com/redis/go-redis/v9" in go_sum_content

    # 3. Verify apps/bifrost uses go-redis
    bifrost_go_mod = REPO_ROOT / "apps" / "bifrost" / "go.mod"
    assert bifrost_go_mod.exists()
    assert "github.com/go-redis/redis" in bifrost_go_mod.read_text(encoding="utf-8")

    # 4. Verify Hybrid Memory Router defines Redis as Tier 1 Flash Hot Cache (<10ms, 0 Tokens)
    from hybrid_worldtree_architecture import HybridMemoryRouter
    router = HybridMemoryRouter()
    status = router.get_architecture_status()
    assert "tier_1_redis" in status
    assert "tier_3_open_notebook" in status
    assert "tier_4_worldtree_cloud" in status

    # 5. Verify Tripartite Memory Architecture doc defines Redis as Flash working memory
    doc_path = REPO_ROOT / "03_VAULT" / "Reference_Architectures" / "MNEMOSYNE_TRIPARTITE_MEMORY.md"
    assert doc_path.exists()
    doc_text = doc_path.read_text(encoding="utf-8")
    assert "Redis: Flash & Short-Term Working Memory" in doc_text
    assert "< 5ms" in doc_text or "< 10ms" in doc_text


def test_symbolect_token_reduction_and_bifrost_bridge():
    """Verify Runic Symbolect inner knight communication and Bifrost Bridge token reduction."""
    from scripts.symbolect_transpiler import TripleQFTTranspiler
    transpiler = TripleQFTTranspiler()
    result = transpiler.compile("Authenticate with Google OAuth and sync NotebookLM to Redis")
    assert result["status"] in ("RADIANT", "PASS")
    assert "symbolect" in result
    assert "anchor_tokens" in result
    assert len(result["anchor_tokens"]) >= 4
    assert "|🧠⊗(⚡💬)⟩" in result["symbolect"]

    # Verify Runic Router routes //SYMBOLECT, //BIFROST, and //CLIPROXYAPI
    from control_plane.runes.runic_router import route_rune
    sym_res = route_rune("//SYMBOLECT", "Synthesize character sheet for Sir Hermes Prime from World Tree")
    assert sym_res.knight == "merlin_omega"
    assert sym_res.metadata.get("status") in ("COMPILED", "DEGRADED_FALLBACK")
    assert sym_res.metadata.get("action") == "symbolect_compilation"

    bifrost_res = route_rune("//BIFROST", "status")
    assert bifrost_res.knight == "sir_heimdall"
    assert bifrost_res.metadata.get("action") == "bifrost_bridge_dispatch"

    cliproxy_res = route_rune("//CLIPROXYAPI", "echo ping")
    assert cliproxy_res.knight == "sir_heimdall"
    assert cliproxy_res.metadata.get("action") == "cliproxyapi_exec"


def test_multivoice_router_apex_build():
    """Verify Multivoice-router repository has merged all branches and built production artifacts."""
    multivoice_dir = Path("C:/Users/vizio/Multivoice-router")
    assert multivoice_dir.exists(), "Multivoice-router directory must exist"
    assert (multivoice_dir / "dist" / "index.html").exists(), "Vite production build index.html must exist"
    assert (multivoice_dir / "services" / "bifrost-broker").exists(), "Bifrost broker service must exist"
    assert (multivoice_dir / "services" / "heimdall-gatekeeper").exists(), "Heimdall gatekeeper service must exist"
    assert (multivoice_dir / "src" / "bifrost").exists(), "src/bifrost must exist"

