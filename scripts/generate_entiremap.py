# SPDX-License-Identifier: MIT

import os
from pathlib import Path
from datetime import datetime

# Dynamic VFS Node Mapping Script
# Maps the Camelot-OS Worldtree nodes into entiremap.md

EXCLUDE_DIRS = {
    '.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache',
    '.ruff_cache', 'target', 'build', 'dist', '.agents', '.claude',
    '.gemini', '.github', '.omp', 'camelot_os.egg-info'
}

def generate_tree(dir_path: Path, prefix: str = "") -> str:
    """Generates a markdown tree representation of the directory."""
    tree_str = ""
    try:
        entries = sorted(list(dir_path.iterdir()), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        return ""
    
    entries = [e for e in entries if e.name not in EXCLUDE_DIRS]
    count = len(entries)
    
    for index, entry in enumerate(entries):
        connector = "└── " if index == count - 1 else "├── "
        tree_str += f"{prefix}{connector}{entry.name}\n"
        
        if entry.is_dir():
            extension = "    " if index == count - 1 else "│   "
            # Cap recursion depth to prevent infinite loops on massive dirs
            if len(prefix) < 16:  
                tree_str += generate_tree(entry, prefix + extension)
    
    return tree_str

def build_entiremap():
    root_dir = Path(os.getcwd())
    
    header = f"""# CAMELOT-OS ♜💠♜ WORLDTREE ENTIRE MAP ♜💠♜
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Context:** Dynamic VFS Node Mapping (vMAX)

This document is dynamically generated to represent the exact, real-time node structure of the Camelot-OS Worldtree.

```text
CAMELOT_OS/
"""
    
    tree_structure = generate_tree(root_dir)
    footer = "```\n"
    
    full_map = header + tree_structure + footer
    
    output_path = root_dir / "entiremap.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_map)
        
    print(f"[+] Successfully generated dynamic map at {output_path}")

if __name__ == "__main__":
    build_entiremap()
