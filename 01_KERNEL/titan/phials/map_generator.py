# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
MAP GENERATOR PHIAL: Dynamic Cartography Engine
Purpose: Generate an authoritative 'entiremap.md' reflecting the kinetic state of the file system.
Ignores noise, annotates structure, and establishes Ground Truth.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# CONFIGURATION
# Resolve Repo Root
ROOT_DIR = Path(__file__).resolve().parents[3]
OUTPUT_FILE = ROOT_DIR / "entiremap.md"

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    ".pytest_cache",
    ".gemini",
    ".antigravity",
    ".openmcp",
    "tmp",
    "logs",
    "archive",
    "_ARCHIVE",
    ".next",
    ".ruff_cache",
    "target",
    ".notebooklm-mcp-cli",
    "venv",
    "dist",
    "backups",
    "assimilated",
    "99_ARCHIVE",
    ".venv_camelot",
    ".claude",
    ".codex",
}
IGNORE_FILES = {".DS_Store", "Thumbs.db", ".gitignore", ".env", "pnpm-lock.yaml", "package-lock.json", "uv.lock"}
MAX_DEPTH = 5

def generate_tree(root_path, padding_str="  "):
    tree_lines = []
    root_str = str(root_path)

    for root, dirs, files in os.walk(root_str):
        # Calculate depth and skip if too deep
        depth = root[len(root_str) :].count(os.sep)
        if depth > MAX_DEPTH:
            continue

        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        dirs.sort()
        files.sort()

        # Formatting
        indent = padding_str * depth
        folder_name = os.path.basename(root)
        if folder_name == "":
            folder_name = os.path.basename(root_str)

        # Determine status annotation
        status = ""
        if "KERNEL" in root: status = " [CORE]"
        elif "VAULT" in root: status = " [SECURE]"
        elif "FORGE" in root: status = " [FORGE]"
        elif "control_plane" in root: status = " [CONTROL]"
        elif "kinetic_edge" in root: status = " [KINETIC]"

        tree_lines.append(f"{indent}📂 {folder_name}/{status}")

        for file in files:
            if file in IGNORE_FILES:
                continue
            tree_lines.append(f"{indent}{padding_str}- {file}")

    return "\n".join(tree_lines)

def generate_map():
    timestamp = datetime.now().isoformat()
    tree_content = generate_tree(ROOT_DIR)

    # Read version from VERSION file
    version_file = ROOT_DIR / "VERSION"
    version = version_file.read_text().strip() if version_file.exists() else "400.1.0"

    content = f"""# CAMELOT APEX OS v{version} — ENTIRE MAP (Territory)
**Timestamp:** {timestamp}
**Version:** {version} (Universal Singularity)
**Root:** `{ROOT_DIR}`

## CYBERTRON TOPOLOGY (Multi-Node)

| Node | Location | Function | Status |
|------|----------|----------|--------|
| CONTROL_PLANE | control_plane/ | Pydantic AI, A2A, Knight dispatch | LOCAL |
| KINETIC_EDGE | kinetic_edge/ | Rust/Go binaries, MCP server | LOCAL |
| EXCALIBUR | 01_KERNEL/EXCALIBUR/ | Core FastAPI kernel | LOCAL |
| SQUIRE_COLONY | 01_KERNEL/agora/Squires/ | sub-agent hive | LOCAL |
| CLIPROXY | ~/CLIProxyAPI/ | LLM Proxy gateway | LOCAL |
| CLOUD_BRAIN | NotebookLM | Distributed knowledge | CLOUD |

## DIRECTORY TREE

---

{tree_content}

---
**[SYSTEM_NOTE]:** This map is auto-generated. Run `01_KERNEL/titan/phials/map_generator.py` to refresh.
"""

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Map generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_map()
