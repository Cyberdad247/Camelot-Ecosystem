# SPDX-License-Identifier: MIT

import argparse

# Need to ensure we can import from CAMELOT_OS
import os
import sys
from pathlib import Path

# Ensure the root directory is in sys.path
HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
if str(HOME) not in sys.path:
    sys.path.insert(0, str(HOME))

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("[SIR_SONUS] ERROR: faster_whisper not installed")
    sys.exit(1)

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "hydration_manager", HOME / "01_KERNEL" / "memory" / "hydration_manager.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
HydrationManager = _mod.HydrationManager

def transcribe(file_path: str):
    print("[SIR_SONUS] Loading faster_whisper model...")
    # Load model. "base" for speed vs accuracy tradeoff.
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print(f"[SIR_SONUS] Transcribing {file_path}...")
    segments, info = model.transcribe(file_path, beam_size=5)
    
    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
    
    transcript = transcript.strip()
    print(f"[SIR_SONUS] Transcript: {transcript}")
    
    if not transcript:
        print("[SIR_SONUS] Empty transcript, not hydrating.")
        return

    # Inject into L1_REDIS for sir_boris
    mgr = HydrationManager(knight_id="SIR_SONUS")
    
    # Store using 'omnivoice_transcript' intent, complexity 5, tier L1
    mgr.store_tissue(
        intent="omnivoice_transcript",
        content={"transcript": transcript, "source_file": file_path, "knight_target": "sir_boris"},
        complexity=5,
        tier="L1"
    )
    print("[SIR_SONUS] Transcript injected into L1_REDIS.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcribe", type=str, help="Path to wav file to transcribe")
    args = parser.parse_args()
    
    if args.transcribe:
        transcribe(args.transcribe)
