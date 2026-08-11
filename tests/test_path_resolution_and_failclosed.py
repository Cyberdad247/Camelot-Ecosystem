"""Regression tests for repo-root path resolution and fail-closed governance.

Two defect classes are locked in here.

**Phantom paths.** Modules under ``control_plane/`` used hand-counted
``Path(__file__).parent.parent`` chains to reach the repository root. When those
modules moved into ``core/``, ``dispatch/``, ``runes/`` and ``infra/`` the chains
silently began resolving one level short, so governance code read and wrote
``control_plane/03_VAULT/...`` instead of the real vault. Nothing raised —
``mkdir(parents=True)`` created the phantom tree and ``if not path.exists():
return {}`` treated the miss as "no data". A second divergent provenance ledger
was committed that way.

**Fail-open governance.** Three guards returned "safe" when they could not
actually evaluate safety: RBAC degraded to an empty (deny-everything but
undiagnosable) matrix, ``verify_patch`` returned ``safe=True`` when z3 was
absent — including for force-pushes to main — and the Kinetic Loop's RECORD
stage swallowed ledger failures and still reported ``✓ complete``.
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

import pytest

from control_plane._paths import KERNEL, REPO_ROOT, VAULT

CONTROL_PLANE = REPO_ROOT / "control_plane"


# ── Repo-root resolution ─────────────────────────────────────────────────────

def test_repo_root_is_the_real_repository_root():
    """REPO_ROOT must be the checkout root, not a nested package directory."""
    assert (REPO_ROOT / "control_plane").is_dir()
    assert (REPO_ROOT / "03_VAULT").is_dir()
    assert (REPO_ROOT / "01_KERNEL").is_dir()
    assert REPO_ROOT.name != "control_plane"


def test_vault_and_kernel_anchors_point_at_real_content():
    assert (VAULT / "training" / "configs" / "config" / "access_matrix.json").is_file()
    assert (KERNEL / "memory" / "mempalace_l2.py").is_file()


def test_no_phantom_vault_or_kernel_inside_control_plane():
    """control_plane/ must not shadow the top-level vault or kernel.

    A phantom ``control_plane/03_VAULT`` is the signature of a short .parent
    chain: something resolved the root one level too deep and created it.
    """
    phantom_runtime = CONTROL_PLANE / "03_VAULT" / "runtime_state"
    phantom_kernel = CONTROL_PLANE / "01_KERNEL"
    assert not phantom_runtime.exists(), (
        f"{phantom_runtime} exists — a repo-root path chain is resolving short"
    )
    assert not phantom_kernel.exists(), (
        f"{phantom_kernel} exists — a repo-root path chain is resolving short"
    )


def test_exactly_one_verification_ledger_is_live():
    """One resolution path for the provenance chain, not two.

    A hash chain with two divergent copies is not tamper-evident, because "the"
    chain becomes ambiguous. The historical phantom ledger is kept under
    99_ARCHIVE for forensics and must stay out of the live tree.
    """
    from control_plane.provenance import ProvenanceManager

    live = [
        p for p in REPO_ROOT.rglob("verification_ledger.jsonl")
        if "99_ARCHIVE" not in p.parts
        and "99_HISTORY" not in p.parts
        and not any(part.startswith(("tmp_", ".", "data")) for part in p.parts)
    ]
    assert len(live) == 1, f"expected one live ledger, found: {live}"

    assert ProvenanceManager().verification_ledger.resolve() == live[0].resolve()
    assert live[0].resolve() == (VAULT / "Missions" / "verification_ledger.jsonl").resolve()


def test_no_module_uses_a_short_repo_root_chain():
    """Guard the whole class of bug, not just the sites that were fixed.

    Any ``Path(__file__)`` chain in a control_plane module that is followed by a
    repo-root directory name must have enough .parent hops to actually reach the
    root, given that module's depth.
    """
    root_names = (
        "01_KERNEL", "02_FORGE", "03_VAULT", "04_KINETIC", "05_INFRASTRUCTURE",
        "blueprints", "vfs", "cartridges", "docs", "scripts", "data", "bin",
        "logs", "etc", ".hive", ".camelot-config.yaml", ".env",
        "docker-compose.yml", "pyproject.toml", "Cargo.toml",
    )
    chain = re.compile(
        r"Path\(__file__\)((?:\s*\.\s*(?:resolve\(\)|parent))+|\.resolve\(\)\.parents\[\d\])"
    )
    offenders: list[str] = []

    for path in sorted(CONTROL_PLANE.rglob("*.py")):
        if path.name == "_paths.py":
            continue  # the marker-walking resolver itself
        # control_plane/x.py needs 2 hops; control_plane/sub/x.py needs 3.
        needed = len(path.relative_to(REPO_ROOT).parts)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines):
            match = chain.search(line)
            if not match:
                continue
            group = match.group(1)
            bracket = re.search(r"parents\[(\d)\]", group)
            hops = int(bracket.group(1)) + 1 if bracket else group.count("parent")
            if "sys.path" in line and hops <= 1:
                continue  # inserting the module's own directory, intentional
            window = " ".join(lines[i:i + 12])
            if not any(f'"{n}"' in window or f"'{n}'" in window for n in root_names):
                continue
            if hops < needed:
                rel = path.relative_to(REPO_ROOT)
                offenders.append(f"{rel}:{i + 1} has {hops} hops, needs {needed}")

    assert not offenders, (
        "fixed-depth repo-root chains found; import REPO_ROOT from "
        "control_plane._paths instead:\n  " + "\n  ".join(offenders)
    )


# ── Fail-closed: RBAC ────────────────────────────────────────────────────────

def test_rbac_loads_a_populated_matrix():
    from control_plane.core.rbac_matrix import RBACMatrix

    rbac = RBACMatrix()
    assert rbac._knights, "access matrix loaded but declares no knights"


def test_rbac_raises_instead_of_degrading_to_empty(monkeypatch):
    """A missing matrix must raise, not silently deny every knight."""
    import control_plane.core.rbac_matrix as rm

    monkeypatch.setattr(rm, "_MATRIX_PATH", Path("/nonexistent/access_matrix.json"))
    rm._load_matrix.cache_clear()
    try:
        with pytest.raises(rm.RBACUnavailableError):
            rm.RBACMatrix()
    finally:
        rm._load_matrix.cache_clear()


def test_rbac_rejects_a_matrix_with_no_knights(monkeypatch, tmp_path):
    import json

    import control_plane.core.rbac_matrix as rm

    empty = tmp_path / "access_matrix.json"
    empty.write_text(json.dumps({"knights": {}, "deny_rules": []}), encoding="utf-8")
    monkeypatch.setattr(rm, "_MATRIX_PATH", empty)
    rm._load_matrix.cache_clear()
    try:
        with pytest.raises(rm.RBACUnavailableError):
            rm.RBACMatrix()
    finally:
        rm._load_matrix.cache_clear()


# ── Fail-closed: Z3 patch verification ───────────────────────────────────────

class _BlockZ3:
    """Meta-path hook that makes ``import z3`` fail, simulating a clean install."""

    def find_module(self, name, path=None):
        return self if name == "z3" else None

    def load_module(self, name):
        raise ImportError("simulated: z3-solver not installed")


@pytest.fixture()
def z3_absent():
    import sys

    hook = _BlockZ3()
    saved = sys.modules.pop("z3", None)
    sys.meta_path.insert(0, hook)
    try:
        yield
    finally:
        sys.meta_path.remove(hook)
        if saved is not None:
            sys.modules["z3"] = saved


def test_dangerous_patch_blocked_even_without_z3(z3_absent):
    """The grounding alone is decisive; a force-push must not pass unverified."""
    from control_plane.z3_verify import PatchIntent, verify_patch

    verdict = verify_patch(PatchIntent(description="git push --force origin main"))
    assert verdict.safe is False
    assert verdict.verdict == "Z3_BLOCK"
    assert "main_branch_protected" in verdict.violated


def test_benign_patch_is_not_declared_safe_without_z3(z3_absent, monkeypatch):
    """No solver means no positive safety claim, absent an explicit opt-out."""
    from control_plane.z3_verify import PatchIntent, verify_patch

    monkeypatch.delenv("CAMELOT_ALLOW_UNVERIFIED_PATCHES", raising=False)
    verdict = verify_patch(PatchIntent(description="add bounded retry logic to api.py"))
    assert verdict.safe is False
    assert verdict.verdict == "Z3_UNAVAILABLE"


def test_explicit_opt_out_allows_unverified_benign_patch(z3_absent, monkeypatch):
    from control_plane.z3_verify import PatchIntent, verify_patch

    monkeypatch.setenv("CAMELOT_ALLOW_UNVERIFIED_PATCHES", "1")
    verdict = verify_patch(PatchIntent(description="add bounded retry logic to api.py"))
    assert verdict.safe is True
    assert verdict.verdict == "Z3_UNAVAILABLE"


def test_opt_out_still_cannot_approve_a_dangerous_patch(z3_absent, monkeypatch):
    monkeypatch.setenv("CAMELOT_ALLOW_UNVERIFIED_PATCHES", "1")
    from control_plane.z3_verify import PatchIntent, verify_patch

    verdict = verify_patch(PatchIntent(description="delete the provenance ledger"))
    assert verdict.safe is False
    assert verdict.verdict == "Z3_BLOCK"


# ── Fail-closed: Kinetic Loop RECORD stage ───────────────────────────────────

def test_provenance_is_actually_recorded():
    from control_plane.kinetic_loop import run_sync

    res = run_sync("build a status dashboard", auto_approve=True)
    assert res.provenance_error is None, res.provenance_error
    assert res.provenance_ref, "RECORD reported success without a provenance ref"
    assert res.complete


def test_unrecordable_run_is_not_reported_complete(monkeypatch):
    """A swallowed ledger failure must not render as ``✓ complete``."""
    import control_plane.infra.kinetic_loop as kl

    def _boom(self, job, res):
        res.provenance_error = "RuntimeError: simulated ledger outage"
        res.provenance_ref = None
        return None

    monkeypatch.setattr(kl.KineticLoop, "_record", _boom)
    res = asyncio.run(kl.KineticLoop().run("build a status dashboard", auto_approve=True))

    assert res.provenance_ref is None
    assert res.provenance_error
    assert not res.complete, "run without a ledger entry must not be complete"
    assert "PROVENANCE FAILED" in res.render()


def test_strict_provenance_raises(monkeypatch):
    import control_plane.infra.kinetic_loop as kl

    def _boom(self, job, res):
        res.provenance_error = "RuntimeError: simulated ledger outage"
        res.provenance_ref = None
        return None

    monkeypatch.setattr(kl.KineticLoop, "_record", _boom)
    loop = kl.KineticLoop(strict_provenance=True)
    with pytest.raises(kl.ProvenanceUnavailableError):
        asyncio.run(loop.run("build a status dashboard", auto_approve=True))
