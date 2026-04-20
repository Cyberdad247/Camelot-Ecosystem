# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
🧬 TITAN EVOLVE (Kinetic Layer)
Purpose: Skill Unlocking & Evolution. 
Act as: The Shaper.
"""
import sys
import os
import re

VAULT_ROOT = r"C:\Users\vizio\CAMELOT_OS\03_VAULT"

SKILLS_MAP = {
    2: "Advanced Reasoning (System 2)",
    3: "Multimodal Analysis (Ocular)",
    4: "Kinetic Refactoring (The Hand)",
    5: "Sovereign Autonomy (Merlin's Voice)"
}

def evolve_knight(agent_name):
    """
    Checks the level of a Knight and unlocks pending skills.
    """
    # Find the agent file
    target_file = None
    for root, dirs, files in os.walk(VAULT_ROOT):
        if f"{agent_name}.md" in files:
            target_file = os.path.join(root, f"{agent_name}.md")
            break
            
    if not target_file:
        print(f"⚠️  Shaper could not find Knight Registry for {agent_name}")
        return

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse current Level
        lvl_match = re.search(r"> Level: (\d+)", content)
        if not lvl_match:
            print(f"⚠️  {agent_name} has no Level recorded. Scribe must process them first.")
            return
            
        current_level = int(lvl_match.group(1))
        
        # Determine unlocked skills
        unlocked = []
        for lvl, skill in SKILLS_MAP.items():
            if current_level >= lvl:
                unlocked.append(skill)
                
        if not unlocked:
            print(f"🌱 {agent_name} is still a novice (Level {current_level}). No skills unlocked yet.")
            return

        # Prepare Skills Section
        skills_text = "## 🧬 Unlocked Skills\n"
        for skill in unlocked:
            skills_text += f"*   [x] **{skill}**\n"
        
        # Update Content
        if "## 🧬 Unlocked Skills" in content:
            # Replace existing section
            content = re.sub(r"## 🧬 Unlocked Skills.*?(?=\n##|\Z)", skills_text, content, flags=re.DOTALL)
        else:
            # Append before Directives or at end
            if "## Directives" in content:
                content = content.replace("## Directives", f"{skills_text}\n## Directives")
            else:
                content += f"\n{skills_text}"
                
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"🧬 [EVOLVE] {agent_name} has been reshaped! Skills synced for Level {current_level}.")
        
    except Exception as e:
        print(f"💥 [EVOLVE] Evolution failed for {agent_name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: titan_evolve.py <agent_name>")
        sys.exit(1)
        
    evolve_knight(sys.argv[1])