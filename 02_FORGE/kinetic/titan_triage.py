# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
⚖️ TITAN TRIAGE (Kinetic Layer)
Purpose: Swarm Orchestration & Resource Allocation.
Act as: The Strategist.
"""
import sys
import os
import json

PERFORMANCE_LEDGER = r"C:\Users\vizio\CAMELOT_OS\03_VAULT\99_SCRATCHPAD\performance_metrics.json"

VIBE_MATRIX = {
    "BUILD": "Industrial/Brutalist",
    "SECURE": "Cyber-Noir",
    "CLEAN": "Minimalist",
    "PLAN": "Geometric/Blueprints",
    "OPTIMIZE": "Neon-Vibrant",
    "RECORD": "Parchment/Steampunk"
}

def analyze_complexity(task_desc):
    """
    Estimates task difficulty.
    Simple: < 50 chars, low risk.
    Critical: Includes keywords like 'security', 'database', 'deploy'.
    """
    desc = task_desc.lower()
    if any(k in desc for k in ["omega", "god-level", "sovereign", "reforge"]):
        return "GOD_LEVEL"
    if any(k in desc for k in ["security", "audit", "cve", "auth", "kernel"]):
        return "CRITICAL"
    if any(k in desc for k in ["deploy", "database", "migration", "production"]):
        return "COMPLEX"
    if len(task_desc) > 200 or "refactor" in desc:
        return "MODERATE"
    return "SIMPLE"

def get_best_knight(role_filter=None):
    """Checks the performance ledger for the most efficient knight."""
    if not os.path.exists(PERFORMANCE_LEDGER):
        return None
    
    try:
        with open(PERFORMANCE_LEDGER, "r") as f:
            data = json.load(f)
        
        # Simple heuristic: average efficiency
        rankings = []
        for name, history in data.items():
            if not history: continue
            avg_eff = sum(h['efficiency'] for h in history) / len(history)
            rankings.append((name, avg_eff))
        
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings[0][0] if rankings else "Sir_Forge"
    except:
        return "Sir_Forge"

def triage(task_desc):
    complexity = analyze_complexity(task_desc)
    
    swarm_config = {
        "GOD_LEVEL": {
            "size": "SUPREME", 
            "leader": "Sir_Arthur", 
            "vibe": "Transcendent / Omega",
            "phases": ["SPEC", "EXPLORE", "REFINE", "IMPLEMENT"],
            "protocol": "Omega",
            "trinity": ["Sir_Aris", "Sir_Vega", "Elder_Kaelen"]
        },
        "SIMPLE": {
            "size": 1, 
            "leader": "Squire_Clean", 
            "vibe": "Minimalist",
            "phases": ["IMPLEMENT"]
        },
        "MODERATE": {
            "size": 2, 
            "leader": "Sir_Forge", 
            "vibe": "Industrial",
            "phases": ["SPEC", "IMPLEMENT"]
        },
        "COMPLEX": {
            "size": 4, 
            "leader": "Sir_Architect", 
            "vibe": "Geometric",
            "phases": ["SPEC", "EXPLORE", "REFINE", "IMPLEMENT"],
            "support": ["Sir_Aris", "Squire_Audit"]
        },
        "CRITICAL": {
            "size": "ALL", 
            "leader": "Sir_Arthur", 
            "vibe": "High-Fantasy",
            "phases": ["SPEC", "EXPLORE", "REFINE", "IMPLEMENT"],
            "trinity": ["Sir_Aris", "Sir_Vega", "Elder_Kaelen"]
        }
    }
    
    config = swarm_config.get(complexity)
    best_performer = get_best_knight()
    
    print(f"⚖️ [TRIAGE] Task Complexity: {complexity}")
    print(f"🏛️ [WAR_ROOM] Allocation: Swarm of {config['size']} agents.")
    print(f"🔄 [PHASES] {', '.join(config['phases'])}")
    
    if complexity == "CRITICAL":
        print(f"🔱 [TRINITY] {', '.join(config['trinity'])} are monitoring.")
    
    print(f"👑 [LEADER] {config['leader']} (Supported by {best_performer if best_performer != config['leader'] else 'Swarm'})")
    print(f"✨ [VIBE] {config['vibe']}")
    
    return {
        "complexity": complexity,
        "swarm_size": config['size'],
        "leader": config['leader'],
        "vibe": config['vibe']
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: titan_triage.py '<task_description>'")
        sys.exit(1)
    
    triage(sys.argv[1])