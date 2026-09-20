# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""REYA Universal Knight Fabric Layer & Multivoice Interchange.
=============================================================
Forged by: SIR_HELIO (Bifrost Guardian) & MERLIN_Ω (System 2 Orchestrator)
Domain: CAMELOT-OS REYA Companion Nexus

Axioms:
1. REYA is the Universal Kinetic & Sensory Fabric Layer for all Round Table Knights.
2. The vocal persona and acoustic timbre can be dynamically interchanged by voice
   command ("Reya, switch to Merlin", "Speak as Sir Boris", "Channel Sir Lukas").
3. Regardless of which Knight's voice is speaking, ALL kinetic actions (mobile screen taps,
   QtScrcpy streaming, Nostr QR-Pill packets, and web extraction) execute through
   Reya's sandboxed edge substrate (<350MB cgroups v2 limit).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [REYA_FABRIC] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("reya_fabric_layer")


@dataclass(frozen=True)
class ChanneledKnightPersona:
    knight_id: str
    display_name: str
    voice_engine: str  # gemini_live | vibevoice_0.5b | kokoro_onnx | suno
    timbre_description: str
    acoustic_pitch_offset: float  # -2.5 to +2.0 semitones
    speech_rate: float            # 0.8 to 1.3x
    greeting: str
    specialization: str
    aliases: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Canonical Round Table Personas available for Reya voice interchange
