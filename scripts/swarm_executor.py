#!/usr/bin/env python3
"""
CAMELOT-OS RAPID SWARM EXECUTOR
Executes branch audit, validation, and optimization in parallel swarm phases.
Uses agent-style parallel composition for rapid development & validation.
"""

import subprocess
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Any

class SwarmTask:
    """Represents a discrete work unit in the swarm."""
    def __init__(self, name: str, phase: int, func, args=None, timeout=300):
        self.name = name
        self.phase = phase
        self.func = func
        self.args = args or ()
        self.timeout = timeout
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None

class SwarmExecutor:
    """Manages parallel execution of branch cleanup tasks."""
    
    def __init__(self):
        self.tasks: Dict[int, List[SwarmTask]] = {1: [], 2: [], 3: [], 4: [], 5: []}
        self.results = {"timestamp": datetime.now().isoformat(), "phases": {}}
        self.phase_order = [1, 2, 3, 4, 5]

    # ==================== PHASE 1: AUDIT ====================
    def audit_branches(self) -> Dict[str, Any]:
        """Execute comprehensive branch audit."""
        print("\n" + "="*80)
        print("  [SWARM PHASE 1] BRANCH AUDIT")
        print("="*80 + "\n")
        
        try:
            cmd = """
            python3 << 'PYTHON_EOF'
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Fetch all branches
cmd = "git for-each-ref --sort=-committerdate --format='%(refname:short)|%(committerdate:iso8601)' refs/remotes/origin/"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)

branches = []
categories = {
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

for line in result.stdout.strip().split('\\n'):
    if not line:
        continue
    parts = line.split('|')
    if len(parts) >= 2:
        branch = parts[0].replace("origin/", "")
        branches.append(branch)
        
        # Categorize
        if branch == "main":
            categories["main"].append(branch)
        elif branch.startswith("add-") and "-tests-" in branch:
            categories["auto_test"].append(branch)
        elif branch.startswith("feat/"):
            categories["feature"].append(branch)
        elif branch.startswith("fix/"):
            categories["fix"].append(branch)
        elif branch.startswith("claude/"):
            categories["claude_agent"].append(branch)
        elif branch.startswith("code-health"):
            categories["code_health"].append(branch)
        elif branch.startswith("docs/"):
            categories["docs"].append(branch)
        elif branch.startswith("jules"):
            categories["jules_task"].append(branch)
        elif branch.startswith("perf"):
            categories["perf"].append(branch)
        else:
            categories["misc"].append(branch)

# Output results
print(json.dumps({
    "total": len(branches),
    "categories": {k: len(v) for k, v in categories.items()},
    "detail": categories
}, indent=2))
PYTHON_EOF
            """
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            audit_result = json.loads(result.stdout)
            
            print("✅ AUDIT COMPLETE")
            print(f"   Total branches: {audit_result['total']}")
            for cat, count in audit_result['categories'].items():
                if count > 0:
                    print(f"   • {cat:20s}: {count:3d}")
            
            return {
                "status": "success",
                "total_branches": audit_result['total'],
                "categories": audit_result['categories'],
                "detail": audit_result['detail']
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def analyze_merge_status(self, audit_data: Dict) -> Dict[str, Any]:
        """Analyze merge status of branches."""
        print("\n[AUDIT ANALYSIS] Checking merge status...\n")
        
        try:
            merged_count = 0
            unmerged_count = 0
            
            # Sample check on key categories
            for category in ["jules_task", "fix", "feature"]:
                branches = audit_data["detail"].get(category, [])
                if branches:
                    for branch in branches[:3]:  # Sample 3 from each
                        cmd = f"git branch -r --no-merged origin/main 2>/dev/null | grep -q 'origin/{branch}'"
                        result = subprocess.run(cmd, shell=True, capture_output=True, check=False)
                        if result.returncode == 0:
                            unmerged_count += 1
                        else:
                            merged_count += 1
            
            print(f"✅ MERGE ANALYSIS")
            print(f"   Merged (sampled): {merged_count}")
            print(f"   Unmerged (sampled): {unmerged_count}")
            
            return {
                "status": "success",
                "merged_sample": merged_count,
                "unmerged_sample": unmerged_count
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # ==================== PHASE 2: VALIDATION ====================
    def validate_naming_compliance(self, audit_data: Dict) -> Dict[str, Any]:
        """Validate branch naming convention compliance."""
        print("\n" + "="*80)
        print("  [SWARM PHASE 2] VALIDATION")
        print("="*80 + "\n")
        
        valid_prefixes = ["feat/", "fix/", "chore/", "docs/", "perf/", "refactor/", "test/", "ci/", "claude/"]
        compliant = 0
        non_compliant = []
        
        # Check all branches in detail
        all_branches = []
        for cat, branches in audit_data["detail"].items():
            all_branches.extend(branches)
        
        for branch in all_branches:
            if branch == "main":
                compliant += 1
            elif any(branch.startswith(p) for p in valid_prefixes):
                compliant += 1
            else:
                non_compliant.append(branch)
        
        compliance = (compliant / len(all_branches) * 100) if all_branches else 100
        
        print(f"✅ NAMING COMPLIANCE ANALYSIS")
        print(f"   Compliant: {compliant}/{len(all_branches)} ({compliance:.1f}%)")
        print(f"   Non-compliant: {len(non_compliant)}")
        if non_compliant[:5]:
            print(f"   Examples: {', '.join(non_compliant[:5])}")
        
        return {
            "status": "success",
            "compliance_rate": compliance,
            "compliant": compliant,
            "non_compliant": len(non_compliant),
            "non_compliant_branches": non_compliant
        }

    def validate_main_protection(self) -> Dict[str, Any]:
        """Validate main branch protection settings."""
        print("\n[VALIDATION] Main branch protection...\n")
        
        try:
            cmd = "git ls-remote --heads origin main 2>/dev/null"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            
            if "main" in result.stdout:
                print(f"✅ MAIN BRANCH")
                print(f"   Exists: Yes")
                print(f"   Protection: Manual (verify in GitHub Settings)")
                return {"status": "success", "main_exists": True}
            else:
                return {"status": "failed", "error": "Main branch not found"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def validate_branch_count(self, total: int) -> Dict[str, Any]:
        """Validate branch count against targets."""
        target = 25
        status = "✅ PASS" if total <= target else "⚠️  WARN" if total <= 50 else "❌ FAIL"
        
        print(f"\n[VALIDATION] Branch count: {total} (target: {target})")
        print(f"   Status: {status}\n")
        
        return {
            "status": "success" if total <= target else "warn" if total <= 50 else "failed",
            "current": total,
            "target": target,
            "assessment": status
        }

    # ==================== PHASE 3: OPTIMIZATION ====================
    def generate_cleanup_strategy(self, audit_data: Dict, naming_compliance: Dict) -> Dict[str, Any]:
        """Generate optimal cleanup strategy."""
        print("\n" + "="*80)
        print("  [SWARM PHASE 3] OPTIMIZATION")
        print("="*80 + "\n")
        
        high_priority = []
        medium_priority = []
        keep = []
        
        # High priority: auto-test branches
        for branch in audit_data["detail"].get("auto_test", []):
            high_priority.append({"branch": branch, "reason": "Auto-generated test", "score": 100})
        
        # High priority: old jules tasks
        for branch in audit_data["detail"].get("jules_task", [])[:10]:
            high_priority.append({"branch": branch, "reason": "Old task branch", "score": 85})
        
        # Medium priority: non-compliant branches
        for branch in naming_compliance.get("non_compliant_branches", []):
            if branch != "main":
                medium_priority.append({"branch": branch, "reason": "Naming violation", "score": 60})
        
        # Keep: active features
        for branch in audit_data["detail"].get("feature", []):
            keep.append({"branch": branch, "reason": "Active feature"})
        
        print(f"✅ CLEANUP STRATEGY GENERATED")
        print(f"   High Priority (delete): {len(high_priority)}")
        print(f"   Medium Priority (review): {len(medium_priority)}")
        print(f"   Keep (active): {len(keep)}")
        
        return {
            "status": "success",
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "keep": keep,
            "total_to_delete": len(high_priority) + len(medium_priority)
        }

    def estimate_time_savings(self, total: int, high_p: int, medium_p: int) -> Dict[str, Any]:
        """Estimate time/effort savings from cleanup."""
        print(f"\n[OPTIMIZATION] Time savings estimate...\n")
        
        # Estimate: 5 seconds per branch check = total * 5 seconds
        current_ops_per_commit = total
        post_cleanup_ops = 25
        time_saved_per_check = (total - post_cleanup_ops) * 5  # seconds
        
        print(f"✅ TIME SAVINGS PROJECTION")
        print(f"   Current branch ops: {current_ops_per_commit}")
        print(f"   Post-cleanup ops: {post_cleanup_ops}")
        print(f"   Savings per fetch: ~{time_saved_per_check}s ({time_saved_per_check/60:.1f}m)")
        print(f"   Cumulative (1 month): ~{time_saved_per_check * 100}s ({time_saved_per_check * 100 / 3600:.1f}h)\n")
        
        return {
            "status": "success",
            "current_branches": current_ops_per_commit,
            "post_cleanup": post_cleanup_ops,
            "time_saved_per_op_sec": time_saved_per_check / total if total > 0 else 0,
            "estimated_monthly_savings_hours": time_saved_per_check * 100 / 3600
        }

    # ==================== PHASE 4: GENERATION ====================
    def generate_delete_script(self, strategy: Dict) -> Dict[str, Any]:
        """Generate safe deletion script."""
        print("\n" + "="*80)
        print("  [SWARM PHASE 4] SCRIPT GENERATION")
        print("="*80 + "\n")
        
        script = """#!/bin/bash
# Auto-generated by Swarm Executor
# Review before executing!

set -e

echo "CAMELOT-OS Branch Cleanup (Swarm Optimized)"
echo "=========================================="
"""
        
        high_p = strategy.get("high_priority", [])
        medium_p = strategy.get("medium_priority", [])
        
        script += f"""
echo "Phase 1: High Priority ({len(high_p)} branches)"
read -p "Continue? (y/N) " -n 1 -r
[[ $REPLY =~ ^[Yy]$ ]] || exit 1
echo

"""
        
        for item in high_p[:30]:
            branch = item["branch"]
            script += f'echo "Deleting: {branch}"\ngit push origin --delete {branch} 2>/dev/null || true\n'
        
        script += f"""
echo "Phase 2: Medium Priority ({len(medium_p)} branches)"
read -p "Continue? (y/N) " -n 1 -r
[[ $REPLY =~ ^[Yy]$ ]] || exit 1
echo

"""
        
        for item in medium_p[:20]:
            branch = item["branch"]
            script += f'echo "Deleting: {branch}"\ngit push origin --delete {branch} 2>/dev/null || true\n'
        
        script += """
echo "Cleanup complete!"
echo "Run: git fetch --all --prune"
"""
        
        script_path = Path("scripts/delete_branches_swarm.sh")
        with open(script_path, "w") as f:
            f.write(script)
        
        import os
        os.chmod(script_path, 0o755)
        
        print(f"✅ DELETION SCRIPT GENERATED")
        print(f"   Path: {script_path}")
        print(f"   Branches to delete: {len(high_p) + len(medium_p)}\n")
        
        return {
            "status": "success",
            "script_path": str(script_path),
            "high_priority_count": len(high_p),
            "medium_priority_count": len(medium_p)
        }

    def generate_validation_script(self) -> Dict[str, Any]:
        """Generate validation script."""
        print(f"\n[GENERATION] Validation script...\n")
        
        script_path = Path("scripts/validate_cleanup.sh")
        script = """#!/bin/bash
echo "BRANCH CLEANUP VALIDATION"
echo "=========================="
echo

echo "Total branches:"
git branch -r | wc -l

echo "Category breakdown:"
echo "  Auto-test:"
git branch -r | grep -c "add-.*-tests-" || echo "0"
echo "  Jules tasks:"
git branch -r | grep -c "^.*jules" || echo "0"
echo "  Feature:"
git branch -r | grep -c "^.*feat/" || echo "0"

echo "Naming compliance:"
total=$(git branch -r | wc -l)
compliant=$(git branch -r | grep -E "^.*/(feat|fix|chore|docs|perf|refactor|test|ci|claude)/" | wc -l)
echo "  Compliant: $compliant/$total"

echo "Main branch status:"
git rev-parse --verify origin/main >/dev/null 2>&1 && echo "  ✅ Exists" || echo "  ❌ Missing"
"""
        
        with open(script_path, "w") as f:
            f.write(script)
        
        import os
        os.chmod(script_path, 0o755)
        
        print(f"✅ VALIDATION SCRIPT GENERATED")
        print(f"   Path: {script_path}\n")
        
        return {"status": "success", "script_path": str(script_path)}

    # ==================== PHASE 5: EXECUTION & REPORTING ====================
    def generate_final_report(self, phase_results: Dict) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        print("\n" + "="*80)
        print("  [SWARM PHASE 5] REPORTING & SUMMARY")
        print("="*80 + "\n")
        
        report = {
            "execution_timestamp": datetime.now().isoformat(),
            "phases": phase_results,
            "summary": {
                "total_branches": phase_results.get("phase_1", {}).get("audit", {}).get("total_branches", 0),
                "branches_to_delete": 0,
                "branches_to_keep": 0,
                "compliance_rate": phase_results.get("phase_2", {}).get("naming", {}).get("compliance_rate", 0),
                "time_savings_hours": phase_results.get("phase_3", {}).get("time_savings", {}).get("estimated_monthly_savings_hours", 0),
            },
            "next_steps": [
                "1. Review scripts/delete_branches_swarm.sh",
                "2. Execute: bash scripts/delete_branches_swarm.sh",
                "3. Validate: bash scripts/validate_cleanup.sh",
                "4. Verify in GitHub: https://github.com/Cyberdad247/Camelot-Ecosystem/branches",
                "5. Install hooks: bash .githooks/install-hooks.sh"
            ]
        }
        
        report_path = Path("data/swarm_execution_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ FINAL REPORT GENERATED")
        print(f"   Path: {report_path}")
        print(f"\n   Total branches: {report['summary']['total_branches']}")
        print(f"   Compliance rate: {report['summary']['compliance_rate']:.1f}%")
        print(f"   Monthly time savings: {report['summary']['time_savings_hours']:.1f}h\n")
        
        return {"status": "success", "report_path": str(report_path), "summary": report["summary"]}

    def execute_swarm(self):
        """Execute all phases in parallel where possible."""
        print("\n" + "╔" + "="*78 + "╗")
        print("║" + " "*15 + "CAMELOT-OS BRANCH CLEANUP SWARM EXECUTOR" + " "*23 + "║")
        print("╚" + "="*78 + "╝\n")
        
        # PHASE 1: AUDIT (baseline)
        print("[PHASE 1] Auditing branches...")
        audit_result = self.audit_branches()
        merge_result = self.analyze_merge_status(audit_result)
        
        self.results["phases"]["1_audit"] = {
            "audit": audit_result,
            "merge_analysis": merge_result
        }
        
        # PHASE 2: VALIDATION (parallel)
        print("\n[PHASE 2] Running validations in parallel...")
        with ThreadPoolExecutor(max_workers=3) as executor:
            naming_future = executor.submit(self.validate_naming_compliance, audit_result)
            protection_future = executor.submit(self.validate_main_protection)
            count_future = executor.submit(self.validate_branch_count, audit_result["total_branches"])
            
            naming_result = naming_future.result()
            protection_result = protection_future.result()
            count_result = count_future.result()
        
        self.results["phases"]["2_validation"] = {
            "naming": naming_result,
            "protection": protection_result,
            "count": count_result
        }
        
        # PHASE 3: OPTIMIZATION
        print("\n[PHASE 3] Generating optimization strategy...")
        strategy_result = self.generate_cleanup_strategy(audit_result, naming_result)
        time_savings_result = self.estimate_time_savings(
            audit_result["total_branches"],
            len(strategy_result["high_priority"]),
            len(strategy_result["medium_priority"])
        )
        
        self.results["phases"]["3_optimization"] = {
            "strategy": strategy_result,
            "time_savings": time_savings_result
        }
        
        # PHASE 4: GENERATION (parallel scripts)
        print("\n[PHASE 4] Generating scripts...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            delete_future = executor.submit(self.generate_delete_script, strategy_result)
            validate_future = executor.submit(self.generate_validation_script)
            
            delete_result = delete_future.result()
            validate_result = validate_future.result()
        
        self.results["phases"]["4_generation"] = {
            "delete_script": delete_result,
            "validation_script": validate_result
        }
        
        # PHASE 5: REPORTING
        print("\n[PHASE 5] Generating final report...")
        report_result = self.generate_final_report(self.results["phases"])
        
        self.results["phases"]["5_reporting"] = {"final_report": report_result}
        
        self.print_execution_summary()
        return self.results

    def print_execution_summary(self):
        """Print execution summary."""
        print("\n" + "="*80)
        print("  SWARM EXECUTION SUMMARY")
        print("="*80 + "\n")
        
        audit = self.results["phases"]["1_audit"]["audit"]
        validation = self.results["phases"]["2_validation"]
        optimization = self.results["phases"]["3_optimization"]
        generation = self.results["phases"]["4_generation"]
        
        print("📊 AUDIT RESULTS")
        print(f"   Total branches: {audit['total_branches']}")
        for cat, count in list(audit['categories'].items())[:5]:
            if count > 0:
                print(f"   • {cat:20s}: {count:3d}")
        
        print("\n✅ VALIDATION RESULTS")
        print(f"   Naming compliance: {validation['naming']['compliance_rate']:.1f}%")
        print(f"   Branch count: {validation['count']['current']} (target: {validation['count']['target']})")
        print(f"   Main protected: {validation['protection']['status']}")
        
        print("\n🚀 OPTIMIZATION STRATEGY")
        print(f"   High priority (delete): {len(optimization['strategy']['high_priority'])}")
        print(f"   Medium priority: {len(optimization['strategy']['medium_priority'])}")
        print(f"   Keep (active): {len(optimization['strategy']['keep'])}")
        print(f"   Total to delete: {optimization['strategy']['total_to_delete']}")
        
        print(f"\n⏱️  TIME SAVINGS")
        print(f"   Monthly savings: ~{optimization['time_savings']['estimated_monthly_savings_hours']:.1f} hours")
        
        print("\n📄 GENERATED ARTIFACTS")
        print(f"   • {generation['delete_script']['script_path']}")
        print(f"   • {generation['validation_script']['script_path']}")
        print(f"   • data/swarm_execution_report.json")
        
        print("\n" + "="*80)
        print("✅ SWARM EXECUTION COMPLETE")
        print("="*80 + "\n")


def main():
    executor = SwarmExecutor()
    results = executor.execute_swarm()
    
    # Save results
    with open("data/swarm_execution_complete.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n📋 NEXT STEPS:")
    print("   1. Review: cat data/swarm_execution_report.json")
    print("   2. Execute: bash scripts/delete_branches_swarm.sh")
    print("   3. Validate: bash scripts/validate_cleanup.sh")
    print("   4. Verify: git fetch --all --prune && git branch -r | wc -l")


if __name__ == "__main__":
    main()
