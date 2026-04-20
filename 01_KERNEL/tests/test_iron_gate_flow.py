# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import json

import websockets


async def test_iron_gate_flow():
    print("=" * 60)
    print("   🛡️ IRON GATE GATED MISSION TEST")
    print("=" * 60)

    uri = "ws://127.0.0.1:18788"

    try:
        async with websockets.connect(uri) as websocket:
            print("\n[STEP 1] INITIATING HIGH-RISK MISSION...")
            await websocket.send(
                json.dumps(
                    {
                        "kind": "start_research",
                        "qfocus": "Please login to my Twitter and check notifications.",
                        "preference": "AUTO",
                    }
                )
            )

            resp = json.loads(await websocket.recv())
            action_id = resp.get("jobId")
            print(f"  → Status: {resp.get('status')}")
            print(f"  → Action ID: {action_id}")

            if resp.get("status") == "PENDING_APPROVAL":
                print("\n[STEP 2] SIMULATING BIOMETRIC APPROVAL...")
                # Simulate mobile node sending approval
                await websocket.send(
                    json.dumps(
                        {
                            "kind": "approval_response",
                            "actionId": action_id,
                            "approved": True,
                            "signature": "BIOMETRIC_TOUCH_ID_v101",
                        }
                    )
                )

                resp2 = json.loads(await websocket.recv())
                print(f"  → Final Job Status: {resp2.get('status')}")
                print(f"  → Summary: {resp2.get('summary')}")
            else:
                print("  ❌ ERROR: Mission was not gated by Iron Gate.")

    except Exception as e:
        print(f"\n[❌ ERROR] {e}")


if __name__ == "__main__":
    asyncio.run(test_iron_gate_flow())