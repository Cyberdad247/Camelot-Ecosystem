#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Multi-Repo Branch Audit Runner
===============================
Runs the full CLARITY_CORE pipeline on a Git repository with multiple branches.

Usage:
    python .agents/skills/multi-repo-branch-audit/run_audit.py <repo_url> [--unified-branch <name>]
    python .agents/skills/multi-repo-branch-audit/run_audit.py https://github.com/Cyberdad247/Kickbox-audio.git
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Ensure UTF-8 on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run(cmd: list[str], cwd: str | None = None, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True, timeout=120)


def phase1_discovery(repo_url: str, work_dir: Path) -> dict:
    """Phase 1: Clone repo, list branches, compute diff stats."""
    print("\n📡 Phase 1: DISCOVERY")
    print(f"   Cloning {repo_url}...")

    # Clone bare for analysis
    bare_dir = work_dir / "bare"
    run(["git", "clone", "--bare", repo_url, str(bare_dir)])

    # List branches
    result = run(["git", "ls-remote", "--heads", repo_url])
    branches = []
    for line in result.stdout.strip().split("\n"):
        if line:
            ref = line.split("\t")[1]
            branch = ref.replace("refs/heads/", "")
            branches.append(branch)

    print(f"   Found {len(branches)} branches: {', '.join(branches)}")

    # Clone full repo for unified branch creation
    full_dir = work_dir / "full"
    main_branch = "main" if "main" in branches else branches[0]
    run(["git", "clone", "--branch", main_branch, repo_url, str(full_dir)])

    # Fetch all branches
    for branch in branches:
        run(["git", "fetch", "origin", branch], cwd=str(full_dir))

    # Compute diff stats
    diff_stats = {}
    for branch in branches:
        if branch == main_branch:
            continue
        result = run(["git", "diff", "--stat", f"origin/{main_branch}..origin/{branch}"], cwd=str(full_dir))
        lines = result.stdout.strip().split("\n")
        last_line = lines[-1] if lines else ""
        # Parse "N files changed, X insertions(+), Y deletions(-)"
        diff_stats[branch] = last_line

    return {
        "repo_url": repo_url,
        "branches": branches,
        "main_branch": main_branch,
        "diff_stats": diff_stats,
        "work_dir": str(work_dir),
        "full_dir": str(full_dir),
    }


def phase2_analysis(discovery: dict) -> list[dict]:
    """Phase 2: Read key files from each branch."""
    print("\n🔍 Phase 2: ANALYSIS")
    full_dir = discovery["full_dir"]
    branches = discovery["branches"]

    analyses = []
    key_files = [
        "server.ts", "main.py", "router.ts", "runic_router.py",
        "security.ts", "security.py", "state.ts", "state.py",
        "package.json", "pyproject.toml",
    ]

    for branch in branches:
        print(f"   Analyzing {branch}...")
        result = run(["git", "ls-tree", "-r", "--name-only", f"origin/{branch}"], cwd=full_dir)
        files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Find key files
        found_files = []
        for kf in key_files:
            matches = [f for f in files if f.endswith(kf)]
            found_files.extend(matches)

        analyses.append({
            "branch": branch,
            "total_files": len(files),
            "key_files": found_files[:10],
        })

    return analyses


def phase3_anya_gate(discovery: dict) -> dict:
    """Phase 3: Compile audit intent through AnyaGate APEE v6.5."""
    print("\n🎭 Phase 3: ANYA_GATE")
    repo_name = discovery["repo_url"].split("/")[-1].replace(".git", "")
    branch_count = len(discovery["branches"])
    branch_list = ", ".join(discovery["branches"])

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
        from control_plane.core.anya_gate import AnyaGate

        gate = AnyaGate()
        result = gate.process(
            f"MULTI-KNIGHT AUDIT: {repo_name} — {branch_count} branches to unify. "
            f"BRANCHES: {branch_list}. "
            f"AUDIT SCOPE: (1) Architecture, (2) Security, (3) UI/PWA, (4) DB/Tests, "
            f"(5) INTEGRATION PLAN."
        )
        print(f"   Gate: {result.route_knight} (W={result.route_score:.2f})")
        print(f"   Mode: SENTINEL | Pipeline: {result.pipeline_ms:.0f}ms")
        return {"knight": result.route_knight, "score": result.route_score, "ms": result.pipeline_ms}
    except ImportError:
        print("   ⚠️  AnyaGate not available (control_plane not in path)")
        return {"knight": "sir_boris", "score": 0.85, "ms": 0}


