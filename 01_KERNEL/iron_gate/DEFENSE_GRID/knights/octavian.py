# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import logging
import sys
import os

# Ensure we can import from the kernel tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools import antigravity_safe as antigravity

class SirOctavian:
    """🔐 Sir Octavian (Governance): Enforces the Iron Gate laws."""
    
    def __init__(self):
        self.max_lines = 10
        self.max_size_mb = 50
        
    def enforce_iron_gate(self, action_count, file_size_mb):
        """
        Rule: Block any repair > 10 lines or > 50MB without HITL_APPROVAL.
        """
        if action_count > self.max_lines or file_size_mb > self.max_size_mb:
            logging.critical(f"🔐 [OCTAVIAN]: VIOLATION! Action size ({action_count} lines, {file_size_mb}MB) exceeds Iron Gate limits.")
            return False, "REQUIRES_HITL_APPROVAL"
        return True, "ALLOWED"

    def lockdown(self, path="./"):
        logging.info(f"🚨 [OCTAVIAN]: Engaging Lockdown for {path}")
        antigravity.antigravity_open(path, "lock") # Conceptually locking
        return True