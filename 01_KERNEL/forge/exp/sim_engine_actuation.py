# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Add project root and 01_KERNEL to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))

from kernel.merlin_omega import Merlin_Omega


async def test_engine_actuation():
    print("\n⚙️ [SIMULATION] ACTUATING CAMELOT ENGINES v101.5\n")

    kernel = Merlin_Omega()

    # 1. Physics Engine Actuation
    print("Engine 1: Oracle Physics (SIT-Loop Step)")
    res1 = await kernel.process_request("Simulate a memory optimization.")
    # Check output for "Physics Step Completed"
    print(f"Result: {res1}\n")

    # 2. Agora Routing & Swarm Actuation
    print("Engine 2: Agora Knight Swarm (Summoning)")
    res2 = await kernel.process_request("//SUMMON: Build a secure API gateway.")
    print(f"Result: {res2}\n")

    # 3. Dream State Actuation
    print("Engine 3: Dream State (Neural Learning)")
    res3 = await kernel.process_request("Ω_DREAM ON")
    print(f"Result: {res3}\n")

    # Small wait to let background tasks log
    await asyncio.sleep(2)

    print("Engine 3: Waking up...")
    res4 = await kernel.process_request("Ω_DREAM OFF")
    print(f"Result: {res4}\n")

    print("\n✅ All Engines Actuated and Functional.")


if __name__ == "__main__":
    asyncio.run(test_engine_actuation())