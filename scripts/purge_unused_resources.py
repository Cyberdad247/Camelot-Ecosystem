#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
r"""
Camelot-OS Resource Reduction & Safe Directory Purge Engine
============================================================

Purges an explicit allowlist of stale build output. Classification and safety
guards are delegated to scripts/vfs_janitorial_sweep.py so that both tools
agree on what is generated versus authored.

Safety contract
---------------
1. Dry run by default. Deletion requires an explicit ``--apply``.
2. Only paths on PURGE_TARGETS are ever considered.
3. Any target with git-tracked content is refused (name collisions are real:
   a source directory named ``target`` must never be deleted).
4. Virtual environments, node_modules, .git, .worktrees and anything under
   03_VAULT are refused unconditionally.
5. Refused targets are reported with the reason, not silently skipped.

Usage
-----
    python scripts/purge_unused_resources.py
    python scripts/purge_unused_resources.py --apply
    python scripts/purge_unused_resources.py --apply --include review
    python scripts/purge_unused_resources.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vfs_janitorial_sweep import (  # noqa: E402
    GIB,
    _dir_size,
    _is_protected_path,
    _probe_git,
    git_tracked_count,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Explicit allowlist. Nothing outside this list is ever deleted.
# Entries that no longer exist are reported as absent, not treated as errors.
PURGE_TARGETS = [
    # 1. Stale Rust Build Targets
    REPO_ROOT / "target",
    REPO_ROOT / "02_FORGE" / "KINETIC_ARMORY" / "target",
    REPO_ROOT / "02_FORGE" / "kinetic" / "target",
    REPO_ROOT / "02_FORGE" / "excalibur-dev" / "target",
    REPO_ROOT / "kinetic_edge" / "target",
    # 2. Stale Duplicate node_modules
    REPO_ROOT / "02_FORGE" / "node_modules",
    # 3. Ephemeral Caches
    REPO_ROOT / ".cache",
    REPO_ROOT / "data" / "go-build",
    REPO_ROOT / "data" / ".pytest_temp",
    REPO_ROOT / ".pytest_cache",
]

# Paths that were historically purged but are retained deliberately.
# Listed so their absence from PURGE_TARGETS is intentional and auditable.
RETIRED_TARGETS = [
    # Nested clones / backups. Destructive to remove and may hold unmerged work.
    "kickbox-audio",
    "free-claude-code",
    "Camelot-OS_vMAX_Singularity",
    "camelot-fable-25",
    "_tmp",
    "Next development",
]


def remove_readonly(func, path, excinfo):
    """rmtree error handler: clear the read-only bit and retry once."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def get_dir_size(path: Path) -> int:
    """Sum file sizes under path without following symlinks."""
    return _dir_size(path)


