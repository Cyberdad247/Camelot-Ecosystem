#!/usr/bin/env python3
"""Squire Foraging Loop - OpenViking Tiered Context Generator
Automatically scans codebase files and compiles L0 (scout), L1 (orient),
and L2 (deep dive) files to feed the local OpenViking and MemCastle systems.
"""
import os
import re
import sys
from pathlib import Path

CAMELOT_ROOT = Path(__file__).resolve().parent.parent
VAULT_RESOURCES = CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "viking_resources"

def parse_file_structure(path: Path) -> dict:
    """Extract code comments, imports, and signatures to compile L0 and L1."""
    ext = path.suffix.lower()
    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    docstring = ""
    signatures = []
    imports = []

    # Simple regex parsers based on extension
    if ext in (".py", ".go", ".rs", ".ts"):
        # Extract imports
        for line in lines:
            if line.startswith("import ") or line.startswith("from ") or line.startswith("\t\"") or line.startswith("import ("):
                imports.append(line.strip())
            # Capture class/func/struct/interface definitions
            if ext == ".py":
                if line.startswith("class ") or line.startswith("def "):
                    signatures.append(line.strip())
            elif ext == ".go":
                if line.startswith("func ") or line.startswith("type ") or line.startswith("struct "):
                    signatures.append(line.strip())
            elif ext == ".rs":
                if line.startswith("pub ") or line.startswith("fn ") or line.startswith("struct ") or line.startswith("impl "):
                    signatures.append(line.strip())
            elif ext == ".ts":
                if "class " in line or "function " in line or "interface " in line or "export " in line:
                    signatures.append(line.strip())

        # Extract top-level module description
        if ext == ".py":
            # Match triple quote docstring at start
            match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if match:
                docstring = match.group(1).strip()
        elif ext in (".go", ".rs", ".ts"):
            # Match leading block or line comments
            comments = []
            for line in lines[:20]:
                if line.startswith("//") or line.startswith("/*") or line.startswith(" *"):
                    comments.append(line.strip("/* ").strip())
            docstring = " ".join(comments)

    if not docstring:
        docstring = f"Code resource file matching suffix {ext} implementing logic for {path.name}."

    return {
        "docstring": docstring,
        "signatures": signatures[:25],  # Cap at 25 signatures for L1 sizing
        "imports": imports[:15],
        "full_content": content
    }

def generate_tiered_context(source_path: Path):
    """Compile and write L0, L1, L2 structures under viking_resources."""
    if not source_path.exists() or source_path.is_dir():
        return

    rel_path = source_path.relative_to(CAMELOT_ROOT)
    dest_dir = VAULT_RESOURCES / rel_path
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Foraging: {rel_path} -> {dest_dir}")
    data = parse_file_structure(source_path)

    # 1. Write L0 Summary (Scout)
    l0_content = f"""# [L0_SUMMARY: {source_path.name}]
# [PROTOCOL: OPENVIKING_SCOUT]

{data["docstring"].split('.')[0]}.
- Path: `viking://resources/{rel_path.as_posix()}`
- Scope: Implements core functionality for {source_path.name} in CAMELOT-OS.
"""
    (dest_dir / "L0_summary.md").write_text(l0_content, encoding="utf-8")

    # 2. Write L1 Overview (Orient)
    signatures_md = "\n".join([f"- `{sig}`" for sig in data["signatures"]]) if data["signatures"] else "- *No classes or functions defined at top-level.*"
    imports_md = "\n".join([f"- `{imp}`" for imp in data["imports"]]) if data["imports"] else "- *No imports detected.*"
    
    l1_content = f"""# [L1_OVERVIEW: {source_path.name}]
# [PROTOCOL: OPENVIKING_ORIENT]

## 1. Description
{data["docstring"]}

## 2. Dependencies / Imports
{imports_md}

## 3. Structural Signatures
{signatures_md}
"""
    (dest_dir / "L1_overview.md").write_text(l1_content, encoding="utf-8")

    # 3. Write L2 Full Data (Deep Dive)
    l2_content = f"""# [L2_FULL_DATA: {source_path.name}]
# [PROTOCOL: OPENVIKING_DEEP_DIVE]

```
{data["full_content"]}
```
"""
    (dest_dir / "L2_full_data.md").write_text(l2_content, encoding="utf-8")

def scan_and_summarize(target_dir: Path):
    """Scan and process files recursively."""
    extensions = {".go", ".py", ".rs", ".ts", ".md"}
    exclude_dirs = {"venv", ".venv", ".git", ".cargo", "data", "logs", "node_modules", "viking_resources"}

    for root, dirs, files in os.walk(target_dir):
        # Exclude specific folders in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in extensions:
                try:
                    generate_tiered_context(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    target = CAMELOT_ROOT
    if len(sys.argv) > 1:
        target = Path(sys.argv[1]).resolve()
    
    print(f"Starting Squire Foraging Loop targeting: {target}")
    scan_and_summarize(target)
    print("--- SQUIRE FORAGING COMPLETE ---")
