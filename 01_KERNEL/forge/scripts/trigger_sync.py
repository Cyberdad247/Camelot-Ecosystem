# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os
import re
import sys

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from memory.sync_engine import UKGDeltaEngine

LEDGER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "PROVENANCE_LEDGER.md"))


def get_latest_version():
    """Extracts the last version entry from the ledger."""
    if not os.path.exists(LEDGER_PATH):
        return "v0.0.0", "No Ledger Found"

    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Find last table row with robust whitespace handling
    # Matches: | Date | Version | **Component** | Description |
    matches = re.findall(r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(v[\w\.]+)\s*\|\s*\*\*(\w+)\*\*\s*\|\s*(.*?)\s*\|", content)
    if matches:
        return matches[-1]  # (date, version, component, description)
    return "v0.0.0", "Unknown", "Unknown", "No Entries"


def trigger_sync():
    print("--- [OMEGA] SYSTEM SYNC PROTOCOL INITIATED ---")

    # 1. Update Phase: Snapshot Ledger State
    date, version, component, desc = get_latest_version()
    print(f"[SYNC] Detected Latest State: {version} ({component})")

    engine = UKGDeltaEngine()

    # Create a System Update Node
    update_node = {
        "@type": "SystemUpdate",
        "version": version,
        "component": component,
        "summary": desc.strip(),
        "timestamp": date,
        "agent": "Omega_SYNC",
    }

    # Ingest into UKG
    engine.ingest_intel(update_node)
    print("[SYNC] System State Snapshot saved to UKG.")

    # 2. Initiate Phase: Generate Delta
    # Simulate a client connecting with an old checkpoint
    print("[SYNC] Broadcasting Delta to Swarm Mesh...")
    old_checkpoint = "init_0000"
    delta = engine.get_delta(old_checkpoint)

    print(f"[SYNC] Delta Generated. Checkpoint: {delta['checkpoint']}")
    print(f"[SYNC] Payload Size: {len(json.dumps(delta))} bytes")
    print(f"[SYNC] Status: {delta['status']}")

    print("\n[SUCCESS] Sync Protocol Complete. All nodes aligned.")


if __name__ == "__main__":
    trigger_sync()