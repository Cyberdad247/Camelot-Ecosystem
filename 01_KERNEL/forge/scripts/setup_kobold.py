# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

KOBOLD_DIR = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\koboldcpp"
MODELS_DIR = os.path.join(KOBOLD_DIR, "models")


def check_kobold():
    print("--- KOBOLDCPP DIAGNOSTIC ---")
    if not os.path.exists(KOBOLD_DIR):
        print("[-] koboldcpp directory not found.")
        return

    print("[+] koboldcpp found.")

    # Check for models
    if not os.path.exists(MODELS_DIR):
        try:
            os.makedirs(MODELS_DIR)
            print(f"[+] Created models directory at {MODELS_DIR}")
        except Exception as e:
            print(f"[-] Failed to create models directory: {e}")

    try:
        gguf_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]
        if not gguf_files:
            print("[!] No GGUF models found in models directory.")
            print("[*] Suggestion: Download a small model like 'TinyLlama-1.1B-Chat-v1.0.Q8_0.gguf' from Hugging Face.")
        else:
            print(f"[+] Found {len(gguf_files)} GGUF models: {gguf_files}")
    except Exception as e:
        print(f"[-] Error listing models: {e}")

    # Check for executable/script
    script = os.path.join(KOBOLD_DIR, "koboldcpp.py")
    if os.path.exists(script):
        print("[+] koboldcpp.py found.")
    else:
        print("[-] koboldcpp.py not found.")


if __name__ == "__main__":
    check_kobold()