# SPDX-License-Identifier: MIT
"""
RBAC matrix regression tests (SP-01 follow-up).

Guards two real failures found 2026-09-19:
1. _MATRIX_PATH pointed at control_plane/03_VAULT/... (nonexistent), so the
   loader returned {} and EVERY knight validated as unknown/BLOCKED.
2. sir_ouroboros (the tensor scorer's default route) and anya_omega (the
   sovereign compiler) had no access records at all.
"""

from control_plane.core import rbac_matrix as rbm
from control_plane.core.rbac_matrix import RBACMatrix


def test_matrix_file_resolves_to_real_repo_path():
    assert rbm._MATRIX_PATH.exists(), f"matrix path missing: {rbm._MATRIX_PATH}"
    assert len(rbm._load_matrix().get("knights", {})) >= 14


def test_registered_knights_validate_clean():
    rbac = RBACMatrix()
    for knight in ("merlin_omega", "sir_ouroboros", "anya_omega"):
        ok, issues = rbac.check(knight, "ORACLE", "general", complexity=0.5)
        assert ok, f"{knight} blocked: {issues}"


def test_unknown_knight_still_blocked():
    rbac = RBACMatrix()
    ok, issues = rbac.check("sir_nobody", "ORACLE", "general", complexity=0.5)
    assert not ok
    assert any("no access record" in i for i in issues)
