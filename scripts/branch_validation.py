#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""
Legacy Branch Validation Tool (Option 3)
Synchronously checks naming compliance of Git branches.
"""

import subprocess
import sys

COMPLIANT_PREFIXES = ["feat/", "fix/", "chore/", "docs/", "perf/", "refactor/", "test/", "ci/", "claude/"]

def run_git(args):
    try:
        res = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git execution failed: {e.stderr}", file=sys.stderr)
        return ""

def main():
    print("========================================================")
    print("🛡️  Legacy Git Branch Validation Scan Active 🛡️")
    print("========================================================")
    
    raw_branches = run_git(["branch", "-a"])
    if not raw_branches:
        print("No branches found.")
        return
        
    violations = []
    compliant_count = 0
    total = 0
    
    for line in raw_branches.splitlines():
        cleaned = line.strip().replace("* ", "").replace("remotes/origin/", "")
        if "HEAD" in cleaned or cleaned == "main" or cleaned == "master" or not cleaned:
            continue
            
        total += 1
        is_compliant = False
        for prefix in COMPLIANT_PREFIXES:
            if cleaned.startswith(prefix):
                is_compliant = True
                break
                
        if is_compliant:
            compliant_count += 1
        else:
            violations.append(cleaned)
            
    compliance_pct = (compliant_count / total) * 100 if total else 100.0
    print(f"Audit Complete. Naming Compliance: {compliance_pct:.2f}% ({compliant_count}/{total})")
    
    if violations:
        print("\nNon-Compliant Branch Violations:")
        for v in violations[:20]:
            print(f"  ❌ {v}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more.")
    else:
        print("\n✅ All branches are 100% compliant with standard prefix naming rules.")

if __name__ == "__main__":
    main()
