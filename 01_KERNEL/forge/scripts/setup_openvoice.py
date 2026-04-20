# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import zipfile

import requests
from tqdm import tqdm

CHECKPOINT_URL = "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip"
BASE_DIR = r"c:\Users\vizio\CAMELOT_OS\docs\EXTERNAL\OpenVoice"
DEST_ZIP = os.path.join(BASE_DIR, "checkpoints_v2.zip")
EXTRACT_DIR = os.path.join(BASE_DIR, "checkpoints_v2")


def download_and_extract():
    print("--- OPENVOICE V2 CHECKPOINT ACTIVATION ---")

    if os.path.exists(EXTRACT_DIR) and os.listdir(EXTRACT_DIR):
        print(f"[+] Checkpoints already exist at {EXTRACT_DIR}")
        return

    print(f"[*] Downloading checkpoints from: {CHECKPOINT_URL}")
    try:
        response = requests.get(CHECKPOINT_URL, stream=True)
        total_size = int(response.headers.get("content-length", 0))

        with (
            open(DEST_ZIP, "wb") as f,
            tqdm(
                desc="OpenVoice V2 Download",
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)

        print(f"[*] Extracting to {EXTRACT_DIR}...")
        with zipfile.ZipFile(DEST_ZIP, "r") as zip_ref:
            zip_ref.extractall(BASE_DIR)

        os.remove(DEST_ZIP)
        print("[+] OpenVoice V2 Activation COMPLETE.")
    except Exception as e:
        print(f"[-] Activation failed: {e}")


if __name__ == "__main__":
    download_and_extract()