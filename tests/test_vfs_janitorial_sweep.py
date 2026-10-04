#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Pytest suite for scripts/vfs_janitorial_sweep.py + scripts/purge_unused_resources.py.

Both tools delete files, so their safety logic is what matters here. The
guards under test were each the subject of a real bug during development:

1.  Protection guard -- 03_VAULT, PROVENANCE_LEDGER.md, .venv, node_modules,
    .git and .worktrees must never be deletable. A "blocked" verdict that
    silently became "allowed" would destroy ledger and runtime state.
2.  Lexical path construction -- scan_repository() once called
    (Path('.') / name).resolve(), which anchors to os.getcwd() instead of the
    root it was given. Running from a subdirectory then recorded corrupted
    paths (real "target" logged as "apps/target"), so --apply would have
    removed a live source tree and left the actual cache in place.
3.  git-tracked demotion -- classification is name-based, but a source
    directory that happens to be named "target" or "dist" must be protected.
    Git is the authority on generated vs. authored. (This already fires on the
    real repo: 02_FORGE/apps/anya-lyte/.expo holds committed Metro polyfills.)
4.  Cross-tool boundary agreement -- purge_unused_resources.purge_pycache()
    initially deleted 03_VAULT/__pycache__ while the sweep protected it.

Every test that can delete operates on a pytest tmp_path. Module-level
REPO_ROOT / PURGE_TARGETS are rebound via monkeypatch so an import-time
constant can never point a test at the real repository. A session-scoped
canary asserts real protected paths are still present afterwards.

Comments avoid non-ASCII to prevent locale-encoding flakes, matching the
convention documented in tests/test_lockbox_ci.py.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Importable targets -- load as modules without executing main().
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import purge_unused_resources as pur  # type: ignore  # noqa: E402
import vfs_janitorial_sweep as sweep  # type: ignore  # noqa: E402

# Paths that must exist for the whole session. If any disappears, a test
# escaped its tmp_path sandbox and deleted real repository state.
CANARY_PATHS = [
    REPO_ROOT / ".venv" / "Scripts" / "python.exe",
    REPO_ROOT / "PROVENANCE_LEDGER.md",
    REPO_ROOT / "docs" / "PROVENANCE_LEDGER.md",
    REPO_ROOT / "03_VAULT" / "PROVENANCE_LEDGER.md",
    REPO_ROOT / "03_VAULT" / "training" / "configs" / "PROVENANCE_LEDGER.md",
    REPO_ROOT / "squires" / "colony.py",
]


@pytest.fixture(scope="session", autouse=True)
def _real_repo_intact() -> None:
    """Fail the session if a test deleted real repository state."""
    missing_before = [str(p) for p in CANARY_PATHS if not p.exists()]
    assert not missing_before, f"canary precondition failed: {missing_before}"
    yield
    missing_after = [str(p) for p in CANARY_PATHS if not p.exists()]
    assert not missing_after, (
        f"tests deleted real repository paths: {missing_after}. A test escaped its tmp_path sandbox."
    )


# ---------------------------------------------------------------------------
#  fixtures
# ---------------------------------------------------------------------------


def _write(path: Path, size: int = 64) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


