# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import logging
import os
import sys
import time

# Ensure kernel path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DEFENSE_GRID.knights import SirCastor, SirKronos, SirOctavian, SirSentinel

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | AEGIS | %(message)s")

class SITLoop:
    """The Sense-Think-Triage Loop Engine."""
    
    def __init__(self, interval=300):
        self.interval = interval
        self.kronos = SirKronos()
        self.sentinel = SirSentinel()
        self.octavian = SirOctavian()
        self.castor = SirCastor()
        self.active = True

    def run(self):
        logging.info("🛡️ [AEGIS]: Autonomous Watchtower SIT Loop Started.")
        try:
            while self.active:
                self.pulse()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logging.warning("⚠️ [AEGIS]: Watchtower Pulse Interrupted.")

    def pulse(self):
        logging.info("🛡️ [AEGIS]: Pulse Initiated...")
        
        # 1. SENSE
        vitals = self.kronos.sense()
        drift = self.sentinel.audit()
        
        # 2. THINK & TRIAGE
        if "CRITICAL" in drift or "CRITICAL" in vitals:
            logging.critical("🚨 [AEGIS]: Critical Threat Detected!")
            self.octavian.lockdown()
        elif "WARNING" in vitals:
            logging.warning("🧹 [AEGIS]: Resource Warnings. Initiating minor cleanup.")
            # Low severity repair via Castor
            self.castor.execute_repair("echo 'Cleaning temp artifacts...'")
        else:
            logging.info("✅ [AEGIS]: System Nominal. Ledger Synced.")

if __name__ == "__main__":
    loop = SITLoop()
    loop.run()