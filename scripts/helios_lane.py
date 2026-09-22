# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Helios Parallel Lane & Worktree Orchestrator CLI.
=====================================================
Manages isolated git worktrees for parallel agent development lanes complying
with HELIOS_PARALLEL_IMPLEMENTATION_DAG.md.

Commands:
    python scripts/helios_lane.py create <lane> <task> [--node-id H-XXX] [--dg-id DG-XXX]
    python scripts/helios_lane.py list
    python scripts/helios_lane.py status <lane> <task>
    python scripts/helios_lane.py handoff <lane> <task>
    python scripts/helios_lane.py remove <lane> <task> [--force]
"""
from __future__ import annotations

import argparse
import datetime
from datetime import timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKTREES_DIR = REPO_ROOT / ".worktrees"


def _run_git(args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def sanitize_identifier(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip().lower())


def get_lane_paths(lane: str, task: str) -> tuple[str, str, Path]:
    s_lane = sanitize_identifier(lane)
    s_task = sanitize_identifier(task)
    branch = f"reforge/helios/{s_lane}/{s_task}"
    folder_name = f"helios_{s_lane}_{s_task}"
    worktree_path = WORKTREES_DIR / folder_name
    return branch, folder_name, worktree_path


def create_lane(
    lane: str,
    task: str,
    node_id: str = "H-XXX",
    dg_id: str = "DG-XXX",
) -> Dict[str, Any]:
    """Create isolated git worktree and scaffold HANDOFF.yaml template."""
    branch, folder_name, worktree_path = get_lane_paths(lane, task)
    WORKTREES_DIR.mkdir(parents=True, exist_ok=True)

    if worktree_path.exists():
        return {
            "status": "EXISTS",
            "message": f"Worktree already exists at {worktree_path}",
            "branch": branch,
            "path": str(worktree_path),
        }

    # Check if branch exists
    chk_branch = _run_git(["branch", "--list", branch])
    branch_exists = bool(chk_branch.stdout.strip())

    if branch_exists:
        res = _run_git(["worktree", "add", str(worktree_path), branch])
    else:
        res = _run_git(["worktree", "add", "-b", branch, str(worktree_path)])

    if res.returncode != 0:
        return {
            "status": "ERROR",
            "message": f"git worktree add failed: {res.stderr.strip()}",
        }

    # Scaffold HANDOFF.yaml template inside worktree
    now_iso = datetime.datetime.now(timezone.utc).isoformat()
    handoff_content = f"""# HELIOS AGENT HANDOFF RECEIPT
# Generated automatically by scripts/helios_lane.py
nodeId: "{node_id}"
canonicalDgId: "{dg_id}"
branch: "{branch}"
lane: "{lane}"
task: "{task}"
createdAt: "{now_iso}"
commits: []
filesChanged: []
contractsChanged: []
testsAdded: []
testsPassed: 0
testsFailed: 0
lintStatus: "PENDING"
compatibilityImpact: "BACKWARD_COMPATIBLE"
securityImpact: ""
rollbackPlan: ""
unresolved: []
evidenceRefs: []
recommendedNextState: "IN_PROGRESS"
"""
    handoff_file = worktree_path / "HANDOFF.yaml"
    handoff_file.write_text(handoff_content, encoding="utf-8")

    return {
        "status": "CREATED",
        "branch": branch,
        "worktree_path": str(worktree_path),
        "handoff_file": str(handoff_file),
    }


def list_lanes() -> List[Dict[str, Any]]:
    """List all registered worktrees and their status."""
    res = _run_git(["worktree", "list", "--porcelain"])
    lines = res.stdout.splitlines()
    worktrees = []
    current: Dict[str, str] = {}

    for line in lines:
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
        elif line.startswith("HEAD "):
            current["commit"] = line.split(" ", 1)[1][:8]

    if current:
        worktrees.append(current)

    helios_lanes = []
    for wt in worktrees:
        wt_path = Path(wt["path"])
        if ".worktrees" in str(wt_path) and "helios_" in wt_path.name:
            has_handoff = (wt_path / "HANDOFF.yaml").exists()
            helios_lanes.append({
                "name": wt_path.name,
                "branch": wt.get("branch", "detached"),
                "commit": wt.get("commit", "unknown"),
                "path": str(wt_path),
                "has_handoff": has_handoff,
            })

    return helios_lanes


def remove_lane(lane: str, task: str, force: bool = False) -> Dict[str, Any]:
    """Safely remove a worktree and prune."""
    branch, folder_name, worktree_path = get_lane_paths(lane, task)
    if not worktree_path.exists():
        return {"status": "NOT_FOUND", "message": f"No worktree found at {worktree_path}"}

    args = ["worktree", "remove", str(worktree_path)]
    if force:
        args.append("--force")

    res = _run_git(args)
    _run_git(["worktree", "prune"])

    if res.returncode != 0:
        return {"status": "ERROR", "message": res.stderr.strip()}

    return {"status": "REMOVED", "branch": branch, "path": str(worktree_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Helios Parallel Lane Orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = subparsers.add_parser("create", help="Create isolated development lane worktree")
    p_create.add_argument("lane", help="Lane category (e.g. contracts, ops, security, ci)")
    p_create.add_argument("task", help="Task name (e.g. registry-lock, telemetry-slo)")
    p_create.add_argument("--node-id", default="H-XXX", help="Helios DAG node ID")
    p_create.add_argument("--dg-id", default="DG-XXX", help="Canonical DG Task ID")

    # list
    subparsers.add_parser("list", help="List all active Helios lanes")

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove lane worktree")
    p_remove.add_argument("lane", help="Lane category")
    p_remove.add_argument("task", help="Task name")
    p_remove.add_argument("--force", action="store_true", help="Force removal")

    args = parser.parse_args()

    if args.command == "create":
        res = create_lane(args.lane, args.task, args.node_id, args.dg_id)
        print(json.dumps(res, indent=2))
        return 0 if res["status"] in ("CREATED", "EXISTS") else 1

    elif args.command == "list":
        lanes = list_lanes()
        print(json.dumps(lanes, indent=2))
        return 0

    elif args.command == "remove":
        res = remove_lane(args.lane, args.task, args.force)
        print(json.dumps(res, indent=2))
        return 0 if res["status"] == "REMOVED" else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
