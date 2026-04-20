# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Piper TTS Setup — Downloads voice models from HuggingFace (rhasspy/piper-voices).

Usage:
    python setup_piper.py                    # Install deps + download default voice
    python setup_piper.py --voice en_US-lessac-medium
    python setup_piper.py --list             # List available English voices
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request

PIPER_MODELS_DIR = os.path.join(
    os.path.expanduser("~"), "CAMELOT_OS", "docs", "EXTERNAL", "piper", "models"
)

HF_PIPER_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

# Curated voice catalog — quality voices tested for Tasha persona
VOICE_CATALOG = {
    # English US
    "en_US-lessac-medium": {"quality": "medium", "sample_rate": 22050, "description": "Female, clear and professional"},
    "en_US-lessac-high": {"quality": "high", "sample_rate": 22050, "description": "Female, high quality"},
    "en_US-amy-medium": {"quality": "medium", "sample_rate": 22050, "description": "Female, warm British-American"},
    "en_US-libritts_r-medium": {"quality": "medium", "sample_rate": 22050, "description": "Multi-speaker corpus"},
    "en_US-ryan-medium": {"quality": "medium", "sample_rate": 22050, "description": "Male, neutral American"},
    "en_US-joe-medium": {"quality": "medium", "sample_rate": 22050, "description": "Male, conversational"},
    # English GB (for Tasha's British persona)
    "en_GB-alba-medium": {"quality": "medium", "sample_rate": 22050, "description": "Female, Scottish English"},
    "en_GB-cori-medium": {"quality": "medium", "sample_rate": 22050, "description": "Female, British English"},
    "en_GB-jenny_dioco-medium": {"quality": "medium", "sample_rate": 22050, "description": "Female, warm British"},
    "en_GB-semaine-medium": {"quality": "medium", "sample_rate": 22050, "description": "Multi-speaker British"},
    # Spanish
    "es_ES-davefx-medium": {"quality": "medium", "sample_rate": 22050, "description": "Male, Castilian Spanish"},
    # French
    "fr_FR-siwis-medium": {"quality": "medium", "sample_rate": 22050, "description": "Female, French"},
}

# Default voice for Tasha (British female)
DEFAULT_VOICE = "en_GB-jenny_dioco-medium"


def _voice_url(voice_name: str, ext: str) -> str:
    """Build HuggingFace URL for a Piper voice file.

    HF path format: {lang}/{lang_REGION}/{speaker}/{quality}/{voice_name}.onnx{ext}
    Example: en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx
    """
    parts = voice_name.split("-")  # e.g., ["en_GB", "jenny_dioco", "medium"]
    lang_code = parts[0]           # en_GB
    speaker = parts[1]             # jenny_dioco
    quality = parts[2]             # medium
    lang_prefix = lang_code.split("_")[0]  # en
    return f"{HF_PIPER_BASE}/{lang_prefix}/{lang_code}/{speaker}/{quality}/{voice_name}.onnx{ext}"


def download_voice(voice_name: str) -> str:
    """Download a Piper voice model + config from HuggingFace."""
    voice_dir = os.path.join(PIPER_MODELS_DIR, voice_name)
    os.makedirs(voice_dir, exist_ok=True)

    onnx_path = os.path.join(voice_dir, f"{voice_name}.onnx")
    config_path = os.path.join(voice_dir, f"{voice_name}.onnx.json")

    if os.path.exists(onnx_path) and os.path.exists(config_path):
        print(f"[+] Voice '{voice_name}' already downloaded.")
        return onnx_path

    # Download ONNX model
    onnx_url = _voice_url(voice_name, "")
    print(f"[*] Downloading {voice_name}.onnx from HuggingFace...")
    try:
        urllib.request.urlretrieve(onnx_url, onnx_path)
        print(f"[+] Downloaded {voice_name}.onnx")
    except Exception as e:
        print(f"[-] Failed to download model: {e}")
        return ""

    # Download config JSON
    config_url = _voice_url(voice_name, ".json")
    print(f"[*] Downloading {voice_name}.onnx.json...")
    try:
        urllib.request.urlretrieve(config_url, config_path)
        print(f"[+] Downloaded {voice_name}.onnx.json")
    except Exception as e:
        print(f"[-] Failed to download config: {e}")
        return ""

    return onnx_path


def install_dependencies():
    """Install Piper TTS Python package and dependencies."""
    print("[*] Installing Piper TTS dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-U",
             "piper-tts", "soundfile", "onnxruntime"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[+] Piper TTS dependencies installed.")
    except Exception as e:
        print(f"[-] Failed to install dependencies: {e}")
        raise


def list_voices():
    """Print the curated voice catalog."""
    print("\n[PIPER VOICE CATALOG]")
    print(f"{'Voice':40s} {'Quality':10s} {'Rate':8s} Description")
    print("-" * 100)
    for name, info in VOICE_CATALOG.items():
        marker = " *" if name == DEFAULT_VOICE else ""
        print(f"{name:40s} {info['quality']:10s} {info['sample_rate']:>8d} {info['description']}{marker}")
    print(f"\n* = Default Tasha voice\nModels dir: {PIPER_MODELS_DIR}")


def get_voice_path(voice_name: str) -> str:
    """Get the ONNX path for a voice, downloading if needed."""
    onnx_path = os.path.join(PIPER_MODELS_DIR, voice_name, f"{voice_name}.onnx")
    if os.path.exists(onnx_path):
        return onnx_path
    return download_voice(voice_name)


def setup_piper(voice_name: str = DEFAULT_VOICE):
    """Full setup: install deps + download voice model."""
    install_dependencies()
    download_voice(voice_name)
    print(f"\n[+] Piper TTS ready with voice: {voice_name}")
    print(f"    Model: {PIPER_MODELS_DIR}/{voice_name}/{voice_name}.onnx")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Piper TTS for Camelot OS")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Voice model name")
    parser.add_argument("--list", action="store_true", help="List available voices")
    args = parser.parse_args()

    if args.list:
        list_voices()
    else:
        setup_piper(args.voice)
