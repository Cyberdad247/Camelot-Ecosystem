# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
🧙‍♂️ MERLIN DISPATCH (Kinetic Layer)
Purpose: Central Command Router. Unifies the Titan System under one CLI.
Act as: The Magician.
"""
import os
import subprocess
import sys

# Tool Registry
# Maps keywords to scripts
REGISTRY = {
    "upgrade": r"02_FORGE\kinetic\knight_upgrade.py",
    "scout": r"02_FORGE\kinetic\ocular_scout.py", 
    "plan": r"02_FORGE\kinetic\titan_architect.py",
    "weave": r"02_FORGE\kinetic\titan_loom.py",
    "optimize": r"02_FORGE\kinetic\titan_alchemist.py",
    "scribe": r"02_FORGE\kinetic\titan_scribe.py",
    "evolve": r"02_FORGE\kinetic\titan_evolve.py",
    "triage": r"02_FORGE\kinetic\titan_triage.py",
    "grade": r"02_FORGE\kinetic\titan_grader.py",
    "dispatch": r"02_FORGE\kinetic\merlin_dispatch.py" 
}

# Aliases
ALIASES = {
    "up": "upgrade",
    "ls": "scout",
    "architect": "plan",
    "loom": "weave",
    "alchemist": "optimize",
    "history": "scribe",
    "xp": "scribe", # Special handling
    "evo": "evolve",
    "swarm": "triage",
    "perf": "metrics",
    "report": "grade"
}


OS_ROOT = r"C:\Users\vizio\CAMELOT_OS"

def run_tool(tool_name, args):
    # Handle Aliases
    if tool_name in ALIASES:
        if tool_name == "xp":
             # Special case for XP
             tool_name = "scribe"
             args = ["--xp"] + args
        elif tool_name == "perf":
             # Special case for Performance Metrics
             tool_name = "scribe"
             args = ["--metrics"] + args
        else:
             tool_name = ALIASES[tool_name]

    if tool_name not in REGISTRY:
        print(f"🧙‍♂️ [MERLIN] I do not know the spell '{tool_name}'.")
        print(f"   Known Spells: {', '.join(REGISTRY.keys())}")
        print(f"   Known Aliases: {', '.join(ALIASES.keys())}")
        return

    script_path = os.path.join(OS_ROOT, REGISTRY[tool_name])
    
    # Construct command
    cmd = ["python", script_path] + args
    
    print(f"🪄 [MERLIN] Casting '{tool_name}'...")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"💥 [MERLIN] The spell backfired: {e}")
    except KeyboardInterrupt:
        print("\n🛑 [MERLIN] Spell interrupted.")

def interactive_mode():
    print("🏰 [MERLIN] The Tower of Camelot is Open. Command me. (Type 'exit' to leave)")
    print("✨ Tip: Use 'xp <knight> <amount>' to award progress.")
    while True:
        try:
            line = input("🧙‍♂️ > ").strip()
            if not line:
                continue
            if line.lower() in ["exit", "quit"]:
                print("👋 [MERLIN] The Tower closes. Safe travels, Sovereign.")
                break
                
            parts = line.split()
            command = parts[0].lower()
            args = parts[1:]
            
            run_tool(command, args)
            
        except KeyboardInterrupt:
            print("\n👋 [MERLIN] The Tower closes.")
            break
        except Exception as e:
            print(f"⚠️  [MERLIN] A mystical error occurred: {e}")


def main():
    if len(sys.argv) < 2:
        interactive_mode()
    else:
        command = sys.argv[1].lower()
        args = sys.argv[2:]
        run_tool(command, args)

if __name__ == "__main__":
    main()