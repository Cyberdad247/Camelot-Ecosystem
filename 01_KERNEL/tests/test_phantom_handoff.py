# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import json
import os
import sys

import websockets

# Add root to path for local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_phantom_handoff():
    print("=" * 60)
    print("   🛰️ PHANTOM-TO-KNIGHT HANDOFF TEST (Phase 33)")
    print("=" * 60)

    uri = "ws://127.0.0.1:18788"

    try:
        async with websockets.connect(uri) as websocket:
            print("\n[STEP 1] CONNECTING AS PHANTOM CONTROLLER...")
            # Handshake as a system/phantom agent
            await websocket.send(json.dumps({"kind": "extension_handshake", "agentId": "phantom_grid_controller_v1"}))

            resp = await websocket.recv()
            print("  → Handshake ACK received.")

            print("\n[STEP 2] DISPATCHING REMOTE MISSION (HANDOFF)...")
            # We use a custom 'kind' that the extension background.js is now listening for
            handoff_payload = {
                "kind": "dispatch_mission",
                "qfocus": "Go to https://news.ycombinator.com and extract the top 3 stories.",
                "device": "DESKTOP",
            }

            # Since the TitanLinkServer currently just returns the processed result to the requester,
            # we need to make sure the server iterates over clients OR we simulate the broadcast.
            # However, for a simple test, we can just send it.
            # In a real scenario, the Server would have a logic to route this.

            # Let's see if we can trigger a relay. I'll update titanlink_server.py
            # to handle 'dispatch_mission' by broadcasting it.

            await websocket.send(json.dumps(handoff_payload))
            print(f"  → Handoff command sent: {handoff_payload['qfocus']}")

            # Wait for any relayed response or ACK
            try:
                # The server might not send an ACK for a dispatch, but let's wait a bit
                resp = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"  → Server Response: {resp}")
            except asyncio.TimeoutError:
                print("  → No immediate response (Expected if server just broadcasts).")

            print("\n✅ Handoff sequence initiated.")
            print("Check the Chrome Extension (Side Panel or Background Console) for activation.")

    except Exception as e:
        print(f"\n[❌ ERROR] Connection failed: {e}")
        print("  (Ensure 'python 01_KERNEL/connectivity/titanlink_server.py' is running)")


if __name__ == "__main__":
    asyncio.run(test_phantom_handoff())