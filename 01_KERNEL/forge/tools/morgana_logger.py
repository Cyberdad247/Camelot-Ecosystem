# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path

# 🛡️ CONFIGURATION
LOG_DIR = Path(r"C:\Users\vizio\CAMELOT_OS\99_HISTORY\morgana_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
CURRENT_LOG_FILE = LOG_DIR / f"session_{datetime.now().strftime('%Y%m%d')}.jsonl"


class MorganaLogger:
    """
    The All-Seeing Eye of Morgana.
    Enforces the 'Atom of History' schema for every system event.
    """

    def __init__(self, actor="SYSTEM"):
        self.actor = actor

    def log(self, action, target, status="SUCCESS", context=None):
        """
        Logs an immutable event atom.
        """
        if context is None:
            context = {}

        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Payload for Hashing
        payload = f"{timestamp}{self.actor}{action}{target}{status}{json.dumps(context, sort_keys=True)}"
        event_hash = hashlib.sha256(payload.encode()).hexdigest()

        event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "actor": self.actor,
            "action": action,
            "target": target,
            "status": status,
            "context": context,
            "hash": event_hash,
        }

        # Atomic Append
        with open(CURRENT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        print(f"👁️ [MORGANA] {action} -> {target} [{status}]")
        return event_id


# Global Instance
logger = MorganaLogger()

if __name__ == "__main__":
    # Test
    logger.log("TEST_EVENT", "Morgana Logger", "SUCCESS", {"version": "1.0"})