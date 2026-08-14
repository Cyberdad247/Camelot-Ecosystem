# SPDX-License-Identifier: MIT

"""TDD-first tests for GraduationFlag (slice #1 Task 1, Step 1)."""
import os
from pathlib import Path
from control_plane.preflight import state


def test_graduation_flag_strict_when_flag_present(tmp_preflight_root: Path):
    flag = state.GraduationFlag(tmp_preflight_root)
    target = flag.path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("vfs-preflight-strict-mode\n")
    assert flag.is_strict() is True


def test_graduation_flag_advisor_when_flag_missing(tmp_preflight_root: Path):
    flag = state.GraduationFlag(tmp_preflight_root)
    assert flag.is_strict() is False


def test_graduation_flag_graduate_writes_atomically(tmp_preflight_root: Path):
    flag = state.GraduationFlag(tmp_preflight_root)
    flag.graduate()
    assert flag.is_strict() is True
    assert flag.path().read_text() == state.FLAG_CONTENTS


def test_graduation_flag_revoke_returns_to_advisor(tmp_preflight_root: Path):
    flag = state.GraduationFlag(tmp_preflight_root)
    flag.graduate()
    flag.revoke()
    assert flag.is_strict() is False
