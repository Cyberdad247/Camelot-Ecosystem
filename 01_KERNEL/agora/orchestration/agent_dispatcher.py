# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[IDENTITY]: CAMELOT_OS Agent Dispatcher v1.0
[MANDATE]: Route raw intelligence to specialized workers for Agency Fulfillment.
[SOVEREIGN]: VaShawn O. Head
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class AgentDispatcher:
    def __init__(self):
        self.output_dir = "02_FORGE/agency_factory/deliverables"
        self.scout_dir = "02_FORGE/agency_factory/scouts"
        
    def triage_lead(self, raw_data: Dict) -> str:
        """
        Determines the next agent based on data salience.
        """
        score = raw_data.get("relevance_score", 0)
        has_tech_gap = raw_data.get("tech_gap_detected", False)
        
        if score > 0.8 and has_tech_gap:
            return "SIR_ORACLE"  # High priority audit
        elif score > 0.5:
            return "SQUIRE_COPY"  # Personalize outreach
        else:
            return "ARCHIVE" # Low priority

    def dispatch_task(self, lead_id: str, agent_id: str, payload: Dict):
        """
        Simulates task handoff to specialized agents.
        Logs action to the Provenance Ledger.
        """
        task_packet = {
            "lead_id": lead_id,
            "client_id": payload.get("client_id", "UNKNOWN_CLIENT"), # Maps to userId in DB
            "agent": agent_id,
            "timestamp": datetime.now().isoformat(),
            "payload": payload,
            "status": "PENDING"
        }
        
        file_path = os.path.join(self.scout_dir, f"task_{lead_id}_{agent_id}.json")
        with open(file_path, "w") as f:
            json.dump(task_packet, f, indent=4)
            
        self._log_to_ledger(f"Dispatched lead {lead_id} to {agent_id}")
        return file_path

    def _log_to_ledger(self, message: str):
        ledger_path = "PROVENANCE_LEDGER.md"
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(f"| {timestamp} | DISPATCHER_Ω | {message} | SUCCESS |\n")

if __name__ == "__main__":
    # Test Cycle
    dispatcher = AgentDispatcher()
    test_lead = {
        "id": "LEAD_001",
        "company": "Sovereign Logistics",
        "relevance_score": 0.95,
        "tech_gap_detected": True
    }
    target = dispatcher.triage_lead(test_lead)
    path = dispatcher.dispatch_task(test_lead["id"], target, test_lead)
    print(f"Task dispatched: {path}")