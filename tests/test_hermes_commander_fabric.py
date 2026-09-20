# SPDX-License-Identifier: MIT

from __future__ import annotations

from control_plane.core.knight_configuration import write_knight_configuration
from control_plane.knight_agent import get_capability, load_roster
from control_plane.switchboard import TERMINAL_REGISTRY


def test_sir_hermes_is_commander_in_roster_and_switchboard() -> None:
    cap = get_capability("sir_hermes")
    terminal = TERMINAL_REGISTRY["sir_hermes"]

    assert "Commander" in cap.function
    assert cap.skillgraph_tier == "S4"
    for capability in (
        "commander",
        "hermes_automation",
        "memory_fabric",
        "all_knight_coordination",
    ):
        assert capability in terminal.capability


def test_hermes_commander_fabric_contract_spans_registered_knights(tmp_path) -> None:
    from control_plane.infra.hermes_commander_fabric import build_hermes_commander_fabric

    roster = load_roster()
    fabric = build_hermes_commander_fabric(root=tmp_path)

    assert fabric["status"] == "CONFIGURED"
    assert fabric["commander_knight"] == "sir_hermes"
    assert fabric["commander_role"] == "COMMANDER_KNIGHT"
    assert fabric["secret_values_serialized"] is False
    assert set(roster).issubset(set(fabric["knight_links"]))

    for knight_id, link in fabric["knight_links"].items():
        assert link["automation"]["controller"] == "sir_hermes"
        assert link["automation"]["enabled"] is True
        assert link["automation"]["safety_boundary"] == "HITL_AND_PRIVACY_GATES_PRESERVED"
        assert link["memory_fabric"]["enabled"] is True
        assert link["memory_fabric"]["cloudbrain_uuid"]
        assert link["memory_fabric"]["mempalace_wing"] == f"WING_WORLDTREE_{knight_id.upper()}"
        assert link["secret_values_serialized"] is False


def test_knight_configuration_persists_hermes_commander_snapshot(tmp_path) -> None:
    snapshot = write_knight_configuration(tmp_path)
    commander = snapshot["hermes_commander"]

    assert commander["commander_knight"] == "sir_hermes"
    assert commander["commander_role"] == "COMMANDER_KNIGHT"
    assert commander["target_count"] >= len(load_roster())
    assert commander["artifact_path"].endswith("hermes_commander_fabric_latest.json")
    assert (tmp_path / "03_VAULT" / "runtime_state" / "hermes_commander_fabric_latest.json").exists()


def test_hermes_memory_fabric_domain_routes_to_sir_hermes() -> None:
    from importlib import util
    from pathlib import Path

    path = Path("01_KERNEL/memory/cloudbrain_connector.py")
    spec = util.spec_from_file_location("cloudbrain_connector_hermes_commander_test", path)
    assert spec is not None
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    assert "commander" in module.NOTEBOOK_DOMAIN_TAGS["SIR_HERMES"]
    assert "hermes_automation" in module.NOTEBOOK_DOMAIN_TAGS["SIR_HERMES"]
    assert "memory_fabric" in module.NOTEBOOK_DOMAIN_TAGS["SIR_HERMES"]
    assert module.route_by_domain(["commander", "hermes_automation", "memory_fabric"])[0] == "SIR_HERMES"
