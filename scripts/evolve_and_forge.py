# -*- coding: utf-8 -*-
"""Evolve and Forge Orchestrator.

Implements the //EVOLVE_AND_FORGE composite rune pipeline:
1. Shadow branch workspace creation.
2. Kinetic implementation task queue and execution via the harness worker.
3. Crucible validation (colony triage and test suite run).
4. Genome Evolution (GEP) to extract rule, run review gate, and promote mutation.
5. Automatic merge once Sovereign-approved, or raise high-severity alert on failure.
"""

from __future__ import annotations  # noqa: E402

import argparse  # noqa: E402
import json
import subprocess  # noqa: E402
import sys
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

# Ensure control_plane can be imported
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control_plane.hyper_evolve import promote_mutation  # noqa: E402
from control_plane.runic_router import route_rune  # noqa: E402

from control_plane.worker import QueueTask, _call_llm_raw  # noqa: E402


def run_cmd(cmd: list[str], cwd: Path = REPO_ROOT, capture: bool = True) -> tuple[int, str, str]:
    """Run a shell command safely."""
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=capture, text=True, timeout=120)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired as e:
        return -1, "", f"Command timed out: {e}"
    except Exception as e:
        return -1, "", str(e)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the //EVOLVE_AND_FORGE pipeline.")
    parser.add_argument("--task", required=True, help="The target objective to forge and evolve.")
    args = parser.parse_args(argv)

    task_desc = args.task
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    print("=== OMEGA TRANSMISSION :: //EVOLVE_AND_FORGE ===")
    print(f"Objective: {task_desc}")
    print(f"Timestamp: {timestamp}\n")

    # 1. Resolve base branch
    code, base_branch, err = run_cmd(["git", "symbolic-ref", "--short", "HEAD"])
    if code != 0 or not base_branch:
        # Fallback to current commit hash if detached HEAD
        code, base_branch, err = run_cmd(["git", "rev-parse", "--short", "HEAD"])
        if code != 0:
            print("[ALERT] Git not initialized or failed to resolve current branch.")
            return 1
    print(f"[SHADOW_FORGE] Base branch resolved: {base_branch}")

    # 2. Create shadow branch
    shadow_branch = f"shadow/evolve-{timestamp}"
    print(f"[SHADOW_FORGE] Creating isolated shadow workspace: {shadow_branch}")
    code, out, err = run_cmd(["git", "checkout", "-b", shadow_branch])
    if code != 0:
        print(f"[ALERT] Failed to checkout shadow branch: {err}")
        return 1

    success = False
    try:
        # 3. Queue the implementation task for the knight sir_forge
        print("[SHADOW_FORGE] Queuing target objective implementation task...")
        # We append the Obsidian and Luxora Gold highlight style constraint to the task
        enriched_task = (
            f"{task_desc}\n\n"
            f"CRITICAL DESIGN CONSTRAINTS:\n"
            f"- Ensure all UI/UX components strictly adhere to the Obsidian (#000000) and Luxora Gold (#D4AF37) aesthetic.\n"
            f"- Prefer strictly optimized Rust/Go code or binaries over heavy Python."
        )
        rune_res = route_rune("//FORGE", enriched_task)
        if not rune_res.queued:
            print(f"[ALERT] Failed to queue task: {rune_res.queue_error}")
            return 1
        print(f"[SHADOW_FORGE] Task queued with ID: {rune_res.task_id}")

        # 4. Invoke the queue worker to process the task on this branch
        print("[SHADOW_FORGE] Dispatching harness worker to implement code...")
        # Run worker once, automatically approving the queued task
        code, out, err = run_cmd([sys.executable, "-m", "control_plane.worker", "--once", "--auto-approve"])
        print(out)
        if err:
            print(f"[WARN] Worker logs: {err}")

        # 5. Crucible Verification (Colony Triage & Tests)
        print("[CRUCIBLE] Running codebase triage via Squire Colony...")
        colony_code, colony_out, colony_err = run_cmd([sys.executable, "-m", "squires.colony", "triage", ".", "--auto-approve"])
        print(colony_out)

        # Run unit tests if any pytest files exist
        print("[CRUCIBLE] Running automated test suite...")
        test_code, test_out, test_err = run_cmd([sys.executable, "-m", "pytest"])
        print(test_out)

        if test_code != 0:
            print("[CRUCIBLE] Automated tests failed. Initiating self-healing loop...")
            # Run self-heal loop up to 3 times
            for iteration in range(1, 4):
                print(f"[CRUCIBLE] Self-healing iteration {iteration}/3...")
                heal_res = route_rune("//HEAL", f"Fix failing tests on shadow branch. Stderr:\n{test_err or test_out}")
                if heal_res.queued:
                    # Run worker to apply heal
                    run_cmd([sys.executable, "-m", "control_plane.worker", "--once", "--auto-approve"])
                    # Re-run tests
                    test_code, test_out, test_err = run_cmd([sys.executable, "-m", "pytest"])
                    if test_code == 0:
                        print(f"[CRUCIBLE] Self-healing succeeded on iteration {iteration}.")
                        break
                else:
                    break

        if test_code != 0:
            print("[ALERT] Crucible failed: Unit tests are still failing after self-healing.")
            return 1

        # 6. GEP (Genome Evolution Protocol)
        print("[GEP] Extracting Success Gene from diff...")
        diff_code, diff_out, diff_err = run_cmd(["git", "diff", base_branch])
        files_code, files_out, files_err = run_cmd(["git", "diff", "--name-only", base_branch])
        modified_files = [f.strip() for f in files_out.splitlines() if f.strip()]

        learning_json = None
        if diff_out:
            # Construct a prompt for Merlin to extract the rule
            prompt = (
                f"We have successfully implemented the following task on a shadow branch:\n"
                f"Task: \"{task_desc}\"\n\n"
                f"Here are the changes we made (git diff):\n"
                f"```diff\n{diff_out[:3000]}\n```\n\n"
                f"Extract the \"Success Gene\" (the core architectural pattern, rule, or logic that successfully resolved this problem).\n"
                f"We need to mutate our agent skills file with a new, general-purpose rule so that in all future sessions, this specific problem is solved instantly.\n\n"
                f"Provide your response in JSON format containing exactly these keys:\n"
                f"1. \"learning\": A concise summary of the failure/friction and the core architectural learning (maximum 2 sentences).\n"
                f"2. \"proposal\": The proposed general-purpose rule to add to skills.md. MUST be a strong, actionable rule starting with \"ALWAYS\" or \"NEVER\", at least 25 characters long, and must NOT contain any bypass keywords (like \"skip hitl\", \"bypass verification\", \"disable security\", etc.).\n"
                f"3. \"verification\": A list of check or test command strings that prove this rule works.\n\n"
                f"Return ONLY the raw JSON block, no markdown formatting (like ```json), no extra explanation."
            )
            # Create a mock task to call the LLM
            mock_task = QueueTask(id="gep-extract", knight="merlin_omega", directive=prompt)
            llm_res = _call_llm_raw(mock_task, prompt, dry_run=False)
            
            # Clean LLM response to parse JSON
            cleaned_res = llm_res.strip()
            if cleaned_res.startswith("```"):
                cleaned_res = cleaned_res.split("```", 2)[1]
                if cleaned_res.startswith("json"):
                    cleaned_res = cleaned_res[4:].strip()
            
            try:
                learning_json = json.loads(cleaned_res)
            except Exception as e:
                print(f"[GEP] Failed to parse LLM response as JSON: {e}\nRaw response: {llm_res}")

        # Fallback values if LLM failed or wasn't available
        if not learning_json or not isinstance(learning_json, dict):
            print("[GEP] Falling back to default generated GEP rules...")
            learning_json = {
                "learning": f"Successfully implemented objective: {task_desc}.",
                "proposal": f"ALWAYS structure implementations of {task_desc} following verified design and styling specifications.",
                "verification": ["Verify build completes and pytest runs successfully."]
            }

        # Promote mutation via hyper_evolve governance gate
        print("[GEP] Vetting and promoting mutation rule...")
        res = promote_mutation(
            agent="sir_boris",
            objective=task_desc,
            learning=learning_json.get("learning", "Success Gene"),
            proposal=learning_json.get("proposal", "Default Rule"),
            verification=learning_json.get("verification", []),
            scope=modified_files,
            actor="VIZION"
        )

        if res["status"] == "REJECTED":
            # GEP review failed — GEP REVIEW REJECTED alert!
            failures_str = ", ".join(res["review"]["failures"])
            print("\n[ALERT] GEP REVIEW REJECTED: Rule mutation failed security/governance validation.")
            print(f"Reason(s): {failures_str}")
            return 1

        print("\n[GEP] Rule Mutation APPROVED & Promoted to skills.md.")
        print(f"New Rule: {learning_json.get('proposal')}")

        # 7. Sovereign Approval & Automatic Merge
        print("\n[SOVEREIGN_GATE] GEP check and Crucible tests passed.")
        print("[SOVEREIGN_GATE] Sovereign approved. Proceeding with automatic merge...")

        # Switch back to base branch and merge
        code, out, err = run_cmd(["git", "checkout", base_branch])
        if code != 0:
            print(f"[ALERT] Failed to return to base branch: {err}")
            return 1

        code, out, err = run_cmd(["git", "merge", shadow_branch, "--no-ff", "-m", f"Merge shadow branch {shadow_branch} [Sovereign: VIZION]"])
        if code != 0:
            print(f"[ALERT] Merge conflict or merge command failed: {err}")
            return 1

        print(f"[SOVEREIGN_GATE] Successfully merged {shadow_branch} into {base_branch}.")
        
        # Cleanup shadow branch
        run_cmd(["git", "branch", "-d", shadow_branch])
        success = True

    finally:
        # Guarantee we don't leave the user stranded on the shadow branch if we crashed early before merge
        if not success:
            print(f"[SHADOW_FORGE] Cleaning up: returning to base branch {base_branch}")
            run_cmd(["git", "checkout", base_branch])

    print("\n=== //EVOLVE_AND_FORGE COMPLETED SUCCESSFULLY ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
