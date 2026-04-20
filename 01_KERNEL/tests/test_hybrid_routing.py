# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import json

import websockets


async def test_hybrid_routing():
    print("=" * 60)
    print("   🎼 HYBRID CONDUCTOR ROUTING TEST")
    print("=" * 60)

    uri = "ws://127.0.0.1:18788"

    try:
        async with websockets.connect(uri) as websocket:
            print("\n[HANDSHAKE]")
            await websocket.send(json.dumps({"kind": "extension_handshake", "agentId": "tester_hub"}))
            await websocket.recv()
            print("  ✅ Ready.")

            print("\n[CASE 1] STEALTH MISSION (Expected: KNIGHT)")
            await websocket.send(
                json.dumps(
                    {
                        "kind": "start_research",
                        "qfocus": "Please login to my Twitter and summarize notifications.",
                        "preference": "AUTO",
                    }
                )
            )
            resp1 = json.loads(await websocket.recv())
            print(f"  → Summary: {resp1.get('summary')}")

            print("\n[CASE 2] BULK MISSION (Expected: PHANTOM)")
            await websocket.send(
                json.dumps(
                    {
                        "kind": "start_research",
                        "qfocus": "Scrape 100 pages of product data from amazon.",
                        "preference": "AUTO",
                    }
                )
            )
            resp2 = json.loads(await websocket.recv())
            print(f"  → Summary: {resp2.get('summary')}")

            print("\n[CASE 3] MANUAL OVERRIDE (Expected: PHANTOM)")
            await websocket.send(
                json.dumps({"kind": "start_research", "qfocus": "Search for news", "preference": "PHANTOM"})
            )
            resp3 = json.loads(await websocket.recv())
            print(f"  → Summary: {resp3.get('summary')}")

    except Exception as e:
        print(f"\n[❌ ERROR] {e}")
        print("  (Ensure 'python 01_KERNEL/connectivity/titanlink_server.py' is running)")


if __name__ == "__main__":
    asyncio.run(test_hybrid_routing())