# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))

from kernel.merlin_omega import Merlin_Omega


async def simulate_routing():
    print("\n⚔️ [SIMULATION] INITIALIZING SOVEREIGN KERNEL...\n")

    # 1. Initialize Kernel (loads Videneptus & Omni-Knights)
    kernel = Merlin_Omega()

    # 2. Define Test Scenarios
    scenarios = [
        ("Design a microservices architecture for a banking app.", "LANCELOT"),
        ("Write a Python script to scrape a website.", "GALAHAD"),
        ("Audit this dependency for security vulnerabilities.", "PERCIVAL"),
        ("Research the latest trends in quantum computing.", "GALAHAD"),  # Fallback to Maker/Researcher
    ]

    for prompt, expected in scenarios:
        print(f"\n🧪 [TEST] Input: '{prompt}'")
        print(f"   [EXPECTED] Route: {expected}")

        # 3. Process via Kernel -> Videneptus -> Omni-Knight
        # Note: In a real flow, this goes via API /agent/dispatch
        # Here we simulate the internal flow triggered by process_request
        response = await kernel.process_request(prompt)

        print(f"   [RESULT] {response}\n")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(simulate_routing())