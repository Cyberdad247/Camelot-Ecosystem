# SPDX-License-Identifier: MIT

"""TDD-first tests for the hitl_on_fail probes.

Covers:
- file_age.check (used by check 030 northstar brief currency, sequence 030)
- yaml_parses.check (used by check 080 lattice yaml consistency, hitl_on_fail)
- vfs_scaffold_integrity (uses file_present; tested via hitl context)

The 'hitl_on_fail: true' label means a REJECTED check surfaces an operator
PROMPT (per VFS_PREFLIGHT_DESIGN.md §4); the probes themselves don't
behave differently — they're tagged in the catalog, not coded into the
probe module. Tests here focus on probe correctness for the same probes.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os

from control_plane.preflight.probes import (
    file_age,
    file_present,
    yaml_parses,
)


# ---- file_age -------------------------------------------------------------

def test_file_age_passes_for_recent(tmp_path):
    p = tmp_path / "fresh.md"
    p.write_text("# fresh")
    ok, days = file_age.check(p, max_age_days=60)
    assert ok is True
    assert days <= 60


def test_file_age_rejects_for_old(tmp_path):
    p = tmp_path / "old.md"
    p.write_text("# old")
    # Backdate mtime to 100 days ago.
    old_ts = (datetime.now(timezone.utc) - timedelta(days=100)).timestamp()
    os.utime(p, (old_ts, old_ts))
    ok, days = file_age.check(p, max_age_days=60)
    assert ok is False
    assert days >= 90


def test_file_age_returns_false_neg1_for_missing(tmp_path):
    ok, days = file_age.check(
        tmp_path / "ghost.md", max_age_days=60
    )
    assert ok is False
    assert days == -1


# ---- vfs_scaffold_integrity (via file_present) ---------------------------

def test_vfs_scaffold_all_required_present(tmp_path):
    """All 5 vfs manifests present => file_present.scan returns 5."""
    for fname in (
        "preflight.md", "systeminstructions.md", "skills.md",
        "rosters.md", "protocols.md",
    ):
        (tmp_path / fname).write_text(f"---\nid: {fname}\n---\n# ok\n")
    found = file_present.scan([
        tmp_path / "preflight.md",
        tmp_path / "systeminstructions.md",
        tmp_path / "skills.md",
        tmp_path / "rosters.md",
        tmp_path / "protocols.md",
    ])
    assert len(found) == 5


def test_vfs_scaffold_missing_one_returns_4(tmp_path):
    """A missing manifest is observable via file_present.scan."""
    for fname in (
        "preflight.md", "systeminstructions.md", "skills.md",
        "rosters.md",  # intentionally write 4 not 5
    ):
        (tmp_path / fname).write_text(f"---\nid: {fname}\n---\n# ok\n")
    found = file_present.scan([
        tmp_path / "preflight.md",
        tmp_path / "systeminstructions.md",
        tmp_path / "skills.md",
        tmp_path / "rosters.md",
        tmp_path / "protocols.md",  # this one is missing
    ])
    assert len(found) == 4
    assert (tmp_path / "protocols.md") not in found


# ---- yaml_parses ----------------------------------------------------------

def test_yaml_parses_passes_on_mapping(tmp_path):
    p = tmp_path / "ok.yaml"
    p.write_text("a: 1\nb: 2\n")
    ok, msg = yaml_parses.check(p)
    assert ok is True
    assert msg == ""


def test_yaml_parses_rejects_non_mapping(tmp_path):
    p = tmp_path / "list.yaml"
    p.write_text("- 1\n- 2\n")
    ok, msg = yaml_parses.check(p)
    assert ok is False
    assert "mapping" in msg


def test_yaml_parses_rejects_missing(tmp_path):
    p = tmp_path / "ghost.yaml"
    ok, msg = yaml_parses.check(p)
    assert ok is False
    assert "missing" in msg
