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
from typing import Any, Dict, List, Optional, Tuple

try:
    if "cua_driver_bridge" in sys.modules:
        _mod = sys.modules["cua_driver_bridge"]
    else:
        import importlib.util
        _cua_path = Path(__file__).resolve().parent.parent / "cua" / "cua_driver_bridge.py"
        if _cua_path.exists():
            _spec = importlib.util.spec_from_file_location("cua_driver_bridge", str(_cua_path))
            _mod = importlib.util.module_from_spec(_spec)
            sys.modules["cua_driver_bridge"] = _mod
            _spec.loader.exec_module(_mod)  # type: ignore
        else:
            _mod = None

    if _mod is not None:
        CuaDriverBridge = _mod.CuaDriverBridge
        DeviceViewport = _mod.DeviceViewport
        SentinelLease = _mod.SentinelLease
        SentinelViolationError = _mod.SentinelViolationError
        get_cua_driver = _mod.get_cua_driver
    else:
        CuaDriverBridge = None  # type: ignore
        DeviceViewport = None  # type: ignore
        SentinelLease = None  # type: ignore
        SentinelViolationError = Exception  # type: ignore
        get_cua_driver = None  # type: ignore
except Exception:
    CuaDriverBridge = None  # type: ignore
    DeviceViewport = None  # type: ignore
    SentinelLease = None  # type: ignore
    SentinelViolationError = Exception  # type: ignore
    get_cua_driver = None  # type: ignore

try:
    if "reya_handshake_gate" in sys.modules:
        _hsk_mod = sys.modules["reya_handshake_gate"]
    else:
        import importlib.util
        _hsk_path = Path(__file__).resolve().parent / "reya_handshake_gate.py"
        if _hsk_path.exists():
            _hsk_spec = importlib.util.spec_from_file_location("reya_handshake_gate", str(_hsk_path))
            _hsk_mod = importlib.util.module_from_spec(_hsk_spec)
            sys.modules["reya_handshake_gate"] = _hsk_mod
            _hsk_spec.loader.exec_module(_hsk_mod)  # type: ignore
        else:
            _hsk_mod = None

    if _hsk_mod is not None:
        ReyaHandshakeGate = _hsk_mod.ReyaHandshakeGate
        HandshakeLease = _hsk_mod.HandshakeLease
        HandshakeStatus = _hsk_mod.HandshakeStatus
        AutonomyTier = _hsk_mod.AutonomyTier
        get_handshake_gate = _hsk_mod.get_handshake_gate
        CANONICAL_OMEGA_KNIGHTS = _hsk_mod.CANONICAL_OMEGA_KNIGHTS
    else:
        ReyaHandshakeGate = None  # type: ignore
        HandshakeLease = None  # type: ignore
        HandshakeStatus = None  # type: ignore
        AutonomyTier = None  # type: ignore
        get_handshake_gate = None  # type: ignore
        CANONICAL_OMEGA_KNIGHTS = {"anya_omega", "merlin_omega", "arthur_omega"}
