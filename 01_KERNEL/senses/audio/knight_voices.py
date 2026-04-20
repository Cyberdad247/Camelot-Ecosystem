# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
KNIGHT_VOICES: Universal Voice Registry
Maps Knight IDs to Piper/Kokoro voice models.
"""

VOICE_PRESETS = {
    "anya": "en_GB-jenny_dioco-medium",
    "tasha": "en_GB-jenny_dioco-medium",
    "merlin": "en_US-ryan-medium",
    "oracle": "en_US-lessac-high",
    "boris": "en_US-joe-medium",
    "lancelot": "en_US-danny-low",
    "veritas": "en_GB-cori-medium",
    "systema": "en_US-lessac-medium",
}

def get_voice(knight_id: str) -> str:
    return VOICE_PRESETS.get(knight_id.lower(), "en_US-lessac-medium")

def get_model(knight_id: str) -> str:
    return VOICE_PRESETS.get(knight_id.lower(), "en_US-lessac-medium")
