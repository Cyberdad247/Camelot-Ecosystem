# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import argparse
import os
import re

# --- CONFIGURATION ---
PATTERNS = [
    r"sk-[a-zA-Z0-9]{20,}",  # OpenAI, Anthropic, etc.
    r"AIza[a-zA-Z0-9-_]{20,}",  # Google Gemini
    r"xai-[a-zA-Z0-9]{20,}",  # xAI
    r"gr-[a-zA-Z0-9]{20,}",  # Groq
    r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+ PRIVATE KEY-----",  # RSA/EC Private Keys
    r'(?i)password\s*[:=]\s*["\'][^"\']{8,}["\']',  # Hardcoded passwords in strings
]

PLACEHOLDER = "PLACEHOLDER_KEY_REMOVED_BY_SIR_SENTINEL"

EXCLUDES = [
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".pytest_cache",
]


def cleanup_file(filepath):
    """Scans and redacts secrets in a single file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        found = False

        for pattern in PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                # Filter out obvious false positives like common library strings if any
                for match in matches:
                    print(f"  [!] Found potential secret in {filepath}: {match[:10]}...")
                    content = content.replace(match, PLACEHOLDER)
                found = True

        if found:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  [+] Redacted secrets in {filepath}")
            return True
    except Exception as e:
        print(f"  [x] Error processing {filepath}: {e}")
    return False


def scan_repository(repo_path):
    """Walks through the repository and cleans up files."""
    print(f"--- CLEANING REPOSITORY: {repo_path} ---")
    files_cleaned = 0
    for root, dirs, files in os.walk(repo_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDES]

        for file in files:
            filepath = os.path.join(root, file)
            # Focus on text/code files
            if file.endswith(
                (".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".env")
            ):
                if cleanup_file(filepath):
                    files_cleaned += 1

    print(f"--- CLEANUP COMPLETE: {files_cleaned} files sanitized ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camelot OS Tainted Cleanup Utility")
    parser.add_argument("path", help="Path to the repository to clean")
    args = parser.parse_args()

    if os.path.exists(args.path):
        scan_repository(args.path)
    else:
        print(f"Error: Path {args.path} does not exist.")