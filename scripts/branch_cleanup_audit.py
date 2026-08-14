#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""
Legacy Branch Cleanup Audit Tool (Option 3)
Performs basic, synchronous scanning of Git branches and outputs a status report.
"""

import subprocess
import sys


def run_git(args):
    try:
        res = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git execution failed: {e.stderr}", file=sys.stderr)
        return ""

def main():
    print("========================================================")
    print("🧹 Legacy Git Branch Cleanup Audit Tool Active 🧹")
    print("========================================================")
    
    # Get all branches
    branches_raw = run_git(["branch", "-a"])
    if not branches_raw:
        print("No branches found or not a git repository.")
        return
        
    branches = []
    for line in branches_raw.splitlines():
        cleaned = line.strip().replace("* ", "")
        if "HEAD" in cleaned or cleaned == "main" or cleaned == "master":
            continue
        branches.append(cleaned)
        
    print(f"Discovered {len(branches)} total active branches (excluding primary branches).")
    
    # Simple categorizer
    categories = {
        "feat": [],
        "fix": [],
        "docs": [],
        "test/auto": [],
        "other": []
    }
    
    for b in branches:
        b_lower = b.lower()
        if "feat" in b_lower:
            categories["feat"].append(b)
        elif "fix" in b_lower:
            categories["fix"].append(b)
        elif "docs" in b_lower:
            categories["docs"].append(b)
        elif "test" in b_lower or "auto" in b_lower:
            categories["test/auto"].append(b)
        else:
            categories["other"].append(b)
            
    print("\nCategory Breakdown:")
    for cat, list_b in categories.items():
        print(f"  - {cat}: {len(list_b)} branches")
        
    print("\nCleanup Deletion Candidates (Merged or Test):")
    candidates = categories["test/auto"] + categories["docs"]
    for c in candidates[:15]:
        print(f"  [DELETE CANDIDATE] {c}")
    if len(candidates) > 15:
        print(f"  ... and {len(candidates) - 15} more.")
        
    print("\nRecommended next step: Run the full Swarm pipeline using scripts/run_swarm.sh")

if __name__ == "__main__":
    main()
