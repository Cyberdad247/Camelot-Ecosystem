# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

from control_plane.mnemosyne_chimera import build_phial_assignments, run_mnemosyne_chimera


def test_build_phial_assignments_maps_research_experts(tmp_path: Path) -> None:
    (tmp_path / "tree_sitter_phial.py").write_text("print('tree')", encoding="utf-8")
    (tmp_path / "memory_decay.py").write_text("print('memory')", encoding="utf-8")
    (tmp_path / "regex_cleaner").mkdir()
    (tmp_path / "regex_cleaner" / "main.py").write_text("print('clean')", encoding="utf-8")

    assignments = build_phial_assignments(tmp_path)

    by_phial = {item["phial"]: item for item in assignments}
    assert by_phial["tree_sitter_phial"]["research_expert"] == "MERLIN_OMEGA"
    assert by_phial["memory_decay"]["research_expert"] == "LADY_MNEMOSYNE"
    assert by_phial["main"]["research_expert"] == "SIR_HERMES"


def test_mnemosyne_chimera_report_first_contract(tmp_path: Path, monkeypatch) -> None:
    scan_root = tmp_path / "scan"
    scan_root.mkdir()
    (scan_root / "module.py").write_text("print('safe')\n", encoding="utf-8")

    # Create phial files in a temp dir so build_phial_assignments finds them
    phial_root = tmp_path / "phials"
    phial_root.mkdir()
    (phial_root / "tree_sitter_phial.py").write_text("# phial\n", encoding="utf-8")
    (phial_root / "memory_decay.py").write_text("# phial\n", encoding="utf-8")
    monkeypatch.setattr("control_plane.mnemosyne_chimera.PHIAL_ROOT", phial_root)

    payload = run_mnemosyne_chimera(scan_path=scan_root, max_files=25, emit_hermes=False, write=False)

    assert payload["schema"] == "camelot.lady-mnemosyne-chimera/v1"
    assert payload["owner"] == "LADY_MNEMOSYNE"
    assert payload["automation_owner"] == "SIR_HERMES"
    assert payload["hermes"]["enabled"] is False
    assert payload["living_system"]["enabled"] is False
    assert payload["squire_triage"]["scan_path"] == str(scan_root.resolve())
    assert payload["squire_triage"]["bounded"] is True
    assert payload["squire_triage"]["max_files"] == 25
    assert payload["phial_research_assignments"]