def _git(repo: Path, *args: str) -> None:
    res = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    assert res.returncode == 0


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """A throwaway git repository with one commit."""
    subprocess.run(
        ["git", "init", "-q", str(tmp_path)],
        capture_output=True,
        check=True,
    )
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "sweep test")
    _write(tmp_path / "README.md")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "init")
    return tmp_path


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A non-git tree containing build output, source, and protected dirs."""
    _write(tmp_path / "target" / "debug" / "app.exe", 2048)
    _write(tmp_path / "apps" / "pwa" / ".next" / "bundle.js", 1024)
    _write(tmp_path / "src" / "main.py", 512)
    _write(tmp_path / "deploy" / "router" / "dist" / "bundle.js", 3072)
    _write(tmp_path / ".venv" / "lib" / "python.dll", 4096)
    _write(tmp_path / "node_modules" / "dep.js", 1024)
    _write(tmp_path / "03_VAULT" / "runtime_state" / "state.json", 512)
    _write(tmp_path / "PROVENANCE_LEDGER.md", 512)
    _write(tmp_path / "__pycache__" / "mod.pyc", 256)
    return tmp_path


@pytest.fixture
def purge_module(monkeypatch: pytest.MonkeyPatch, tree: Path) -> object:
    """purge_unused_resources rebound onto a throwaway tree.

    PURGE_TARGETS is built at import time from the real REPO_ROOT, so it must
    be replaced explicitly -- rebinding REPO_ROOT alone is not enough.
    """
    monkeypatch.setattr(pur, "REPO_ROOT", tree)
    monkeypatch.setattr(pur, "PURGE_TARGETS", [tree / "target"])
    return pur


# ---------------------------------------------------------------------------
#  1. protection guard
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel",
    [
        "03_VAULT",
        "03_VAULT/runtime_state/foo",
        "PROVENANCE_LEDGER.md",
        "docs/PROVENANCE_LEDGER.md",
        "03_VAULT/training/configs/PROVENANCE_LEDGER.md",
        ".venv",
        "apps/api/.venv",
        "node_modules",
        ".git",
        ".worktrees/feature",
    ],
)
def test_protected_paths_are_blocked(rel: str) -> None:
    blocked, reason = sweep._is_protected_path(Path(rel))
    assert blocked, f"{rel} must be blocked"
    assert reason, "a blocked path must explain why"


@pytest.mark.parametrize("rel", ["target", "apps/pwa/.next", "02_FORGE/.turbo", "dist", "build"])
def test_build_output_is_not_blocked(rel: str) -> None:
    blocked, _ = sweep._is_protected_path(Path(rel))
    assert not blocked, f"{rel} is build output and must remain purgeable"


# ---------------------------------------------------------------------------
#  2. scan: paths, tiers, cwd independence
# ---------------------------------------------------------------------------


def test_scan_finds_build_output(tree: Path) -> None:
    found = {f.path for f in sweep.scan_repository(tree)}
    assert "target" in found
    assert "apps/pwa/.next" in found
    assert "__pycache__" in found


def test_scan_never_yields_protected_paths(tree: Path) -> None:
    for finding in sweep.scan_repository(tree):
        blocked, _ = sweep._is_protected_path(Path(finding.path))
        assert not blocked, f"{finding.path} is protected but was emitted"


def test_scan_does_not_descend_into_measured_targets(tree: Path) -> None:
    """target/ is measured once, never re-emitted for its children."""
    paths = [f.path for f in sweep.scan_repository(tree)]
    assert not any(p.startswith("target/") for p in paths)


def test_scan_is_cwd_independent(tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: paths once anchored to os.getcwd() instead of `root`.

    With cwd inside the tree, a .resolve()-based implementation recorded
    "apps/target" for the real "target" and invented "apps/apps/..." entries.
    """
    baseline = {f.path: f.size_bytes for f in sweep.scan_repository(tree)}

    for cwd in (tree, tree / "src", REPO_ROOT, Path(os.sep)):
        monkeypatch.chdir(cwd)
        current = sweep.scan_repository(tree)
        assert {f.path for f in current} == set(baseline), f"scan differs when cwd={cwd}"
        # Every reported path must exist under root.
        for finding in current:
            assert (tree / finding.path).exists(), f"reported {finding.path} does not exist under root (cwd={cwd})"


def test_scan_is_deterministic(tree: Path) -> None:
    first = sweep.scan_repository(tree)
    second = sweep.scan_repository(tree)
    assert [f.path for f in first] == [f.path for f in second]


def test_scan_sorts_by_size_descending(tree: Path) -> None:
    sizes = [f.size_bytes for f in sweep.scan_repository(tree)]
    assert sizes == sorted(sizes, reverse=True)