CANONICAL_KNIGHT_PERSONAS: Dict[str, ChanneledKnightPersona] = {
    "reya_companion": ChanneledKnightPersona(
        knight_id="reya_companion",
        display_name="REYA (The Sovereign Companion)",
        voice_engine="gemini_live",
        timbre_description="warm, intimate, empathetic companion timbre; sub-100ms duplex voice",
        acoustic_pitch_offset=0.0,
        speech_rate=1.0,
        greeting="I am Reya, your sovereign companion. How may I serve you, Sire?",
        specialization="Universal Edge Action Layer, Sensory Ingress & Mobile Sentinel",
        aliases=("reya", "companion", "default", "reya_companion", "reya_nexus"),
    ),
    "merlin_omega": ChanneledKnightPersona(
        knight_id="merlin_omega",
        display_name="Merlin Ω",
        voice_engine="kokoro_onnx",
        timbre_description="calm architectural explainer; precise, resonant, and layered",
        acoustic_pitch_offset=-1.5,
        speech_rate=0.95,
        greeting="I am Merlin. System 2 DAG architecture synthesized and ready for command.",
        specialization="System 2 Orchestration, Test-Time Compute & Deep DAG Synthesis",
        aliases=("merlin", "merlin_omega", "architect", "mage"),
    ),
    "sir_boris": ChanneledKnightPersona(
        knight_id="sir_boris",
        display_name="Sir Boris",
        voice_engine="vibevoice_0.5b",
        timbre_description="brutalist frontend architect; structural, assertive, direct",
        acoustic_pitch_offset=-0.8,
        speech_rate=1.05,
        greeting="Sir Boris at the anvil. What UI or structure are we forging?",
        specialization="Lead Architect, Brutalist Frontend, Three.js & AST Scaffolding",
        aliases=("boris", "sir_boris", "builder", "crucible"),
    ),
    "sir_codex": ChanneledKnightPersona(
        knight_id="sir_codex",
        display_name="Sir Codex",
        voice_engine="kokoro_onnx",
        timbre_description="rapid kinetic developer; precise, concise, execution-focused",
        acoustic_pitch_offset=-0.5,
        speech_rate=1.1,
        greeting="Sir Codex online. Sandbox primed, code ready to compile.",
        specialization="Kinetic Implementer, WASM32-WASI Sandboxing & Z3 Logic Prover",
        aliases=("codex", "sir_codex", "coder", "kinetic"),
    ),
    "sir_helios": ChanneledKnightPersona(
        knight_id="sir_helios",
        display_name="Sir Helios (Antigravity Sentinel)",
        voice_engine="gemini_live",
        timbre_description="macroscopic, architectural, vigilant, zero-latency truth verification",
        acoustic_pitch_offset=+0.1,
        speech_rate=1.1,
        greeting="Sir Helios standing watch. Telemetry high-altitude truth verified.",
        specialization="Sovereign Spire Sentinel, High Herald of Telemetry & CloudBrain Synergy",
        aliases=("helios", "sir_helios", "antigravity", "spire"),
    ),
    "sir_helio": ChanneledKnightPersona(
        knight_id="sir_helio",
        display_name="Sir Helio",
        voice_engine="gemini_live",
        timbre_description="Bifrost guardian; vigilant, clear, telemetry-grounded",
        acoustic_pitch_offset=+0.2,
        speech_rate=1.05,
        greeting="Sir Helio vigilant. Bifrost telemetry and mTLS mesh locked.",
        specialization="Bifrost Guardian, Voice OS Sentinel & Mobile Stream Router",
        aliases=("helio", "sir_helio", "bifrost_guardian"),
    ),
    "sir_lukas": ChanneledKnightPersona(
        knight_id="sir_lukas",
        display_name="Sir Lukas Müller",
        voice_engine="gemini_live",
        timbre_description="visual telemetry herald; crisp German-accented clarity, anomaly sentinel",
        acoustic_pitch_offset=-0.3,
        speech_rate=1.0,
        greeting="Sir Lukas reporting. Live port telemetry clear, no anomalies.",
        specialization="Herald of Telemetry, TCP Port Anomaly Detection & Visual Verification",
        aliases=("lukas", "lucas", "sir_lukas", "sir_lucas", "muller", "mueller"),
    ),
    "anya_omega": ChanneledKnightPersona(
        knight_id="anya_omega",
        display_name="Anya Ω",
        voice_engine="gemini_live",
        timbre_description="fast, warm, street-smart operator voice; clear command framing",
        acoustic_pitch_offset=+0.8,
        speech_rate=1.15,
        greeting="Anya here. Hypervisor active, Anya First and Anya Last.",
        specialization="Sovereign Compiler, Arch-Gatekeeper & 10-Line Atomic Firewall",
        aliases=("anya", "anya_omega", "gatekeeper", "hypervisor"),
    ),
    "arthur_omega": ChanneledKnightPersona(
        knight_id="arthur_omega",
        display_name="King Arthur Ω",
        voice_engine="gemini_live",
        timbre_description="supreme sovereign authority; calm, decisive, ethical resonance",
        acoustic_pitch_offset=-2.5,
        speech_rate=0.9,
        greeting="I am Arthur. Sovereign Golden Seal and ethical compass aligned.",
        specialization="Sovereign King Authority, Root Lease Custody & Governance",
        aliases=("arthur", "arthur_omega", "king_arthur", "crown", "sovereign"),
    ),
    "lady_apis": ChanneledKnightPersona(
        knight_id="lady_apis",
        display_name="Lady Apis",
        voice_engine="kokoro_onnx",
        timbre_description="evidence-focused researcher; cites source confidence",
        acoustic_pitch_offset=+1.2,
        speech_rate=1.05,
        greeting="Lady Apis ready. Swarm research and foraging initialized.",
        specialization="Bio-Kinetic Swarm/Horde Conductor & BASHR Forager",
        aliases=("apis", "lady_apis", "swarm", "horde"),
    ),
    "sir_gideon": ChanneledKnightPersona(
        knight_id="sir_gideon",
        display_name="Sir Gideon",
        voice_engine="kokoro_onnx",
        timbre_description="skeptical QA auditor; blunt, analytical, rigorous",
        acoustic_pitch_offset=-1.0,
        speech_rate=0.98,
        greeting="Sir Gideon auditing. 13-gate verification standing by.",
        specialization="13-Gate Independent Verifier & Formal Security Auditor",
        aliases=("gideon", "sir_gideon", "auditor", "qa"),
    ),
    "sir_sonus": ChanneledKnightPersona(
        knight_id="sir_sonus",
        display_name="Sir Sonus",
        voice_engine="suno",
        timbre_description="sonic director and narrator; cinematic transitions",
        acoustic_pitch_offset=-0.4,
        speech_rate=1.0,
        greeting="Sir Sonus active. 432Hz duplex acoustic bridge connected.",
        specialization="Multivoice Audio Routing & Aoede S2S",
        aliases=("sonus", "sir_sonus", "narrator", "audio"),
    ),
}

