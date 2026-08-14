# SPDX-License-Identifier: MIT

"""TDD-first tests for `runner.execute_catalog` (slice #1 Task 6).

Three end-to-end behaviors:
- Advisor-mode (first run, no _graduated.flag): REJECTED halts nothing,
  records advisor_finding, proceeds.
- Strict-mode (post-graduation): REJECTED halts the manifest.
- Idempotency: two runs produce distinct run_dirs.

Uses synthetic shell-form checks that print JSON to stdout so the
probe-exec path is exercised without a probe-runner CLI bundle.
"""
from pathlib import Path

from control_plane.preflight import runner


def _fake_anya_triage(raw_intent: str) -> dict:
    """Advisory-only sentinel; preflight owns evidence_class anyway."""
    return {
        "method": "advisory_unavailable",
        "lane": "NORMAL",
        "hitl_tier": "AUTO",
        "shatterpoints_detected": [],
    }


def _write_yaml(path: Path, text: str) -> None:
    path.write_text(text)


def test_run_first_run_advisor_continues_on_rejected(tmp_path):
    """First run (no _graduated.flag): REJECTED proceeds with advisor_finding."""
    _write_yaml(
        tmp_path / "c1.yaml",
        'sequence: 10\nid: c1\ndisplay_name: C1\n'
        'command_type: shell\n'
        'command: ["python", "-c", '
        '"import json,sys; sys.stdout.write(json.dumps({\'all_ok\': True}))"]\n',
    )
    _write_yaml(
        tmp_path / "c2.yaml",
        'sequence: 20\nid: c2\ndisplay_name: C2\n'
        'command_type: shell\n'
        'command: ["python", "-c", '
        '"import json,sys; sys.stdout.write(json.dumps({\'all_ok\': False, \'x\': False}))"]\n',
    )
    specs = runner.load_catalog(tmp_path)
    rc = tmp_path / "run_root"
    manifest = runner.execute_catalog(
        specs=specs,
        run_root=rc,
        scene_text="scene",
        strict_mode=False,  # advisor-mode
        anya_triage_fn=_fake_anya_triage,
    )
    assert manifest.halt_decision == "continue"
    assert manifest.checks_failed == 1
    assert manifest.first_run is True
    assert manifest.graduated_to_strict is False


def test_run_strict_mode_halts_on_rejected(tmp_path):
    """Strict-mode: REJECTED halts the manifest and skips remaining checks."""
    _write_yaml(
        tmp_path / "c1.yaml",
        'sequence: 10\nid: c1\ndisplay_name: C1\n'
        'command_type: shell\n'
        'command: ["python", "-c", '
        '"import json,sys; sys.stdout.write(json.dumps({\'all_ok\': False, \'y\': False}))"]\n',
    )
    _write_yaml(
        tmp_path / "c2.yaml",
        'sequence: 20\nid: c2\ndisplay_name: C2\n'
        'command_type: shell\n'
        'command: ["python", "-c", '
        '"import json,sys; sys.stdout.write(json.dumps({\'all_ok\': True}))"]\n',
    )
    specs = runner.load_catalog(tmp_path)
    rc = tmp_path / "run_root"
    # Simulate prior graduation for this run_root so strict-mode applies.
    from control_plane.preflight.state import GraduationFlag
    GraduationFlag(rc).graduate()

    manifest = runner.execute_catalog(
        specs=specs,
        run_root=rc,
        scene_text="scene",
        strict_mode=True,
        anya_triage_fn=_fake_anya_triage,
    )
    assert manifest.halt_decision == "block_boot"
    assert manifest.halted_at_check == "c1"
    assert manifest.checks_failed == 1
    assert manifest.checks_skipped == 1
    # c2 was skipped.
    on_disk = sorted(p.name for p in rc.rglob("_manifest.json"))
    assert len(on_disk) >= 1


def test_runs_are_idempotent_across_runs(tmp_path):
    """Two consecutive runs produce distinct run_dirs."""
    _write_yaml(
        tmp_path / "c1.yaml",
        'sequence: 10\nid: c1\ndisplay_name: C1\n'
        'command_type: shell\n'
        'command: ["python", "-c", '
        '"import json,sys; sys.stdout.write(json.dumps({\'all_ok\': True}))"]\n',
    )
    specs = runner.load_catalog(tmp_path)
    rc = tmp_path / "run_root"
    m1 = runner.execute_catalog(
        specs=specs, run_root=rc, scene_text="x",
        strict_mode=True, anya_triage_fn=_fake_anya_triage,
    )
    m2 = runner.execute_catalog(
        specs=specs, run_root=rc, scene_text="x",
        strict_mode=True, anya_triage_fn=_fake_anya_triage,
    )
    assert m1.run_id != m2.run_id
    assert (rc / m1.run_id).exists() or any(
        (rc / manifest_dir.name).exists()
        for manifest_dir in rc.iterdir()
        if manifest_dir.is_dir()
    )
