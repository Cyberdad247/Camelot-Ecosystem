#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
VFS Janitorial Sweep — measured resource audit for CAMELOT-OS
============================================================

Reports ACTUAL host and repository resource state. Every number emitted here is
read from the live system via psutil / os.scandir at the moment of the run.
Nothing is modelled, extrapolated, or simulated.

Safety contract
---------------
1. Read-only by default. Deletion requires an explicit ``--apply``.
2. Never deletes virtual environments (.venv), node_modules, or any tracked
   source. Those are classified PROTECTED and reported, never removed.
3. Never deletes git worktrees (.worktrees/) — they hold unmerged commits.
4. Never touches PROVENANCE_LEDGER.md or its mirrors, or any file under 03_VAULT.
5. Every removal is logged to the report with its byte size measured pre-delete.

Usage
-----
    python scripts/vfs_janitorial_sweep.py                # audit only
    python scripts/vfs_janitorial_sweep.py --json         # machine readable
    python scripts/vfs_janitorial_sweep.py --top 25      # deeper listing
    python scripts/vfs_janitorial_sweep.py --apply        # purge SAFE tier
    python scripts/vfs_janitorial_sweep.py --apply --include review
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[1]

GIB = 1024**3

# ── Classification ───────────────────────────────────────────────────────────
# SAFE    : regenerable build output, no source, no VCS state
# REVIEW  : regenerable but expensive to rebuild (needs human call)
# PROTECT : environment, dependency tree, or unmerged work — never auto-removed

SAFE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".turbo",
    ".next",
    ".cache",
    "target",  # rust build output, cargo cleanable
}

REVIEW_DIR_NAMES = {
    "dist",
    "build",
    ".expo",
}

PROTECTED_DIR_NAMES = {
    ".venv",
    "venv",
    "node_modules",
    ".git",
    ".worktrees",
}

# Never descend into these — they are protected or uninteresting.
PRUNE_DIRS = PROTECTED_DIR_NAMES | {"data", "_tmp"}

VAULT_PREFIX = "03_VAULT"
LEDGER_NAMES = {"PROVENANCE_LEDGER.md"}

# Age (in days) after which a SAFE directory is considered stale.
STALE_DAYS = 30

# Set once git availability is probed; None = not yet probed.
_GIT_UNAVAILABLE = False


def _probe_git() -> bool:
    """Confirm git is usable before trusting git_tracked_count()."""
    global _GIT_UNAVAILABLE
    try:
        res = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=30, check=False)
        _GIT_UNAVAILABLE = res.returncode != 0
    except (OSError, subprocess.SubprocessError):
        _GIT_UNAVAILABLE = True
    return not _GIT_UNAVAILABLE


@dataclass
class Finding:
    """One reclaimable directory, classified and measured."""

    path: str
    size_bytes: int
    tier: str
    reason: str
    age_days: int
    removed: bool = False
    error: str = ""

    @property
    def size_gib(self) -> float:
        return self.size_bytes / GIB


@dataclass
class HostReport:
    total_bytes: int
    available_bytes: int
    used_bytes: int
    percent_used: float
    swap_total_bytes: int
    swap_used_bytes: int
    psutil_available: bool
    top_processes: list[dict] = field(default_factory=list)


# ── Measurement ──────────────────────────────────────────────────────────────


def _dir_size(path: Path) -> int:
    """Sum apparent file sizes under path. Never follows symlinks."""
    total = 0
    stack = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        else:
                            total += entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except (PermissionError, OSError):
            continue
    return total