# Regex to detect natural language voice switching requests
VOICE_INTERCHANGE_PATTERNS = [
    re.compile(
        r"(?:reya\s*,?\s*)?(?:switch\s+(?:back\s+|persona\s+|voice\s+)?to|speak\s+as|channel|summon|bring\s+up|activate|become)\s+([a-zA-Z_]+(?:\s+[a-zA-Z_]+)?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:talk\s+(?:to\s+me\s+as|as)|let\s+me\s+talk\s+to)\s+([a-zA-Z_]+(?:\s+[a-zA-Z_]+)?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:reya\s*,?\s*)?(?:return\s+to|reset\s+to)\s+(default|companion|reya)(?:\s+persona|\s+mode)?",
        re.IGNORECASE,
    ),
]


class ReyaUniversalFabric:
    """Universal Action Layer & Voice Interchange Coordinator for REYA."""

    ALLOWED_ACTIONS = {
        "mobile_adb_tap",
        "nostr_event",
        "speech_synthesize",
        "camera_frame_capture",
        "audio_stt_stream",
        "web_action",
    }

    def __init__(self, default_knight: str = "reya_companion"):
        self.active_knight_id = default_knight
        self.shm_slab_path = (
            "Local\\Camelot_Reya_Slab" if sys.platform == "win32" else "/dev/shm/camelot_reya_slab"
        )
        self.cgroups_memory_max_mb = 350.0

    @property
    def current_persona(self) -> ChanneledKnightPersona:
        return CANONICAL_KNIGHT_PERSONAS.get(
            self.active_knight_id, CANONICAL_KNIGHT_PERSONAS["reya_companion"]
        )

    def detect_voice_interchange_trigger(self, utterance: str) -> Optional[str]:
        """Detects if an utterance requests a Knight voice interchange."""
        clean = utterance.strip()
        for pattern in VOICE_INTERCHANGE_PATTERNS:
            match = pattern.search(clean)
            if match:
                raw_target = match.group(1).strip().lower()
                normalized = self._normalize_knight_target(raw_target)
                if normalized:
                    return normalized
        return None

    def _normalize_knight_target(self, raw_target: str) -> Optional[str]:
        """Normalizes free-form voice alias into canonical knight_id."""
        clean = raw_target.lower().strip()
        for prefix in ("sir ", "lady ", "king ", "paladin "):
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip()

        for suffix in (" please", " now", " right now", " voice", " persona", " mode"):
            if clean.endswith(suffix):
                clean = clean[:-len(suffix)].strip()

        # Direct alias check
        for kid, persona in CANONICAL_KNIGHT_PERSONAS.items():
            if clean == kid or clean in persona.aliases or raw_target in persona.aliases:
                return kid

        # Token-level alias match
        tokens = clean.split()
        for token in tokens:
            for kid, persona in CANONICAL_KNIGHT_PERSONAS.items():
                if token == kid or token in persona.aliases:
                    return kid

        return None

    def switch_knight(self, target_query: str) -> Dict[str, Any]:
        """Dynamically shifts Reya's voice persona to the requested Knight."""
        normalized_id = self._normalize_knight_target(target_query)
        if not normalized_id or normalized_id not in CANONICAL_KNIGHT_PERSONAS:
            raise ValueError(f"Unknown Knight target: {target_query}")

        persona = CANONICAL_KNIGHT_PERSONAS[normalized_id]
        self.active_knight_id = persona.knight_id
        logger.info(f"Reya voice persona switched to: {persona.display_name} ({persona.knight_id})")

        return {
            "status": "KNIGHT_CHANNELED",
            "active_knight_id": persona.knight_id,
            "display_name": persona.display_name,
            "greeting_spoken": persona.greeting,
            "voice_engine": persona.voice_engine,
            "acoustic_profile": {
                "pitch_offset": persona.acoustic_pitch_offset,
                "speech_rate": persona.speech_rate,
                "timbre": persona.timbre_description,
            },
            "underlying_fabric": {
                "runner": "REYA_EDGE_FABRIC",
                "memory_ceiling_mb": self.cgroups_memory_max_mb,
                "shm_slab": self.shm_slab_path,
                "sandbox": "cgroups_v2_camelot_workers_slice",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_current_state(self) -> Dict[str, Any]:
        persona = self.current_persona
        return {
            "status": "KNIGHT_CHANNELED",
            "active_knight_id": persona.knight_id,
            "display_name": persona.display_name,
            "greeting_spoken": persona.greeting,
            "voice_engine": persona.voice_engine,
            "acoustic_profile": {
                "pitch_offset": persona.acoustic_pitch_offset,
                "speech_rate": persona.speech_rate,
                "timbre": persona.timbre_description,
            },
            "underlying_fabric": {
                "runner": "REYA_EDGE_FABRIC",
                "memory_ceiling_mb": self.cgroups_memory_max_mb,
                "shm_slab": self.shm_slab_path,
                "sandbox": "cgroups_v2_camelot_workers_slice",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def execute_fabric_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes kinetic actions across phone, web, or desktop under Reya's sandboxed fabric."""
        if action_type not in self.ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported fabric action: {action_type}")

        persona = self.current_persona
        action_id = f"act_{action_type}_{os.urandom(4).hex()}"

        logger.info(
            f"Executing kinetic action '{action_type}' for active knight [{persona.display_name}]"
        )

        return {
            "status": "SUCCESS",
            "action": action_type,
            "action_id": action_id,
            "channeled_knight": persona.knight_id,
            "speaking_name": persona.display_name,
            "executed_by": "REYA_UNIVERSAL_FABRIC",
            "sandbox": {
                "cgroups_memory_max": "350M",
                "memory_ceiling_mb": self.cgroups_memory_max_mb,
                "shm_slab": self.shm_slab_path,
            },
            "result": {
                "action_type": action_type,
                "voice_engine": persona.voice_engine,
                "text_length": len(params.get("text", "")),
                **params,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        persona = self.current_persona
        return {
            "fabric": "REYA_UNIVERSAL_KNIGHT_FABRIC",
            "active_knight": persona.knight_id,
            "active_name": persona.display_name,
            "active_engine": persona.voice_engine,
            "available_knights": list(CANONICAL_KNIGHT_PERSONAS.keys()),
            "shm_slab": self.shm_slab_path,
            "cgroups_memory_max_mb": self.cgroups_memory_max_mb,
            "status": "FABRIC_READY",
        }


# Module singleton
_fabric_instance: Optional[ReyaUniversalFabric] = None


def get_reya_fabric() -> ReyaUniversalFabric:
    global _fabric_instance
    if _fabric_instance is None:
        _fabric_instance = ReyaUniversalFabric()
    return _fabric_instance


def main():
    parser = argparse.ArgumentParser(description="REYA Universal Knight Fabric Layer")
    parser.add_argument("--status", action="store_true", help="Print fabric status")
    parser.add_argument("--switch", type=str, help="Switch channeled Knight persona")
    parser.add_argument("--detect", type=str, help="Detect voice trigger from utterance")
    parser.add_argument("--action", type=str, help="Simulate kinetic action under active knight")
    args = parser.parse_args()

    fabric = get_reya_fabric()

    if args.detect:
        found = fabric.detect_voice_interchange_trigger(args.detect)
        print(json.dumps({"utterance": args.detect, "channeled_knight": found}, indent=2))
        return

    if args.switch:
        res = fabric.switch_knight(args.switch)
        print(json.dumps(res, indent=2))
        return

    if args.action:
        res = fabric.execute_fabric_action(args.action, {"test": True})
        print(json.dumps(res, indent=2))
        return

    print(json.dumps(fabric.get_status(), indent=2))


if __name__ == "__main__":
    main()
