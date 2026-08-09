#!/usr/bin/env python3
"""
Camelot-OS Swarm Execution Engine
Orchestrates a 5-phase pipeline for Git branch cleanup, compliance validation,
and repository optimization.

Phases:
1. Audit: Retrieve all branches, analyze merge status, age, and assign delete scores.
2. Validation: Parallel checks for naming compliance, branch protection, and count thresholds.
3. Optimization: Calculate fetching overhead savings and prioritize deletion strategy.
4. Generation: Parallel creation of safe deletion and verification scripts.
5. Reporting: Output JSON metrics and a detailed summary of repository health.
"""

import os
import sys
import re
import json
import logging
import subprocess
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Tuple, Optional

# Configure Logging with premium formatting
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/swarm_executor.log", mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("SwarmExecutor")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
os.makedirs("scripts", exist_ok=True)
os.makedirs("docs", exist_ok=True)

# Domain constants for branch naming compliance
COMPLIANT_PREFIXES = ["feat/", "fix/", "chore/", "docs/", "perf/", "refactor/", "test/", "ci/", "claude/"]

@dataclass
class BranchInfo:
    name: str
    is_remote: bool
    commit_hash: str
    commit_date: str
    author: str
    message: str
    is_merged: bool = False
    category: str = "misc"
    delete_score: int = 0  # 0 to 100

@dataclass
class SwarmTask:
    name: str
    description: str
    status: str = "PENDING"
    error: Optional[str] = None
    result: Any = None

