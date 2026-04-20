# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Rotel Python Client — Kinetic Telemetry Bridge.
Binds Python reasoning nodes to the Rust-based Rotel collector on :4317.
"""

import os
import json
import socket
import requests
import datetime
from typing import Optional

ROTEL_URL = "http://127.0.0.1:4317/v1/logs"

# Load Kinetic Token from registry
def get_kinetic_token():
    try:
        registry_path = os.path.join(os.path.dirname(__file__), "..", "config", "registry", "secrets.json")
        with open(registry_path, 'r') as f:
            return json.load(f).get("kinetic_token")
    except Exception:
        return os.getenv("CAMELOT_KINETIC_TOKEN", "default-token")

KINETIC_TOKEN = get_kinetic_token()


def utc_timestamp() -> str:
    """Return an RFC3339-style UTC timestamp without relying on deprecated utcnow()."""
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

class RotelClient:
    """Synchronous bridge to the Rust Rotel collector."""
    
    def __init__(self, component: str):
        self.component = component
        self.host = socket.gethostname()

    def log(self, level: str, message: str, metadata: Optional[dict] = None):
        """Send a log entry to Rotel."""
        payload = {
            "level": level.upper(),
            "message": message,
            "component": self.component,
            "timestamp": utc_timestamp(),
            "metadata": metadata or {}
        }
        
        headers = {
            "X-API-Key": KINETIC_TOKEN
        }
        
        try:
            # We use a short timeout to prevent blocking the kernel if Rotel is down
            response = requests.post(ROTEL_URL, json=payload, headers=headers, timeout=0.1)
            return response.status_code == 200
        except Exception:
            # Silently fail if Rotel is not reachable (Law of Kinetic Purity: Telemetry must not crash execution)
            return False

    def info(self, message: str, **kwargs):
        return self.log("INFO", message, kwargs)

    def warn(self, message: str, **kwargs):
        return self.log("WARN", message, kwargs)

    def error(self, message: str, **kwargs):
        return self.log("ERROR", message, kwargs)

    def debug(self, message: str, **kwargs):
        return self.log("DEBUG", message, kwargs)

# Global singleton for common kernel logging
logger = RotelClient("merlin_core")
