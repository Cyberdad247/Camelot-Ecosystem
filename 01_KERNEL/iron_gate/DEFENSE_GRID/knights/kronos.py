# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import subprocess
import logging
import os

class SirKronos:
    """📊 Sir Kronos (Metrics): Uses rotel to generate resource heatmaps."""
    
    def __init__(self, threshold_ram_gb=8, threshold_cpu=80):
        self.threshold_ram_gb = threshold_ram_gb
        self.threshold_cpu = threshold_cpu
        self.rotel_path = r"C:\Users\vizio\CAMELOT_OS\02_FORGE\kinetic\rotel\target\release\rotel.exe"
        
    def sense(self):
        logging.info("📊 [KRONOS]: Checking system vitals via Rotel...")
        try:
            # Check if binary exists, otherwise use fallback logic or mock
            if os.path.exists(self.rotel_path):
                res = subprocess.run(
                    [self.rotel_path, "--check-resources"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                return res.stdout
            else:
                # Mock output if binary missing for now
                return f"WARNING: RAM usage at 75% | CPU at {self.threshold_cpu - 5}%"
        except Exception as e:
            logging.error(f"KRONOS ERROR: {e}")
            return str(e)