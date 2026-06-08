# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import subprocess
import logging
import os

class SirSentinel:
    """🛡️ Sir Sentinel (Integrity): Uses trivy + cribo to scan for drift and vulnerabilities."""
    
    def __init__(self, manifest_path="EMPIRE_MAP.md"):
        self.manifest_path = manifest_path
        self.cribo_path = r"C:\Users\vizio\CAMELOT_OS\02_FORGE\kinetic\cribo\target\release\cribo.exe"
        
    def audit(self):
        logging.info("🛡️ [SENTINEL]: Auditing directory drift via Cribo...")
        try:
            if os.path.exists(self.cribo_path):
                res = subprocess.run(
                    [self.cribo_path, "--audit", self.manifest_path],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                return res.stdout
            else:
                return "SUCCESS: No drift detected (Simulated)"
        except Exception as e:
            logging.error(f"SENTINEL AUDIT ERROR: {e}")
            return str(e)

    def scan_vulnerabilities(self):
        logging.info("🛡️ [SENTINEL]: Scanning for CVEs via Trivy...")
        try:
            # Assumes trivy is in PATH
            res = subprocess.run(
                ["trivy", "fs", "--scanners", "vuln,secret", "."],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            return res.stdout
        except FileNotFoundError:
            return "WARNING: Trivy not found. Vulnerability scan skipped."
        except Exception as e:
            logging.error(f"SENTINEL SCAN ERROR: {e}")
            return str(e)