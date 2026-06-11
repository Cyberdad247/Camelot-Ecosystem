# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import subprocess

PUTER_DIR = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\puter"


def ready_puter():
    print("--- PUTER CLOUD OS INITIALIZATION ---")
    if not os.path.exists(PUTER_DIR):
        print("[-] Puter directory not found.")
        return

    print("[*] Installing dependencies with npm (isolated)...")
    try:
        # Using --no-workspaces to avoid local conflict with CAMELOT_OS workspace
        npm = "npm.cmd" if __import__("sys").platform == "win32" else "npm"
        subprocess.run([npm, "install", "--no-workspaces"], cwd=PUTER_DIR, shell=False, check=True)
        print("[+] Puter dependencies installed.")
    except Exception as e:
        print(f"[-] Failed to install dependencies: {e}")


if __name__ == "__main__":
    ready_puter()