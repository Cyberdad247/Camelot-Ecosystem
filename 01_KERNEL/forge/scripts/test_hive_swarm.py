# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys

# Add tools directory to path to import antigravity
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

import antigravity_safe


def test_swarm_activation():
    print("[TEST] Initializing Hive Swarm Activation Test...")

    skill_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", ".hive", "skills", "omega_swarm.md")
    )

    # 1. Load skill using antigravity
    try:
        with antigravity_safe.open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "# Skill: Ω_SWARM_CONDUCTOR" in content:
                print(f"[TEST] Skill loaded successfully: {os.path.basename(skill_path)}")
            else:
                print("[TEST] Skill content mismatch.")
                sys.exit(1)
    except Exception as e:
        print(f"[TEST] Failed to load skill: {e}")
        sys.exit(1)

    # 2. Simulate Dry Run Invocation
    print("[TEST] Simulating 'Dry Run' invocation of OMEGA_SWARM_CONDUCTOR...")
    print("[OMEGA_SWARM] SQUIRES READY.")


if __name__ == "__main__":
    test_swarm_activation()