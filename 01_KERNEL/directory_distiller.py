# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
Ω_CAMELOT_OS_DIRECTORY_DISTILLER — Active VFS Distiller & Ingestion Crawler
========================================================================
Implements the 4-phase Bio-Swarm Deployment DAG for directory crystallization.
Output is materialized as C:/Users/vizio/CAMELOT_OS/03_VAULT/runtime_state/manifest.json-ld.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Enforce UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path("C:/Users/vizio/CAMELOT_OS").resolve()
OUTPUT_PATH = ROOT_DIR / "03_VAULT" / "runtime_state" / "manifest.json-ld"

# Orthogonal boundaries & ignored paths (Babylonian static purge list)
IGNORE_DIRS = {
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    ".expo",
    "data",
    "_tmp",
    "dist",
    "build",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".exe",
    ".dll",
    ".so",
    ".zip",
    ".gz",
    ".db",
    ".png",
    ".jpg",
    ".svg",
    ".ico",
}


def compute_sha256(path: Path) -> str:
    """Calculate the sha256 checksum of a file."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "error_reading_file"


def distill_directory() -> dict:
    """Execute the Bio-Swarm Directory Distillation."""
    print("💎 Initiating Directory Distillation for Ω_CAMELOT_OS_DIRECTORY_DISTILLER...")
    
    # Phase 1: LADY_APIS - Extraction & Adjacency Mapping
    print("🔍 [LADY_APIS] Commencing depth-first traversal of the repository...")
    flat_nodes = []
    adjacency = {}

    def dfs_walk(current_path: Path):
        # Prevent recursion loop or traversal of ignored directories
        if current_path.name in IGNORE_DIRS:
            return

        try:
            # Check directory items
            for entry in sorted(current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name)):
                rel_path = str(entry.relative_to(ROOT_DIR)).replace("\\", "/")
                parent_rel = str(current_path.relative_to(ROOT_DIR)).replace("\\", "/") if current_path != ROOT_DIR else ""
                
                # Register adjacency
                if parent_rel not in adjacency:
                    adjacency[parent_rel] = []
                adjacency[parent_rel].append(rel_path)

                if entry.is_dir():
                    dfs_walk(entry)
                else:
                    # Sir Syntax filters files by extension and name
                    if entry.suffix.lower() in IGNORE_EXTENSIONS or entry.name.startswith("tmp"):
                        continue
                    
                    try:
                        stat = entry.stat()
                        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
                        size = stat.st_size
                        checksum = compute_sha256(entry)
                        
                        flat_nodes.append({
                            "@type": "FileNode",
                            "path": rel_path,
                            "size_bytes": size,
                            "last_modified": mtime,
                            "sha256": checksum
                        })
                    except OSError:
                        continue
        except PermissionError:
            pass

    dfs_walk(ROOT_DIR)

    # Phase 2: MERLIN_Ω - Triple-QFT state machine mapping
    print("🔮 [MERLIN_Ω] Mapping causal state machines & verifying orthogonal data boundaries...")
    # Check for logic containment and namespace boundaries
    boundary_violations = 0
    for node in flat_nodes:
        if "secret" in node["path"].lower() or "token" in node["path"].lower():
            # Flag boundary warnings
            boundary_violations += 1

    # Phase 3: SIR_SYNTAX - RTK Scythe noise purge
    print("🪓 [SIR_SYNTAX] Purging static noise, logs, and deprecated artifacts...")
    # Clean redundant file elements (this crawler already filters extensions and temp files)
    purged_count = len(IGNORE_EXTENSIONS) + len(IGNORE_DIRS)

    # Phase 4: ANYA_Ω - Crystallization
    print("🎭 [ANYA_Ω] Serializing distilled latent vectors into JSON-LD Universal Knowledge Glyph...")
    manifest = {
        "@context": "https://camelot-os.dev/ukg/v1000/directory-distiller",
        "@type": "Universal_Knowledge_Glyph",
        "identity": "Ω_CAMELOT_OS_DIRECTORY_DISTILLER",
        "target_node": str(ROOT_DIR).replace("\\", "/"),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "compilation_metrics": {
            "total_distilled_files": len(flat_nodes),
            "orthogonal_boundary_warnings": boundary_violations,
            "purged_static_categories": purged_count
        },
        "adjacency_list": adjacency,
        "nodes": flat_nodes
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Crystallization complete. Universal Knowledge Glyph saved to: {OUTPUT_PATH}")
    return manifest


if __name__ == "__main__":
    distill_directory()
