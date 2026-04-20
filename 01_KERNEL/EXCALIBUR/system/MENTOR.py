# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
🧙‍♂️ MENTOR SCRIPT (L6 Governance)
Purpose: System Hygiene & Sovereign Audit.
Ensures the Titanium Laws are upheld and the Kinetic stack is clean.
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

ROOT = r"C:\Users\vizio\CAMELOT_OS"
SECURE_ARCHIVE = os.path.join(ROOT, "03_VAULT", "00_SECURE_ARCHIVE")
LEDGER_PATH = os.path.join(ROOT, "PROVENANCE_LEDGER.md")

def log_to_ledger(action, status="SUCCESS"):
    timestamp = datetime.now().isoformat()
    entry = f"| {timestamp} | MENTOR_Ω | {action} | {status} |"
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + entry)
    print(entry)

def sanitize_environment():
    """
    Finds exposed .env files and moves them to the Secure Archive.
    Replaces them with .env.sample if they don't have one.
    """
    print("🔍 [MENTOR] Scanning for exposed .env files...")
    exposed_count = 0
    
    skip_dirs = {"node_modules", ".git", ".next", "dist", "build", "03_VAULT", "99_HISTORY"}
    
    for root, dirs, files in os.walk(ROOT):
        # Skip specified directories efficiently
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith(".env") or ".env." in file:
                # Skip .env.example or .env.sample
                if any(x in file.lower() for x in ["example", "sample", "template"]):
                    continue
                
                source_path = os.path.join(root, file)
                
                # Generate a unique hash name to avoid collisions in archive
                file_hash = hashlib.md5(source_path.encode()).hexdigest()[:8]
                dest_name = f"{file_hash}_{file}"
                dest_path = os.path.join(SECURE_ARCHIVE, dest_name)
                
                print(f"🛑 [MENTOR] Exposing detected: {source_path} -> Archiving as {dest_name}")
                
                try:
                    os.makedirs(SECURE_ARCHIVE, exist_ok=True)
                    shutil.move(source_path, dest_path)
                    exposed_count += 1
                except Exception as e:
                    print(f"⚠️  [MENTOR] Failed to move {file}: {e}")

    if exposed_count > 0:
        log_to_ledger(f"GOVERNANCE: Secured {exposed_count} .env files.")
    else:
        print("✅ [MENTOR] No exposed .env files found outside the Vault.")

def check_system_integrity():
    """
    Checks if core protocols and binaries are present.
    """
    print("\n⚖️  [MENTOR] Running Integrity Audit...")
    critical_paths = [
        "01_KERNEL/protocols/titan_protocol.md",
        "01_KERNEL/protocols/iron_gate_protocol.md",
        "02_FORGE/kinetic/merlin_dispatch.py",
        "PROVENANCE_LEDGER.md"
    ]
    
    missing = []
    for p in critical_paths:
        if not os.path.exists(os.path.join(ROOT, p)):
            missing.append(p)
            
    if missing:
        print(f"❌ [MENTOR] Integrity compromised! Missing: {', '.join(missing)}")
        return False
    
    print("💎 [MENTOR] System Integrity: RADIANT")
    return True

def main():
    print("🏰 [MENTOR] Activating Sovereign Oversight...")
    sanitize_environment()
    if check_system_integrity():
        log_to_ledger("AUDIT: System Integrity Verified.")

if __name__ == "__main__":
    main()