# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

TRAINING_ROOT = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL"
UNSLOTH_DIR = os.path.join(TRAINING_ROOT, "unsloth")
LIGHTNING_DIR = os.path.join(TRAINING_ROOT, "lightning")


def check_training_stack():
    print("--- TRAINING STACK DIAGNOSTIC ---")

    # Check Unsloth
    if os.path.exists(UNSLOTH_DIR):
        print("[+] Unsloth repo found.")
    else:
        print("[-] Unsloth repo missing.")

    # Check Lightning
    if os.path.exists(LIGHTNING_DIR):
        print("[+] Lightning repo found.")
    else:
        print("[-] Lightning repo missing.")

    print("\n--- Next Steps ---")
    print("1. Install unsloth via `pip install unsloth` (Requires CUDA 12.1/11.8).")
    print("2. Verify lightning installation.")


if __name__ == "__main__":
    check_training_stack()