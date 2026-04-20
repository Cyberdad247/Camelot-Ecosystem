# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys

# Add project root and 01_KERNEL to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "01_KERNEL"))

from kernel.agora.context import SovereignContext
from kernel.agora.protocol import ANPEnvelope
from kernel.agora.videneptus import Videneptus


async def test_notebook_knight_flow():
    print("\n📚 [SIMULATION] TESTING NOTEBOOK KNIGHT FLOW (Librarian Integration)\n")

    # 1. Initialize Videneptus (The Router)
    router_node = Videneptus()

    # 2. Create a Sovereign Context with a research intent
    context = SovereignContext(
        session_id="research_session_123", intent="Research the best practices for implementing a REST API in FastAPI."
    )

    # 3. Simulate Merlin sending a ROUTING_REQUEST to Videneptus
    envelope = ANPEnvelope(
        sender="MERLIN", recipient="VIDENEPTUS", protocol="ROUTING_REQUEST", payload={"context": context.__dict__}
    )

    print(f"Sovereign Intent: {context.intent}")

    # 4. Videneptus processes the request and routes to NotebookKnight
    await router_node.receive(envelope)

    print("\n✅ Simulation Event Loop Finished.")


if __name__ == "__main__":
    asyncio.run(test_notebook_knight_flow())