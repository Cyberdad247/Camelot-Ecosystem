# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
from datetime import datetime

def generate_tree(startpath):
    output = []
    output.append("# 🗺️ CAMELOT APEX: ENTIRE MAP (Territory)")
    output.append(f"**Timestamp:** {datetime.now().isoformat()}")
    output.append("**Mode:** Kinetic Purity [Active]")
    output.append(f"**Root:** `{startpath}`")
    output.append("")
    output.append("---")
    output.append("")
    output.append("📂 CAMELOT_OS/")
    
    exclude_dirs = {
        '.git', '.venv', '__pycache__', 'node_modules', '.next', '.pytest_cache', 
        '.antigravity_backups', 'temp_remotion', 'temp_supermemory', 'temp_trivy',
        'dist', 'archive'
    }
    
    def walk_dir(path, indent="  ", depth=0):
        if depth > 10: # Safety cap
            return
        
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return

        # Separate files and dirs
        files = [i for i in items if os.path.isfile(os.path.join(path, i))]
        dirs = [i for i in items if os.path.isdir(os.path.join(path, i))]
        
        # Files first (as per existing pattern in entiremap.md)
        for f in files:
            output.append(f"{indent}- {f}")
            
        for d in dirs:
            if d in exclude_dirs:
                continue
            
            # Limit recursion to core directories
            if d not in {"01_KERNEL", "src", "config", "docs", "scripts"}:
                output.append(f"{indent}📂 {d}/")
                continue

            tag = ""
            if d == "01_KERNEL":
                tag = " [CORE]"
            
            output.append(f"{indent}📂 {d}/{tag}")
            walk_dir(os.path.join(path, d), indent + "  ", depth + 1)

    walk_dir(startpath)
    return "\n".join(output)

if __name__ == "__main__":
    root = r"c:\Users\vizio\CAMELOT_OS"
    tree = generate_tree(root)
    with open(os.path.join(root, "entiremap.md"), "w", encoding="utf-8") as f:
        f.write(tree)
    print("entiremap.md updated successfully.")
    print("Done")
