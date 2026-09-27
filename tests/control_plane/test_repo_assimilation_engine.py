# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Unit and Integration Test Battery for GitHub Repository Assimilation System.
=============================================================================
Validates:
1. Anya First Gate: Repo foraging, technology stack extraction, zero-trust safety.
2. Isolated Git Branching: Protection of `main` via dedicated cartridge branch.
3. Merlin Synthesis: Cartridge manifest generation, aspects, and deterministic hashing.
4. Schema Compliance: Adherence to Draft 2020-12 cartridge-manifest.schema.json.
5. Merlin Crucible Gate: Formal validation and regression checks.
6. Anya Last Gate: Cryptographic receipt sealing and Living Tissue sync.
7. Runic Dispatch: Routing of //ASSIMILATE_REPO, //CARTRIDGE_BRANCH, and //CARTRIDGE_VERIFY.
"""

from __future__ import annotations

import json
from pathlib import Path

from control_plane.infra.repo_assimilation_engine import (
    RepoAssimilationEngine,
    build_vps_hub_default_cartridge,
)
from control_plane.runes.runic_router import RUNIC_COMMANDS, normalize_rune, route_rune

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HUB_DIR = REPO_ROOT / "apps" / "camelot-vps-hub"


def test_repo_forage_and_anya_first_gate():
    """Verify repo foraging scans technology stack and passes Anya First Gate."""
    engine = RepoAssimilationEngine()
    info = engine.forage_repo(
        repo_url="https://github.com/Cyberdad247/Camelot-VPS.git",
        local_path=HUB_DIR,
    )
    assert info["anya_first_gate"] == "PASSED"
    assert "node_typescript" in info["stack_tags"]
    assert "rust_cargo" in info["stack_tags"]
    assert info["contracts_present"] is True
    assert info["apps_present"] is True


def test_isolated_branch_creation():
    """Verify branch creation protects main and establishes isolated workspace."""
    engine = RepoAssimilationEngine()
    res = engine.create_isolated_branch(
        local_path=HUB_DIR,
        branch_name="cartridge/vps-hub-cartridge-v1",
        base_branch="main",
    )
    assert res["isolated"] is True
    assert res["branch"] == "cartridge/vps-hub-cartridge-v1"
    assert res["status"] == "BRANCH_READY"


def test_cartridge_manifest_synthesis_and_hash_integrity():
    """Verify Merlin synthesis generates deterministic SHA-256 payload hash."""
    engine = RepoAssimilationEngine()
    cartridge_id, name, aspects, branch_name = build_vps_hub_default_cartridge()
    cfg = engine.synthesize_cartridge(
        cartridge_id=cartridge_id,
        name=name,
        aspects=aspects,
        target_repo="https://github.com/Cyberdad247/Camelot-VPS.git",
        branch=branch_name,
    )
    assert cfg.cartridge_id == "vps-hub-cartridge-v1"
    assert len(cfg.aspects) == 5
    assert cfg.integrity["payload_hash"].startswith("sha256:")
    assert cfg.compute_hash() == cfg.integrity["payload_hash"]


def test_cartridge_schema_compliance():
    """Verify synthesized manifest adheres to contracts/schemas/cartridge-manifest.schema.json."""
    schema_path = HUB_DIR / "contracts" / "schemas" / "cartridge-manifest.schema.json"
    assert schema_path.is_file(), "Schema file must exist"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    required_fields = schema.get("required", [])

    cartridge_file = HUB_DIR / "cartridges" / "vps-hub-cartridge-v1.json"
    assert cartridge_file.is_file(), "Cartridge manifest must exist"

    manifest = json.loads(cartridge_file.read_text(encoding="utf-8"))
    for req in required_fields:
        assert req in manifest, f"Manifest missing required field {req}"

    aspect_ids = [a["id"] for a in manifest.get("aspects", [])]
    assert "aspect_multivoice" in aspect_ids
    assert "aspect_honcho" in aspect_ids
    assert "aspect_bifrost_mobile" in aspect_ids
    assert "aspect_task_dag" in aspect_ids
    assert "aspect_heimdall" in aspect_ids


def test_merlin_omega_crucible_verification():
    """Verify Merlin Compatibility Crucible passes formal validation."""
    engine = RepoAssimilationEngine()
    cartridge_id, name, aspects, branch_name = build_vps_hub_default_cartridge()
    cfg = engine.synthesize_cartridge(
        cartridge_id=cartridge_id,
        name=name,
        aspects=aspects,
        target_repo="https://github.com/Cyberdad247/Camelot-VPS.git",
        branch=branch_name,
    )
    crucible_res = engine.verify_crucible(local_path=HUB_DIR, cartridge=cfg)
    assert crucible_res["crucible_verdict"] == "CERTIFIED"
    assert crucible_res["merlin_signoff"] is True
    assert crucible_res["schema_compliant"] is True
    assert crucible_res["aspects_verified"] == 5


def test_anya_last_gate_seal_and_tissue_sync(tmp_path):
    """Verify Anya Last Gate signs receipt and updates living tissue."""
    receipts_dir = tmp_path / "receipts"
    engine = RepoAssimilationEngine(receipts_dir=receipts_dir)
    cartridge_id, name, aspects, branch_name = build_vps_hub_default_cartridge()
    cfg = engine.synthesize_cartridge(
        cartridge_id=cartridge_id,
        name=name,
        aspects=aspects,
        target_repo="https://github.com/Cyberdad247/Camelot-VPS.git",
        branch=branch_name,
    )
    receipt = engine.seal_and_integrate(local_path=HUB_DIR, cartridge=cfg)
    assert receipt.anya_last_gate == "SEALED"
    assert receipt.merlin_crucible == "CERTIFIED"
    assert receipt.merge_status == "STAGED_FOR_MAIN"
    assert receipt.receipt_signature.startswith("ed25519_sig_")

    receipt_file = receipts_dir / f"{receipt.delivery_id}.json"
    assert receipt_file.is_file()

    # Verify tissue was updated
    tissue_path = REPO_ROOT / "03_VAULT" / "runtime_state" / "open_notebook" / "vps_hub_kvm563_tissue.json"
    tissue = json.loads(tissue_path.read_text(encoding="utf-8"))
    node = tissue[0] if isinstance(tissue, list) else tissue
    assert "vps-hub-cartridge-v1" in node.get("active_cartridges", [])


def test_runic_commands_assimilation_dispatch():
    """Verify runic table registration and dispatch for assimilation runes."""
    assert "//ASSIMILATE_REPO" in RUNIC_COMMANDS
    assert "//CARTRIDGE_BRANCH" in RUNIC_COMMANDS
    assert "//CARTRIDGE_VERIFY" in RUNIC_COMMANDS

    assert RUNIC_COMMANDS["//ASSIMILATE_REPO"]["knight"] == "merlin_omega"
    assert RUNIC_COMMANDS["//CARTRIDGE_BRANCH"]["knight"] == "sir_forge"
    assert RUNIC_COMMANDS["//CARTRIDGE_VERIFY"]["knight"] == "merlin_omega"

    # Verify aliases
    assert normalize_rune("//assimilate-repo") == "//ASSIMILATE_REPO"
    assert normalize_rune("$assimilate-repo") == "//ASSIMILATE_REPO"
    assert normalize_rune("//cartridge-branch") == "//CARTRIDGE_BRANCH"
    assert normalize_rune("$cartridge-branch") == "//CARTRIDGE_BRANCH"
    assert normalize_rune("//cartridge-verify") == "//CARTRIDGE_VERIFY"
    assert normalize_rune("$cartridge-verify") == "//CARTRIDGE_VERIFY"

    # Route verification rune
    res = route_rune("//CARTRIDGE_VERIFY vps-hub-cartridge-v1", context={"hydrate": False})
    meta = res.metadata
    assert meta.get("action") == "cartridge_verify"
    assert meta.get("crucible_verdict") == "CERTIFIED"
    assert meta.get("aspects_verified") == 5
    assert meta.get("schema_compliant") is True


def test_purge_merged_branches_functionality():
    """Verify branch purge engine correctly detects merged branches and respects protected lists."""
    engine = RepoAssimilationEngine()
    staging_path = REPO_ROOT / ".camelot" / "staging" / "repos" / "Camelot-VPS"
    target = staging_path if staging_path.exists() else HUB_DIR

    # Dry run purge
    res = engine.purge_merged_branches(
        local_path=target,
        base_branch="main",
        remote="origin",
        delete_remote=True,
        dry_run=True,
    )
    assert res["status"] == "PURGE_COMPLETED"
    assert res["dry_run"] is True
    assert "main" in res["protected"]
    assert "HEAD" in res["protected"]
    assert "origin/main" in res["protected"]
    # All identified remote branches should be feature branches
    for b in res["purged_remote"]:
        assert b.startswith("feature/")


def test_purge_branches_runic_dispatch():
    """Verify //PURGE_BRANCHES registration, aliases, and route execution."""
    assert "//PURGE_BRANCHES" in RUNIC_COMMANDS
    assert RUNIC_COMMANDS["//PURGE_BRANCHES"]["knight"] == "merlin_omega"

    assert normalize_rune("//purge-branches") == "//PURGE_BRANCHES"
    assert normalize_rune("$purge-branches") == "//PURGE_BRANCHES"
    assert normalize_rune("//prune_branches") == "//PURGE_BRANCHES"
    assert normalize_rune("/prune-branches") == "//PURGE_BRANCHES"

    res = route_rune("//PURGE_BRANCHES --dry-run", context={"hydrate": False})
    meta = res.metadata
    assert meta.get("action") == "purge_branches"
    assert meta.get("status") == "PURGE_COMPLETED"
    assert meta.get("dry_run") is True

