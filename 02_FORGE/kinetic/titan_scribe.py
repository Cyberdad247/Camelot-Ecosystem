# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
📜 TITAN SCRIBE (Kinetic Layer)
Purpose: The Historian & Teacher. Records errors to Learning Log.
Act as: Sir Scribe.
"""
import sys
import os
import datetime

LEARNING_LOG = r"C:\Users\vizio\CAMELOT_OS\03_VAULT\99_SCRATCHPAD\Learning_Log.md"

def scribe_error(error_msg, context="General"):
    """
    Records an error to the Learning Log.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ensure Scratchpad exists
    os.makedirs(os.path.dirname(LEARNING_LOG), exist_ok=True)
    
    if not os.path.exists(LEARNING_LOG):
        with open(LEARNING_LOG, "w", encoding="utf-8") as f:
            f.write("# 📜 The Scroll of Wisdom (Learning Log)\n\n")

    entry = f"""
### 🛑 Error Encountered
**Time**: {timestamp}
**Context**: {context}
**Error**: `{error_msg}`

#### 🧠 Analysis (The Lesson)
*   [ ] **Root Cause**: ...
*   [ ] **Solution**: ...
*   [ ] **Titan Rule**: ...

---
"""
    with open(LEARNING_LOG, "a", encoding="utf-8") as f:
        f.write(entry)
        
    print(f"📜 Scribe has recorded this failure in the Scroll of Wisdom: {LEARNING_LOG}")

import re
def calculate_level(xp):
    """
    Calculates level based on XP thresholds.
    L1: 0, L2: 100, L3: 300, L4: 600, L5: 1000
    """
    if xp < 100: return 1
    if xp < 300: return 2
    if xp < 600: return 3
    if xp < 1000: return 4
    return 5 + (xp - 1000) // 1000 # Scaling after L5

import json
PERFORMANCE_LEDGER_JSON = r"C:\Users\vizio\CAMELOT_OS\03_VAULT\99_SCRATCHPAD\performance_metrics.json"

def record_performance(agent_name, task_id, duration, efficiency):
    """
    Logs performance metrics (speed & efficiency) for a specific task.
    Updates the central JSON ledger and the individual Knight registry.
    """
    # 1. Update JSON Ledger
    metrics = {}
    if os.path.exists(PERFORMANCE_LEDGER_JSON):
        try:
            with open(PERFORMANCE_LEDGER_JSON, "r") as f:
                metrics = json.load(f)
        except: metrics = {}
    
    if agent_name not in metrics:
        metrics[agent_name] = []
    
    metrics[agent_name].append({
        "task_id": task_id,
        "duration": duration,
        "efficiency": efficiency,
        "timestamp": datetime.datetime.now().isoformat()
    })
    
    with open(PERFORMANCE_LEDGER_JSON, "w") as f:
        json.dump(metrics, f, indent=4)

    # 2. Update Knight Registry (MD)
    vault_root = r"C:\Users\vizio\CAMELOT_OS\03_VAULT"
    target_file = None
    for root, dirs, files in os.walk(vault_root):
        if f"{agent_name}.md" in files:
            target_file = os.path.join(root, f"{agent_name}.md")
            break
            
    if target_file:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add Performance Table if not exists
        if "## 📈 Performance History" not in content:
            content += "\n## 📈 Performance History\n| Task | Speed (s) | Efficiency (%) | Date |\n| :--- | :--- | :--- | :--- |\n"
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        new_row = f"| {task_id[:10]} | {duration:.2f}s | {efficiency}% | {date_str} |\n"
        content += new_row
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"📊 [METRICS] {agent_name} performance recorded: {duration}s @ {efficiency}%")

def award_xp(agent_name, amount, reason="Successful Kinetic Execution"):
    """
    Awards XP to a Knight by updating their local Markdown registry.
    Handles leveling logic.
    """
    vault_root = r"C:\Users\vizio\CAMELOT_OS\03_VAULT"
    # Find the agent file
    target_file = None
    for root, dirs, files in os.walk(vault_root):
        if f"{agent_name}.md" in files:
            target_file = os.path.join(root, f"{agent_name}.md")
            break
            
    if not target_file:
        print(f"⚠️  Scribe could not find Knight Registry for {agent_name}")
        return

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse current XP
        xp_match = re.search(r"> XP: (\d+)", content)
        current_xp = int(xp_match.group(1)) if xp_match else 0
        new_xp = current_xp + amount
        
        # Parse current Level
        lvl_match = re.search(r"> Level: (\d+)", content)
        old_level = int(lvl_match.group(1)) if lvl_match else 1
        new_level = calculate_level(new_xp)
        
        # Update Content
        # Update XP
        if xp_match:
            content = re.sub(r"> XP: \d+", f"> XP: {new_xp}", content)
        else:
            content = re.sub(r"(> Status: ACTIVE)", f"\\1\n> XP: {new_xp}", content)
            
        # Update Level
        if lvl_match:
            content = re.sub(r"> Level: \d+", f"> Level: {new_level}", content)
        else:
            # Insert Level after XP
            content = re.sub(r"(> XP: \d+)", f"\\1\n> Level: {new_level}", content)
            
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"✨ [XP] {agent_name} gained {amount} XP! (Total: {new_xp})")
        if new_level > old_level:
            print(f"🎊 [LEVEL UP] {agent_name} reached Level {new_level}!")
            # Award bonus for leveling up? Maybe 10 bonus XP? 
            # No, avoid infinite loops. Just log it.
        
    except Exception as e:
        scribe_error(f"Failed to award XP to {agent_name}: {e}", "Scribe XP Subsystem")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: titan_scribe.py <error_message> [context]")
        print("       titan_scribe.py --xp <agent> <amount> <reason>")
        sys.exit(1)
        
    if sys.argv[1] == "--xp":
         if len(sys.argv) < 4:
             print("Usage: --xp <agent> <amount>")
             sys.exit(1)
         award_xp(sys.argv[2], int(sys.argv[3]))
    elif sys.argv[1] == "--metrics":
         if len(sys.argv) < 6:
             print("Usage: --metrics <agent> <task_id> <duration> <efficiency>")
             sys.exit(1)
         record_performance(sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5]))
    else:
        msg = sys.argv[1]
        ctx = sys.argv[2] if len(sys.argv) > 2 else "Kinetic Execution"
        scribe_error(msg, ctx)