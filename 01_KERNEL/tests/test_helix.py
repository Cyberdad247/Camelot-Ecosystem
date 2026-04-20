# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Engines.coherence_engine import coherence

async def test_helix_logic():
    print("🧬 [HELIX TEST] Igniting...")
    
    # 1. Define broken code
    broken_code = """
    def add_numbers(a, b)
        return a + b
    """
    
    task = "Write a python function to add two numbers."
    
    # 2. Verify Limit (Should fail)
    print("\n--- PHASE 1: VERIFICATION ---")
    verification = await coherence.verify_output(task, broken_code)
    print(f"Initial Score: {verification.get('score')}")
    
    if verification.get("valid") is True:
        print("❌ Test Failed: Logic validated broken code.")
        return

    # 3. Heal (Helix Loop)
    print("\n--- PHASE 2: HELIX LOOP ---")
    healed = await coherence.helix_verify_loop(task, broken_code)
    
    print("\n[FINAL CODE]:")
    print(healed)
    
    if "def add_numbers(a, b):" in healed:
        print("✅ [HELIX TEST] SUCCESS: Code healed.")
    else:
        print("❌ [HELIX TEST] FAILURE: Code still broken.")

if __name__ == "__main__":
    asyncio.run(test_helix_logic())