def _dir_age_days(path: Path) -> int:
    try:
        return (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 86400
    except OSError:
        return 0


def _is_protected_path(rel: Path) -> tuple[bool, str]:
    """Hard guard: returns (blocked, reason) for paths that must never be deleted."""
    posix = rel.as_posix()
    if posix.startswith(VAULT_PREFIX):
        return True, "under 03_VAULT (ledger + runtime state)"
    if rel.name in LEDGER_NAMES:
        return True, "provenance ledger"
    if any(part in PROTECTED_DIR_NAMES for part in rel.parts):
        return True, "environment/dependency/VCS path"
    return False, ""


def git_tracked_count(path: Path, root: Path) -> int:
    """Count git-tracked files under path. Returns -1 if git is unavailable.

    Name-based classification alone is unsafe: a source directory that happens
    to be called ``target`` or ``build`` would be swept. Git is the authority on
    what is generated versus authored.
    """
    if _GIT_UNAVAILABLE or not (root / ".git").exists():
        return -1
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--", str(path)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return -1
    if out.returncode != 0:
        return -1
    return len([ln for ln in out.stdout.splitlines() if ln.strip()])


def scan_repository(root: Path) -> list[Finding]:
    """Walk the repo once, classifying every reclaimable directory."""
    findings: list[Finding] = []

    for dirpath, dirnames, _ in os.walk(root, topdown=True):
        current = Path(dirpath)
        rel_dir = current.relative_to(root)

        # Drop never-walk subtrees first. `data/` in particular holds pytest's
        # basetemp, so walking it reports dozens of transient fixture dirs.
        for pruned in [d for d in dirnames if d in PRUNE_DIRS]:
            dirnames.remove(pruned)

        for name in sorted(dirnames):
            candidate = current / name
            # Build the relative path lexically. Calling .resolve() here would
            # anchor the result to os.getcwd() instead of `root`, silently
            # recording the wrong path whenever cwd differs from root.
            rel = Path(os.path.normpath(rel_dir / name))

            blocked, reason = _is_protected_path(rel)
            if blocked:
                dirnames.remove(name)
                continue

            # A symlinked directory can point outside the repository. We do not
            # own what it references, so it is never a purge candidate.
            if candidate.is_symlink():
                dirnames.remove(name)
                continue

            if name in SAFE_DIR_NAMES:
                tier, why = "SAFE", f"regenerable build output ({name})"
            elif name in REVIEW_DIR_NAMES:
                tier, why = "REVIEW", f"regenerable artifact ({name})"
            else:
                continue

            # A candidate holding tracked source is authored, not generated.
            tracked = git_tracked_count(rel, root)
            if tracked > 0:
                tier = "PROTECT"
                why = f"{tracked} git-tracked file(s) — authored source, not build output"

            size = _dir_size(candidate)
            age = int(_dir_age_days(candidate))
            findings.append(
                Finding(
                    path=rel.as_posix(),
                    size_bytes=size,
                    tier=tier,
                    reason=why,
                    age_days=age,
                )
            )
            # Do not descend into a target we already measured.
            dirnames.remove(name)

    findings.sort(key=lambda f: f.size_bytes, reverse=True)
    return findings


def measure_protected(root: Path, names: set[str]) -> list[Finding]:
    """Measure PROTECTED dirs for reporting only. Never returns tier != PROTECT."""
    out: list[Finding] = []
    for dirpath, dirnames, _ in os.walk(root, topdown=True):
        current = Path(dirpath)
        rel_dir = current.relative_to(root)
        for name in sorted(dirnames):
            if name not in names:
                continue
            rel = rel_dir / name
            blocked, reason = _is_protected_path(rel)
            if blocked and "environment" not in reason:
                continue
            out.append(
                Finding(
                    path=rel.as_posix(),
                    size_bytes=_dir_size(current / name),
                    tier="PROTECT",
                    reason=reason or "environment or dependency tree",
                    age_days=int(_dir_age_days(current / name)),
                )
            )
            dirnames.remove(name)
    out.sort(key=lambda f: f.size_bytes, reverse=True)
    return out


def measure_host() -> HostReport:
    if psutil is None:
        return HostReport(0, 0, 0, 0.0, 0, 0, False)

    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()

    top: list[dict] = []
    procs = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            info = proc.info
            if info["memory_info"] is not None:
                procs.append((info["memory_info"].rss, info["name"], info["pid"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(reverse=True)
    for rss, name, pid in procs[:10]:
        top.append({"pid": pid, "name": name, "rss_bytes": rss})

    return HostReport(
        total_bytes=vm.total,
        available_bytes=vm.available,
        used_bytes=vm.used,
        percent_used=vm.percent,
        swap_total_bytes=sw.total,
        swap_used_bytes=sw.used,
        psutil_available=True,
        top_processes=top,
    )


# ── Deletion ─────────────────────────────────────────────────────────────────


def _on_rm_error(func, path, _exc):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def apply_purge(findings: list[Finding], tiers: set[str], root: Path) -> int:
    """Remove findings whose tier is in `tiers`. Returns bytes reclaimed."""
    reclaimed = 0
    for finding in findings:
        if finding.tier not in tiers:
            continue
        target = root / finding.path

        blocked, _ = _is_protected_path(Path(finding.path))
        if blocked:
            finding.error = "blocked by protection guard"
            continue
        if not target.exists():
            continue

        try:
            shutil.rmtree(target, onerror=_on_rm_error)
            finding.removed = True
            reclaimed += finding.size_bytes
        except OSError as exc:
            finding.error = f"{type(exc).__name__}: {exc}"
    return reclaimed


# ── Reporting ────────────────────────────────────────────────────────────────


def _gb(value: int) -> str:
    return f"{value / GIB:.2f} GB"


def print_report(
    host: HostReport,
    findings: list[Finding],
    protected: list[Finding],
    top: int,
    reclaimed: int,
    applied: bool,
) -> None:
    line = "=" * 74
    print(line)
    print("  VFS JANITORIAL SWEEP — measured resource audit")
    print(f"  {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    print(line)

    print("\n[HOST MEMORY]")
    if not host.psutil_available:
        print("  psutil unavailable — cannot measure (pip install psutil)")
    else:
        print(f"  total       {_gb(host.total_bytes):>12}")
        print(f"  used        {_gb(host.used_bytes):>12}  ({host.percent_used:.1f}%)")
        print(f"  available   {_gb(host.available_bytes):>12}")
        print(f"  swap        {_gb(host.swap_used_bytes):>12}  of {_gb(host.swap_total_bytes)}")
        if host.top_processes:
            print("\n  top processes by RSS:")
            for proc in host.top_processes:
                print(f"    {proc['rss_bytes'] / GIB:6.2f} GB  {proc['name']}  (pid {proc['pid']})")

    tiers: dict[str, list[Finding]] = {}
    for finding in findings:
        tiers.setdefault(finding.tier, []).append(finding)

    for tier in ("SAFE", "REVIEW"):
        group = tiers.get(tier, [])
        if not group:
            continue
        total = sum(f.size_bytes for f in group)
        print(f"\n[{tier}] {len(group)} dirs, {_gb(total)} reclaimable")
        for finding in group[:top]:
            state = "REMOVED" if finding.removed else f"age {finding.age_days}d"
            print(f"  {_gb(finding.size_bytes):>10}  {finding.path}  ({state})")
        if len(group) > top:
            print(f"  ... and {len(group) - top} more")

    if protected:
        ptotal = sum(f.size_bytes for f in protected)
        print(f"\n[PROTECT] {len(protected)} dirs, {_gb(ptotal)} — never auto-removed")
        for finding in protected[:top]:
            print(f"  {_gb(finding.size_bytes):>10}  {finding.path}  ({finding.reason})")
        if len(protected) > top:
            print(f"  ... and {len(protected) - top} more")

    print("\n" + line)
    if applied:
        print(f"  RECLAIMED {_gb(reclaimed)} (measured before deletion)")
        failures = [f for f in findings if f.error]
        if failures:
            print(f"  {len(failures)} path(s) failed — rerun to retry")
    else:
        safe = tiers.get("SAFE", [])
        stotal = sum(f.size_bytes for f in safe)
        print("  DRY RUN — no files removed.")
        print(f"  Re-run with --apply to reclaim {_gb(stotal)} of SAFE build output.")
    print(line)


# ── Entry ────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vfs_janitorial_sweep",
        description="Measured RAM/disk audit for CAMELOT-OS. Read-only unless --apply.",
    )
    parser.add_argument("--apply", action="store_true", help="Perform deletions")
    parser.add_argument(
        "--include",
        choices=["safe", "review"],
        default="safe",
        help="Which tier --apply acts on (default: safe)",
    )
    parser.add_argument("--top", type=int, default=15, help="Rows per tier (default: 15)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit 2 if host memory is above --critical-pct",
    )
    parser.add_argument("--critical-pct", type=float, default=90.0, help="Memory alert threshold")
    args = parser.parse_args(argv)

    root = Path(os.path.normpath(REPO_ROOT))
    if not root.exists():
        print(f"repo root not found: {root}", file=sys.stderr)
        return 1
    if not _probe_git():
        print(
            "warning: git unavailable — falling back to name-only classification",
            file=sys.stderr,
        )

    host = measure_host()
    findings = scan_repository(root)
    protected = measure_protected(root, {".venv", "node_modules"})

    reclaimed = 0
    if args.apply:
        tiers = {"SAFE", "REVIEW"} if args.include == "review" else {"SAFE"}
        reclaimed = apply_purge(findings, tiers, root)

    if args.json:
        payload = {
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "repo_root": str(root),
            "host": asdict(host),
            "reclaimable": [asdict(f) for f in findings],
            "protected": [asdict(f) for f in protected],
            "reclaimed_bytes": reclaimed,
            "applied": args.apply,
        }
        print(json.dumps(payload, indent=2))
    else:
        print_report(host, findings, protected, args.top, reclaimed, args.apply)

    if args.fail_on_critical and host.psutil_available:
        if host.percent_used >= args.critical_pct:
            print(
                f"\nCRITICAL: memory {host.percent_used:.1f}% >= {args.critical_pct}% threshold",
                file=sys.stderr,
            )
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