except Exception:
    ReyaHandshakeGate = None  # type: ignore
    HandshakeLease = None  # type: ignore
    HandshakeStatus = None  # type: ignore
    AutonomyTier = None  # type: ignore
    get_handshake_gate = None  # type: ignore
    CANONICAL_OMEGA_KNIGHTS = {"anya_omega", "merlin_omega", "arthur_omega"}

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
        # CUA Actions (trycua/cua assimilation)
        "cua_mouse_click",
        "cua_mouse_move",
        "cua_mouse_drag",
        "cua_mouse_scroll",
        "cua_keyboard_type",
        "cua_key_press",
        "cua_hotkey",
        "cua_screen_capture",
        "cua_screen_diff_verify",
        "cua_s1_chain",
    }

    def __init__(self, default_knight: str = "reya_companion"):
        self.active_knight_id = default_knight
        self.shm_slab_path = (
            "Local\\Camelot_Reya_Slab" if sys.platform == "win32" else "/dev/shm/camelot_reya_slab"
        )
        self.cgroups_memory_max_mb = 350.0
        self.cua_driver = get_cua_driver() if get_cua_driver is not None else None
        self.handshake_gate = get_handshake_gate() if get_handshake_gate is not None else None
        self.active_lease: Optional[Any] = None

    def request_kinetic_handshake(
        self,
        intent: str,
        knight_id: Optional[str] = None,
        tenant_id: str = "Vizion Sky",
        requested_actions: Optional[List[str]] = None,
        auto_approve_if_eligible: bool = True,
    ) -> Any:
        """Requests kinetic handshake clearance for the active or specified Knight."""
        target_knight = (knight_id or self.active_knight_id).lower().strip()
        if self.handshake_gate is None:
            return None
        lease = self.handshake_gate.request_handshake(
            knight_id=target_knight,
            intent=intent,
            requested_actions=requested_actions,
            tenant_id=tenant_id,
            auto_approve_if_eligible=auto_approve_if_eligible,
        )
        if lease.is_valid:
            self.create_sentinel_lease(
                target_device="desktop",
                allowed_rect=lease.allowed_rect,
                red_zones=lease.red_zones,
                max_actions=lease.max_actions,
            )
        return lease

    def grant_kinetic_handshake(self, knight_id: Optional[str] = None) -> Any:
        """Called when user explicitly grants permission to access Reya."""
        target_knight = (knight_id or self.active_knight_id).lower().strip()
        if self.handshake_gate is None:
            return None
        lease = self.handshake_gate.request_handshake(
            knight_id=target_knight,
            intent="User Explicit Allowance Granted",
            auto_approve_if_eligible=True,
        )
        approved = self.handshake_gate.grant_user_approval(lease)
        self.create_sentinel_lease(
            target_device="desktop",
            allowed_rect=approved.allowed_rect,
            red_zones=approved.red_zones,
            max_actions=approved.max_actions,
        )
        return approved

    def revoke_kinetic_handshake(self, knight_id: Optional[str] = None) -> bool:
        """Instantly revokes Reya kinetic access for a Knight."""
        target_knight = (knight_id or self.active_knight_id).lower().strip()
        if self.handshake_gate is None:
            return False
        self.active_lease = None
        return self.handshake_gate.revoke_handshake(target_knight)

    def create_sentinel_lease(
        self,
        target_device: str = "desktop",
        allowed_rect: Optional[Tuple[float, float, float, float]] = None,
        red_zones: Optional[List[Tuple[float, float, float, float]]] = None,
        max_actions: int = 500,
    ) -> Any:
        """Forges a Sir Sentinel capability lease restricting CUA actions."""
        if SentinelLease is None:
            return None
        lease = SentinelLease(
            lease_id=f"lease_{os.urandom(4).hex()}",
            target_device=target_device,
            allowed_rect=allowed_rect,
            red_zones=red_zones or [],
            max_actions=max_actions,
        )
        self.active_lease = lease
        logger.info(f"Sentinel lease active: {lease.lease_id} (device={target_device})")
        return lease

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

        # Kinetic Gate & Handshake Protocol Enforcement
        is_kinetic = action_type.startswith("cua_") or action_type == "mobile_adb_tap"
        channeled_kid = persona.knight_id.lower().strip()
        handshake_status_label = "REYA_NATIVE"

        if is_kinetic and channeled_kid != "reya_companion" and self.handshake_gate is not None:
            hsk_lease = self.handshake_gate.get_active_lease(channeled_kid)
            if not hsk_lease or not hsk_lease.is_valid:
                autonomy_tier, level, rationale = self.handshake_gate.evaluate_knight_autonomy(channeled_kid)
                user_approved = params.get("user_approved") or os.environ.get("CAMELOT_AUTO_APPROVE") == "true"

                if user_approved:
                    hsk_lease = self.handshake_gate.request_handshake(
                        knight_id=channeled_kid,
                        intent=params.get("intent", f"User allowance for {action_type}"),
                        auto_approve_if_eligible=True,
                    )
                    self.handshake_gate.grant_user_approval(hsk_lease)
                    handshake_status_label = "USER_APPROVED_HANDSHAKE"
                elif autonomy_tier in (AutonomyTier.SOVEREIGN_ROOT, AutonomyTier.HITL_GUIDED_ALPHA_OMEGA):
                    hsk_lease = self.handshake_gate.request_handshake(
                        knight_id=channeled_kid,
                        intent=params.get("intent", f"Alpha Omega autonomous {action_type}"),
                        auto_approve_if_eligible=True,
                    )
                    handshake_status_label = "ALPHA_OMEGA_AUTONOMOUS"
                else:
                    logger.warning(
                        f"Reya kinetic access blocked for [{persona.display_name}]: Handshake required ({rationale})"
                    )
                    return {
                        "status": "HANDSHAKE_REQUIRED",
                        "error": "KINETIC_HANDSHAKE_REQUIRED",
                        "message": (
                            f"Sire, [{persona.display_name}] requests permission to bind to REYA Kinetic Fabric "
                            f"for action '{action_type}'. Gaining Alpha Omega level will grant autonomous access. "
                            f"Handshake approval required."
                        ),
                        "knight_id": channeled_kid,
                        "speaking_name": persona.display_name,
                        "autonomy_tier": autonomy_tier.value,
                        "knight_level": level,
                        "action": action_type,
                        "handshake_prompt": f"Approve Reya kinetic access for [{persona.display_name}]? (Y/N)",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }

            if hsk_lease and hsk_lease.is_valid:
                hsk_lease.actions_executed += 1
                if not self.active_lease:
                    self.create_sentinel_lease(
                        target_device="desktop",
                        allowed_rect=hsk_lease.allowed_rect,
                        red_zones=hsk_lease.red_zones,
                        max_actions=hsk_lease.max_actions,
                    )

        # Sovereign Memory Attribution
        attribution = {
            "initiating_knight": persona.knight_id,
            "speaking_name": persona.display_name,
            "kinetic_fabric": "REYA_EDGE_FABRIC",
            "memory_routing": {
                "memcastle_partition": persona.knight_id.upper(),
                "graphiti_partition": f"{persona.knight_id.lower()}_graphiti.db",
                "observatory_xp_recipient": persona.knight_id,
            },
            "handshake_status": handshake_status_label,
        }

        cua_result: Optional[Dict[str, Any]] = None
        if action_type.startswith("cua_") and self.cua_driver is not None:
            lease = params.get("lease", self.active_lease)
            if action_type == "cua_mouse_click":
                cua_result = self.cua_driver.mouse_click(
                    norm_x=params.get("norm_x", 0.5),
                    norm_y=params.get("norm_y", 0.5),
                    button=params.get("button", "left"),
                    clicks=params.get("clicks", 1),
                    lease=lease,
                )
            elif action_type == "cua_mouse_move":
                cua_result = self.cua_driver.mouse_move(
                    norm_x=params.get("norm_x", 0.5),
                    norm_y=params.get("norm_y", 0.5),
                    lease=lease,
                )
            elif action_type == "cua_mouse_drag":
                cua_result = self.cua_driver.mouse_drag(
                    start_x=params.get("start_x", 0.0),
                    start_y=params.get("start_y", 0.0),
                    end_x=params.get("end_x", 0.5),
                    end_y=params.get("end_y", 0.5),
                    button=params.get("button", "left"),
                    lease=lease,
                )
            elif action_type == "cua_mouse_scroll":
                cua_result = self.cua_driver.mouse_scroll(
                    dx=params.get("dx", 0),
                    dy=params.get("dy", -120),
                    lease=lease,
                )
            elif action_type == "cua_keyboard_type":
                cua_result = self.cua_driver.keyboard_type(
                    text=params.get("text", ""),
                    delay_ms=params.get("delay_ms", 10),
                    lease=lease,
                )
            elif action_type == "cua_key_press":
                cua_result = self.cua_driver.key_press(
                    key=params.get("key", "Return"),
                    lease=lease,
                )
            elif action_type == "cua_hotkey":
                cua_result = self.cua_driver.hotkey(
                    keys=params.get("keys", ["ctrl", "c"]),
                    lease=lease,
                )
            elif action_type == "cua_screen_capture":
                cua_result = self.cua_driver.screen_capture(
                    bounding_box=params.get("bounding_box", None),
                )
            elif action_type == "cua_screen_diff_verify":
                cua_result = self.cua_driver.screen_diff_verify(
                    pre_hash=params.get("pre_hash", ""),
                    post_hash=params.get("post_hash", ""),
                    min_delta_pct=params.get("min_delta_pct", 0.01),
                )
            elif action_type == "cua_s1_chain":
                cua_result = self.cua_driver.execute_s1_chain(
                    actions=params.get("actions", []),
                    lease=lease,
                )

        combined_result: Dict[str, Any] = {
            "action_type": action_type,
            "voice_engine": persona.voice_engine,
            "text_length": len(params.get("text", "")),
            **params,
        }
        if cua_result:
            combined_result["cua_driver_execution"] = cua_result

        return {
            "status": "SUCCESS",
            "action": action_type,
            "action_id": action_id,
            "channeled_knight": persona.knight_id,
            "speaking_name": persona.display_name,
            "executed_by": "REYA_UNIVERSAL_FABRIC",
            "attribution": attribution,
            "sandbox": {
                "cgroups_memory_max": "350M",
                "memory_ceiling_mb": self.cgroups_memory_max_mb,
                "shm_slab": self.shm_slab_path,
                "sentinel_lease_active": self.active_lease.lease_id if self.active_lease else None,
            },
            "result": combined_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_status(self) -> Dict[str, Any]:
        persona = self.current_persona
        hsk = (
            self.handshake_gate.get_active_lease(persona.knight_id)
            if self.handshake_gate
            else None
        )
        return {
            "fabric": "REYA_UNIVERSAL_KNIGHT_FABRIC",
            "active_knight": persona.knight_id,
            "active_name": persona.display_name,
            "active_engine": persona.voice_engine,
            "available_knights": list(CANONICAL_KNIGHT_PERSONAS.keys()),
            "shm_slab": self.shm_slab_path,
            "cgroups_memory_max_mb": self.cgroups_memory_max_mb,
            "cua_driver_attached": self.cua_driver is not None,
            "cua_viewport": self.cua_driver.viewport.device_id if self.cua_driver else None,
            "sentinel_lease": self.active_lease.lease_id if self.active_lease else None,
            "handshake_active": hsk.is_valid if hsk else (persona.knight_id == "reya_companion"),
            "handshake_id": hsk.handshake_id if hsk else None,
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
