# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import json

import websockets


async def test_extension_handshake():
    print("=" * 60)
    print("   🧪 NANO-KNIGHTS EXTENSION BRIDGE TEST")
    print("=" * 60)

    uri = "ws://127.0.0.1:18788"

    try:
        async with websockets.connect(uri) as websocket:
            print("\n[STEP 1] TESTING EXTENSION HANDSHAKE...")
            await websocket.send(json.dumps({"kind": "extension_handshake", "agentId": "nano_knight_swarm_v3"}))

            # Wait for ACK
            resp = await websocket.recv()
            ack = json.loads(resp)
            print(f"  → Handshake ACK: {ack}")

            if ack.get("kind") == "handshake_ack" and ack.get("status") == "ACCEPTED":
                print("  ✅ Extension Bridge ACTIVE")
                print(f"  → Permissions: {ack.get('permissions')}")
            else:
                print("  ❌ Unexpected response")

            print("\n[STEP 2] TESTING HEARTBEAT...")
            await websocket.send(json.dumps({"kind": "heartbeat"}))
            resp = await websocket.recv()
            print(f"  → Response: {resp}")

    except Exception as e:
        print(f"\n[❌ ERROR] Connection failed: {e}")
        print("  (Ensure 'python 01_KERNEL/connectivity/titanlink_server.py' is running)")


if __name__ == "__main__":
    asyncio.run(test_extension_handshake())