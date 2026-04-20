# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Chimera Fusion API Stress Test

Simulates multiple concurrent high-intensity fusion requests to validate:
1. Capability discovery performance
2. Fusion strategy execution latency
3. Judge adjudication throughput
4. System stability under load
"""

import os
import sys
import time
import json
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://127.0.0.1:8000/v2/fusion"
MERGE_URL = f"{BASE_URL}/merge"
CONCURRENCY = 3  # Number of parallel fusion threads
TOTAL_REQUESTS = 9

# Test Scenarios
SCENARIOS = [
    {
        "goal": "Design a high-frequency trading backend with fraud detection",
        "required_capabilities": ["backend", "security", "data_science"],
        "fusion_type": "ensemble"
    },
    {
        "goal": "Refine a strategy for global market expansion",
        "required_capabilities": ["planning", "strategy"],
        "fusion_type": "serial"
    },
    {
        "goal": "Audit a Kubernetes cluster for privilege escalation risks",
        "required_capabilities": ["security", "systems_engineering", "architecture"],
        "fusion_type": "serial"
    },
    {
        "goal": "Generate creative campaign for AI safety awareness",
        "required_capabilities": ["creative", "writing", "strategy"],
        "fusion_type": "ensemble"
    }
]

def run_fusion_request(request_id: int):
    """Executes a single fusion request and returns metrics."""
    scenario = SCENARIOS[request_id % len(SCENARIOS)]
    start_time = time.time()
    
    try:
        response = requests.post(MERGE_URL, json=scenario, timeout=45)
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            return {
                "id": request_id,
                "status": "SUCCESS",
                "latency_ms": latency,
                "chimera_id": data.get("chimera_id"),
                "judge_score": data.get("judge_score"),
                "verdict": data.get("verdict"),
                "agents": len(data.get("agents_involved", []))
            }
        else:
            return {
                "id": request_id,
                "status": "ERROR",
                "code": response.status_code,
                "error": response.text,
                "latency_ms": latency
            }
    except Exception as e:
        return {
            "id": request_id,
            "status": "FAILURE",
            "error": str(e),
            "latency_ms": (time.time() - start_time) * 1000
        }

def run_stress_test():
    """Orchestrates the multi-threaded stress test."""
    print(f"🚀 Initializing Chimera Stress Test...")
    print(f"[*] Target: {MERGE_URL}")
    print(f"[*] Load: {TOTAL_REQUESTS} total requests, {CONCURRENCY} concurrent threads")
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = {executor.submit(run_fusion_request, i): i for i in range(TOTAL_REQUESTS)}
        
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            status_icon = "✅" if res["status"] == "SUCCESS" else "❌"
            print(f"{status_icon} Request {res['id']:02d}: {res['status']} | Latency: {res['latency_ms']:.2f}ms | Judge: {res.get('judge_score', 'N/A')}")
            
    total_time = time.time() - start_time
    
    # Summary Statistics
    successes = [r for r in results if r["status"] == "SUCCESS"]
    latencies = [r["latency_ms"] for r in successes]
    scores = [r["judge_score"] for r in successes if r["judge_score"] is not None]
    
    print("\n" + "="*50)
    print("      CHIMERA FUSION STRESS TEST SUMMARY")
    print("="*50)
    print(f"Total Requests:   {TOTAL_REQUESTS}")
    print(f"Successful:       {len(successes)}")
    print(f"Failed/Error:     {TOTAL_REQUESTS - len(successes)}")
    print(f"Total Duration:   {total_time:.2f}s")
    print(f"Throughput:       {len(successes)/total_time:.2f} req/s")
    
    if latencies:
        print(f"Avg Latency:      {sum(latencies)/len(latencies):.2f}ms")
        print(f"Min/Max Latency:  {min(latencies):.2f}ms / {max(latencies):.2f}ms")
    
    if scores:
        print(f"Avg Judge Score:  {sum(scores)/len(scores):.2f}")
        
    print("="*50)

if __name__ == "__main__":
    # Ensure server is running before starting test
    # (Alternatively, run this in a background task)
    run_stress_test()