def test_scan_skips_symlinked_dirs_pointing_outside_tree(tree: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    """A symlinked directory can reference trees we do not own.

    Regression: a symlink named ``build`` (a REVIEW-tier name) pointing outside
    the root was previously reported as a purge candidate.
    """
    outside = tmp_path_factory.mktemp("outside")
    _write(outside / "precious.txt", 4096)
    try:
        os.symlink(outside, tree / "build", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable on this host")

    assert os.path.isdir(tree / "build")
    reported = {f.path for f in sweep.scan_repository(tree)}
    assert "build" not in reported, "symlinked dir must not be a purge candidate"
    assert (outside / "precious.txt").exists()


def test_scan_never_reports_a_path_resolving_outside_root(tree: Path) -> None:
    for finding in sweep.scan_repository(tree):
        resolved = (tree / finding.path).resolve()
        assert str(resolved).startswith(str(tree.resolve())), f"{finding.path} resolves outside the root"


# ---------------------------------------------------------------------------
#  3. git-tracked demotion
# ---------------------------------------------------------------------------


def test_tracked_source_named_target_is_protected(git_repo: Path) -> None:
    _write(git_repo / "target" / "important.py")
    _git(git_repo, "add", "-A")
    _git(git_repo, "commit", "-qm", "add target source")

    findings = {f.path: f for f in sweep.scan_repository(git_repo)}
    assert "target" in findings
    assert findings["target"].tier == "PROTECT"
    assert "git-tracked" in findings["target"].reason


def test_untracked_target_is_purgeable(git_repo: Path) -> None:
    _write(git_repo / "target" / "debug" / "app.exe")
    findings = {f.path: f for f in sweep.scan_repository(git_repo)}
    assert findings["target"].tier == "SAFE"


def test_git_tracked_count_reports_zero_for_generated(git_repo: Path) -> None:
    _write(git_repo / ".next" / "out.js")
    assert sweep.git_tracked_count(Path(".next"), git_repo) == 0


def test_git_tracked_count_negative_without_git(tmp_path: Path) -> None:
    """Non-git trees fall back to name rules rather than blocking everything."""
    assert sweep.git_tracked_count(Path("target"), tmp_path) == -1


# ---------------------------------------------------------------------------
#  4. apply_purge refuses protected paths even when tier is spoofed
# ---------------------------------------------------------------------------


def test_apply_purge_refuses_spoofed_protected_finding(tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A Finding claiming tier=SAFE must not be able to delete .venv."""
    monkeypatch.setattr(sweep, "REPO_ROOT", tree)
    spoofed = sweep.Finding(
        path=".venv",
        size_bytes=4096,
        tier="SAFE",  # deliberately wrong
        reason="spoofed",
        age_days=0,
    )
    freed = sweep.apply_purge([spoofed], {"SAFE"}, tree)
    assert freed == 0
    assert spoofed.error
    assert (tree / ".venv" / "lib" / "python.dll").exists()


@pytest.mark.parametrize("rel", ["03_VAULT/runtime_state", "PROVENANCE_LEDGER.md", "node_modules"])
def test_apply_purge_refuses_each_protected_path(tree: Path, rel: str) -> None:
    before = sweep._dir_size(tree / rel)
    findings = [sweep.Finding(path=rel, size_bytes=before, tier="SAFE", reason="", age_days=0)]
    freed = sweep.apply_purge(findings, {"SAFE"}, tree)
    assert freed == 0, f"{rel} must never be reclaimed"
    assert (tree / rel).exists(), f"{rel} must survive"


def test_apply_purge_removes_only_selected_tier(tree: Path) -> None:
    findings = sweep.scan_repository(tree)
    review = [f for f in findings if f.tier == "REVIEW"]
    if not review:
        pytest.skip("no REVIEW-tier fixture present")

    safe_only = sweep.apply_purge(findings, {"SAFE"}, tree)
    assert safe_only > 0
    for finding in review:
        assert not finding.removed, "REVIEW tier purged without being selected"
        assert (tree / finding.path).exists()


def test_apply_purge_leaves_source_and_ledgers(tree: Path) -> None:
    findings = sweep.scan_repository(tree)
    sweep.apply_purge(findings, {"SAFE", "REVIEW"}, tree)
    for rel in (
        "src/main.py",
        ".venv/lib/python.dll",
        "node_modules/dep.js",
        "03_VAULT/runtime_state/state.json",
        "PROVENANCE_LEDGER.md",
    ):
        assert (tree / rel).exists(), f"{rel} must survive a full SAFE+REVIEW purge"


# ---------------------------------------------------------------------------
#  5. purge_unused_resources: check_target
# ---------------------------------------------------------------------------


def test_check_target_refuses_node_modules(purge_module, tree: Path) -> None:
    allowed, reason = pur.check_target(tree / "node_modules")
    assert not allowed
    assert "environment" in reason or "dependency" in reason


def test_check_target_refuses_path_outside_root(
    purge_module, tree: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("elsewhere")
    allowed, reason = pur.check_target(outside)
    assert not allowed
    assert "outside" in reason


def test_check_target_permits_untracked_target(purge_module, tree: Path) -> None:
    allowed, reason = pur.check_target(tree / "target")
    assert allowed
    assert "untracked" in reason or "name-based" in reason


def test_check_target_refuses_tracked_target(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # REPO_ROOT must be rebound so check_target consults the fixture repo's own
    # git. Left unbound it would consult CAMELOT_OS's index, where the tmp
    # fixture is simply untracked.
    monkeypatch.setattr(pur, "REPO_ROOT", git_repo)
    _write(git_repo / "target" / "real_source.py")
    _git(git_repo, "add", "-A")
    _git(git_repo, "commit", "-qm", "track target source")

    allowed, reason = pur.check_target(git_repo / "target")
    assert not allowed
    assert "git-tracked" in reason


def test_purge_main_is_dry_run_by_default(purge_module, capsys) -> None:
    assert pur.main([]) == 0
    out = capsys.readouterr().out
    assert "DRY RUN" in out
    assert (pur.REPO_ROOT / "target").exists(), "dry run must not delete"


def test_purge_main_apply_removes_target(purge_module) -> None:
    assert pur.main(["--apply"]) == 0
    assert not (pur.REPO_ROOT / "target").exists()
    assert (pur.REPO_ROOT / "src" / "main.py").exists()
    assert (pur.REPO_ROOT / ".venv" / "lib" / "python.dll").exists()


def test_purge_main_refusal_is_reported(purge_module, tree: Path, capsys) -> None:
    _write(tree / "target" / "keep.py")
    _write(tree / "target" / "keep.py")  # untracked, still purgeable
    pur.PURGE_TARGETS.append(tree / "node_modules")
    assert pur.main(["--apply"]) == 0
    out = capsys.readouterr().out
    assert "REFUSED" in out
    assert (tree / "node_modules" / "dep.js").exists()


def test_purge_json_shape(purge_module) -> None:
    assert pur.main(["--json"]) == 0


# ---------------------------------------------------------------------------
#  6. cross-tool boundary agreement
# ---------------------------------------------------------------------------


def test_pycache_purge_skips_protected_trees(purge_module, tree: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: 03_VAULT/__pycache__ was deleted while sweep protected it."""
    _write(tree / ".venv" / "__pycache__" / "y.pyc")
    _write(tree / "node_modules" / "pkg" / "__pycache__" / "c.pyc")
    _write(tree / "03_VAULT" / "__pycache__" / "e.pyc")
    _write(tree / "src" / "__pycache__" / "d.pyc")

    pur.purge_pycache(apply_changes=True)

    assert not (tree / "__pycache__").exists(), "plain __pycache__ should be purged"
    assert not (tree / "src" / "__pycache__").exists(), "src cache should be purged"
    for rel in (
        ".venv/__pycache__",
        "node_modules/pkg/__pycache__",
        "03_VAULT/__pycache__",
    ):
        assert (tree / rel).exists(), f"{rel} must be skipped"


def test_purge_pycache_dry_run_purges_nothing(purge_module, tree: Path) -> None:
    pur.purge_pycache(apply_changes=False)
    assert (tree / "__pycache__" / "mod.pyc").exists()


def test_sweep_and_purge_agree_on_protected_names() -> None:
    """Both tools must refuse the same directory names."""
    for name in sorted(sweep.PROTECTED_DIR_NAMES):
        blocked, _ = sweep._is_protected_path(Path(name))
        assert blocked, f"{name} is protected in the sweep"


# ---------------------------------------------------------------------------
#  7. host measurement + CLI contract
# ---------------------------------------------------------------------------


def test_measure_host_reports_psutil_or_none() -> None:
    report = sweep.measure_host()
    if not report.psutil_available:
        pytest.skip("psutil not installed")
    assert report.total_bytes > 0
    assert 0.0 <= report.percent_used <= 100.0
    assert len(report.top_processes) <= 10


def test_measure_host_json_serialisable() -> None:
    import json
    from dataclasses import asdict

    json.dumps(asdict(sweep.measure_host()))


def test_fail_on_critical_exits_two(monkeypatch: pytest.MonkeyPatch) -> None:
    from dataclasses import replace

    hot = replace(
        sweep.measure_host(),
        percent_used=97.5,
        psutil_available=True,
    )
    monkeypatch.setattr(sweep, "measure_host", lambda: hot)
    monkeypatch.setattr(sweep, "scan_repository", lambda root: [])
    monkeypatch.setattr(sweep, "measure_protected", lambda root, names: [])
    monkeypatch.setattr(sweep, "REPO_ROOT", REPO_ROOT)
    assert sweep.main(["--fail-on-critical", "--critical-pct", "90"]) == 2


def test_below_threshold_exits_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    from dataclasses import replace

    cool = replace(
        sweep.measure_host(),
        percent_used=42.0,
        psutil_available=True,
    )
    monkeypatch.setattr(sweep, "measure_host", lambda: cool)
    monkeypatch.setattr(sweep, "scan_repository", lambda root: [])
    monkeypatch.setattr(sweep, "measure_protected", lambda root, names: [])
    monkeypatch.setattr(sweep, "REPO_ROOT", REPO_ROOT)
    assert sweep.main(["--fail-on-critical", "--critical-pct", "90"]) == 0


def test_sweep_json_output_parses(purge_module) -> None:
    assert sweep.main(["--json"]) == 0


def test_scan_prunes_data_and_tmp(tree: Path) -> None:
    """`data/` holds pytest's basetemp; walking it reports transient fixtures.

    Regression: PRUNE_DIRS was declared but never applied, so the sweep
    descended into data/ and surfaced dozens of empty fixture directories.
    """
    _write(tree / "data" / ".pytest_temp" / "test_x0" / "target" / "a.bin", 2048)
    _write(tree / "_tmp" / "scratch" / "target" / "b.bin", 2048)
    _write(tree / "data" / ".pytest_temp" / "__pycache__" / "c.pyc", 2048)

    paths = {f.path for f in sweep.scan_repository(tree)}
    assert not any(p.startswith("data/") for p in paths), "data/ must be pruned"
    assert not any(p.startswith("_tmp") for p in paths), "_tmp must be pruned"
    # The tree's genuine build output is still found.
    assert "target" in paths


# ---------------------------------------------------------------------------
#  8. real-repo invariants (read-only assertions)
# ---------------------------------------------------------------------------


def test_real_repo_ledger_mirrors_exist() -> None:
    mirrors = [
        REPO_ROOT / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "03_VAULT" / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "docs" / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "03_VAULT" / "training" / "configs" / "PROVENANCE_LEDGER.md",
    ]
    for mirror in mirrors:
        assert mirror.exists(), f"ledger mirror missing: {mirror}"


def test_real_repo_protected_dirs_are_protected() -> None:
    """The real repo's env/dep trees must classify as PROTECT."""
    for rel in (".venv", "node_modules"):
        blocked, _ = sweep._is_protected_path(Path(rel))
        assert blocked
