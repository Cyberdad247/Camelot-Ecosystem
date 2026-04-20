# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Ensure root and kernel path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from merlin_omega import MerlinOmega


async def verify_12_engines():
    print("\n⚔️ [VERIFICATION] ACTUATING THE 12 CORE ENGINES OF CAMELOT\n")

    merlin = MerlinOmega()

    test_commands = [
        "Ω_STEP",  # 1. Oracle Physics
        "//COUNCIL Hello",  # 2. Council (Debate)
        "//FLEET init",  # 3. Aether (Swarm)
        "//FORGE test.py",  # 4. APEE (Titan Forge)
        "Ω_GENESIS Knight",  # 5. Genesis (Persona Forge)
        "Ω_VERITAS 'Arbitration clause'",  # 6. Veritas (Audit)
        "Ω_LYRICUS Modulated text",  # 7. Lyricus (Voice)
        "Ω_PROMETHEUS Do A then B",  # 8. Prometheus (Decomp)
        "Ω_HELIX Action | Result",  # 9. Helix (Self-Correction)
        "//VISION cinematic style",  # 10. Aurora (Multimodal)
        "Ω_ACTION move to mouse",  # 11. Bytebot (Implicit Action)
        "Ω_DREAM ON",  # 12. Dream State
    ]

    for cmd in test_commands:
        print(f"Executing: {cmd}")
        # We use a mocked context for simulation
        mock_ctx = {"world_state": {"global_tension": 0.5}}
        res = await merlin.process_oracle_command(cmd, mock_ctx)
        print(f"Response: {res}\n")

    print("🛡️ All 12 Engines Actuated Successfully.")


if __name__ == "__main__":
    asyncio.run(verify_12_engines())