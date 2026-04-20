# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import subprocess
import urllib.request

MODELS_DIR = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\kokoro-onnx\models"
ONNX_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_BIN_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


def setup_voice_stack():
    print("[*] Installing voice stack dependencies...")
    try:
        subprocess.check_call(["pip", "install", "-U", "kokoro-onnx", "soundfile", "onnxruntime"])
        print("[+] Dependencies installed successfully.")
    except Exception as e:
        print(f"[-] Failed to install dependencies: {e}")
        return

    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    onnx_path = os.path.join(MODELS_DIR, "kokoro-v1.0.onnx")
    voices_path = os.path.join(MODELS_DIR, "voices-v1.0.bin")

    if not os.path.exists(onnx_path):
        print(f"[*] Downloading Kokoro ONNX model from {ONNX_MODEL_URL}...")
        urllib.request.urlretrieve(ONNX_MODEL_URL, onnx_path)
        print("[+] Downloaded kokoro-v1.0.onnx")
    else:
        print("[+] Kokoro ONNX model already exists.")

    if not os.path.exists(voices_path):
        print(f"[*] Downloading voices bin from {VOICES_BIN_URL}...")
        urllib.request.urlretrieve(VOICES_BIN_URL, voices_path)
        print("[+] Downloaded voices-v1.0.bin")
    else:
        print("[+] Voices bin already exists.")


if __name__ == "__main__":
    setup_voice_stack()