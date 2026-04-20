# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
swarm_controller.py

Phase 5: Swarm Controller.
Acts as the client bridge to the Hivemind (Go Orchestrator).
Dispatches tasks to the localized agent swarm via HTTP.
"""

import requests
import json
import subprocess
import time
import os
import sys

# Add KERNEL to path for telemetry import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
try:
    from senses.telemetry_client import RotelClient
    telemetry = RotelClient("swarm_controller")
except ImportError:
    class DummyLogger:
        def info(self, *args, **kwargs): pass
    telemetry = DummyLogger()

HIVEMIND_URL = "http://localhost:8081/dispatch"
HIVEMIND_EXE = os.path.join(os.path.dirname(__file__), "hivemind", "hivemind.exe")

def ensure_hivemind_running():
    """Checks if Hivemind is running on port 8081, starts if not."""
    try:
        requests.get("http://localhost:8081/health", timeout=1)
        print("✅ [CONTROLLER] Hivemind is active.")
        return True
    except requests.ConnectionError:
        print("⚠️ [CONTROLLER] Hivemind offline. Igniting...")
        # Start Hivemind in background
        if not os.path.exists(HIVEMIND_EXE):
             print(f"❌ Hivemind executable not found at {HIVEMIND_EXE}")
             return False
        
        subprocess.Popen([HIVEMIND_EXE], cwd=os.path.join(os.path.dirname(__file__), "..", "..")) # Run from root
        time.sleep(2) # Wait for startup
        return True

def dispatch_crusade(objective: str, phases: list):
    """Dispatches a multi-phase crusade to the Hivemind."""
    telemetry.info("CRUSADE_DISPATCHED", objective=objective, phases=phases)
    payload = {
        "objective": objective,
        "phases": phases
    }
    
    try:
        start_time = time.time()
        print(f"🚀 [CONTROLLER] Dispatching Crusade: '{objective}'")
        response = requests.post(HIVEMIND_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        duration = result.get("total_ms", 0)
        
        telemetry.info("CRUSADE_COMPLETE", objective=objective, duration_ms=duration)
        print(f"✅ [CONTROLLER] Crusade Complete in {duration}ms")
        for res in result.get("results", []):
            print(f"   └─ [{res['task_id'].upper()}] {res['status']}: {res['output'][:100]}...")
            
    except Exception as e:
        print(f"❌ [CONTROLLER] Dispatch Failed: {e}")

if __name__ == "__main__":
    import argparse
    from directive_queue import queue
    
    parser = argparse.ArgumentParser()
    parser.add_argument("task", nargs="?", help="Task to execute")
    parser.add_argument("--daemon", action="store_true", help="Run in Autonomous Mode")
    args = parser.parse_args()

    if ensure_hivemind_running():
        if args.daemon:
            print("👁️ [CONTROLLER] Entering SINGULARITY MODE (Autonomous Loop)...")
            CONSECUTIVE_IDLE = 0
            
            while True:
                # 1. Check Directive Queue
                task_entry = queue.pop()
                
                if task_entry:
                    print(f"\n⚡ [AUTONOMY] Processing Directive: {task_entry['task']}")
                    # Dispatch to Hivemind
                    try:
                        dispatch_crusade(task_entry['task'], ["reason", "audit"])
                        queue.complete(task_entry, "SUCCESS")
                        CONSECUTIVE_IDLE = 0
                    except Exception as e:
                        print(f"❌ Task Failed: {e}")
                        task_entry["status"] = "failed"
                else:
                    # 2. Idle / Self-Maintenance
                    CONSECUTIVE_IDLE += 1
                    if CONSECUTIVE_IDLE % 60 == 0: # Every ~60s
                        print(f"💤 [AUTONOMY] System Stable. Idle Cycle: {CONSECUTIVE_IDLE}")
                        
                    # 3. Proactive Health Check (Every 10 mins approx)
                    if CONSECUTIVE_IDLE > 600:
                        print("🩺 [AUTONOMY] Initiating Self-Audit...")
                        dispatch_crusade("Verify System Integrity and Check Provenance Ledger.", ["audit"])
                        CONSECUTIVE_IDLE = 0
                        
                time.sleep(1) 

        elif args.task:
             # Manual Command
             dispatch_crusade(args.task, ["reason", "audit"])
        else:
            print("Usage: python swarm_controller.py <task> OR --daemon")