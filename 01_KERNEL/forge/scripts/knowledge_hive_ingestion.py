# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import datetime
import glob
import os

# CONFIG
BASE_DIR = r"c:\Users\vizio\CAMELOT_OS"
EXTERNAL_DIR = os.path.join(BASE_DIR, "docs", "EXTERNAL")
OUTPUT_FILE = os.path.join(BASE_DIR, "docs", "REPORTS", "INTEGRATED_KNOWLEDGE_BASE.md")


def ingest_knowledge():
    print("--- CAMELOT KNOWLEDGE HIVE INGESTION STARTING ---")

    knowledge_blobs = []

    # 1. SCAN FOR READMEs
    readme_paths = glob.glob(os.path.join(EXTERNAL_DIR, "**", "README.md"), recursive=True)
    print(f"Found {len(readme_paths)} documentation sources.")

    for path in readme_paths:
        rel_path = os.path.relpath(path, EXTERNAL_DIR)
        repo_name = rel_path.split(os.sep)[0]

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                blob = f"## REPOSITORY: {repo_name}\n"
                blob += f"**Source Path:** `{rel_path}`\n\n"
                blob += content
                blob += "\n\n---\n\n"
                knowledge_blobs.append(blob)
        except Exception as e:
            print(f"Skipping {path} due to error: {e}")

    # 2. WRITE INTEGRATED KNOWLEDGE BASE
    header = "# 🧠 CAMELOT OS: INTEGRATED KNOWLEDGE BASE\n"
    header += f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"**Scope:** {len(readme_paths)} Assimilated Repositories\n\n"
    header += "This document serves as the unified context for the Camelot OS Intelligence Swarms.\n\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header)
        for blob in knowledge_blobs:
            f.write(blob)

    print(f"Integration Complete. Knowledge Base saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    ingest_knowledge()