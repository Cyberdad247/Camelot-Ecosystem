#!/usr/bin/env python3
"""
CAMELOT-OS Branch Cleanup & Audit Tool
Categorizes, audits, and proposes deletions for 130+ branches.
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class BranchAudit:
    def __init__(self):
        self.branches = {}
        self.categories = {
            "auto_test": [],
            "feature": [],
            "fix": [],
            "claude_agent": [],
            "code_health": [],
            "docs": [],
            "jules_task": [],
            "perf": [],
            "misc": [],
            "main": [],
        }
        self.delete_candidates = []
        self.keep_candidates = []

    def get_all_branches(self) -> List[Tuple[str, str, datetime]]:
        """Fetch all branches with commit dates."""
        try:
            cmd = "git for-each-ref --sort=-committerdate --format='%(refname:short)|%(committerdate:iso8601)' refs/remotes/origin/"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            branches = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 2:
                    branch_name = parts[0]
                    try:
                        commit_date = datetime.fromisoformat(parts[1].replace('Z', '+00:00'))
                        branches.append((branch_name, parts[1], commit_date))
                    except (ValueError, IndexError):
                        pass
            return branches
        except Exception as e:
            print(f"[ERROR] Failed to fetch branches: {e}")
            return []

    def is_merged_to_main(self, branch: str) -> bool:
        """Check if branch is merged to main."""
        try:
            cmd = f"git branch -r --no-merged origin/main | grep -q 'origin/{branch}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, check=False)
            return result.returncode != 0  # returncode 0 = not in the list = merged
        except Exception:
            return False

    def categorize_branch(self, branch: str) -> str:
        """Categorize branch by name pattern."""
        if branch == "main":
            return "main"
        elif branch.startswith("add-") and "-tests-" in branch:
            return "auto_test"
        elif branch.startswith("feat/"):
            return "feature"
        elif branch.startswith("fix/"):
            return "fix"
        elif branch.startswith("claude/"):
            return "claude_agent"
        elif branch.startswith("code-health"):
            return "code_health"
        elif branch.startswith("docs/"):
            return "docs"
        elif branch.startswith("jules"):
            return "jules_task"
        elif branch.startswith("perf"):
            return "perf"
        else:
            return "misc"

    def audit(self):
        """Run full audit."""
        print("\n" + "="*70)
        print("  CAMELOT-OS BRANCH AUDIT & CLEANUP")
        print("="*70 + "\n")

        branches = self.get_all_branches()
        print(f"[*] Found {len(branches)} branches (including remotes)\n")

        # Categorize
        for branch_name, commit_date_str, commit_date in branches:
            clean_name = branch_name.replace("origin/", "")
            category = self.categorize_branch(clean_name)
            self.categories[category].append(clean_name)
            self.branches[clean_name] = {
                "date": commit_date,
                "date_str": commit_date_str,
                "category": category,
                "merged": self.is_merged_to_main(clean_name),
                "days_old": (datetime.now(commit_date.tzinfo) - commit_date).days if commit_date.tzinfo else 0
            }

        # Print summary
        print("[CATEGORY SUMMARY]")
        for category, branches_list in self.categories.items():
            if branches_list:
                print(f"  {category:20s}: {len(branches_list):3d} branches")

        # Analyze deletion candidates
        print("\n[DELETION ANALYSIS]")
        self._analyze_deletions()

        # Print recommendations
        self._print_recommendations()

        # Export detailed report
        self._export_report()

    def _analyze_deletions(self):
        """Determine which branches should be deleted."""
        days_threshold = 30
        now = datetime.now(self.branches[list(self.branches.keys())[0]]["date"].tzinfo) if self.branches else datetime.now()

        for branch, info in self.branches.items():
            if branch == "main":
                self.keep_candidates.append(branch)
                continue

            score = 0
            reasons = []

            # Auto-test branches: always delete
            if info["category"] == "auto_test":
                score += 100
                reasons.append("Auto-generated test branch (duplicate)")

            # Jules task branches: delete if merged or 30+ days old
            if info["category"] == "jules_task":
                if info["merged"]:
                    score += 80
                    reasons.append("Merged task branch")
                if info["days_old"] >= days_threshold:
                    score += 50
                    reasons.append(f"Task branch not updated for {info['days_old']} days")

            # Fix branches: keep if recent, delete if merged + old
            if info["category"] == "fix":
                if info["merged"] and info["days_old"] >= days_threshold:
                    score += 60
                    reasons.append(f"Old merged fix branch ({info['days_old']} days)")
                elif not info["merged"] and info["days_old"] >= 60:
                    score += 40
                    reasons.append(f"Unmerged fix branch ({info['days_old']} days old)")

            # Feature branches: keep active ones
            if info["category"] == "feature":
                if info["merged"]:
                    score += 40
                    reasons.append("Merged feature branch")
                elif info["days_old"] >= 60:
                    score += 30
                    reasons.append(f"Stale feature branch ({info['days_old']} days)")

            # Docs branches: can delete after merge
            if info["category"] == "docs":
                if info["merged"]:
                    score += 50
                    reasons.append("Merged documentation branch")

            # Code health: keep if active, delete if old
            if info["category"] == "code_health":
                if info["days_old"] >= days_threshold:
                    score += 40
                    reasons.append(f"Code health refactor ({info['days_old']} days old)")

            if score >= 40:
                self.delete_candidates.append((branch, score, reasons))
            else:
                self.keep_candidates.append(branch)

        self.delete_candidates.sort(key=lambda x: x[1], reverse=True)

    def _print_recommendations(self):
        """Print cleanup recommendations."""
        print(f"\n[CANDIDATES FOR DELETION] ({len(self.delete_candidates)} branches)")
        print("-" * 70)

        if not self.delete_candidates:
            print("  (No candidates identified)")
        else:
            # Group by score tier
            high = [x for x in self.delete_candidates if x[1] >= 80]
            medium = [x for x in self.delete_candidates if 40 <= x[1] < 80]
            low = [x for x in self.delete_candidates if x[1] < 40]

            if high:
                print("\n  [HIGH PRIORITY] Delete immediately")
                for branch, score, reasons in high[:15]:
                    print(f"    - {branch}")
                    for reason in reasons:
                        print(f"      • {reason}")

            if medium:
                print(f"\n  [MEDIUM PRIORITY] Review & delete ({len(medium)} branches)")
                for branch, score, reasons in medium[:10]:
                    merged_status = "✓ merged" if self.branches[branch]["merged"] else "✗ not merged"
                    days = self.branches[branch]["days_old"]
                    print(f"    - {branch} [{merged_status}, {days}d old]")

            if low:
                print(f"\n  [LOW PRIORITY] Keep for now ({len(low)} branches)")

        print(f"\n[KEEP CANDIDATES] ({len(self.keep_candidates)} branches)")
        print("-" * 70)
        keep_active = [b for b in self.keep_candidates if b != "main" and self.branches[b]["days_old"] < 30]
        if keep_active:
            print(f"  Active branches (updated <30 days):")
            for branch in keep_active[:15]:
                info = self.branches[branch]
                print(f"    - {branch:50s} ({info['category']:12s}, {info['days_old']}d old)")

    def _export_report(self):
        """Export detailed JSON report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_branches": len(self.branches),
            "delete_candidates": len(self.delete_candidates),
            "keep_candidates": len(self.keep_candidates),
            "categories": {cat: len(branches) for cat, branches in self.categories.items()},
            "deletion_list": [
                {
                    "branch": branch,
                    "score": score,
                    "reasons": reasons,
                    "merged": self.branches[branch]["merged"],
                    "days_old": self.branches[branch]["days_old"],
                }
                for branch, score, reasons in self.delete_candidates
            ],
            "recommendations": {
                "immediate_action": [
                    f"git push origin --delete {branch}"
                    for branch, score, _ in self.delete_candidates[:20]
                    if score >= 80
                ],
                "review_then_delete": [
                    f"git push origin --delete {branch}"
                    for branch, score, _ in self.delete_candidates
                    if 40 <= score < 80
                ][:30],
            }
        }

        report_path = Path("data/branch_audit_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n[REPORT EXPORTED] {report_path}")

    def print_cleanup_script(self):
        """Generate shell script for cleanup."""
        script_path = Path("scripts/delete_branches.sh")
        
        high_priority = [b for b, s, _ in self.delete_candidates if s >= 80]
        medium_priority = [b for b, s, _ in self.delete_candidates if 40 <= s < 80]

        script_content = f"""#!/bin/bash
# Auto-generated branch cleanup script
# Generated: {datetime.now().isoformat()}
# Review BEFORE executing!

set -e

echo "=================================================="
echo "CAMELOT-OS Branch Cleanup"
echo "=================================================="
echo ""
echo "Total branches to delete: {len(self.delete_candidates)}"
echo "  High priority: {len(high_priority)}"
echo "  Medium priority: {len(medium_priority)}"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# High priority (auto-test, old tasks)
echo ""
echo "[PHASE 1] Deleting high-priority branches ({len(high_priority)})"
"""

        for branch in high_priority:
            script_content += f"""
echo "  Deleting: {branch}"
git push origin --delete {branch} 2>/dev/null || echo "    Already deleted or error"
"""

        script_content += f"""
# Medium priority (old merged branches)
echo ""
echo "[PHASE 2] Deleting medium-priority branches ({len(medium_priority)})"
"""

        for branch in medium_priority[:30]:  # Limit to 30 per phase
            script_content += f"""
echo "  Deleting: {branch}"
git push origin --delete {branch} 2>/dev/null || echo "    Already deleted or error"
"""

        script_content += f"""
echo ""
echo "=================================================="
echo "Cleanup complete!"
echo "Run: git fetch --all --prune"
echo "=================================================="
"""

        with open(script_path, "w") as f:
            f.write(script_content)
        
        import os
        os.chmod(script_path, 0o755)
        print(f"[SCRIPT GENERATED] {script_path}")
        print(f"  Run with: bash {script_path}")


def main():
    audit = BranchAudit()
    audit.audit()
    audit.print_cleanup_script()

    print("\n[NEXT STEPS]")
    print("  1. Review the report: data/branch_audit_report.json")
    print("  2. Review the script: scripts/delete_branches.sh")
    print("  3. Execute cleanup:   bash scripts/delete_branches.sh")
    print("  4. Prune local cache: git fetch --all --prune")
    print("  5. Set branch protections & naming conventions in Settings → Branches")
    print("")


if __name__ == "__main__":
    main()
