# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))

from kernel.merlin_omega import Merlin_Omega


async def simulate_oracle():
    print("\n🔮 [SIMULATION] INITIALIZING ORACLE HYPERVISOR...\n")

    # 1. Initialize Kernel
    kernel = Merlin_Omega()

    # 2. Define Simulation Scenario
    prompts = [
        "Ω_ORACLE: Initialize simulation. Era: 2050. Factions: CyberPunks vs Corp.",
        "Ω_STEP: Advance time.",
        "Ω_STEP: Advance time again.",
        "Ω_XRAY: Why did the CyberPunks attack?",
        "Ω_FORK: Create a peaceful timeline.",
    ]

    for prompt in prompts:
        print(f"\n🧪 [TEST] Input: '{prompt}'")

        # 3. Process Request
        # Note: We send "ORACLE" in prompt to trigger intercept
        response = await kernel.process_request(prompt)

        print(f"   [RESULT] {response}\n")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(simulate_oracle())