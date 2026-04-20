# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
🔄 LOCAL-FIRST SYNC PROTOCOL
Based on Kleppmann et al. (2019)
==============================================================================
Implements state reconciliation for offline-capable agentic systems.
==============================================================================
"""

import hashlib
import json
import time


class SyncProtocol:
    """
    Manages state integrity between Lukas (Local) and Morgana (Cloud).
    Utilizes a 'Version Clock' hierarchy.
    """

    def __init__(self):
        self.version = 0
        self.local_state_hash = None
        self.last_sync_timestamp = 0

    def generate_state_hash(self, data: dict) -> str:
        """Creates a stable hash of the system state."""
        state_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()

    def reconcile(self, local_data: dict, cloud_data: dict) -> dict:
        """
        Performs conflict resolution.
        Local-first principle: Local changes take precedence if timestamps match.
        """
        print("🔄 [SYNC] Reconciling local and cloud state...")

        local_v = local_data.get("version", 0)
        cloud_v = cloud_data.get("version", 0)

        if local_v >= cloud_v:
            # Local is up-to-date or ahead
            print("✅ [SYNC] Local state is master. Propagating to cloud.")
            return local_data
        else:
            # Cloud is ahead (unusual in local-first, but possible via other devices)
            print("⚠️ [SYNC] Cloud state is ahead. Merging...")
            # Basic merge strategy: Unified keys
            merged = {**cloud_data, **local_data}
            merged["version"] = cloud_v + 1
            return merged

    def broadcast_handshake(self, agent_id: str):
        """Broadcasts a sync request to the swarm."""
        return {"agent": agent_id, "timestamp": time.time(), "action": "SYNC_REQUEST", "protocol": "LOCAL_FIRST_v1.0"}


# Singleton
sync_proto = SyncProtocol()