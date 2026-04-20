# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Ω_DEFENSE_GRID_v2.0 :: ROTEL_TELEMETRY_ENGINE
Author: Sir Forge (Lukas)
Mode: BEAVER 🦫
"""

import json
import logging
import os
import time
from typing import Any, Dict

# Configure Logging (Kinetic Standard)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | ROTEL | %(message)s")


class RotelMonitor:
    """
    The Rotel Telemetry Engine.
    Monitors System Vitals and reports to the Defense Grid.
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            # Resolve relative to this script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.yaml")

        self.config = self._load_config(config_path)
        self.active = True

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads grid configuration safely."""
        try:
            if not os.path.exists(path):
                logging.warning(f"Config not found at {path}. Using defaults.")
                return {"memory_threshold_mb": 1024, "interval": 5}

            # Simple parser mock to avoid PyYAML dependency if not guaranteed
            # In production, we'd use yaml.safe_load
            return {"memory_threshold_mb": 1024, "interval": 5}
        except Exception as e:
            logging.error(f"Config Load Failure: {e}")
            return {}

    def get_memory_usage(self) -> Dict[str, float]:
        """
        Retrieves current memory stats.
        Uses psutil if available, else mocks for bootstrap compatibility.
        """
        try:
            import psutil

            mem = psutil.virtual_memory()
            return {
                "total": mem.total / (1024 * 1024),
                "available": mem.available / (1024 * 1024),
                "percent": mem.percent,
            }
        except ImportError:
            logging.warning("psutil not found. Using kinetic simulation.")
            return {"total": 16384, "available": 8192, "percent": 50.0}

    def scan(self):
        """Execute a Rotel Scan Cycle."""
        logging.info("Initiating Rotel Scan...")
        stats = self.get_memory_usage()

        logging.info(f"Memory Status: {stats['percent']}% Used ({stats['available']:.2f} MB Free)")

        threshold = self.config.get("memory_threshold_mb", 1024)
        if stats["available"] < threshold:
            self.trigger_alert("CRITICAL_MEMORY_LOW", stats)

    def trigger_alert(self, code: str, data: Dict[str, Any]):
        """Dispatches an alert to the Watchtower using Kinetic Rotel."""
        alert_payload = {"timestamp": time.time(), "code": code, "data": data, "origin": "ROTEL_PRIME"}
        logging.critical(f"ALERT DISPATCHED: {json.dumps(alert_payload)}")

        # KINETIC UPGRADE: Pipe to Rust Rotel Binary
        import subprocess

        rotel_path = r"C:\Users\vizio\CAMELOT_OS\02_FORGE\kinetic\rotel\target\release\rotel.exe"
        if os.path.exists(rotel_path):
            attrs = json.dumps({"code": code, "origin": "DEFENSE_GRID"})
            try:
                subprocess.run(
                    [rotel_path, "log", "--name", "DEFENSE_ALERT", "--attrs", attrs], check=True, capture_output=True
                )
                logging.info("Kinetic Telemetry Sync: SUCCESS")
            except Exception as e:
                logging.error(f"Kinetic Telemetry Sync: FAILED ({e})")
        else:
            logging.error("Rotel Binary not found. Kinetic Telemetry offline.")


if __name__ == "__main__":
    rotel = RotelMonitor()
    rotel.scan()