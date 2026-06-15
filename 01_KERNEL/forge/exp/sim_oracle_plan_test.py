# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))

from kernel.merlin_omega import Merlin_Omega


async def test_full_oracle_flow():
    print("\n⚔️ [SIMULATION] TESTING FULL ORACLE DEPLOYMENT (Prompt Arsenal + HITL)\n")

    kernel = Merlin_Omega()

    # 1. Activate Oracle Mode
    print("--- 1. ACTIVATION ---")
    res1 = await kernel.process_request("/plan --mode ORACLE")
    print(f"User: /plan --mode ORACLE\nResult: {res1}\n")

    # 2. Genesis (Scenario Generation)
    print("--- 2. GENESIS (Prompt Arsenal) ---")
    res2 = await kernel.process_request("Omega_GENESIS: Cyberpunk 2077 in Neo-Tokyo")
    print(f"User: Omega_GENESIS: Cyberpunk 2077 in Neo-Tokyo\nResult: {res2}\n")

    # 3. Step (Physics)
    print("--- 3. PHYSICS STEP ---")
    res3 = await kernel.process_request("Omega_STEP: Advance time")
    print(f"User: Omega_STEP: Advance time\nResult: {res3}\n")

    # 4. Fork (HITL Gate) - EXPECT WARNING
    print("--- 4. FORK (HITL Trigger) ---")
    res4 = await kernel.process_request("Omega_FORK: Split timeline")
    print(f"User: Omega_FORK: Split timeline\nResult: {res4}\n")

    # 5. Confirm Fork
    print("--- 5. CONFIRMATION ---")
    res5 = await kernel.process_request("Omega_FORK: Split timeline Omega_CONFIRM")
    print(f"User: Omega_FORK: Split timeline Omega_CONFIRM\nResult: {res5}\n")


if __name__ == "__main__":
    asyncio.run(test_full_oracle_flow())