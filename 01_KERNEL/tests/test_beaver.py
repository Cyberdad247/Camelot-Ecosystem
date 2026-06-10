# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import requests

BASE_URL = os.getenv("CAMELOT_TEST_BASE_URL", "http://localhost:8001")
TOKEN = os.getenv("CAMELOT_TEST_TOKEN", "merlin-v100-dev")


def trigger_beaver():
    headers = {"Content-Type": "application/json", "x-camelot-token": TOKEN}

    print("\n--- TRIGGERING BEAVER CARTRIDGE ---")
    payload = {"intent": "/plan Refactor the backend to Microservices --mode BEAVER", "agent_id": "MERLIN"}

    try:
        r = requests.post(f"{BASE_URL}/agent/dispatch", headers=headers, json=payload)
        print(f"Status: {r.status_code}")
        response_json = r.json()

        # Print the thought process to show the Council formation
        print(f"\n[MERLIN RESPONSE]:\n{response_json.get('response', 'No response')}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    trigger_beaver()