# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import hashlib
import json
import os
from typing import Any, Dict


class UKGDeltaEngine:
    """
    UKG Sync Delta Engine
    Generates change-feeds (deltas) for mobile/edge nodes.
    """

    def __init__(self, ukg_path: str = "03_VAULT/UKG/current_state.json"):
        self.ukg_path = ukg_path

    def get_current_checkpoint(self) -> str:
        """Returns a hash of the current UKG state."""
        if not os.path.exists(self.ukg_path):
            return "empty"
        with open(self.ukg_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def get_delta(self, client_checkpoint: str) -> Dict[str, Any]:
        """
        Calculates the delta between the client's checkpoint and the current state.
        For v1, we return the whole UKG if the checkpoint mismatch is detected.
        """
        current_checkpoint = self.get_current_checkpoint()

        if client_checkpoint == current_checkpoint:
            return {"checkpoint": current_checkpoint, "nodes": [], "status": "UP_TO_DATE"}

        # Load UKG
        if not os.path.exists(self.ukg_path):
            return {"checkpoint": current_checkpoint, "nodes": [], "status": "EMPTY"}

        with open(self.ukg_path, "r") as f:
            full_ukg = json.load(f)

        # Wrap as JSON-LD nodes
        nodes = []
        if "UKG_NODE" in full_ukg:
            nodes.append(
                {
                    "@type": "UKGRoot",
                    "id": full_ukg["UKG_NODE"].get("SESSION_ID", "root"),
                    "content": full_ukg["UKG_NODE"],
                }
            )

        return {"checkpoint": current_checkpoint, "nodes": nodes, "status": "DELTA_SYNC"}

    def get_partial_delta(self, last_n: int = 5) -> Dict[str, Any]:
        """Returns the last N nodes from the WEB_INTEL registry."""
        if not os.path.exists(self.ukg_path):
            return {"nodes": [], "status": "EMPTY"}

        with open(self.ukg_path, "r") as f:
            state = json.load(f)

        intel = state.get("UKG_NODE", {}).get("WEB_INTEL", [])
        return {"nodes": intel[-last_n:], "status": "PARTIAL_SYNC", "count": len(intel)}

    def ingest_intel(self, intel: Dict[str, Any]):
        """Ingests web intel into the UKG."""
        if not os.path.exists(self.ukg_path):
            state = {"@context": "https://camelot.os/ukg", "UKG_NODE": {"WEB_INTEL": []}}
        else:
            with open(self.ukg_path, "r") as f:
                state = json.load(f)

        if "UKG_NODE" not in state:
            state["UKG_NODE"] = {}

        if "WEB_INTEL" not in state["UKG_NODE"]:
            state["UKG_NODE"]["WEB_INTEL"] = []

        state["UKG_NODE"]["WEB_INTEL"].append(intel)

        with open(self.ukg_path, "w") as f:
            json.dump(state, f, indent=4)
        try:
            print(f"[UKG] Ingested intel from {str(intel.get('agent', 'unknown')).encode('ascii', 'ignore').decode()}")
        except Exception:
            print("[UKG] Intel Ingested.")

    def ingest_node(self, node: Dict[str, Any]):
        """Ingests a device node into the UKG."""
        if not os.path.exists(self.ukg_path):
            state = {"@context": "https://camelot.os/ukg", "UKG_NODE": {"DEVICES": []}}
        else:
            with open(self.ukg_path, "r") as f:
                try:
                    state = json.load(f)
                except json.JSONDecodeError:
                    state = {"@context": "https://camelot.os/ukg", "UKG_NODE": {}}

        if "UKG_NODE" not in state:
            state["UKG_NODE"] = {}

        if "DEVICES" not in state["UKG_NODE"]:
            state["UKG_NODE"]["DEVICES"] = []

        # Check if exists and update
        devices = state["UKG_NODE"]["DEVICES"]
        existing = next((i for i, d in enumerate(devices) if d.get("id") == node.get("id")), None)

        if existing is not None:
            devices[existing] = node
        else:
            devices.append(node)

        with open(self.ukg_path, "w") as f:
            json.dump(state, f, indent=4)
        print(f"[UKG] Ingested node: {node.get('label')}")


if __name__ == "__main__":
    engine = UKGDeltaEngine()
    print(json.dumps(engine.get_delta("init"), indent=2))