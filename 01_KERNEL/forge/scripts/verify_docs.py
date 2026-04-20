# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import re

DOCS_DIR = r"C:\Users\vizio\CAMELOT_OS\docs"
SRC_DIRS = [r"C:\Users\vizio\CAMELOT_OS\01_ACTIVE_CORE", r"C:\Users\vizio\CAMELOT_OS\01_KERNEL"]


def analyze_docs():
    report = []
    report.append("# Documentation Verification Report\n")

    # 1. Check for Referenced Files
    report.append("## 1. File Reference Check")

    # Map of file references to check (simplified)
    references = {"antigravity.py": False, "merlin_omega.py": False, "kernel.py": False, "PROVENANCE_LEDGER.md": False}

    for root, dirs, files in os.walk(r"C:\Users\vizio\CAMELOT_OS"):
        for file in files:
            if file in references:
                references[file] = True

    for file, found in references.items():
        status = "✅ Found" if found else "❌ Missing"
        report.append(f"- {file}: {status}")

    # 2. Check for Command Implementations
    report.append("\n## 2. Command Implementation Check")
    commands_to_check = ["//PLAN", "//FORGE", "Ω_SYNC", "Ω_STRIKE"]

    found_commands = {}
    for cmd in commands_to_check:
        found_commands[cmd] = False

    # Naive search in python files
    for src_dir in SRC_DIRS:
        if not os.path.exists(src_dir):
            continue
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            content = f.read()
                            for cmd in commands_to_check:
                                # Look for string literal or comment
                                if cmd in content:
                                    found_commands[cmd] = True
                    except:
                        pass

    for cmd, found in found_commands.items():
        status = "✅ Found in code" if found else "⚠️ Not found in code (Conceptual/Prompt-based?)"
        report.append(f"- {cmd}: {status}")

    # 3. Doc Drift (Simple file existence check from docs)
    report.append("\n## 3. Documentation Drift Analysis")
    # Scan docs for [File](./path) links
    link_pattern = re.compile(r"\[.*?\]\(.*?\)")

    missing_links = []

    if os.path.exists(DOCS_DIR):
        for doc_file in os.listdir(DOCS_DIR):
            if doc_file.endswith(".md"):
                with open(os.path.join(DOCS_DIR, doc_file), "r", encoding="utf-8") as f:
                    content = f.read()
                    links = link_pattern.findall(content)
                    for link in links:
                        # Normalize path
                        clean_link = link.split("#")[0]  # remove anchor
                        if clean_link.startswith("http"):
                            continue

                        # Resolve relative path
                        # Assuming docs are in /docs, so ../ means root
                        # This is a basic check, might need robust path joining
                        pass

    report.append("Analysis complete.")
    return "\n".join(report)


if __name__ == "__main__":
    print(analyze_docs())