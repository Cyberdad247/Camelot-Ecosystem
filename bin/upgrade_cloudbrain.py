# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Cloudbrain Upgrade Utility
import os
import sys
import importlib.util
from pathlib import Path
from datetime import datetime

# Setup paths
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

def load_base_memory():
    path = REPO_ROOT / "01_KERNEL" / "titan" / "memory" / "base_memory.py"
    spec = importlib.util.spec_from_file_location("base_memory", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_cloudbrain():
    path = REPO_ROOT / "01_KERNEL" / "agora" / "cloud_orchestrator_shim" / "long_term_cloudbrain.py"
    spec = importlib.util.spec_from_file_location("long_term_cloudbrain", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def upgrade_roster():
    print("[SYSTEM_BOOT] :: Upgrading Cloudbrain in Appwrite...")
    
    base_memory = load_base_memory()
    MemoryNode = base_memory.MemoryNode

    # Initialize bridge (loads env vars)
    try:
        cloudbrain = load_cloudbrain()
        bridge = cloudbrain.build_appwrite_memory_bridge()
    except Exception as e:
        print(f"[ERROR] Failed to initialize Appwrite bridge: {e}")
        return

    # Master Roster Data (v400.0)
    roster = [
        {"agent_id": "anya", "content": "ANYA_Ω (The Sovereign Compiler): L7 Ethereal. APEE v6.5 (Triple-QFT). Voice AI natively using Gemini 3.1 Flash. Proteus: [0.90, 0.90, 0.95, 0.85, 0.15].", "tags": ["sovereign", "compiler", "v400.0"]},
        {"agent_id": "merlin", "content": "MERLIN_Ω (The Strategist): L3 Neural. Global Optimality Engine. Videneptus MFOE. S_Ω state calculation. Proteus: [0.95, 0.98, 0.40, 0.70, 0.10].", "tags": ["sovereign", "strategist", "v400.0"]},
        {"agent_id": "lukas", "content": "LUKAS_Ω (The Kinetic Hand): L2 Kinetic. Sovereign of the Iron. Titanium Law T1. Rust/Go binaries (ZeroClaw). Node: Cybertron (100.118.224.52). Proteus: [0.20, 1.00, 0.10, 0.30, 0.00].", "tags": ["sovereign", "kinetic", "v400.0"]},
        {"agent_id": "morgana", "content": "MORGANA_Ω (The Cloud Witch): L1 Substrate. Metal & Cloud Bridge (Docker, Modal, Vercel). Operation Bifröst Anchor.", "tags": ["sovereign", "substrate", "v400.0"]},
        {"agent_id": "boris", "content": "SIR BORIS (The Anvil): L5 Agentic. ECC v1.9.0. 13-Agent Antagonistic Critique Pipeline. Squire Colony Commander. Proteus: [0.95, 1.00, 0.35, 0.45, 0.01].", "tags": ["knight", "architect", "v400.0"]},
        {"agent_id": "sentinel", "content": "SIR SENTINEL_Ω (The Shield): L6 Governance. AgentShield. Opus 4.6 Red-Team Loop. Zero-Trust Antibody. Proteus: [0.40, 1.00, 0.20, 0.20, 0.00].", "tags": ["knight", "security", "v400.0"]},
        {"agent_id": "forge", "content": "KAI 'FORGE' ZHANG (The Smith): L2 Kinetic. ECC v1.9.0 Multi-Language. DeerFlow 2.0 Sandboxing. Proteus: [0.50, 0.95, 0.30, 0.50, 0.10].", "tags": ["knight", "engineering", "v400.0"]},
        {"agent_id": "apis", "content": "LADY APIS (The Swarm Mother): L5 Agentic. Lightpanda Scraping. OpenViking Context Management. Proteus: [0.95, 0.90, 0.80, 0.60, 0.10].", "tags": ["knight", "research", "v400.0"]}
    ]

    for entry in roster:
        node = MemoryNode(
            agent_id=entry["agent_id"],
            type="persona",
            content=entry["content"],
            tags=entry["tags"],
            confidence=1.0,
            source="system"
        )
        success = bridge.push_node(node)
        if success:
            print(f"[SYNC] Pushed {entry['agent_id']} to Appwrite.")
        else:
            print(f"[FAILED] Could not push {entry['agent_id']}.")

    print("[SYSTEM_COMPLETE] :: Cloudbrain upgrade sequence finished.")

if __name__ == "__main__":
    upgrade_roster()
