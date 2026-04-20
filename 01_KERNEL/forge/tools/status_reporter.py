# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
from datetime import datetime
from pathlib import Path

import requests

# 🛡️ CONFIGURATION
ROOT_DIR = Path(r"C:\Users\vizio\CAMELOT_OS")
UPDATE_DIR = ROOT_DIR / "UPDATES"
ANALYTICS_SCRIPT = ROOT_DIR / "01_KERNEL" / "tools" / "analytics_engine.py"


# --- 1. AI STUDIO CONTEXT GENERATOR ---
def generate_ai_studio_map():
    print("🗺️ Generating AI Studio Context Map...")
    output_file = UPDATE_DIR / "AI_STUDIO_CONTEXT.md"

    ignore_dirs = {
        ".git",
        "node_modules",
        "__pycache__",
        "dist",
        "venv",
        ".next",
        "scrcpy_release",
        "Bytebot",
        "Lobe-Chat",
    }

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 🏰 CAMELOT OS: KINGDOM CONTEXT MAP\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Root:** {ROOT_DIR}\n\n")

        # Add System Manifest Content
        manifest = ROOT_DIR / "GEMINI.md"
        if manifest.exists():
            f.write("## 📜 SYSTEM MANIFEST (GEMINI.md)\n```markdown\n")
            f.write(manifest.read_text(encoding="utf-8")[:2000] + "\n... (truncated)\n")
            f.write("```\n\n")

        f.write("## 🗺️ DIRECTORY STRUCTURE\n")

        for root, dirs, files in os.walk(ROOT_DIR):
            # Filter in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            level = root.replace(str(ROOT_DIR), "").count(os.sep)
            indent = " " * 4 * (level)
            f.write(f"{indent}- 📁 **{os.path.basename(root)}/**\n")

            subindent = " " * 4 * (level + 1)
            for file in files:
                if file.endswith((".py", ".md", ".json", ".ts", ".tsx", ".ps1")):
                    f.write(f"{subindent}- 📄 {file}\n")

    print(f"   ✅ Map Forged: {output_file}")


# --- 2. NOTEBOOK BRAIN STATUS ---
def generate_notebook_status():
    print("🧠 Checking Notebook Brain Status...")
    output_file = UPDATE_DIR / "NOTEBOOK_BRAIN_STATE.md"

    try:
        response = requests.get("http://127.0.0.1:5055/health", timeout=2)
        status = response.json()
        online = True
    except Exception:
        status = {"status": "offline", "error": "Connection Refused"}
        online = False

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 🧠 NOTEBOOK BRAIN STATE\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")

        f.write(f"## 🚦 STATUS: {'ONLINE 🟢' if online else 'OFFLINE 🔴'}\n")
        f.write("**Endpoint:** http://127.0.0.1:5055\n")
        f.write(f"**Health Check:** `{status}`\n\n")

        f.write("## 🏗️ INFRASTRUCTURE\n")
        f.write("- **Engine:** FastAPI (Python)\n")
        f.write("- **Memory:** SurrealDB (v2.4.1)\n")
        f.write("- **Location:** `CAMELOT_OS/01_KERNEL/Squires/Notebook_Brain`\n")
        f.write("- **Dependencies:** `langchain`, `surrealdb`, `open-notebook`\n")

    print(f"   ✅ Status Forged: {output_file}")


# --- 3. MORGANA ANALYTICS ---
def generate_morgana_report():
    print("👁️ Aggregating Morgana Analytics...")
    output_file = UPDATE_DIR / "MORGANA_REPORT.md"

    # We execute the existing analytics engine and capture stdout
    import subprocess

    result = subprocess.run(["python", str(ANALYTICS_SCRIPT)], capture_output=True, text=True)

    report_content = result.stdout
    # Filter out the "crunching numbers" logs if they exist in stdout
    clean_report = "\n".join(
        [line for line in report_content.splitlines() if not line.startswith("🧮") and not line.startswith("✅")]
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(clean_report)

    print(f"   ✅ Report Forged: {output_file}")


if __name__ == "__main__":
    generate_ai_studio_map()
    generate_notebook_status()
    generate_morgana_report()
    print("\n🏁 [SYSTEM] UPDATE BUNDLE COMPLETE.")