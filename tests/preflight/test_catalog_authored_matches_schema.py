# SPDX-License-Identifier: MIT

"""TDD-first test: the authored vfs/checks/*.yaml catalog parses cleanly.

Per plan §Task 5 Step 3: this test asserts the catalog as-written
parses through `runner.load_catalog` (CONFIRMED-only gate, sequence
uniqueness, required fields). It does NOT yet exercise the orchestrator
(Task 6 wires that); the runner currently raises an ImportError if
probe-runner CLIs aren't yet on disk.
"""
from pathlib import Path
from control_plane.preflight import runner

CATALOG_DIR = Path(__file__).resolve().parents[2] / "vfs" / "checks"


def test_catalog_loads_clean():
    specs = runner.load_catalog(CATALOG_DIR)
    assert len(specs) == 8, f"expected 8 checks, got {len(specs)}"


def test_catalog_execution_order():
    specs = runner.load_catalog(CATALOG_DIR)
    assert [s.sequence for s in specs] == [
        10, 20, 30, 40, 50, 60, 70, 80,
    ]


def test_catalog_ids_match_spec():
    specs = runner.load_catalog(CATALOG_DIR)
    expected_ids = {
        "env_dependency_match", "foss_validation_constraints",
        "northstar_brief_currency", "port_readiness_scan",
        "provenance_ledger_writable", "tool_registry_presence",
        "vfs_scaffold_integrity", "lattice_yaml_consistency",
    }
    assert {s.id for s in specs} == expected_ids


def test_catalog_hitl_subset_matches_spec():
    specs = runner.load_catalog(CATALOG_DIR)
    hitl = {s.id for s in specs if s.hitl_on_fail}
    assert hitl == {
        "northstar_brief_currency",
        "port_readiness_scan",
        "vfs_scaffold_integrity",
    }


def test_catalog_command_type_is_python_module_for_all():
    """The 8 authored checks all use python_module wrappers
    (`control_plane.preflight.probes.*_run`)."""
    specs = runner.load_catalog(CATALOG_DIR)
    for s in specs:
        assert s.command_type == "python_module", (
            f"check {s.id} uses {s.command_type}"
        )
        assert s.command[0] == "python"
        assert s.command[1] == "-m"
        # 3rd token is the probe-runner module path
        assert "control_plane.preflight.probes." in s.command[2], (
            f"check {s.id} expects probe-runner CLI at token[2]; got {s.command[2]!r}"
        )


def test_catalog_authority_patterns_only():
    """reserved: an extra rule that the COMMAND for each spec starts with
    a known-safe argv pattern. python_module's invocations of the
    runner are the only safe form; shell specs are deliberately not
    used in this initial slice.
    """
    specs = runner.load_catalog(CATALOG_DIR)
    assert all(s.command_type != "shell" for s in specs), (
        "shell command_type should not be used in slice #1 catalog"
    )
