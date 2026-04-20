# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

import requests
from tqdm import tqdm

MODEL_URL = (
    "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
)
DEST_PATH = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\koboldcpp\models\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"


def download_model(url, dest):
    print("--- FETCHING LOCAL MODEL (TinyLlama) ---")
    if os.path.exists(dest):
        print(f"[+] Model already exists at {dest}")
        return

    print(f"[*] Downloading from: {url}")
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))

        os.makedirs(os.path.dirname(dest), exist_ok=True)

        with (
            open(dest, "wb") as f,
            tqdm(
                desc="Model Download",
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)

        print(f"[+] Download complete: {dest}")
    except Exception as e:
        print(f"[-] Download failed: {e}")


if __name__ == "__main__":
    download_model(MODEL_URL, DEST_PATH)