# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))

from kernel.merlin_omega import Merlin_Omega


async def test_excalibur_bridge():
    print("\n⚔️ [SIMULATION] TESTING EXCALIBUR BRIDGE (Gemini x OpenCode Hybrid)\n")

    kernel = Merlin_Omega()

    # Task: Strategic analysis followed by Kinetic delegation
    prompt = "Ω_OPEN: Refactor the logger in api_server.py to use a more structured JSON format."

    print(f"Sovereign Intent: {prompt}")
    res = await kernel.process_request(prompt)

    print(f"\nResult from Hybrid Engine:\n{res}")


if __name__ == "__main__":
    asyncio.run(test_excalibur_bridge())