# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
⚖️ TITAN GRADER (Kinetic Layer)
Purpose: Performance Analysis & Resource Optimization.
Act as: Sir Judge.
"""
import json
import os

TELEMETRY_LOG = r"C:\Users\vizio\CAMELOT_OS\03_VAULT\99_SCRATCHPAD\efficiency_metrics.json"

def calculate_grade(success_rate, avg_duration):
    """
    Grades based on success and speed.
    """
    if success_rate > 0.95:
        if avg_duration < 3.0: return "S"
        return "A"
    if success_rate > 0.85:
        return "B"
    return "C"

def generate_report():
    if not os.path.exists(TELEMETRY_LOG):
        print("📜 [REPORT] No telemetry data found. Go forth and execute, Knights!")
        return

    with open(TELEMETRY_LOG, "r") as f:
        data = json.load(f)

    print("🏰 [CAMELOT] SOVEREIGN REPORT CARD")
    print("-" * 40)
    
    knights = {}
    for entry in data:
        k = entry["knight"]
        if k not in knights:
            knights[k] = {"tasks": 0, "success": 0, "duration": 0}
        knights[k]["tasks"] += 1
        if entry["success"]:
            knights[k]["success"] += 1
        knights[k]["duration"] += entry["duration_sec"]

    print(f"{'Knight':<15} | {'Tasks':<5} | {'SR':<6} | {'Avg':<6} | {'Grade'}")
    print("-" * 40)
    
    for k, stats in knights.items():
        sr = stats["success"] / stats["tasks"]
        avg = stats["duration"] / stats["tasks"]
        grade = calculate_grade(sr, avg)
        
        print(f"{k:<15} | {stats['tasks']:<5} | {sr*100:>5.1f}% | {avg:>5.1f}s | {grade}")

    print("-" * 40)
    print("💡 [ORCHESTRATION] Recommending S-Tier Knights for CRITICAL tasks.")

if __name__ == "__main__":
    generate_report()