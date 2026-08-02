# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
KNIGHT_VOICES: Universal Voice Registry + Vocal Architecture Schema
====================================================================
Merlin Omega Mathematical Architecture for each Knight vocal weight:

  V_Omega(k) = { F0(k), WPM(k), Δformant(k), ε(k), ρ(k), Σ(k) }

  F0(k)        = round(110 + 75 × ω_k)            Hz  — fundamental frequency
  WPM(k)       = round(130 + 40 × ω_k)                — synthesis cadence
  Δformant(k)  = round(1.0 − 2.0 × π_k, 2)            — warmth dimension [-1,+1]
  ε(k)         = round(0.30 + 0.70 × ω_k, 2)           — energy coefficient
  ρ(k)         = round(1.00 − 0.60 × π_k, 2)           — prosody/expressiveness
  Σ(k)         = SHA256(k)[:16]                         — audio encryption seed

  where ω_k = soul_router weight, π_k = privacy_level (both ∈ [0,1])
"""

from __future__ import annotations

import hashlib
from typing import NamedTuple

# ── Vocal Profile Schema ──────────────────────────────────────────────────────

class KnightVocalProfile(NamedTuple):
    """Complete vocal architecture for a Knight node."""
    piper_model:   str    # primary zero-cost TTS model (Piper/Kokoro)
    f0_hz:         int    # fundamental frequency (Hz)
    wpm:           int    # synthesis cadence (words per minute)
    formant_shift: float  # warmth dimension: -1.0 warm → +1.0 cool
    energy:        float  # synthesis intensity [0.0 → 1.0]
    prosody:       float  # expressiveness [0.0 → 1.0]
    tts_engine:    str    # preferred engine: "kokoro"|"piper"|"silero"|"speecht5"
    stt_engine:    str    # preferred STT: "faster_whisper"|"wav2vec2"|"silero_only"
    sigma:         str    # SHA256(knight_id)[:16] — audio watermark/encryption seed


def _sigma(knight_id: str) -> str:
    return hashlib.sha256(knight_id.encode("utf-8")).hexdigest()[:16]


def _profile(
    piper_model:   str,
    weight:        float,
    privacy:       float,
    tts_engine:    str = "piper",
    stt_engine:    str = "faster_whisper",
    knight_id:     str = "",
) -> KnightVocalProfile:
    return KnightVocalProfile(
        piper_model   = piper_model,
        f0_hz         = round(110 + 75  * weight),
        wpm           = round(130 + 40  * weight),
        formant_shift = round(1.0 - 2.0 * privacy, 2),
        energy        = round(0.30 + 0.70 * weight, 2),
        prosody       = round(1.00 - 0.60 * privacy, 2),
        tts_engine    = tts_engine,
        stt_engine    = stt_engine,
        sigma         = _sigma(knight_id or piper_model),
    )


# ── Full Knight Roster ────────────────────────────────────────────────────────
# Format: knight_id → KnightVocalProfile(model, ω, π, tts_engine, stt_engine)
# All 31 Excalibur agents + 17 switchboard terminals

KNIGHT_PROFILES: dict[str, KnightVocalProfile] = {

    # ── Sovereign / Core ────────────────────────────────────────────────────
    "anya": _profile(
        "en_GB-jenny_dioco-medium", weight=0.96, privacy=0.10,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="anya"),
    "tasha": _profile(
        "en_GB-jenny_dioco-medium", weight=0.92, privacy=0.20,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="tasha"),
    "merlin": _profile(
        "en_US-ryan-medium", weight=0.88, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="merlin"),
    "oracle": _profile(
        "en_US-lessac-high", weight=0.95, privacy=0.30,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="oracle"),
    "boris": _profile(
        "en_US-joe-medium", weight=0.85, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="boris"),
    "lancelot": _profile(
        "en_US-danny-low", weight=0.78, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="lancelot"),
    "veritas": _profile(
        "en_GB-cori-medium", weight=0.88, privacy=0.40,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="veritas"),
    "systema": _profile(
        "en_US-lessac-medium", weight=0.80, privacy=0.40,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="systema"),

    # ── Excalibur Roster (non-sir entries) ──────────────────────────────────
    "king_arthur": _profile(
        "en_US-lessac-high", weight=1.00, privacy=0.10,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="king_arthur"),
    "sir_visage": _profile(
        "en_GB-alan-low", weight=0.80, privacy=0.20,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_visage"),
    "sir_hydron": _profile(
        "en_US-lessac-medium", weight=0.82, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_hydron"),
    "sir_syntax": _profile(
        "en_US-ryan-medium", weight=0.78, privacy=0.20,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_syntax"),
    "sir_forgemaster": _profile(
        "en_US-joe-medium", weight=0.75, privacy=0.60,
        tts_engine="silero", stt_engine="faster_whisper", knight_id="sir_forgemaster"),
    "sir_stitch": _profile(
        "en_US-lessac-medium", weight=0.76, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_stitch"),
    "sir_alchemist": _profile(
        "en_US-danny-low", weight=0.82, privacy=0.40,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_alchemist"),
    "baron_vaelen": _profile(
        "en_GB-cori-medium", weight=0.84, privacy=0.50,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="baron_vaelen"),
    "dame_sparkle": _profile(
        "en_GB-jenny_dioco-medium", weight=0.86, privacy=0.20,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="dame_sparkle"),
    "lukas": _profile(
        "en_US-joe-medium", weight=0.90, privacy=0.20,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="lukas"),
    "lady_veritas": _profile(
        "en_GB-cori-medium", weight=0.88, privacy=0.40,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="lady_veritas"),
    "sir_occam": _profile(
        "en_US-lessac-high", weight=0.87, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_occam"),
    "sir_gareth": _profile(
        "en_US-lessac-medium", weight=0.79, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_gareth"),
    "lady_apis": _profile(
        "en_GB-jenny_dioco-medium", weight=0.88, privacy=0.10,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="lady_apis"),
    "sir_dagonet": _profile(
        "en_US-danny-low", weight=0.74, privacy=0.20,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_dagonet"),
    "sir_sonus": _profile(
        "en_US-lessac-high", weight=0.93, privacy=0.10,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="sir_sonus"),
    "kaito": _profile(
        "en_US-ryan-medium", weight=0.83, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="kaito"),
    "squire_galahad": _profile(
        "en_US-lessac-medium", weight=0.65, privacy=0.20,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="squire_galahad"),
    "sir_scavenger": _profile(
        "en_US-danny-low", weight=0.72, privacy=0.50,
        tts_engine="silero", stt_engine="faster_whisper", knight_id="sir_scavenger"),
    "morgana": _profile(
        "en_GB-cori-medium", weight=0.91, privacy=0.60,
        tts_engine="speecht5", stt_engine="faster_whisper", knight_id="morgana"),

    # ── Switchboard Terminals (v701 manifest — 17 terminals) ────────────────
    "sir_alex": _profile(
        "en_US-lessac-high", weight=0.88, privacy=0.30,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="sir_alex"),
    "sir_boris": _profile(
        "en_US-joe-medium", weight=0.85, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_boris"),
    "sir_codex": _profile(
        "en_US-ryan-medium", weight=0.75, privacy=0.20,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_codex"),
    "sir_forge": _profile(
        "en_US-ryan-medium", weight=0.70, privacy=0.70,
        tts_engine="silero", stt_engine="faster_whisper", knight_id="sir_forge"),
    "sir_ghost": _profile(
        "en_US-lessac-medium", weight=1.00, privacy=1.00,
        tts_engine="silero", stt_engine="silero_only", knight_id="sir_ghost"),
    "sir_gideon": _profile(
        "en_GB-cori-medium", weight=0.85, privacy=0.50,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_gideon"),
    "sir_helio": _profile(
        "en_US-lessac-high", weight=0.90, privacy=0.20,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="sir_helio"),
    "sir_jcode": _profile(
        "en_US-danny-low", weight=0.87, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_jcode"),
    "sir_liberte": _profile(
        "en_US-lessac-medium", weight=0.80, privacy=0.50,
        tts_engine="silero", stt_engine="wav2vec2", knight_id="sir_liberte"),
    "sir_link": _profile(
        "en_US-danny-low", weight=0.78, privacy=0.20,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_link"),
    "sir_merlin": _profile(
        "en_US-ryan-medium", weight=0.82, privacy=0.30,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_merlin"),
    "sir_mnemo": _profile(
        "en_US-lessac-high", weight=0.92, privacy=0.40,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="sir_mnemo"),
    "sir_pi": _profile(
        "en_US-lessac-medium", weight=0.82, privacy=0.50,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_pi"),
    "sir_saltare": _profile(
        "en_US-lessac-medium", weight=0.80, privacy=0.40,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_saltare"),
    "sir_sentinel": _profile(
        "en_GB-cori-medium", weight=0.85, privacy=0.50,
        tts_engine="piper", stt_engine="faster_whisper", knight_id="sir_sentinel"),
    "sir_octavian": _profile(
        "en_US-lessac-high", weight=0.88, privacy=0.30,
        tts_engine="kokoro", stt_engine="faster_whisper", knight_id="sir_octavian"),
}

# Build flat VOICE_PRESETS for backward compatibility with piper_tts.py
VOICE_PRESETS: dict[str, str] = {k: v.piper_model for k, v in KNIGHT_PROFILES.items()}

DEFAULT_VOICE = KNIGHT_PROFILES["tasha"].piper_model


# ── Public API ────────────────────────────────────────────────────────────────

def get_voice(knight_id: str) -> str:
    """Return the Piper model string for a knight ID."""
    p = KNIGHT_PROFILES.get(knight_id.lower())
    return p.piper_model if p else "en_US-lessac-medium"


def get_profile(knight_id: str) -> KnightVocalProfile | None:
    """Return the full vocal profile for a knight ID."""
    return KNIGHT_PROFILES.get(knight_id.lower())


def get_sigma(knight_id: str) -> str:
    """Return the 16-char encryption seed (SHA256 fragment) for a knight."""
    p = KNIGHT_PROFILES.get(knight_id.lower())
    return p.sigma if p else _sigma(knight_id)


def vocal_weight_vector(knight_id: str) -> dict:
    """Return the full Merlin Omega vocal weight vector as a plain dict."""
    p = get_profile(knight_id)
    if not p:
        return {}
    return {
        "knight_id":     knight_id,
        "piper_model":   p.piper_model,
        "F0_hz":         p.f0_hz,
        "WPM":           p.wpm,
        "delta_formant": p.formant_shift,
        "epsilon":       p.energy,
        "rho":           p.prosody,
        "tts_engine":    p.tts_engine,
        "stt_engine":    p.stt_engine,
        "sigma":         p.sigma,
    }
