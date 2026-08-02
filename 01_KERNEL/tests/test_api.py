# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

import requests

BASE_URL = os.getenv("CAMELOT_TEST_BASE_URL", "http://localhost:8001")
TOKEN = os.getenv("CAMELOT_TEST_TOKEN", "merlin-v100-dev")


def test_api():
    headers = {"Content-Type": "application/json", "x-camelot-token": TOKEN}

    # 1. VALID REQUEST
    print("\n--- TEST 1: VALID REQUEST ---")
    payload = {"intent": "Build a neural bridge.", "agent_id": "MORGANA"}
    r = requests.post(f"{BASE_URL}/agent/dispatch", headers=headers, json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

    # 2. SCHEMA VIOLATION (Missing 'intent')
    print("\n--- TEST 2: SCHEMA VIOLATION ---")
    payload = {"agent_id": "MERLIN"}
    r = requests.post(f"{BASE_URL}/agent/dispatch", headers=headers, json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

    # 3. SECURITY VIOLATION (Invalid Token)
    print("\n--- TEST 3: SECURITY VIOLATION ---")
    bad_headers = headers.copy()
    bad_headers["x-camelot-token"] = "HACKER_TOKEN"
    r = requests.post(f"{BASE_URL}/agent/dispatch", headers=bad_headers, json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")


if __name__ == "__main__":
    test_api()