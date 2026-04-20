# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import importlib.util


# Helper to import from directories starting with numbers
def import_from_kernel(module_path, item_name):
    spec = importlib.util.spec_from_file_location(item_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, item_name)


# Resolve paths
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
planning_engine_path = os.path.join(base_path, "01_KERNEL/reasoning/planning_engine.py")
prometheus_decomp_path = os.path.join(base_path, "01_KERNEL/reasoning/prometheus_decomp.py")

planner = import_from_kernel(planning_engine_path, "planner")
prometheus = import_from_kernel(prometheus_decomp_path, "prometheus")


def run_simulation():
    print("STARTING PLANNING ENGINE SIMULATION [PARK ET AL. 2023]\n")

    # 1. SET GOAL
    goal = "Build a local-first synchronization protocol and deploy it to the edge then verify latency."
    print(f"[GOAL]: {goal}")

    # 2. DECOMPOSE VIA PROMETHEUS
    subtasks = prometheus.decompose(goal)
    print(f"[DECOMPOSITION]: {subtasks}")

    # 3. CREATE PLAN
    plan_id = planner.create_plan(goal, subtasks)
    print(f"[PLAN_ID]: {plan_id}\n")

    # 4. EXECUTE FIRST TASK
    print("--- Executing Step 1 ---")
    action = planner.get_next_action(plan_id)
    print(f"[ACTION]: {action['description']}")

    # Simulate completion
    planner.complete_task(plan_id, result="Protocol designed with Version Clocks.")
    print("[STATUS]: Completed. Result recorded.\n")

    # 5. TRIGGER REFLECTION/REVISION
    # Simulate a mid-plan realization (e.g., edge latency is higher than expected)
    print("--- Triggering Plan Revision (Reflection) ---")
    feedback = "Edge latency detected at 800ms. Need to add a compression step before deploy."
    new_future_tasks = ["Optimize edge binaries with Cribo", "Deploy to the edge", "Verify latency results"]
    planner.revise_plan(plan_id, feedback, new_future_tasks)
    print("[REVISION]: Added optimization step based on feedback.\n")

    # 6. VERIFY FINAL STATE
    print("--- Final Plan State ---")
    plan_json = planner.export_plan(plan_id)
    print(plan_json)


if __name__ == "__main__":
    try:
        run_simulation()
    except Exception as e:
        print(f"\nSIMULATION FAILED: {str(e)}")