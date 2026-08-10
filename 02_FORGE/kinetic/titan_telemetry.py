# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
🛰️ TITAN TELEMETRY (Kinetic Layer)
Purpose: Accuracy and Speed monitoring. 
Act as: Sir Watcher.
"""
import json
import os
from datetime import datetime

TELEMETRY_LOG = r"C:\Users\vizio\CAMELOT_OS\03_VAULT\99_SCRATCHPAD\efficiency_metrics.json"

def log_task_performance(knight_name, task_type, duration, success, difficulty):
    """
    Logs task metrics to a persistent JSON store.
    """
    timestamp = datetime.now().isoformat()
    
    entry = {
        "knight": knight_name,
        "task": task_type,
        "duration_sec": round(duration, 4),
        "success": success,
        "difficulty": difficulty,
        "timestamp": timestamp
    }
    
    os.makedirs(os.path.dirname(TELEMETRY_LOG), exist_ok=True)
    
    data = []
    if os.path.exists(TELEMETRY_LOG):
        with open(TELEMETRY_LOG, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    
    data.append(entry)
    
    with open(TELEMETRY_LOG, "w") as f:
        json.dump(data, f, indent=4)

def get_knight_efficiency(knight_name):
    """
    Calculates avg speed and success rate for a knight.
    """
    if not os.path.exists(TELEMETRY_LOG):
        return None
        
    with open(TELEMETRY_LOG, "r") as f:
        data = json.load(f)
        
    knight_data = [d for d in data if d["knight"] == knight_name]
    if not knight_data:
        return None
        
    total_tasks = len(knight_data)
    successes = sum(1 for d in knight_data if d["success"])
    total_duration = sum(d["duration_sec"] for d in knight_data)
    
    return {
        "tasks": total_tasks,
        "success_rate": f"{(successes / total_tasks) * 100:.1f}%",
        "avg_duration": f"{total_duration / total_tasks:.2f}s"
    }

if __name__ == "__main__":
    # Self-test
    import random
    log_task_performance("Sir_Forge", "Scaffold", random.uniform(2, 10), True, "MODERATE")
    print(f"Stats for Sir_Forge: {get_knight_efficiency('Sir_Forge')}")