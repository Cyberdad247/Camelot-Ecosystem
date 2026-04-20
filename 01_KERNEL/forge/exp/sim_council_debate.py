# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))

from kernel.merlin_omega import Merlin_Omega


async def test_council_debate():
    print("\n🏛️ [SIMULATION] TESTING THE COUNCIL OF PEERS (Simulated Debate)\n")

    kernel = Merlin_Omega()

    # Task: A complex architectural decision
    prompt = "//COUNCIL Should we implement a real-time event bus for the Holotable using Redis or WebSockets?"

    print(f"Sovereign Intent: {prompt}\n")
    res = await kernel.process_request(prompt)

    print(res)


if __name__ == "__main__":
    asyncio.run(test_council_debate())