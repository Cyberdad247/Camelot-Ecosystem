# SPDX-License-Identifier: MIT

"""TDD-first tests for the control_plane.preflight CLI (slice #1 Task 7)."""
import os
import subprocess
import sys



def _run_cli(*args, env_extra=None, cwd=None):
    """Invoke `python -m control_plane.preflight <args>` and return
    the CompletedProcess. Caller sets cwd/env to scope the test."""
    full_env = dict(os.environ)
    # Wipe any inherited escape-hatch env vars so the rejection tests
    # can prove the CLI catches them.
    for k in ("CAMELOT_SKIP_PREFLIGHT", "CAMELOT_BYPASS_PREFLIGHT"):
        full_env.pop(k, None)
    if env_extra:
        full_env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "control_plane.preflight", *args],
        capture_output=True,
        text=True,
        env=full_env,
        cwd=cwd or os.getcwd(),
        timeout=30,
    )


def test_cli_rejects_skip_sovereign_flag():
    r = _run_cli("--run", "--skip-sovereign")
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_rejects_force_flag():
    r = _run_cli("--run", "--force")
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_rejects_no_preflight_flag():
    r = _run_cli("--run", "--no-preflight")
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_rejects_bypass_flag():
    r = _run_cli("--run", "--bypass")
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_rejects_camelot_skip_preflight_env():
    r = _run_cli("--run", env_extra={"CAMELOT_SKIP_PREFLIGHT": "1"})
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_rejects_bypass_preflight_env():
    r = _run_cli("--run", env_extra={"CAMELOT_BYPASS_PREFLIGHT": "1"})
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_self_test_returns_0():
    """`--test` mode runs an inline synthetic catalog and exits 0
    on success. Useful for verifying the orchestrator without
    real vfs/checks/ infrastructure."""
    r = _run_cli("--test")
    assert r.returncode == 0, (
        f"expected 0; got stderr={r.stderr!r} stdout={r.stdout!r}"
    )
    assert "self-test all checks passing" in r.stdout


def test_cli_list_prints_catalog():
    r = _run_cli("--list")
    # The committed catalog has 8 checks; --list should succeed.
    assert r.returncode == 0, (
        f"expected 0; got stderr={r.stderr!r}"
    )
    expected_ids = [
        "env_dependency_match",
        "foss_validation_constraints",
        "northstar_brief_currency",
        "port_readiness_scan",
        "provenance_ledger_writable",
        "tool_registry_presence",
        "vfs_scaffold_integrity",
        "lattice_yaml_consistency",
    ]
    for expected_id in expected_ids:
        assert expected_id in r.stdout, (
            f"missing {expected_id} in --list output: {r.stdout!r}"
        )
