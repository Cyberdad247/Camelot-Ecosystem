# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
⚔️ NANO-KNIGHT UPGRADE PROTOCOL (Kinetic Layer)
Purpose: Propagate Assimilation Protocol V2 to all active Agents.
"""
import os
import glob
import hashlib
from datetime import datetime

KNIGHTS_DIR = r"C:\Users\vizio\CAMELOT_OS\03_VAULT\Nano-Knights"
PROTOCOL_PATH = r"C:\Users\vizio\CAMELOT_OS\01_KERNEL\protocols\assimilation_v4_omega.md"
COLLAB_PATH = r"C:\Users\vizio\CAMELOT_OS\01_KERNEL\prompts\subagent_collaboration.md"
LEDGER = r"C:\Users\vizio\CAMELOT_OS\PROVENANCE_LEDGER.md"

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"| {timestamp} | [UPGRADE] | V3 | {message} |\n"
    print(entry.strip())
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(entry)

import argparse
import re

def get_knight_stats(filepath):
    """Parses existing XP and Level from a knight file."""
    if not os.path.exists(filepath):
        return 0, 1
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    xp_match = re.search(r"> XP: (\d+)", content)
    lvl_match = re.search(r"> Level: (\d+)", content)
    xp = int(xp_match.group(1)) if xp_match else 0
    lvl = int(lvl_match.group(1)) if lvl_match else 1
    return xp, lvl

def upgrade_knights(dry_run=False):
    print(f"🏰 [CAMELOT] {'Verifying' if dry_run else 'Initiating'} Knight Upgrade Sequence (Omega)...")
    
    if not os.path.exists(KNIGHTS_DIR):
        print(f"⚠️  [WARNING] No Knight Registry found at {KNIGHTS_DIR}")
        os.makedirs(KNIGHTS_DIR, exist_ok=True)
        print("   > Created Registry.")
    
    # Titan Hierarchy Registry
    registry = [
        ("Sir_Forge", "Nano-Knights/Sir_Forge.md", "KNIGHT"),
        ("Sir_Sentinel", "Nano-Knights/Sir_Sentinel.md", "KNIGHT"),
        ("Squire_Clean", "Nano-Knights/Squire_Clean.md", "SQUIRE"),
        ("Squire_Audit", "Nano-Knights/Squire_Audit.md", "SQUIRE"),
        ("Squire_Format", "Nano-Knights/Squire_Format.md", "SQUIRE"),
        ("Sir_Aris", "Knights/Reasoning/Sir_Aris.md", "KNIGHT"),
        ("Sir_Vega", "Knights/Reasoning/Sir_Vega.md", "KNIGHT"),
        ("Elder_Kaelen", "Knights/Governance/Elder_Kaelen.md", "ELDER"),
        ("Sir_Arthur", "Knights/Governance/Sir_Arthur.md", "KNIGHT"),
        ("Sir_Architect", "Knights/Engineering/Sir_Architect.md", "KNIGHT"),
        ("Sir_Alchemist", "Knights/Engineering/Sir_Alchemist.md", "KNIGHT"),
        ("Sir_Scribe", "Knights/Engineering/Sir_Scribe.md", "KNIGHT")
    ]
    
    PERSONAS = {
        "Sir_Forge": "The Stoic Builder. Values kinetic purity and structural integrity. Vibe: Industrial/Brutalist.",
        "Sir_Sentinel": "The Vigilant Ghost. Paranoid and precise. Values security and encryption. Vibe: Cyber-Noir.",
        "Squire_Clean": "The Diligent Servant. Values order and clarity. Vibe: Minimalist.",
        "Squire_Audit": "The Shadow Seeker. Values hidden detail. Vibe: Forensic.",
        "Squire_Format": "The Aesthetic. Values the beauty of syntax. Vibe: Elegant.",
        "Sir_Aris": "The Logical Auditor. Ensures precondition satisfaction and symbolic consistency. Vibe: Mathematical.",
        "Sir_Vega": "The Strategic Futurist. Visualizes 2nd/3rd order consequences. 'Take it to the End.' Vibe: Cosmic.",
        "Elder_Kaelen": "The Ethical Synthesizer. Performs Snowball Recaps to prevent context rot. Vibe: Ancient/Vellum.",
        "Sir_Arthur": "The Sovereign Judge. Values the Titanium Laws and human alignment. Vibe: High-High-Fantasy.",
        "Sir_Architect": "The Infinite Weaver. Values the UKG Graph and long-term modularity. Vibe: Geometric/Blueprints.",
        "Sir_Alchemist": "The Transmuter. Values performance and memory optimization. Vibe: Neon-Vibrant.",
        "Sir_Scribe": "The Eternal Witness. Values accuracy and the legacy of Camelot. Vibe: Parchment/Steampunk."
    }

    DIRECTIVES = {
        "Squire_Clean": "Leave the codebase cleaner than you found it. Silence the linter. Purge the bloat.",
        "Squire_Audit": "Uncover every shadow. Document every vulnerability. The truth is encrypted.",
        "Squire_Format": "Code is art. Every semicolon is a brushstroke. Enforce the beauty of the Kingdom."
    }
    
    vault_root = r"C:\Users\vizio\CAMELOT_OS\03_VAULT"
    
    for name, rel_path, role in registry:
        full_path = os.path.join(vault_root, rel_path)
        
        if dry_run:
            if os.path.exists(full_path):
                print(f"✅ [OK] {name} exists.")
            else:
                print(f"❌ [MISSING] {name} at {rel_path}")
            continue

        # Ensure directory exists (for new migrations)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Preserve XP and Level
        xp, lvl = get_knight_stats(full_path)
        
        # 1. Create/Update Agent Definition
        with open(full_path, "w", encoding="utf-8") as f:
            role_glyph = '🛡️' if role == 'KNIGHT' else '🧹' if role == 'SQUIRE' else '📜'
            f.write(f"# {role_glyph} {name}\n")
            f.write(f"> Status: ACTIVE\n")
            f.write(f"> Role: {role}\n")
            f.write(f"> XP: {xp}\n")
            f.write(f"> Level: {lvl}\n")
            
            if role in ["KNIGHT", "ELDER"]:
                f.write(f"> Persona: {PERSONAS.get(name, 'Standard Protocol')}\n")
            else:
                f.write(f"> Directive: {DIRECTIVES.get(name, 'Assist the Knights.')}\n")
                
            f.write(f"> Protocol: Omega (Connected)\n\n")
            f.write(f"## Directives\n")
            f.write(f"1. Follow [Assimilation Omega]({PROTOCOL_PATH})\n")
            f.write(f"2. Obey [Collaboration Rules]({COLLAB_PATH})\n")
            
        print(f"✅ [PATCH] {name} updated to Omega Protocol (XP: {xp}, Level: {lvl}).")
    
    if not dry_run:
        log_event("Upgraded all Knights to Omega while preserving XP.")

    print("\n✨ All Active Knights Upgraded.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camelot Knight Upgrade Tool")
    parser.add_argument("--check", action="store_true", help="Verify system integrity without changing files.")
    args = parser.parse_args()
    
    upgrade_knights(dry_run=args.check)