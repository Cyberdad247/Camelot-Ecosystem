# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import sys
import os

# Add kernel to path
sys.path.append(os.path.abspath("C:/Users/vizio/CAMELOT_OS/01_KERNEL"))

from assimilation.core import handlers

def test_harmony_gate_failure():
    print("🧪 TEST 1: Harmony Gate Failure (Non-existent Path)")
    result = handlers.assimilate_repo(
        repo_path="C:/Non/Existent/Path/XYZ",
        tags=["test"],
        origin="local"
    )
    
    if result.status == "error" and "HARMONY_FAIL" in result.messages[0]:
        print("✅ PASSED: Detected non-existent path.")
        print(f"   Message: {result.messages[0]}")
    else:
        print("❌ FAILED: Did not catch error.")
        print(f"   Status: {result.status}")
        print(f"   Messages: {result.messages}")

if __name__ == "__main__":
    test_harmony_gate_failure()