# SPDX-License-Identifier: MIT

"""tests.preflight.test_awaken — boot_vfs_preflight shape tests (Task 8).

These tests verify the boot-phase wrapper's (bool, msg) contract
matches the EXCALIBUR pre-flight sibling signature so the existing
boot_sequence.run_boot() loop renders both rows uniformly.

Tests do NOT subprocess out to bin/awaken.py — that is Task 9's
job. These tests are local, fast, and focused on the wrapper.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from control_plane.preflight.boot_integration import (
    boot_vfs_preflight,
    _summarize_manifest,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# catalog YAML format matches the real vfs/checks catalog.
PASSING_CATALOG = """\
sequence: "001"
id: a_passing_check
display_name: always-passes test (file_age on real file)
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.file_age_run",
         "--path", "bin/awaken.py",
         "--max-age-days", "365"]
timeout_s: 5
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: false
remediation_hint: "n/a"
"""

# For the rejection test we need a probe that returns all_ok=False when
# the input path is missing. Use vfs_present_run with a fake --required
# path that doesn't exist.
REJECTING_CATALOG = """\
sequence: "001"
id: a_required_path_check
display_name: a probe that rejects (vfs_present_run on missing path)
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.vfs_present_run",
         "--required", "/this/path/does/not/exist/anywhere-1234567890"]
timeout_s: 5
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: false
remediation_hint: "n/a"
"""


@pytest.fixture
def home_with_catalog(tmp_path: Path) -> Path:
    """Synthetic CAMELOT home: vfs/checks + run_root."""
    (tmp_path / "vfs" / "checks").mkdir(parents=True)
    (tmp_path / "vfs" / "checks" / "001_pass.yaml").write_text(
        PASSING_CATALOG, encoding="utf-8"
    )
    (tmp_path / "03_VAULT" / "runtime_state" / "preflight").mkdir(
        parents=True
    )
    return tmp_path


@pytest.fixture
def home_with_rejecting_catalog(tmp_path: Path) -> Path:
    """Synthetic CAMELOT home with a rejecting check."""
    (tmp_path / "vfs" / "checks").mkdir(parents=True)
    (tmp_path / "vfs" / "checks" / "001_reject.yaml").write_text(
        REJECTING_CATALOG, encoding="utf-8"
    )
    (tmp_path / "03_VAULT" / "runtime_state" / "preflight").mkdir(
        parents=True
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_boot_vfs_preflight_passes_on_clean_catalog(
    home_with_catalog: Path,
) -> None:
    """A catalog-only-passing run returns (True, '...')."""
    ok, msg = boot_vfs_preflight(home_with_catalog)
    assert ok is True
    assert "VFS_PREFLIGHT GO" in msg
    assert "catalog_hash=" in msg


def test_boot_vfs_preflight_returns_false_on_reject(
    home_with_rejecting_catalog: Path,
) -> None:
    """A rejecting check returns (False, '... REJECT: ...') only in strict mode.

    Day-0 (advisor mode, no _graduated.flag) softens REJECT into an
    advisor_finding and proceeds; the boot proceeds with a GO row
    annotated with `halt=continue`. After sovereign graduation via
    `--graduate` (which writes `_graduated.flag`), a REJECT halts
    the boot — the test for that is below.
    """
    # Strict mode: write the graduation flag at the proper path.
    from control_plane.preflight.state import GraduationFlag
    GraduationFlag(home_with_rejecting_catalog / "03_VAULT" / "runtime_state").graduate()
    ok, msg = boot_vfs_preflight(home_with_rejecting_catalog)
    assert ok is False
    assert "VFS_PREFLIGHT REJECT" in msg
    assert "ADR 0006" in msg or "halt" in msg.lower()


def test_boot_vfs_preflight_advisor_mode_proceeds_on_reject(
    home_with_rejecting_catalog: Path,
) -> None:
    """Day-0 advisor mode softens REJECT into an advisor_finding."""
    # No graduation flag written — pure day-0 advisor mode.
    ok, msg = boot_vfs_preflight(home_with_rejecting_catalog)
    assert ok is True
    assert "VFS_PREFLIGHT GO" in msg
    assert "strict_mode=False" in msg


def test_boot_vfs_preflight_handles_missing_catalog_root(
    tmp_path: Path,
) -> None:
    """No catalog dir → graceful error, not a crash."""
    # Do not create vfs/checks/ — execute_catalog raises
    # CatalogError or FileNotFoundError for empty catalog dir;
    # wrapper catches and returns (False, "...error...").
    (tmp_path / "03_VAULT" / "runtime_state" / "preflight").mkdir(
        parents=True
    )
    ok, msg = boot_vfs_preflight(tmp_path)
    # Empty catalog dir yields zero checks → no rejects → ok=True.
    # That is correct: nothing failed ⇒ proceed.
    if ok:
        assert "GO" in msg
    else:
        assert "error" in msg.lower() or "REJECT" in msg


def test_summarize_manifest_format() -> None:
    """_summarize_manifest builds a one-line summary with catalog_hash + halt."""
    m = {
        "checks": [{}] * 8,
        "halt_decision": "allow_boot",
        "catalog_hash": "deadbeefcafe1234",
    }
    out = _summarize_manifest(m)
    assert "8 check(s)" in out
    assert "catalog_hash=deadbeef" in out
    assert "halt=allow_boot" in out


# ---------------------------------------------------------------------------
# E2E: advisor -> strict graduation + idempotency (Task 9 folded E2E)
# ---------------------------------------------------------------------------


def test_boot_advisor_graduation_writes_flag_then_strict(
    home_with_catalog: Path,
) -> None:
    """First all-CONFIRMED run graduates advisor -> strict (spec §6.2).

    Regression guard for the pre-fix root mismatch: the flag must land
    at <home>/03_VAULT/runtime_state/preflight/_graduated.flag (the SAME
    path strict detection reads), not a nested preflight/preflight/ dir.
    """
    ok, msg = boot_vfs_preflight(home_with_catalog)
    assert ok is True
    assert "strict_mode=False" in msg
    flag = (
        home_with_catalog
        / "03_VAULT" / "runtime_state" / "preflight" / "_graduated.flag"
    )
    assert flag.exists()
    assert flag.read_text(encoding="utf-8") == "vfs-preflight-strict-mode\n"
    # Second run now reads strict mode from the same flag.
    ok2, msg2 = boot_vfs_preflight(home_with_catalog)
    assert ok2 is True
    assert "strict_mode=True" in msg2


def test_boot_e2e_two_runs_produce_distinct_dirs(
    home_with_catalog: Path,
) -> None:
    """AC7: two boot runs in the same minute = two distinct run dirs."""
    boot_vfs_preflight(home_with_catalog)
    boot_vfs_preflight(home_with_catalog)
    run_dir = home_with_catalog / "03_VAULT" / "runtime_state" / "preflight"
    run_dirs = sorted(p for p in run_dir.iterdir() if p.is_dir())
    assert len(run_dirs) == 2, f"expected 2 run dirs, got {len(run_dirs)}"
    assert run_dirs[0].name != run_dirs[1].name
    for d in run_dirs:
        assert (d / "_manifest.json").exists()
        assert any(d.glob("*.json"))  # per-check artifacts present
