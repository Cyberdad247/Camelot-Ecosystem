# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
MAP GENERATOR PHIAL: Dynamic Cartography Engine
Purpose: Generate an authoritative 'entiremap.md' reflecting the kinetic state of the file system.
Ignores noise, annotates structure, and establishes Ground Truth.
"""

import os
from datetime import datetime

# CONFIGURATION
ROOT_DIR = r"C:\Users\vizio\CAMELOT_OS"
OUTPUT_FILE = r"C:\Users\vizio\CAMELOT_OS\entiremap.md"
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
    ".venv",
    "dist",
    "backups",
    "assimilated",
    "99_ARCHIVE",
    ".venv_camelot",
    ".claude",
    ".codex",
    ".camelot-config.yaml",
}
IGNORE_FILES = {".DS_Store", "Thumbs.db", ".gitignore", ".env", "pnpm-lock.yaml", "package-lock.json"}
MAX_DEPTH = 5


def generate_tree(root_path, padding_str="  "):
    tree_lines = []

    for root, dirs, files in os.walk(root_path):
        # Calculate depth and skip if too deep
        depth = root[len(root_path) :].count(os.sep)
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
            folder_name = os.path.basename(root_path)

        # Determine status annotation (Cybertron node heuristic)
        status = ""
        if "KERNEL" in root:
            status = " [CORE]"
        elif "VAULT" in root:
            status = " [SECURE]"
        elif "FORGE" in root:
            status = " [FORGE]"
        elif "squires" in root.lower():
            status = " [COLONY]"
        elif "control_plane" in root:
            status = " [CONTROL]"
        elif "kinetic_edge" in root:
            status = " [KINETIC]"
        elif "99_ARCHIVE" in root:
            status = " [ARCHIVE]"

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
    version_file = os.path.join(ROOT_DIR, "VERSION")
    if os.path.exists(version_file):
        with open(version_file, "r") as vf:
            version = vf.read().strip()
    else:
        version = "400.1.0"

    content = f"""# CAMELOT APEX OS v{version} — ENTIRE MAP (Territory)
**Timestamp:** {timestamp}
**Version:** {version} (Universal Singularity)
**Mode:** Kinetic Purity [Active]
**Root:** `{ROOT_DIR}`

## CYBERTRON TOPOLOGY (Multi-Node)

| Node | Location | Function | Status |
|------|----------|----------|--------|
| CONTROL_PLANE | control_plane/ | Pydantic AI, A2A, Knight dispatch | LOCAL |
| KINETIC_EDGE | kinetic_edge/mcp_server/ | Rust Axum MCP, port 3001 | LOCAL |
| EXCALIBUR | 01_KERNEL/EXCALIBUR/ | Core FastAPI kernel | LOCAL |
| SQUIRE_COLONY | squires/ | 8 nano-knight sub-agents | LOCAL |
| CLIPROXY | ~/CLIProxyAPI/ | Zero-Burn proxy, 29+ models, port 8080 | LOCAL |
| LIGHTPANDA | WSL Ubuntu :9222 | Zig headless browser CDP | LOCAL (WSL) |
| MODAL_BRAIN | Modal cloud | excalibur-brain, T4 GPU | CLOUD |
| MODAL_TASHA | Modal cloud | tasha-voice-agent, LiveKit | CLOUD |
| FORGE_UI | 02_FORGE/web/ | TypeScript/React dashboard | LOCAL |
| VAULT | 03_VAULT/ | AES-256-GCM credentials, training configs | LOCAL |
| CLOUD_BRAIN | NotebookLM (RPC) | Living Camelot-OS v.400, 132 notebooks | CLOUD |

## KINETIC EDGE — Module Architecture (Lukas_Omega / L2)

| Module | File | Purpose | Status |
|--------|------|---------|--------|
| AgentArmor PDG | main.rs | Program Dependency Graph taint analysis — 5 rules, sandbox enforcement | ACTIVE |
| Bifrost Gate | bifrost.rs | 3-layer auth: loopback / Tailnet+token / reject. Constant-time comparison | ACTIVE |
| AP2 Settlement | ap2_settlement.rs | ed25519 cryptographic compute settlement between agents | ACTIVE |
| TurboQuant | turboquant.rs | PolarQuant KV cache compression, 32K context, 2GB RAM budget | SCAFFOLD |
| WASI-NN | wasi_nn.rs | WASM neural inference bindings (Ternary158/ONNX/OpenVINO) | SCAFFOLD |

## KINETIC ARMORY — Binary Status

| Binary | Language | Location | Size | Status |
|--------|----------|----------|------|--------|
| Saltare | Go | 02_FORGE/KINETIC_ARMORY/Saltare/saltare.exe | 37.6MB | COMPILED |
| Saltare-MCP | Go | 02_FORGE/KINETIC_ARMORY/Saltare/bin/saltare-mcp.exe | 8.3MB | COMPILED |
| Cribo | Rust | 02_FORGE/kinetic/bin/cribo.exe | 669KB | COMPILED |
| Rotel | Rust | 02_FORGE/kinetic/bin/rotel.exe | 894KB | COMPILED |
| Ledger | Go | 02_FORGE/kinetic/bin/ledger.exe | 734KB | COMPILED |
| camelot-mcp-edge | Rust | kinetic_edge/mcp_server/target/release/ | ~4MB | COMPILED |

## DIRECTORY TREE

---

{tree_content}

---
**[SYSTEM_NOTE]:** This map is auto-generated. Do not edit manually. Run `01_KERNEL/titan/phials/map_generator.py` to refresh.
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Map generated at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_map()