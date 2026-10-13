r"""
tests.control_plane.test_vkg_execution_engine
==============================================
Unit tests verifying the implementation of the Full-Spectrum Compression Equation:
    Execution = \int (V0 \cdot V1) \longrightarrow (V2 \cap V3) \longrightarrow V4 \circlearrowright L5
"""

import pytest
from control_plane.runners.vkg_execution_engine import (
    ConstraintIntersectionError,
    GovernanceVetoError,
    L5_Reflection,
    V0_Governance,
    V1_Intent,
    V2_Structure,
    V3_Shield,
    V4_Foundation,
    VKGFullSpectrumEngine,
)


def test_full_spectrum_engine_successful_execution():
    """Verify that a compliant intent and valid structure traverse the full pipeline."""
    engine = VKGFullSpectrumEngine()

    intent = V1_Intent(
        goal="Synthesize quantum telemetry crystal",
        requested_capabilities={"vfs.read", "process.allowlisted", "telemetry.emit"},
        requested_ram_mb=1024,
        target_arch="x86_64",
        is_server_target=False,
    )

    structure = V2_Structure(
        schema_version="camelot-cartridge/1",
        entrypoint="run_synthesis",
        required_capabilities={"vfs.read", "process.allowlisted"},
    )

    receipt, reflected_state = engine.execute(intent, structure)

    # V4 Foundation validations
    assert receipt.status == "VERIFIED_SUCCESS"
    assert receipt.exit_code == 0
    assert receipt.receipt_id.startswith("RCPT_")
    assert receipt.vfs_coordinate.startswith("vfs://worldtree/receipts/")
    assert len(receipt.blake3_digest) == 64

    # L5 Reflection validations
    assert reflected_state.cycle_count == 1
    assert reflected_state.crystal_updated is True
    assert reflected_state.vfs_crystal_uri == "vfs://worldtree/crystals/reflection_cycle_1.vkg"
    assert len(reflected_state.new_invariants_learned) == 2


def test_v0_governance_veto_on_global_law_03_node_ram_ceiling():
    """Verify that intent requesting > 4096 MB on a standard node triggers V0 veto."""
    engine = VKGFullSpectrumEngine()

    intent = V1_Intent(
        goal="Exceed node memory budget",
        requested_capabilities={"vfs.read"},
        requested_ram_mb=5000,  # Exceeds 4096 MB node limit
        is_server_target=False,
    )
    structure = V2_Structure(required_capabilities={"vfs.read"})

    with pytest.raises(GovernanceVetoError) as exc_info:
        engine.execute(intent, structure)

    assert "exceeds ceiling 4096 MB" in str(exc_info.value)


def test_v0_governance_allows_up_to_8192_mb_for_sovereign_server():
    """Verify that intent requesting <= 8192 MB is accepted only when is_server_target=True."""
    engine = VKGFullSpectrumEngine()

    # 6144 MB on server target should pass V0
    server_intent = V1_Intent(
        goal="Bifrost central gateway aggregation",
        requested_capabilities={"vfs.read"},
        requested_ram_mb=6144,
        is_server_target=True,
    )
    structure = V2_Structure(required_capabilities={"vfs.read"})

    receipt, reflected_state = engine.execute(server_intent, structure)
    assert receipt.status == "VERIFIED_SUCCESS"
    assert reflected_state.cycle_count == 1

    # But > 8192 MB on server target must fail V0
    server_overbudget_intent = V1_Intent(
        goal="Exceed central server ceiling",
        requested_capabilities={"vfs.read"},
        requested_ram_mb=9000,
        is_server_target=True,
    )
    with pytest.raises(GovernanceVetoError) as exc_info:
        engine.execute(server_overbudget_intent, structure)

    assert "exceeds ceiling 8192 MB" in str(exc_info.value)


def test_v0_governance_veto_on_strictly_denied_capabilities():
    """Verify that intent requesting prohibited capabilities (e.g. direct_main_branch_write) is vetoed."""
    engine = VKGFullSpectrumEngine()

    intent = V1_Intent(
        goal="Bypass branch protection",
        requested_capabilities={"direct_main_branch_write", "vfs.read"},
        requested_ram_mb=512,
    )
    structure = V2_Structure(required_capabilities={"vfs.read"})

    with pytest.raises(GovernanceVetoError) as exc_info:
        engine.execute(intent, structure)

    assert "strictly denied capabilities" in str(exc_info.value)
    assert "direct_main_branch_write" in str(exc_info.value)


def test_v3_shield_constraint_intersection_veto_on_missing_capabilities():
    r"""Verify that (V2 \cap V3) fails when structure demands capabilities not approved in intent."""
    engine = VKGFullSpectrumEngine()

    intent = V1_Intent(
        goal="Read only intent",
        requested_capabilities={"vfs.read"},
        requested_ram_mb=512,
    )
    # Structure demands process.allowlisted which was NOT requested or approved
    structure = V2_Structure(
        required_capabilities={"vfs.read", "process.allowlisted"},
    )

    with pytest.raises(ConstraintIntersectionError) as exc_info:
        engine.execute(intent, structure)

    assert "V3 Shield Veto" in str(exc_info.value)
    assert "process.allowlisted" in str(exc_info.value)


def test_l5_reflection_cycle_increments_and_preserves_history():
    """Verify that multiple successive executions monotonically increment the reflection cycle."""
    engine = VKGFullSpectrumEngine()

    intent = V1_Intent(
        goal="Iterative cycle",
        requested_capabilities={"vfs.read", "process.allowlisted"},
        requested_ram_mb=512,
    )
    structure = V2_Structure(required_capabilities={"vfs.read", "process.allowlisted"})

    _, state_1 = engine.execute(intent, structure)
    assert state_1.cycle_count == 1
    assert state_1.vfs_crystal_uri == "vfs://worldtree/crystals/reflection_cycle_1.vkg"

    _, state_2 = engine.execute(intent, structure)
    assert state_2.cycle_count == 2
    assert state_2.vfs_crystal_uri == "vfs://worldtree/crystals/reflection_cycle_2.vkg"


