# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# tests/test_vmax_cloudbrain_assimilation.py
"""
Unit and integration tests for vMAX 3.1 & CloudBrain Assimilation Pipeline:
  1. Runtime Planes (RP0 - RP6) classification
  2. Documentation Layers (DL0 - DL5) mapping to VKG nodes
  3. Master Compendium in-place mutator ($O(1)$ slot economy)
  4. Runic router integration for //ASSIMILATE
  5. Strict RAM ceiling boundaries (4 GB Node / 8 GB Server / 256 MB Arthur)
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from control_plane.assimilation.vmax_plane_router import (
    DocumentationLayer,
    RuntimePlane,
    VMAXPlaneRouter,
    DL_TO_VKG_MAPPING,
    KNIGHT_PLANE_AFFINITY,
)
from control_plane.assimilation.compendium_mutator import (
    MasterCompendiumMutator,
    CompendiumMutationResult,
)
from control_plane.runes.runic_router import route_rune


def test_vmax_plane_router_classification():
    """Verify classification of knights and tasks into proper RP and DL layers."""
    # Test 1: Sir Arthur governance
    v1 = VMAXPlaneRouter.classify_task(
        task_id="T01",
        knight_id="SIR_ARTHUR",
        action="audit knight behavioral contract and laws",
        requested_ram_mb=128,
        is_server=False,
    )
    assert v1.runtime_plane == RuntimePlane.RP1_AUTHORITY_AND_EVIDENCE
    assert v1.doc_layer == DocumentationLayer.DL0_GOVERNANCE
    assert v1.vkg_node == "V0_SINGULARITY"
    assert v1.ram_ceiling_mb == 256  # Arthur VPS ceiling

    # Test 2: Lady Mnemosyne research & cognition
    v2 = VMAXPlaneRouter.classify_task(
        task_id="T02",
        knight_id="LADY_MNEMOSYNE",
        action="reflect and learn invariants from memory",
        requested_ram_mb=512,
        is_server=False,
    )
    assert v2.runtime_plane == RuntimePlane.RP4_COGNITION_KNOWLEDGE_VOICE
    assert v2.doc_layer == DocumentationLayer.DL5_REFLECTION
    assert v2.vkg_node == "L5_RECURSIVE_FREQUENCY"
    assert v2.ram_ceiling_mb == 4096

    # Test 3: Server plane allocation
    v3 = VMAXPlaneRouter.classify_task(
        task_id="T03",
        knight_id="SIR_HELIO",
        action="bifrost gateway routing",
        requested_ram_mb=6144,
        is_server=True,
    )
    assert v3.runtime_plane == RuntimePlane.RP2_GOVERNED_CONNECTIVITY
    assert v3.ram_ceiling_mb == 8192
    assert not v3.requires_hitl


def test_dl_to_vkg_mathematical_isomorphism():
    """Verify that all DL0-DL5 layers are isomorphic to the VKG functional equation."""
    assert DL_TO_VKG_MAPPING[DocumentationLayer.DL0_GOVERNANCE] == "V0_SINGULARITY"
    assert DL_TO_VKG_MAPPING[DocumentationLayer.DL1_INTENT] == "V1_HORIZON"
    assert DL_TO_VKG_MAPPING[DocumentationLayer.DL2_STRUCTURE] == "V2_SKELETON"
    assert DL_TO_VKG_MAPPING[DocumentationLayer.DL3_GUARDRAILS] == "V3_SHIELD"
    assert DL_TO_VKG_MAPPING[DocumentationLayer.DL4_OPERATIONS] == "V4_FOUNDATION"
    assert DL_TO_VKG_MAPPING[DocumentationLayer.DL5_REFLECTION] == "L5_RECURSIVE_FREQUENCY"


def test_master_compendium_in_place_mutator():
    """Verify that compendium mutator enforces O(1) slot footprint without slot consumption."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        mutator = MasterCompendiumMutator(vfs_notebooks_root=tmp_path)

        nb_id = "test-notebook-uuid-001"
        knowledge_1 = [
            {"anchor": "ANCHOR_01", "subject": "Anya Gate", "status": "VERIFIED"},
            {"anchor": "ANCHOR_02", "subject": "Bifrost Bridge", "status": "ACTIVE"},
        ]

        # Initial Creation
        res1 = mutator.mutate_in_place(
            notebook_id=nb_id,
            title="Core OS Test",
            domain="Kernel Daemons",
            new_knowledge=knowledge_1,
            governing_knight="LADY_MNEMOSYNE",
        )
        assert res1.status == "CONVERGED_SUCCESS"
        assert res1.action == "MUTATED_IN_PLACE" or res1.action == "FORGED_FRESH"
        assert res1.cloudbrain_slot_delta == 0
        assert res1.total_anchors == 2

        compendium_file = tmp_path / nb_id / "Master_Compendium.md"
        assert compendium_file.exists()
        content = compendium_file.read_text(encoding="utf-8")
        assert "Anya Gate" in content
        assert "Bifrost Bridge" in content

        # In-Place Mutation with New Knowledge and Duplicate
        knowledge_2 = [
            {"anchor": "ANCHOR_02", "subject": "Bifrost Bridge", "status": "ACTIVE"},  # duplicate
            {"anchor": "ANCHOR_03", "subject": "Triple-QFT", "status": "COMPILED"},     # new
        ]
        res2 = mutator.mutate_in_place(
            notebook_id=nb_id,
            title="Core OS Test",
            domain="Kernel Daemons",
            new_knowledge=knowledge_2,
            governing_knight="MERLIN_OMEGA",
        )
        assert res2.status == "CONVERGED_SUCCESS"
        assert res2.cloudbrain_slot_delta == 0
        assert res2.total_anchors == 3
        assert "ANCHOR_03" in res2.added_anchors
        assert "ANCHOR_02" not in res2.added_anchors

        updated_content = compendium_file.read_text(encoding="utf-8")
        assert "Triple-QFT" in updated_content


def test_runic_router_assimilate_dispatch():
    """Verify that route_rune for //ASSIMILATE invokes the vMAX plane router."""
    res = route_rune("//ASSIMILATE", "assimilate cloudbrain architecture")
    assert res.rune == "//ASSIMILATE"
    assert res.knight == "sir_helio"
    data = res.metadata
    assert data.get("action") == "vmax_assimilate"
    assert "runtime_plane" in data
    assert "doc_layer" in data
    assert data.get("status") == "ASSIMILATED_INTO_VMAX_PIPELINE"