def check_target(target: Path) -> tuple[bool, str]:
    """Decide whether `target` may be deleted. Returns (allowed, reason).

    Order matters: protection guards run before the git check so that a
    misconfigured environment is refused for the clearest possible reason.
    """
    try:
        rel = Path(os.path.normpath(target.relative_to(REPO_ROOT)))
    except ValueError:
        return False, "outside repository root"

    blocked, reason = _is_protected_path(rel)
    if blocked:
        return False, reason

    if not (REPO_ROOT / ".git").exists():
        return True, "no git context; name-based allowlist only"

    tracked = git_tracked_count(rel, REPO_ROOT)
    if tracked < 0:
        return True, "git unavailable; name-based allowlist only"
    if tracked > 0:
        return False, f"{tracked} git-tracked file(s) — authored source, refusing"

    return True, "untracked build output"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="purge_unused_resources",
        description="Safely purge stale build output. Dry run unless --apply.",
    )
    parser.add_argument("--apply", action="store_true", help="Perform deletions")
    parser.add_argument(
        "--include",
        choices=["safe", "review"],
        default="safe",
        help="Purge SAFE tier only, or SAFE+REVIEW (default: safe)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--purge-pycache",
        action="store_true",
        help="Also purge __pycache__ outside protected trees",
    )
    args = parser.parse_args(argv)

    if not REPO_ROOT.exists():
        print(f"repo root not found: {REPO_ROOT}", file=sys.stderr)
        return 1
    if not _probe_git():
        print(
            "warning: git unavailable — falling back to name-only classification",
            file=sys.stderr,
        )

    # Explicit allowlist is tiered: dist/build are regenerable but expensive to
    # rebuild, so they only qualify when --include review is passed.
    review_names = {"dist", "build"}
    purged: list[dict] = []
    refused: list[dict] = []
    absent: list[str] = []

    for target in PURGE_TARGETS:
        if not target.exists():
            absent.append(os.path.normpath(str(target.relative_to(REPO_ROOT))))
            continue

        rel = Path(os.path.normpath(target.relative_to(REPO_ROOT)))
        if rel.name in review_names and args.include != "review":
            absent.append(f"{rel.as_posix()} (REVIEW tier — pass --include review to purge)")
            continue

        allowed, reason = check_target(target)
        rel_str = str(rel)
        if not allowed:
            refused.append({"path": rel_str, "reason": reason})
            continue

        size = get_dir_size(target)
        if args.apply:
            try:
                shutil.rmtree(target, onerror=remove_readonly)
                purged.append({"path": rel_str, "size_bytes": size, "reason": reason})
            except OSError as exc:
                refused.append({"path": rel_str, "reason": f"delete failed: {exc}"})
        else:
            purged.append({"path": rel_str, "size_bytes": size, "reason": reason})

    pycache_purged: list[dict] = []
    if args.purge_pycache:
        pycache_purged = purge_pycache(apply_changes=args.apply)

    reclaimable = sum(item["size_bytes"] for item in purged)
    if args.apply:
        reclaimable += sum(item["size_bytes"] for item in pycache_purged)

    if args.json:
        print(
            json.dumps(
                {
                    "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "applied": args.apply,
                    "tier": args.include,
                    "purged": purged,
                    "refused": refused,
                    "absent": absent,
                    "pycache_purged": pycache_purged,
                    "reclaimable_bytes": reclaimable,
                    "retired_targets_never_purged": RETIRED_TARGETS,
                },
                indent=2,
            )
        )
    else:
        line = "=" * 74
        print(line)
        print("  CAMELOT-OS SAFE RESOURCE PURGE")
        print(f"  {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
        print(line)

        print(f"\n[SCANNED] {len(PURGE_TARGETS)} allowlisted targets")
        for item in purged:
            print(
                f"  {'REMOVED' if args.apply else 'WOULD PURGE':>12}"
                f"  {item['size_bytes'] / GIB:7.2f} GB  {item['path']}"
            )
        for item in refused:
            print(f"  {'REFUSED':>12}            {item['path']}  ({item['reason']})")
        if absent:
            print(f"\n[ABSENT] {len(absent)} target(s) not on disk:")
            for path in absent:
                print(f"            {path}")

        if args.purge_pycache:
            pc_total = sum(i["size_bytes"] for i in pycache_purged)
            print(f"\n[PYCACHE] {len(pycache_purged)} dirs, {pc_total / GIB:.2f} GB")

        print("\n[RETIRED] never purged by this tool:")
        for name in RETIRED_TARGETS:
            print(f"            {name}")

        print("\n" + line)
        if args.apply:
            print(f"  RECLAIMED {reclaimable / GIB:.2f} GB (measured before deletion)")
        else:
            print("  DRY RUN — no files removed.")
            print(f"  Re-run with --apply to reclaim {reclaimable / GIB:.2f} GB.")
        print(line)

    return 0


def purge_pycache(apply_changes: bool) -> list[dict]:
    """Purge __pycache__ dirs, skipping protected trees.

    Walks with pruning so node_modules and virtualenvs are never traversed.
    """
    from vfs_janitorial_sweep import PROTECTED_DIR_NAMES

    results: list[dict] = []
    for dirpath, dirnames, _ in os.walk(REPO_ROOT, topdown=True):
        current = Path(dirpath)
        rel_dir = Path(os.path.normpath(current.relative_to(REPO_ROOT)))

        for name in list(dirnames):
            if name in PROTECTED_DIR_NAMES or name in {"data", ".git"}:
                dirnames.remove(name)
                continue
            if name != "__pycache__":
                continue
            candidate = current / name
            # Honour the same 03_VAULT boundary the sweep enforces, so the two
            # tools can never disagree about what is off-limits.
            blocked, _reason = _is_protected_path(Path(os.path.normpath(rel_dir / name)))
            if blocked:
                dirnames.remove(name)
                continue
            size = _dir_size(candidate)
            results.append(
                {
                    "path": (rel_dir / name).as_posix(),
                    "size_bytes": size,
                    "removed": False,
                }
            )
            if apply_changes:
                try:
                    shutil.rmtree(candidate, onerror=remove_readonly)
                    results[-1]["removed"] = True
                except OSError:
                    results.pop()
            dirnames.remove(name)
    return results


if __name__ == "__main__":
    raise SystemExit(main())