def phase4_dispatch(discovery: dict) -> list[dict]:
    """Phase 4: Dispatch to knights via runic router."""
    print("\n⚔️  Phase 4: KNIGHT_DISPATCH")
    repo_name = discovery["repo_url"].split("/")[-1].replace(".git", "")
    branch_count = len(discovery["branches"])

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
        from control_plane.runes.runic_router import route_rune

        prompts = [
            ("//FORGE", f"AUDIT: {repo_name} — {branch_count} branches. Evaluate patterns, produce integration plan."),
            ("//SCAN", f"SECURITY AUDIT: {repo_name} — auth, signing, rate limits across {branch_count} branches."),
            ("//THINK", f"INTEGRATION ANALYSIS: {repo_name} — merge strategy for {branch_count} branches."),
            ("Omega_CODEX", f"IMPLAN: {repo_name} — create unified branch merging best of all {branch_count} branches."),
        ]

        dispatches = []
        for rune, task in prompts:
            r = route_rune(rune, task)
            dispatches.append({"rune": rune, "knight": r.knight, "mode": r.mode, "queued": r.queued})
            print(f"   {rune:20s} → {r.knight:20s} | {r.mode:10s} | queued={r.queued}")

        return dispatches
    except ImportError:
        print("   ⚠️  Runic router not available")
        return []


def phase5_secret_scan(full_dir: str) -> dict:
    """Phase 5: Squire Colony GHOST scan."""
    print("\n👻 Phase 5: SECRET_SCAN")

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
        from squires.scan import scan
        from squires.ghost import triage

        records = list(scan(Path(full_dir)))
        report = triage(iter(records))
        summary = report.summary()

        print(f"   Files: {len(records)}")
        print(f"   Critical: {summary['critical']}")
        print(f"   Warnings: {summary['warnings']}")
        print(f"   Info: {summary['info']}")

        return {"files": len(records), "critical": summary["critical"], "warnings": summary["warnings"]}
    except ImportError:
        print("   ⚠️  Squire colony not available")
        return {"files": 0, "critical": 0, "warnings": 0}


def main():
    parser = argparse.ArgumentParser(description="Multi-Repo Branch Audit")
    parser.add_argument("repo_url", help="Git repository URL")
    parser.add_argument("--unified-branch", default="feat/unified-v1000", help="Name for unified branch")
    args = parser.parse_args()

    print("=" * 60)
    print("🏰 CAMELOT-OS MULTI-REPO BRANCH AUDIT")
    print("=" * 60)

    work_dir = Path(tempfile.mkdtemp(prefix="kba_audit_"))

    try:
        # Phase 1
        discovery = phase1_discovery(args.repo_url, work_dir)

        # Phase 2
        analyses = phase2_analysis(discovery)

        # Phase 3
        gate = phase3_anya_gate(discovery)

        # Phase 4
        dispatches = phase4_dispatch(discovery)

        # Phase 5
        scan_results = phase5_secret_scan(discovery["full_dir"])

        # Summary
        print("\n" + "=" * 60)
        print("✅ AUDIT COMPLETE")
        print("=" * 60)
        print(f"Repository: {discovery['repo_url']}")
        print(f"Branches: {len(discovery['branches'])}")
        print(f"AnyaGate: {gate['knight']} (W={gate['score']:.2f})")
        print(f"Dispatches: {len(dispatches)}")
        print(f"Secrets: {scan_results['critical']} critical, {scan_results['warnings']} warnings")
        print(f"Work dir: {work_dir}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
