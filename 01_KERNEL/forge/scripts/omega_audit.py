# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mocking the verification since we can't run full extension logic effectively in this script
# but we can check file presence and content signatures.


class SystemAudit:
    def __init__(self):
        self.report = []
        self.status = "NOMINAL"
        # Updated path logic: scripts/ is one level deeper than kernel root
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nano_forge", "extension"))

    def check_file(self, rel_path, required_str):
        path = os.path.join(self.base_path, rel_path)
        if not os.path.exists(path):
            self.report.append(f"[FAIL] Missing File: {rel_path}")
            self.status = "DEGRADED"
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if required_str in content:
                    self.report.append(f"[PASS] Verified: {rel_path} (Contains signature)")
                    return True
                else:
                    self.report.append(f"[FAIL] Integrity Check: {rel_path} missing signature '{required_str}'")
                    self.status = "DEGRADED"
                    return False
        except Exception as e:
            self.report.append(f"[FAIL] Error reading {rel_path}: {e}")
            self.status = "ERROR"
            return False

    def run(self):
        print("--- [SENTINEL] OMEGA SYSTEM WIDE AUDIT ---")
        print("Target: v4.0 Meta-Cognitive Stack")
        print(f"Time: {datetime.now().isoformat()}\n")

        # Phase 51: Mirror
        self.check_file("src/logic/action_executor.js", "REFLECT_ON_ACTION")

        # Phase 51.5: Killswitch (Kernel side)
        killswitch_path = os.path.abspath(
            os.path.join(self.base_path, "..", "..", "security", "killswitch_controller.py")
        )
        if os.path.exists(killswitch_path):
            self.report.append("[PASS] Verified: killswitch_controller.py exists")
        else:
            self.report.append("[FAIL] Missing: killswitch_controller.py")
            self.status = "DEGRADED"

        # Phase 52: Semantic Anchors
        self.check_file("src/logic/semantic_anchor.js", "PICK_SEMANTIC_ANCHOR")

        # Phase 53: Mission DAG
        self.check_file("src/logic/goal_orchestrator.js", "DECOMPOSE_MISSION")

        # Phase 54: Predict
        self.check_file("src/logic/goal_orchestrator.js", "PREDICT_NEXT_MOVE")

        # Phase 55: Hive Learning
        self.check_file("src/intelligence/synthesis_engine.js", "crystallize")

        # Phase 57: Expansion
        self.check_file("src/logic/mesh_manager.js", "processSignal")

        print("\n".join(self.report))
        print(f"\n[SYSTEM STATUS]: {self.status}")


if __name__ == "__main__":
    audit = SystemAudit()
    audit.run()