def test_knight_advanced_oversight_delegation_success():
    """Verify that a designated governing Knight can exert successful advanced oversight over target Knight."""
    from control_plane.runners.vkg_execution_engine import KnightOversightRule

    sentinel_rule = KnightOversightRule(
        governing_knight="SIR_SENTINEL",
        target_knights={"SIR_CODEX", "SIR_FORGE"},
        max_ram_mb=1024,
        forbidden_capabilities={"raw_socket.open"},
    )
    v0 = V0_Governance(knight_oversight_registry={"SIR_SENTINEL": sentinel_rule})
    engine = VKGFullSpectrumEngine(governance=v0)

    intent = V1_Intent(
        goal="Audit and compile kinetic patch",
        requested_capabilities={"vfs.read", "process.allowlisted"},
        requested_ram_mb=512,
        governing_knight="SIR_SENTINEL",
        target_knight="SIR_CODEX",
    )
    structure = V2_Structure(
        entrypoint="kinetic_patch",
        required_capabilities={"vfs.read", "process.allowlisted"},
    )

    receipt, state = engine.execute(intent, structure)
    assert receipt.status == "VERIFIED_SUCCESS"
    assert receipt.governing_knight == "SIR_SENTINEL"
    assert receipt.target_knight == "SIR_CODEX"
    assert any("GOVERNOR_OVERSIGHT_STAMPED: SIR_SENTINEL -> SIR_CODEX" in inv for inv in state.new_invariants_learned)


def test_knight_advanced_oversight_veto_on_unauthorized_target_knight():
    """Verify that a governor is vetoed if attempting to govern a Knight outside its remit."""
    from control_plane.runners.vkg_execution_engine import KnightOversightRule

    sentinel_rule = KnightOversightRule(
        governing_knight="SIR_SENTINEL",
        target_knights={"SIR_CODEX"},  # Only authorized over SIR_CODEX
        max_ram_mb=1024,
    )
    v0 = V0_Governance(knight_oversight_registry={"SIR_SENTINEL": sentinel_rule})
    engine = VKGFullSpectrumEngine(governance=v0)

    # Attempt to govern SIR_BORIS when only authorized over SIR_CODEX
    intent = V1_Intent(
        goal="Unauthorized oversight attempt",
        requested_capabilities={"vfs.read"},
        governing_knight="SIR_SENTINEL",
        target_knight="SIR_BORIS",
    )
    structure = V2_Structure(required_capabilities={"vfs.read"})

    with pytest.raises(GovernanceVetoError) as exc_info:
        engine.execute(intent, structure)

    assert "does not hold oversight authority over SIR_BORIS" in str(exc_info.value)


def test_knight_advanced_oversight_veto_on_governor_memory_or_capability_breach():
    """Verify that governor-specific lower RAM ceilings and capability bans are enforced."""
    from control_plane.runners.vkg_execution_engine import KnightOversightRule

    arthur_scarcity_rule = KnightOversightRule(
        governing_knight="SIR_ARTHUR",
        target_knights={"NANO_SQUIRE"},
        max_ram_mb=256,  # Edge node 256MB scarcity ceiling
        forbidden_capabilities={"vfs_mutation"},
    )
    v0 = V0_Governance(knight_oversight_registry={"SIR_ARTHUR": arthur_scarcity_rule})
    engine = VKGFullSpectrumEngine(governance=v0)

    # 1. Test RAM breach under governor rule
    overbudget_intent = V1_Intent(
        goal="Edge squire patrol",
        requested_capabilities={"vfs.read"},
        requested_ram_mb=512,  # exceeds 256MB governor limit (even though < 4096MB node law)
        governing_knight="SIR_ARTHUR",
        target_knight="NANO_SQUIRE",
    )
    structure = V2_Structure(required_capabilities={"vfs.read"})

    with pytest.raises(GovernanceVetoError) as exc_info:
        engine.execute(overbudget_intent, structure)

    assert "exceeds governor limit 256 MB" in str(exc_info.value)

    # 2. Test forbidden capability breach under governor rule
    forbidden_intent = V1_Intent(
        goal="Edge mutation attempt",
        requested_capabilities={"vfs.read", "vfs_mutation"},
        requested_ram_mb=128,
        governing_knight="SIR_ARTHUR",
        target_knight="NANO_SQUIRE",
    )
    with pytest.raises(GovernanceVetoError) as exc_info:
        engine.execute(forbidden_intent, structure)

    assert "Denied capabilities ['vfs_mutation']" in str(exc_info.value)


def test_runic_router_knight_gov_dispatch():
    """Verify that //KNIGHT_GOV and //OVERSIGHT route cleanly through runic_router."""
    from control_plane.runes.runic_router import route_rune

    res = route_rune("//KNIGHT_GOV", "governor=SIR_SENTINEL target=SIR_CODEX max_ram=1024 action=pqc_verify")
    assert res.rune == "//KNIGHT_GOV"
    assert res.metadata["action"] == "knight_governance_oversight"
    assert res.metadata["governing_knight"] == "SIR_SENTINEL"
    assert res.metadata["target_knight"] == "SIR_CODEX"
    assert res.metadata["status"] == "VERIFIED_SUCCESS"
    assert res.metadata["receipt_id"].startswith("RCPT_")

