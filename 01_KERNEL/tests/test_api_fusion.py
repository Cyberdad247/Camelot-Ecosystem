# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import requests
import json

url = "http://127.0.0.1:8000/v2/fusion/merge"
data = {
    "goal": "Test Fusion Architecture",
    "required_capabilities": ["architecture", "backend"],
    "fusion_type": "ensemble"
}

print(f"[*] Sending Fusion Request to {url}...")
try:
    response = requests.post(url, json=data, timeout=30)
    print(f"[+] Status Code: {response.status_code}")
    if response.status_code == 200:
        print("[+] Fusion Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"[-] Error: {response.text}")
except Exception as e:
    print(f"[-] Request Failed: {e}")