class SwarmExecutor:
    def __init__(self, dry_run: bool = False, simulate: bool = False):
        self.dry_run = dry_run
        self.simulate = simulate
        self.tasks: Dict[str, SwarmTask] = {}
        self.pipeline_state: Dict[str, Any] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "simulate": self.simulate,
            "phases": {}
        }
        logger.info(f"Swarm Executor initialized (Dry-run={self.dry_run}, Simulate={self.simulate})")

    def register_task(self, name: str, description: str) -> None:
        self.tasks[name] = SwarmTask(name=name, description=description)

    def _run_git_cmd(self, args: List[str]) -> str:
        """Helper to run a git command and return output."""
        if self.simulate:
            return ""
        try:
            res = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="ignore"
            )
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: git {' '.join(args)} - Error: {e.stderr}")
            raise RuntimeError(f"Git command failed: {e.stderr.strip()}")

    # =========================================================================
    # PHASE 1: AUDIT
    # =========================================================================
    def execute_phase_1_audit(self) -> Dict[str, Any]:
        logger.info("--- Starting Phase 1: Audit ---")
        self.register_task("audit_fetch", "Fetch and parse Git branches and metadata")
        
        branches: List[BranchInfo] = []
        
        if self.simulate:
            # Generate simulated branches for deep testing (over 130 branches as requested)
            logger.info("Simulation mode: Generating 135 mock branches across 9 categories")
            mock_authors = ["jules", "boris", "alex", "forge", "sentinel", "lady_apis", "merlin"]
            mock_categories = ["auto_test", "jules_task", "fix", "feature", "perf", "docs", "code_health", "claude_agent", "misc"]
            
            for i in range(135):
                cat = mock_categories[i % len(mock_categories)]
                author = mock_authors[i % len(mock_authors)]
                name = ""
                
                if cat == "auto_test":
                    name = f"test/auto-verify-{i}"
                elif cat == "jules_task":
                    name = f"claude/jules-task-refactor-{i}"
                elif cat == "fix":
                    name = f"fix/latency-patch-{i}"
                elif cat == "feature":
                    name = f"feat/quantum-lattice-{i}"
                elif cat == "perf":
                    name = f"perf/zero-kv-cache-{i}"
                elif cat == "docs":
                    name = f"docs/manifest-rev-{i}"
                elif cat == "code_health":
                    name = f"refactor/ssm-core-{i}"
                elif cat == "claude_agent":
                    name = f"claude/agent-swarm-node-{i}"
                else:
                    name = f"temp-sandbox-branch-{i}"
                
                # Alternate local / remote
                is_remote = (i % 2 == 0)
                if is_remote:
                    name = f"origin/{name}"
                
                is_merged = (i % 3 != 0)  # 2/3 merged
                # Base delete score logic
                delete_score = 0
                if cat == "auto_test":
                    delete_score = 100
                elif cat == "jules_task":
                    delete_score = 80
                elif cat == "fix":
                    delete_score = 60 if is_merged else 40
                elif cat == "feature":
                    delete_score = 30 if is_merged else 10
                else:
                    delete_score = 50
                
                # Mock date (older branches get higher scores)
                days_ago = (i * 3) + 1
                date_str = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                branches.append(BranchInfo(
                    name=name,
                    is_remote=is_remote,
                    commit_hash=f"abcdef{i:03d}",
                    commit_date=date_str,
                    author=author,
                    message=f"Optimizing lattice components, iteration {i}",
                    is_merged=is_merged,
                    category=cat,
                    delete_score=min(100, delete_score + (days_ago // 10))
                ))
        else:
            # Real repository execution
            logger.info("Executing real Git audit")
            # Fetch prune to sync remote tracking
            try:
                self._run_git_cmd(["fetch", "--all", "--prune"])
            except Exception as e:
                logger.warning(f"Git fetch failed, proceeding with local cache: {e}")

            # Get branches from git for-each-ref
            fmt = "%(refname:short)|%(objectname:short)|%(committerdate:short)|%(authorname)|%(subject)"
            raw_branches = self._run_git_cmd(["for-each-ref", "--format", fmt, "refs/heads", "refs/remotes"])
            
            # Determine main/master branch merged status
            merged_to_main = set()
            try:
                raw_merged = self._run_git_cmd(["branch", "-a", "--merged", "origin/main"])
                for b in raw_merged.splitlines():
                    cleaned = b.strip().replace("* ", "")
                    merged_to_main.add(cleaned)
            except Exception:
                try:
                    raw_merged = self._run_git_cmd(["branch", "-a", "--merged", "main"])
                    for b in raw_merged.splitlines():
                        cleaned = b.strip().replace("* ", "")
                        merged_to_main.add(cleaned)
                except Exception as ex:
                    logger.warning(f"Could not determine merged status: {ex}")
            
            for line in raw_branches.splitlines():
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) < 5:
                    continue
                name, commit, date, author, message = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                if "origin/HEAD" in name or name == "main" or name == "master":
                    continue
                
                is_remote = name.startswith("origin/")
                is_merged = name in merged_to_main or f"remotes/{name}" in merged_to_main
                
                # Categorization logic
                cat = "misc"
                name_lower = name.lower()
                if "auto_test" in name_lower or "test/" in name_lower or "verify" in name_lower:
                    cat = "auto_test"
                elif "jules" in name_lower or "jules_task" in name_lower:
                    cat = "jules_task"
                elif "fix/" in name_lower or "patch" in name_lower:
                    cat = "fix"
                elif "feat/" in name_lower or "feature/" in name_lower:
                    cat = "feature"
                elif "perf/" in name_lower:
                    cat = "perf"
                elif "docs/" in name_lower:
                    cat = "docs"
                elif "refactor/" in name_lower or "chore/" in name_lower or "clean" in name_lower:
                    cat = "code_health"
                elif "claude/" in name_lower or "agent/" in name_lower:
                    cat = "claude_agent"

                # Calculate delete score
                # Base deletion score rules
                delete_score = 0
                if cat == "auto_test":
                    delete_score = 100
                elif cat == "jules_task":
                    delete_score = 80
                elif cat == "fix":
                    delete_score = 65 if is_merged else 35
                elif cat == "feature":
                    delete_score = 25 if is_merged else 10
                elif cat == "code_health":
                    delete_score = 70 if is_merged else 40
                elif cat == "docs" or cat == "perf":
                    delete_score = 60 if is_merged else 30
                else:
                    delete_score = 50

                # Age modifier (days since last commit)
                try:
                    commit_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                    days_old = (datetime.datetime.now() - commit_dt).days
                    # Add 1 point per 5 days of age, max +30
                    delete_score += min(30, days_old // 5)
                except ValueError:
                    pass

                branches.append(BranchInfo(
                    name=name,
                    is_remote=is_remote,
                    commit_hash=commit,
                    commit_date=date,
                    author=author,
                    message=message,
                    is_merged=is_merged,
                    category=cat,
                    delete_score=min(100, delete_score)
                ))

        # Summarize category counts
        cat_counts: Dict[str, int] = {}
        for b in branches:
            cat_counts[b.category] = cat_counts.get(b.category, 0) + 1
        
        result_data = {
            "total_branches": len(branches),
            "merged_count": sum(1 for b in branches if b.is_merged),
            "unmerged_count": sum(1 for b in branches if not b.is_merged),
            "local_count": sum(1 for b in branches if not b.is_remote),
            "remote_count": sum(1 for b in branches if b.is_remote),
            "category_counts": cat_counts,
            "branches": [asdict(b) for b in branches]
        }
        
        self.tasks["audit_fetch"].status = "SUCCESS"
        self.tasks["audit_fetch"].result = result_data
        self.pipeline_state["phases"]["1_audit"] = result_data
        
        logger.info(f"Phase 1: Audit Complete. Audited {len(branches)} branches.")
        return result_data

    # =========================================================================
    # PHASE 2: VALIDATION (3 Parallel Jobs)
    # =========================================================================
    def _validate_naming_compliance(self, branches: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("Job 1: Running Naming Compliance Check")
        non_compliant = []
        compliant_count = 0
        
        for b in branches:
            b_name = b["name"].replace("origin/", "")
            is_compliant = False
            for prefix in COMPLIANT_PREFIXES:
                if b_name.startswith(prefix):
                    is_compliant = True
                    break
            
            if is_compliant:
                compliant_count += 1
            else:
                non_compliant.append(b["name"])
        
        compliance_pct = (compliant_count / len(branches)) * 100 if branches else 100.0
        return {
            "compliance_percentage": round(compliance_pct, 2),
            "compliant_count": compliant_count,
            "non_compliant_count": len(non_compliant),
            "violations": non_compliant
        }

    def _validate_main_protection(self) -> Dict[str, Any]:
        logger.info("Job 2: Running Main Branch Protection Check")
        main_exists = False
        master_exists = False
        
        if self.simulate:
            main_exists = True
            master_exists = True
        else:
            try:
                branches_raw = self._run_git_cmd(["branch", "-a"])
                main_exists = any("main" in line for line in branches_raw.splitlines())
                master_exists = any("master" in line for line in branches_raw.splitlines())
            except Exception as e:
                logger.error(f"Error checking main branch presence: {e}")

        return {
            "main_branch_exists": main_exists,
            "legacy_master_exists": master_exists,
            "status": "PASS" if main_exists else "FAIL",
            "required_actions": ["Clean up legacy master branch"] if master_exists else []
        }

    def _validate_branch_count_threshold(self, count: int) -> Dict[str, Any]:
        logger.info("Job 3: Running Branch Count Threshold Check")
        # Threshold boundaries: PASS (<=25) | WARN (26-50) | FAIL (>50)
        target = 25
        status = "PASS"
        if count > 50:
            status = "FAIL"
        elif count > target:
            status = "WARN"
            
        return {
            "current_count": count,
            "target_threshold": target,
            "status": status,
            "details": f"Status is {status} because count {count} is threshold boundary."
        }

    def execute_phase_2_validation(self) -> Dict[str, Any]:
        logger.info("--- Starting Phase 2: Validation (Parallel Execution) ---")
        self.register_task("validation_naming", "Check compliance with naming taxonomy")
        self.register_task("validation_protection", "Verify primary branch protections")
        self.register_task("validation_count", "Analyze count against threshold limit")
        
        audit_data = self.pipeline_state["phases"]["1_audit"]
        branches = audit_data["branches"]
        total_count = audit_data["total_branches"]
        
        validation_results = {}
        
        # Dispatch 3 jobs in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix="ValidatorSwarm") as executor:
            future_naming = executor.submit(self._validate_naming_compliance, branches)
            future_protect = executor.submit(self._validate_main_protection)
            future_count = executor.submit(self._validate_branch_count_threshold, total_count)
            
            # Gather results
            validation_results["naming"] = future_naming.result()
            validation_results["protection"] = future_protect.result()
            validation_results["count_threshold"] = future_count.result()
            
        self.tasks["validation_naming"].status = "SUCCESS"
        self.tasks["validation_naming"].result = validation_results["naming"]
        
        self.tasks["validation_protection"].status = "SUCCESS"
        self.tasks["validation_protection"].result = validation_results["protection"]
        
        self.tasks["validation_count"].status = "SUCCESS"
        self.tasks["validation_count"].result = validation_results["count_threshold"]
        
        overall_status = "PASS"
        if validation_results["count_threshold"]["status"] == "FAIL" or validation_results["protection"]["status"] == "FAIL":
            overall_status = "FAIL"
        elif validation_results["count_threshold"]["status"] == "WARN":
            overall_status = "WARN"
            
        validation_results["overall_status"] = overall_status
        self.pipeline_state["phases"]["2_validation"] = validation_results
        
        logger.info(f"Phase 2: Validation Complete. Status: {overall_status}")
        return validation_results

    # =========================================================================
    # PHASE 3: OPTIMIZATION
    # =========================================================================
    def execute_phase_3_optimization(self) -> Dict[str, Any]:
        logger.info("--- Starting Phase 3: Optimization ---")
        self.register_task("optimization_savings", "Calculate network latency and cleanup strategies")
        
        audit_data = self.pipeline_state["phases"]["1_audit"]
        branches = audit_data["branches"]
        total_branches = audit_data["total_branches"]
        
        # Categorize into priority queues
        high_priority = []    # Auto-test + old tasks
        medium_priority = []  # Old fixes + naming violations
        keep = []             # Active features
        
        for b in branches:
            score = b["delete_score"]
            if score >= 75:
                high_priority.append(b["name"])
            elif score >= 45:
                medium_priority.append(b["name"])
            else:
                keep.append(b["name"])
                
        # Estimate monthly fetching time savings
        current_fetch_overhead = total_branches * 5.0
        post_fetch_overhead = 25 * 5.0
        savings_per_fetch = max(0.0, current_fetch_overhead - post_fetch_overhead)
        monthly_fetches = 100
        monthly_time_saved_hours = round((savings_per_fetch * monthly_fetches) / 3600.0, 2)
        
        optimization_data = {
            "strategy": {
                "high_priority_delete_count": len(high_priority),
                "medium_priority_delete_count": len(medium_priority),
                "keep_count": len(keep),
                "high_priority_branches": high_priority,
                "medium_priority_branches": medium_priority,
                "keep_branches": keep
            },
            "metrics": {
                "current_overhead_seconds_per_fetch": current_fetch_overhead,
                "target_overhead_seconds_per_fetch": post_fetch_overhead,
                "savings_seconds_per_fetch": savings_per_fetch,
                "estimated_monthly_hours_saved": monthly_time_saved_hours
            }
        }
        
        self.tasks["optimization_savings"].status = "SUCCESS"
        self.tasks["optimization_savings"].result = optimization_data
        self.pipeline_state["phases"]["3_optimization"] = optimization_data
        
        logger.info(f"Phase 3: Optimization Complete. Est. Savings: {monthly_time_saved_hours} hours/month.")
        return optimization_data

    # =========================================================================
    # PHASE 4: GENERATION (2 Parallel Jobs)
    # =========================================================================
    def _generate_delete_script(self, high_priority: List[str], medium_priority: List[str]) -> str:
        logger.info("Job 1: Generating Safe Deletion Script")
        filepath = "scripts/delete_branches_swarm.sh"
        
        # Split into local and remote branches to execute correctly
        local_high = [b for b in high_priority if not b.startswith("origin/")]
        remote_high = [b.replace("origin/", "") for b in high_priority if b.startswith("origin/")]
        
        local_med = [b for b in medium_priority if not b.startswith("origin/")]
        remote_med = [b.replace("origin/", "") for b in medium_priority if b.startswith("origin/")]

        content = f"""#!/bin/bash
# =========================================================================
# Camelot-OS Phased Safe Deletion Script
# Generated by SwarmExecutor on {datetime.date.today().isoformat()}
# =========================================================================

echo "========================================================"
echo "🛡️  Camelot-OS Sovereign Branch Cleanup Daemon Active 🛡️"
echo "========================================================"
echo "This script executes safe, interactive, multi-phase branch deletion."
echo "Press Ctrl+C at any time to abort."
echo ""

# Function to confirm action
confirm_phase() {{
    read -p "Proceed with $1? [y/N]: " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}}

# PHASE 1: High Priority Deletions ({len(high_priority)} branches)
echo "--------------------------------------------------------"
echo "PHASE 1: High Priority Deletions (Auto-test/Old tasks)"
echo "--------------------------------------------------------"
if confirm_phase "Phase 1 High Priority Deletions"; then
    echo "Executing Phase 1 deletions..."
"""
        
        if local_high:
            content += "    # Delete Local High Priority Branches\n"
            content += "    git branch -D " + " ".join(local_high) + " || true\n\n"
        if remote_high:
            content += "    # Delete Remote High Priority Branches\n"
            for rb in remote_high:
                content += f"    git push origin --delete {rb} || true\n"
            content += "\n"
            
        content += f"""else
    echo "Phase 1 skipped."
fi

# PHASE 2: Medium Priority Deletions ({len(medium_priority)} branches)
echo "--------------------------------------------------------"
echo "PHASE 2: Medium Priority Deletions (Old fixes/Violations)"
echo "--------------------------------------------------------"
if confirm_phase "Phase 2 Medium Priority Deletions"; then
    echo "Executing Phase 2 deletions..."
"""

        if local_med:
            content += "    # Delete Local Medium Priority Branches\n"
            content += "    git branch -D " + " ".join(local_med) + " || true\n\n"
        if remote_med:
            content += "    # Delete Remote Medium Priority Branches\n"
            for rb in remote_med:
                content += f"    git push origin --delete {rb} || true\n"
            content += "\n"

        content += """else
    echo "Phase 2 skipped."
fi

echo ""
echo "🎉 Cleanup Run Complete. Fetching prune to align git state..."
git fetch --all --prune || true
echo "✅ State synchronized."
"""
        if not self.dry_run:
            with open(filepath, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            try:
                os.chmod(filepath, 0o755)
            except Exception:
                pass
                
        return filepath

    def _generate_validate_script(self) -> str:
        logger.info("Job 2: Generating Post-Cleanup Validation Script")
        filepath = "scripts/validate_cleanup.sh"
        
        content = """#!/bin/bash
# =========================================================================
# Camelot-OS Branch Cleanup Validation Script
# Generated by SwarmExecutor on {}
# =========================================================================

echo "========================================================"
echo "🔍 Camelot-OS Post-Cleanup Validation Suite 🔍"
echo "========================================================"
echo ""

# Count active branches
total_branches=$(git branch -a | grep -v "HEAD" | wc -l)
echo "Total remaining branches (local + remote): $total_branches"

if [ "$total_branches" -le 25 ]; then
    echo "✅ PASS: Branch count is within boundaries ($total_branches <= 25)."
else
    echo "⚠️  WARN: Branch count exceeds ideal threshold ($total_branches > 25)."
fi

# Check naming compliance
non_compliant_count=0
while read -r branch; do
    cleaned=$(echo "$branch" | sed 's/^[ *]*//' | sed 's/remotes\\/origin\\///')
    
    # Skip main and master from prefix check
    if [ "$cleaned" == "main" ] || [ "$cleaned" == "master" ]; then
        continue
    fi
    
    compliant=false
    for prefix in "feat/" "fix/" "chore/" "docs/" "perf/" "refactor/" "test/" "ci/" "claude/"; do
        if [[ "$cleaned" == $prefix* ]]; then
            compliant=true
            break
        fi
    done
    
    if [ "$compliant" = false ]; then
        echo "❌ Violator: $cleaned"
        non_compliant_count=$((non_compliant_count + 1))
    fi
done < <(git branch -a | grep -v "HEAD")

echo ""
if [ "$non_compliant_count" -eq 0 ]; then
    echo "✅ PASS: 100% Naming Taxonomy Compliance achieved."
else
    echo "❌ FAIL: Found $non_compliant_count naming taxonomy violations."
fi
""".format(datetime.date.today().isoformat())

        if not self.dry_run:
            with open(filepath, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            try:
                os.chmod(filepath, 0o755)
            except Exception:
                pass
                
        return filepath

    def execute_phase_4_generation(self) -> Dict[str, Any]:
        logger.info("--- Starting Phase 4: Generation (Parallel Execution) ---")
        self.register_task("generation_delete_script", "Generate phased interactive branch deletion script")
        self.register_task("generation_validate_script", "Generate validation check suite script")
        
        opt_data = self.pipeline_state["phases"]["3_optimization"]
        high_priority = opt_data["strategy"]["high_priority_branches"]
        medium_priority = opt_data["strategy"]["medium_priority_branches"]
        
        generation_results = {}
        
        # Parallel generation of two script builders
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="GeneratorSwarm") as executor:
            future_delete = executor.submit(self._generate_delete_script, high_priority, medium_priority)
            future_validate = executor.submit(self._generate_validate_script)
            
            generation_results["delete_script"] = future_delete.result()
            generation_results["validate_script"] = future_validate.result()
            
        self.tasks["generation_delete_script"].status = "SUCCESS"
        self.tasks["generation_delete_script"].result = generation_results["delete_script"]
        
        self.tasks["generation_validate_script"].status = "SUCCESS"
        self.tasks["generation_validate_script"].result = generation_results["validate_script"]
        
        self.pipeline_state["phases"]["4_generation"] = generation_results
        logger.info("Phase 4: Generation Complete. Created cleanup and validation utilities.")
        return generation_results

    # =========================================================================
    # PHASE 5: REPORTING
    # =========================================================================
    def execute_phase_5_reporting(self) -> Dict[str, Any]:
        logger.info("--- Starting Phase 5: Reporting ---")
        self.register_task("reporting_export", "Export pipeline artifacts and console dashboard summaries")
        
        audit_data = self.pipeline_state["phases"]["1_audit"]
        validation_data = self.pipeline_state["phases"]["2_validation"]
        opt_data = self.pipeline_state["phases"]["3_optimization"]
        gen_data = self.pipeline_state["phases"]["4_generation"]
        
        overall_summary = {
            "timestamp": self.pipeline_state["timestamp"],
            "total_branches_analyzed": audit_data["total_branches"],
            "naming_compliance_pct": validation_data["naming"]["compliance_percentage"],
            "branch_count_status": validation_data["count_threshold"]["status"],
            "overall_pipeline_status": validation_data["overall_status"],
            "high_priority_removals": opt_data["strategy"]["high_priority_delete_count"],
            "medium_priority_removals": opt_data["strategy"]["medium_priority_delete_count"],
            "estimated_savings_hours_monthly": opt_data["metrics"]["estimated_monthly_hours_saved"],
            "delete_script_path": gen_data["delete_script"],
            "validate_script_path": gen_data["validate_script"]
        }
        
        report_data = {
            "summary": overall_summary,
            "tasks": {name: {"status": t.status, "description": t.description} for name, t in self.tasks.items()}
        }
        
        self.tasks["reporting_export"].status = "SUCCESS"
        self.tasks["reporting_export"].result = report_data
        
        self.pipeline_state["phases"]["5_reporting"] = report_data
        
        # Save JSON files
        if not self.dry_run:
            with open("data/swarm_execution_report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
            with open("data/swarm_execution_complete.json", "w", encoding="utf-8") as f:
                json.dump(self.pipeline_state, f, indent=2)
                
        logger.info("Phase 5: Reporting Complete. Artifacts saved in data/ directory.")
        self._output_terminal_dashboard(overall_summary, audit_data, validation_data)
        
        return report_data

    def _output_terminal_dashboard(self, summary: Dict[str, Any], audit: Dict[str, Any], validation: Dict[str, Any]) -> None:
        """Prints a beautiful summary to the stdout console."""
        print("\n" + "="*80)
        print("CAMELOT-OS SWARM PIPELINE COMPLETION REPORT".center(80))
        print("="*80)
        print(f"Pipeline Executed At   : {summary['timestamp']}")
        print(f"Overall Run Status     : {summary['overall_pipeline_status']}")
        print(f"Total Branches Audited : {summary['total_branches_analyzed']}")
        print(f"Naming Compliance Pct  : {summary['naming_compliance_pct']}%")
        print(f"Threshold Audit Status : {summary['branch_count_status']}")
        print("-"*80)
        print("ESTIMATED OPTIMIZATIONS".center(80))
        print("-"*80)
        print(f"High Priority Removals (Auto-test/Old tasks)   : {summary['high_priority_removals']}")
        print(f"Medium Priority Removals (Violations/Old fixes) : {summary['medium_priority_removals']}")
        print(f"Estimated Developer Time Saved (Monthly)        : {summary['estimated_savings_hours_monthly']} hours")
        print("-"*80)
        print("GENERATED SCRIPTS".center(80))
        print("-"*80)
        print(f"Safe Phased Deletion Script : {summary['delete_script_path']}")
        print(f"Post-cleanup Check Suite     : {summary['validate_script_path']}")
        print("="*80)
        print("Next recommended action: bash scripts/run_swarm.sh or execute cleanup script manually.")
        print("="*80 + "\n")

    # =========================================================================
    # RUN PIPELINE
    # =========================================================================
    def run(self) -> None:
        try:
            self.execute_phase_1_audit()
            self.execute_phase_2_validation()
            self.execute_phase_3_optimization()
            self.execute_phase_4_generation()
            self.execute_phase_5_reporting()
            logger.info("Swarm Executor run completed successfully.")
        except Exception as e:
            logger.critical(f"Swarm Pipeline failed: {e}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Camelot-OS Swarm Execution Pipeline Engine")
    parser.add_argument("--dry-run", action="store_true", help="Execute without writing script outputs")
    parser.add_argument("--simulate", action="store_true", help="Simulate a 130+ branch repository footprint for pipeline verification")
    args = parser.parse_args()

    executor = SwarmExecutor(dry_run=args.dry_run, simulate=args.simulate)
    executor.run()
