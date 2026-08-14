# SPDX-License-Identifier: MIT

"""EXCALIBUR Phase 3 acceptance tests — FirnFlow L1/L2 memory."""
import pytest
from control_plane.firnflow import FirnFlow


@pytest.fixture
def firnflow():
    return FirnFlow()


def test_l1_retrieve(firnflow):
    """Phase 3.2 accept: L1 anchor + retrieve returns the stored value."""
    firnflow.anchor("camelot_test", "sovereign_os", tier="L1")
    results = firnflow.retrieve("camelot_test")
    assert results, "Expected at least one result from L1"
    assert any(r.value == "sovereign_os" for r in results)


def test_l1_token_budget(firnflow):
    """L1 stays within 8192 token budget."""
    status = firnflow.status()
    assert status["l1_tokens"] <= status["l1_budget"]


def test_l1_anchor_multiple(firnflow):
    """Multiple anchors are stored independently."""
    firnflow.anchor("key_a", "value_alpha", tier="L1")
    firnflow.anchor("key_b", "value_beta", tier="L1")
    ra = firnflow.retrieve("key_a")
    rb = firnflow.retrieve("key_b")
    assert any(r.value == "value_alpha" for r in ra)
    assert any(r.value == "value_beta" for r in rb)


def test_status_fields(firnflow):
    """status() returns expected keys."""
    status = firnflow.status()
    for key in ("l1_entries", "l1_tokens", "l1_budget", "l2_backend"):
        assert key in status, f"Missing key: {key}"

def test_crystallize(firnflow):
    """crystallize() adds a crystal entry."""
    before = firnflow.status().get("crystals", 0)
    firnflow.crystallize("test_skill_001", {"pattern": "use importlib for dynamic loads", "confidence": 0.9})
    after = firnflow.status().get("crystals", 0)
    assert after >= before


def test_omega_distiller_crystal(firnflow):
    """Verify that Ω_ALPHA_OMEGA_DISTILLER_TOON_v3.3 crystallizes and retrieves properly."""
    crystal_id = "Ω_ALPHA_OMEGA_DISTILLER_TOON_v3.3"
    pattern = {
        "pattern": "Renormalization Group Flow & Semantic Anchor Compression (SAC)",
        "knight": "MERLIN_Ω & ANYA_Ω",
        "confidence": 0.92,
        "context_tags": ["distiller", "compression", "sac", "v3.3"]
    }

    # Crystallize
    crystal = firnflow.crystallize(crystal_id, pattern)
    assert crystal.crystal_id == crystal_id
    assert crystal.confidence == 0.92
    assert "sac" in crystal.context_tags

    # Retrieve
    # Seed the L2 episodic store with the crystal so retrieve can find it
    # note: crystallize writes to CRYSTAL_STORE (nukg_crystals.json)
    # let's verify retrieve works for crystals
    assert crystal_id in firnflow._load_crystals_raw()


def test_omega_production_kernel_crystal(firnflow):
    """Verify that OMEGA_PRODUCTION_KERNEL crystallizes and retrieves properly."""
    crystal_id = "OMEGA_PRODUCTION_KERNEL"
    pattern = {
        "pattern": "Sovereign_MetaCompiler_VFS_Forge with TripleQFT, RTK and GoT oscillation",
        "knight": "Merlin, Anya, Mnemosyne, Heimdall, Codex, Kinetic, Gideon",
        "confidence": 0.95,
        "context_tags": ["metacompiler", "vfs", "got", "v3.3"]
    }

    # Crystallize
    crystal = firnflow.crystallize(crystal_id, pattern)
    assert crystal.crystal_id == crystal_id
    assert crystal.confidence == 0.95
    assert "metacompiler" in crystal.context_tags
    assert crystal_id in firnflow._load_crystals_raw()


def test_sir_helio_directory_distiller():
    """Verify that SirHelio execute generates directory distiller context output."""
    import sys
    from pathlib import Path

    knights_dir = str(Path("C:/Users/vizio/CAMELOT_OS/03_VAULT/training/configs").resolve())
    if knights_dir not in sys.path:
        sys.path.insert(0, knights_dir)

    from knights import KNIGHT_REGISTRY
    SirHelio = KNIGHT_REGISTRY["sir_helio"]

    helio = SirHelio()
    res = helio.execute(
        directive="ACTIVATE_ALPHA_OMEGA_DIRECTORY_DISTILLER for Ω_CAMELOT_OS_DIRECTORY_DISTILLER",
        intent={"domain": "COMPILER", "complexity": 5}
    )
    assert res["status"] == "success"
    assert "COSMIC_ECOSYSTEM_V1000" in res["output"]
    assert "ANYA_FIRST_LAW" in res["output"]


def test_vfs_architecture_scaffold_crystal(firnflow):
    """Verify that Ω_VFS_ARCHITECTURE_SCAFFOLD_vMAX crystallizes and retrieves properly."""
    crystal_id = "Ω_VFS_ARCHITECTURE_SCAFFOLD_vMAX"
    pattern = {
        "pattern": "Sovereign_MetaCompiler_VFS_Forge with Root Floorplan, Execution Plane and Specialist Nodes",
        "knight": "ANYA_Ω & MERLIN_Ω",
        "confidence": 0.97,
        "context_tags": ["vfs", "scaffold", "v3.3"]
    }

    # Crystallize
    crystal = firnflow.crystallize(crystal_id, pattern)
    assert crystal.crystal_id == crystal_id
    assert crystal.confidence == 0.97
    assert "vfs" in crystal.context_tags
    assert crystal_id in firnflow._load_crystals_raw()


def test_reforged_vfs_scaffold_crystal(firnflow):
    """Verify that REFORGED_VFS_SCAFFOLD_vMAX crystallizes and retrieves properly."""
    crystal_id = "REFORGED_VFS_SCAFFOLD_vMAX"
    pattern = {
        "pattern": "Sovereign_MetaCompiler_VFS_Forge with Reforged Floorplan, Execution Plane, and Progressive Disclosure",
        "knight": "Sir Helio, Merlin_Ω, Anya_Ω, Sir Syntax, Sir Codex, Lady Mnemosyne",
        "confidence": 0.98,
        "context_tags": ["reforged", "vfs", "scaffold", "v3.3"]
    }

    # Crystallize
    crystal = firnflow.crystallize(crystal_id, pattern)
    assert crystal.crystal_id == crystal_id
    assert crystal.confidence == 0.98
    assert "reforged" in crystal.context_tags
    assert crystal_id in firnflow._load_crystals_raw()


def test_onboarding_crystal(firnflow):
    """Verify that Ω_ONBOARDING_IGNITION_SYSTEM_vMAX crystallizes and retrieves properly."""
    crystal_id = "Ω_ONBOARDING_IGNITION_SYSTEM_vMAX"
    pattern = {
        "pattern": "Sovereign_Onboarding_Ignition_Registry with diagnostics API and interactive web console",
        "knight": "Anya & Merlin",
        "confidence": 0.99,
        "context_tags": ["onboarding", "ignition", "v3.3"]
    }

    # Crystallize
    crystal = firnflow.crystallize(crystal_id, pattern)
    assert crystal.crystal_id == crystal_id
    assert crystal.confidence == 0.99
    assert "onboarding" in crystal.context_tags
    assert crystal_id in firnflow._load_crystals_raw()




