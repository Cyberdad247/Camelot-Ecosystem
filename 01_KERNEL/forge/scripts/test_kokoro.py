# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

import soundfile as sf
from kokoro_onnx import Kokoro

MODELS_DIR = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\kokoro-onnx\models"
ONNX_PATH = os.path.join(MODELS_DIR, "kokoro-v1.0.onnx")
VOICES_PATH = os.path.join(MODELS_DIR, "voices-v1.0.bin")
OUTPUT_PATH = r"c:\Users\vizio\CAMELOT_OS\docs\ARTIFACTS\test_synthesis.wav"


def test_synthesis():
    if not os.path.exists(ONNX_PATH) or not os.path.exists(VOICES_PATH):
        print("❌ Models not found. Run setup_voice_stack.py first.")
        return

    print("[*] Initializing Kokoro...")
    kokoro = Kokoro(ONNX_PATH, VOICES_PATH)

    text = "Hello. This is the Camelot Voice Swarm. System check, normal."
    print(f"[*] Synthesizing: '{text}'")

    samples, sample_rate = kokoro.create(text, voice="af_bella", speed=1.0, lang="en-us")

    sf.write(OUTPUT_PATH, samples, sample_rate)
    print(f"[+] Audio saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    test_synthesis()