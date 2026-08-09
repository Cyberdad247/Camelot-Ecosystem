#!/usr/bin/env python3
"""
CAMELOT-OS Branch Management Validation & Configuration
Validates and reports on branch cleanup completion and enforces naming conventions.
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class BranchValidator:
    def __init__(self):
        self.repo_url = "https://github.com/Cyberdad247/Camelot-Ecosystem"
        self.main_branch = "main"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": {},
            "recommendations": [],
            "action_items": []
        }

    def validate_branch_count(self) -> Dict:
        """Validate current branch count."""
        try:
            cmd = "git branch -r | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            count = int(result.stdout.strip())
            
            target = 20  # Target: main + 15-20 active feature/fix branches
            status = "✅ PASS" if count <= target else "⚠️  WARN" if count <= 30 else "❌ FAIL"
            
            return {
                "metric": "Branch Count",
                "current": count,
                "target": target,
                "status": status,
                "description": f"Current branch count: {count} (target: {target})"
            }
        except Exception as e:
            return {
                "metric": "Branch Count",
                "status": "❌ ERROR",
                "error": str(e)
            }

    def validate_main_branch_protection(self) -> Dict:
        """Validate main branch is protected."""
        try:
            # Check if main branch exists and is protected
            cmd = "git ls-remote --heads origin main"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            
            if "main" in result.stdout:
                return {
                    "metric": "Main Branch Protection",
                    "status": "✅ PASS (exists)",
                    "description": "Main branch exists",
                    "action": "⚠️  MANUAL: Verify in GitHub Settings → Branches → Branch Protection Rules"
                }
            else:
                return {
                    "metric": "Main Branch Protection",
                    "status": "❌ FAIL",
                    "description": "Main branch not found"
                }
        except Exception as e:
            return {
                "metric": "Main Branch Protection",
                "status": "❌ ERROR",
                "error": str(e)
            }

    def validate_naming_conventions(self) -> Dict:
        """Validate branch naming conventions."""
        try:
            cmd = "git branch -r | grep -v 'origin/HEAD\\|origin/main'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            
            branches = [b.strip().replace("origin/", "") for b in result.stdout.strip().split('\n') if b.strip()]
            
            valid_prefixes = [
                "feat/", "fix/", "chore/", "docs/", 
                "perf/", "refactor/", "test/", "ci/"
            ]
            
            compliant = 0
            non_compliant = []
            
            for branch in branches:
                if branch == "main":
                    continue
                    
                is_valid = any(branch.startswith(prefix) for prefix in valid_prefixes)
                if is_valid:
                    compliant += 1
                else:
                    non_compliant.append(branch)
            
            compliance_rate = (compliant / len(branches) * 100) if branches else 100
            status = "✅ PASS" if compliance_rate >= 90 else "⚠️  WARN" if compliance_rate >= 70 else "❌ FAIL"
            
            return {
                "metric": "Branch Naming Conventions",
                "status": status,
                "total_branches": len(branches),
                "compliant": compliant,
                "non_compliant": len(non_compliant),
                "compliance_rate": f"{compliance_rate:.1f}%",
                "non_compliant_examples": non_compliant[:5],
                "description": f"{compliance_rate:.1f}% of branches follow naming conventions"
            }
        except Exception as e:
            return {
                "metric": "Branch Naming Conventions",
                "status": "❌ ERROR",
                "error": str(e)
            }

    def validate_auto_cleanup_enabled(self) -> Dict:
        """Validate auto-delete merged branches setting."""
        return {
            "metric": "Auto-delete Merged Branches",
            "status": "⚠️  MANUAL",
            "description": "Must be enabled in GitHub Settings → Branches",
            "steps": [
                "1. Go to Repository Settings",
                "2. Click 'Branches' in sidebar",
                "3. Enable 'Automatically delete head branches' under Merge button settings",
                "4. Save"
            ]
        }

    def validate_recent_activity(self) -> Dict:
        """Check if recently active branches."""
        try:
            cmd = "git for-each-ref --sort=-committerdate --format='%(refname:short)|%(committerdate:unix)' refs/remotes/origin/ | head -5"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            
            branches_info = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                branch = parts[0].replace("origin/", "")
                branches_info.append(branch)
            
            return {
                "metric": "Recent Branch Activity",
                "status": "ℹ️  INFO",
                "description": "Most recently updated branches",
                "recent_branches": branches_info,
                "action": "Verify these are active work branches"
            }
        except Exception as e:
            return {
                "metric": "Recent Branch Activity",
                "status": "⚠️  WARN",
                "error": str(e)
            }

    def run_validation(self):
        """Run all validations."""
        print("\n" + "="*80)
        print("  CAMELOT-OS BRANCH MANAGEMENT VALIDATION")
        print("="*80 + "\n")

        validations = [
            self.validate_branch_count(),
            self.validate_main_branch_protection(),
            self.validate_naming_conventions(),
            self.validate_auto_cleanup_enabled(),
            self.validate_recent_activity(),
        ]

        for validation in validations:
            self._print_validation(validation)
            self.results["validation_results"][validation.get("metric", "Unknown")] = validation

        self._print_summary(validations)
        self._export_results()

    def _print_validation(self, result: Dict):
        """Print a validation result."""
        metric = result.get("metric", "Unknown")
        status = result.get("status", "⚠️  UNKNOWN")
        description = result.get("description", "")
        
        print(f"{status} {metric}")
        if description:
            print(f"     {description}")
        
        if "current" in result and "target" in result:
            print(f"     Current: {result['current']} | Target: {result['target']}")
        
        if "compliance_rate" in result:
            print(f"     Compliance: {result['compliance_rate']} ({result['compliant']}/{result['total_branches']})")
        
        if "non_compliant_examples" in result and result["non_compliant_examples"]:
            print(f"     Non-compliant examples: {', '.join(result['non_compliant_examples'][:3])}")
        
        if "action" in result:
            print(f"     {result['action']}")
        
        if "steps" in result:
            for step in result["steps"]:
                print(f"     {step}")
        
        if "recent_branches" in result:
            for branch in result["recent_branches"]:
                print(f"     • {branch}")
        
        print()

    def _print_summary(self, validations: List[Dict]):
        """Print validation summary."""
        print("="*80)
        print("  SUMMARY")
        print("="*80)
        
        pass_count = sum(1 for v in validations if "✅" in v.get("status", ""))
        warn_count = sum(1 for v in validations if "⚠️" in v.get("status", ""))
        fail_count = sum(1 for v in validations if "❌" in v.get("status", ""))
        
        print(f"\n  ✅ PASS:  {pass_count}")
        print(f"  ⚠️  WARN:  {warn_count}")
        print(f"  ❌ FAIL:  {fail_count}\n")

    def _export_results(self):
        """Export validation results."""
        report_path = Path("data/branch_validation_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"[REPORT SAVED] {report_path}\n")

    def print_implementation_guide(self):
        """Print implementation guide for branch management."""
        guide = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   BRANCH MANAGEMENT IMPLEMENTATION GUIDE                   ║
╚════════════════════════════════════════════════════════════════════════════╝

[PHASE 1] RUN CLEANUP AUDIT & DELETION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Run the audit tool:
     $ python scripts/branch_cleanup_audit.py

  2. Review the generated report:
     $ cat data/branch_audit_report.json

  3. Review the deletion script:
     $ cat scripts/delete_branches.sh

  4. Execute cleanup (phases):
     $ bash scripts/delete_branches.sh

  5. Prune local cache:
     $ git fetch --all --prune


[PHASE 2] ENFORCE BRANCH PROTECTION & NAMING (GITHUB SETTINGS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Navigate to: https://github.com/Cyberdad247/Camelot-Ecosystem/settings/branches

  2A. Main Branch Protection
  ───────────────────────────
  [ ] Enable branch protection rule for 'main'
      Pattern: main
      
      ✓ Require a pull request before merging
        • Require approvals: 1
        • Require review from code owners: (if CODEOWNERS exists)
        • Dismiss stale pull request approvals when new commits are pushed
        • Require approval of the most recent reviewable push
      
      ✓ Require status checks to pass before merging
        • Require branches to be up to date before merging
        • Require passing CI checks: (select forge-ci.yml or equivalent)
      
      ✓ Restrict who can push to matching branches
        • Allow specified actors to bypass required pull requests:
          (leave empty unless you need admin override)


  2B. Auto-delete Merged Branches
  ────────────────────────────────
  In 'Merge button' section, enable:
      ✓ Automatically delete head branches


  2C. Create Branch Naming Ruleset (Optional but Recommended)
  ──────────────────────────────────────────────────────────
  Settings → Code, security, and analysis → Rules → New rule

  Target branches:
    - Exclude: main
    - Include: *

  Enforcement:
    ✓ Require pull request before merging
    ✓ Require status checks to pass
    ✓ Require linear history


[PHASE 3] ADD PRE-COMMIT HOOK FOR BRANCH NAMING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Create: .githooks/check-branch-name.sh

    #!/bin/bash
    branch=$(git rev-parse --abbrev-ref HEAD)
    
    if [[ "$branch" == "main" || "$branch" == "develop" ]]; then
      exit 0
    fi
    
    pattern="^(feat|fix|chore|docs|perf|refactor|test|ci)/"
    if ! [[ $branch =~ $pattern ]]; then
      echo "❌ Branch name does not follow convention: $branch"
      echo "Use: feat/, fix/, chore/, docs/, perf/, refactor/, test/, ci/"
      exit 1
    fi

  Install hook:
    $ git config core.hooksPath .githooks
    $ chmod +x .githooks/check-branch-name.sh


[PHASE 4] UPDATE CONTRIBUTING DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Add to CONTRIBUTING.md or README.md:

    ## Branch Naming Convention

    All branches (except main) MUST follow this format:

      {type}/{description}-{ticket-number}

    Where {type} is one of:
      • feat/    - New feature
      • fix/     - Bug fix
      • chore/   - Build, deps, or tooling changes
      • docs/    - Documentation only
      • perf/    - Performance optimization
      • refactor/ - Code restructuring (no behavior change)
      • test/    - Test additions/improvements
      • ci/      - CI/CD pipeline changes

    Examples:
      ✅ feat/multivoice-router
      ✅ fix/bifrost-dispatch-triage
      ✅ chore/update-dependencies
      ❌ update-stuff
      ❌ test-branch-123


[PHASE 5] VERIFY & DOCUMENT COMPLETION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Run final validation:
    $ python scripts/branch_validation.py

  Commit the audit/cleanup scripts:
    $ git add scripts/branch_cleanup_audit.py scripts/branch_validation.py
    $ git add data/branch_audit_report.json data/branch_validation_report.json
    $ git commit -m "chore: document branch cleanup and management setup"
    $ git push origin main


[SUCCESS CRITERIA]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Branch count reduced from 130+ to ~20-25
  ✅ Main branch protection enabled with PR requirement
  ✅ All remaining branches follow naming convention
  ✅ Auto-delete merged branches enabled
  ✅ Contributing guide updated with branch naming rules
  ✅ Pre-commit hook installed for branch name validation
  ✅ Validation reports committed to repo


[MAINTENANCE]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Run monthly:
    $ python scripts/branch_cleanup_audit.py
    $ python scripts/branch_validation.py

  This identifies stale branches before they accumulate.
"""
        print(guide)


def main():
    validator = BranchValidator()
    validator.run_validation()
    validator.print_implementation_guide()


if __name__ == "__main__":
    main()
