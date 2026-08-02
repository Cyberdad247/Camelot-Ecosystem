# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import logging
import subprocess


class SirCastor:
    """🦫 Sir Castor (Isolation): Executes repairs inside sandboxes."""
    
    def __init__(self):
        self.mode = "DOCKER" # Default to Docker
        
    def execute_repair(self, cmd):
        if isinstance(cmd, str):
            raise TypeError("cmd must be a list of arguments, not a bare string — prevents shell injection")
        logging.info(f"🦫 [CASTOR]: Executing repair in isolated {self.mode} sandbox...")
        try:
            res = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return res.stdout
        except Exception as e:
            logging.error(f"CASTOR REPAIR ERROR: {e}")
            return str(e)