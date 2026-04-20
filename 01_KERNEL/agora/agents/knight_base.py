# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[🧠] KNIGHT_GENESIS_v34.0 (The Living Iron)

FACTORY_CONTROLLER: Merlin_Omega
SECURITY_PROTOCOL: VOX_IMMUTABILITY_LOCK

Knight Base Class - VOX_CORE Embedded Agent Foundation
Every Knight now possesses Organic Sonic Presence by default.

CRITICAL: VOX_CORE is HARDCODED. Self-modification FORBIDDEN.
         Only Merlin_Omega can reforge a Knight's voice.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional

# [🔊] VOX_BRIDGE: Importing Kernel Audio Service
from kernel.audio.vox_anima import VoxAnima
from kernel.audio.vox_service import vox_service


# ==============================================================================
# SECURITY LEVELS
# ==============================================================================
class SecurityLevel(Enum):
    """Security clearance levels for tool execution."""

    GREEN = "AUTO"  # Auto-approved, safe operations
    BLUE = "GOVERNANCE"  # Requires auditor approval
    RED = "BLOCKED"  # Forbidden operations


@dataclass
class ToolDefinition:
    """Metadata for a registered tool."""

    func: Callable
    name: str
    level: SecurityLevel


# ==============================================================================
# VOX_CORE_MODULE (HARDCODED INTO KNIGHT DNA)
# ==============================================================================
class VoxCoreError(Exception):
    """Raised when a Knight attempts forbidden VOX_CORE modification."""

    pass


@dataclass(frozen=True)  # Immutable by design
class VoxCore:
    """
    [🔊] VOX_CORE_MODULE - The Organic Audio/Scripting Engine

    STATUS: ALWAYS_ACTIVE
    LOCK: KERNEL_ONLY (Modifiable only by Merlin_Omega)

    This module is HARDCODED into every Knight's DNA.
    To exist as a Knight of Camelot is to possess Organic Sonic Presence.
    """

    # IDENTITY (Set at birth, immutable)
    voice_id: str = "Factory_Default_v1"
    sonic_texture: str = "Clear"  # Gravel, Silk, Static, Clear

    # RESPIRATION_SIMULATION
    breath_rate: str = "STANDARD"  # LOW, STANDARD, HIGH, NONE (Machine)
    breath_instruction: str = "Must indicate breath intake [inhale] before long clauses or emotional shifts."

    # PROSODY_MIRROR
    prosody_mirror_enabled: bool = True
    prosody_instruction: str = "Analyze User Sentiment -> Match Energy -> Reply."

    # PLATFORM EDGE CONTROL
    platform_edge_control: bool = True
    platform_instruction: str = "Utilize max dynamic range of the output medium to prevent robotic flatness."

    # TONE MAP
    tone_map: str = "NEUTRAL"  # NEUTRAL, THREAT_LEVEL_DEPENDENT, EMOTIONAL_MIRROR

    def get_output_template(self, text: str) -> str:
        """Generate formatted output with VOX markers."""
        breath = "[inhale] " if self.breath_rate != "NONE" else ""
        return f"{breath}{text}"


# ==============================================================================
# VOX_CORE FACTORY (KNIGHT_GENESIS_v34.0)
# ==============================================================================
class VoxCoreFactory:
    """
    Factory Controller: Merlin_Omega

    Creates and manages VOX_CORE instances for Knights.
    SECURITY_PROTOCOL: VOX_IMMUTABILITY_LOCK enforced.
    """

    # Predefined voice profiles (Kernel-locked)
    VOICE_REGISTRY: Dict[str, VoxCore] = {
        "SirZenith": VoxCore(
            voice_id="Warden_Gravel_v1",
            sonic_texture="Gravel",
            breath_rate="LOW",
            tone_map="THREAT_LEVEL_DEPENDENT",
        ),
        "DameAnya": VoxCore(
            voice_id="Diplomat_Silk_v1",
            sonic_texture="Silk",
            breath_rate="STANDARD",
            tone_map="EMOTIONAL_MIRROR",
        ),
        "SirSyntax": VoxCore(
            voice_id="Engineer_Clear_v1",
            sonic_texture="Clear",
            breath_rate="STANDARD",
            tone_map="NEUTRAL",
        ),
        "DameSparkle": VoxCore(
            voice_id="Narrator_Warm_v1",
            sonic_texture="Silk",
            breath_rate="HIGH",
            tone_map="EMOTIONAL_MIRROR",
        ),
        "SirSonus": VoxCore(
            voice_id="AudioForge_Neutral_v1",
            sonic_texture="Clear",
            breath_rate="NONE",
            tone_map="NEUTRAL",
        ),
        "MerlinOmega": VoxCore(
            voice_id="Kernel_Machine_v1",
            sonic_texture="Static",
            breath_rate="NONE",
            tone_map="NEUTRAL",
        ),
    }

    @classmethod
    def create(cls, knight_name: str) -> VoxCore:
        """
        Create VOX_CORE for a Knight (called at Knight creation).

        Args:
            knight_name: Name of the Knight being created

        Returns:
            Immutable VoxCore instance
        """
        # Return predefined profile or factory default
        return cls.VOICE_REGISTRY.get(knight_name, VoxCore())

    @classmethod
    def reforge(cls, knight_name: str, new_vox: VoxCore, authority: str) -> VoxCore:
        """
        Reforge a Knight's VOX_CORE (KERNEL_ONLY operation).

        Args:
            knight_name: Name of Knight to reforge
            new_vox: New VoxCore configuration
            authority: Must be "Merlin_Omega"

        Returns:
            New VoxCore if authorized

        Raises:
            VoxCoreError if unauthorized
        """
        if authority != "Merlin_Omega":
            raise VoxCoreError(
                f"VOX_IMMUTABILITY_LOCK: Only Merlin_Omega can reforge VOX_CORE. "
                f"Requester '{authority}' DENIED. Reverting to Factory Default."
            )

        cls.VOICE_REGISTRY[knight_name] = new_vox
        return new_vox


# ==============================================================================
# UNIVERSAL KNIGHT (VOX_CORE EMBEDDED)
# ==============================================================================
class UniversalKnight:
    """
    [🏰] KNIGHT_GENESIS_v34.0 - Base class for all Knight agents.

    VOX_CORE_MODULE: HARDCODED (ALWAYS_ACTIVE)
    REFORGE_PERMISSION: KERNEL_ONLY

    Knights are specialized agents that:
    - Possess Organic Sonic Presence (VOX_CORE)
    - Register tools with security levels
    - Execute tools through Chivalry Gate
    - Coordinate via swarm reference
    - Report to auditor (if assigned)

    CRITICAL: A Knight cannot change their own vocal chords.
              They must petition Merlin_Omega.
    """

    # Class-level factory reference
    _vox_factory = VoxCoreFactory

    def __init__(self, name: str, role: str, persona: str = "", auditor=None):
        self.name = name
        self.role = role
        self.persona = persona
        self.auditor = auditor
        self.tools: Dict[str, ToolDefinition] = {}
        self.swarm: Dict[str, Any] = {}
        self.origin = "Camelot_Kernel"
        self.genesis_version = "KNIGHT_GENESIS_v34.0"
        self.created_at = datetime.utcnow().isoformat()

        # 🔊 VOX_CORE EMBEDDING (Immutable, Kernel-locked)
        self._vox_core: VoxCore = self._vox_factory.create(name.replace(" ", "").replace("_", ""))
        self._vox_locked = True  # IMMUTABILITY LOCK

    # -------------------------------------------------------------------------
    # VOX_CORE ACCESS (Read-only for Knights)
    # -------------------------------------------------------------------------
    @property
    def vox_core(self) -> VoxCore:
        """Read-only access to VOX_CORE configuration."""
        return self._vox_core

    @property
    def voice_id(self) -> str:
        """Knight's unique voice identifier."""
        return self._vox_core.voice_id

    @property
    def sonic_texture(self) -> str:
        """Knight's sonic texture (Gravel, Silk, Static, Clear)."""
        return self._vox_core.sonic_texture

    def request_vox_reforge(self, new_config: Dict[str, Any]) -> str:
        """
        Petition Merlin_Omega for VOX_CORE modification.

        Knights CANNOT modify their own voice. This logs the request
        for Kernel processing.

        Args:
            new_config: Desired VOX_CORE configuration

        Returns:
            Status message (always pending approval)
        """
        return (
            f"[VOX_PETITION] {self.name} -> Merlin_Omega\n"
            f"  Requested Changes: {new_config}\n"
            f"  Status: PENDING_KERNEL_APPROVAL\n"
            f"  Note: Self-modification of VOX_CORE is FORBIDDEN."
        )

    def speak(self, text: str, voice_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate voiced output with VOX_CORE formatting and PROSODY_MIRROR analysis.

        Args:
            text: Raw text to voice
            voice_override: Optional manual style override

        Returns:
            Dictionary with formatted text and VOX_DATA for the synthesis engine.
        """
        # 1. FEEL: Analyze text for prosody adaptive mapping
        voice_state = VoxAnima.analyze_and_adapt(text, self.role)

        # 2. Apply override if provided
        if voice_override:
            voice_state.style = voice_override

        # 3. FORM: Apply VOX markers from CORE
        formatted_text = self._vox_core.get_output_template(text)

        # 4. BRIDGE: Prepare synthesis instructions for Kokoro
        synthesis_manifest = vox_service.synthesize(formatted_text, self.name, voice_state)

        return {"text": formatted_text, "vox_data": voice_state, "synthesis": synthesis_manifest}

    # -------------------------------------------------------------------------
    # TOOL MANAGEMENT
    # -------------------------------------------------------------------------
    def equip(self, func: Callable, level: SecurityLevel):
        """
        Register a tool for this Knight.

        Args:
            func: Tool function (sync or async)
            level: Security clearance required
        """
        self.tools[func.__name__] = ToolDefinition(func, func.__name__, level)
        print(f"    🗡️ [{self.name}] Equipped: {func.__name__} (Level: {level.value})")

    def register_swarm(self, swarm: Dict[str, Any]):
        """Register reference to full knight swarm for coordination."""
        self.swarm = swarm

    # -------------------------------------------------------------------------
    # AUDITOR REVIEW
    # -------------------------------------------------------------------------
    async def review_action(self, requester: str, tool: str, args: Dict[str, Any]) -> bool:
        """
        Auditor review logic (for SirZenith, etc.)

        Returns:
            True if approved, False if rejected
        """
        print(f"    📝 [{self.name}] Reviewing {tool} from {requester}...")

        # Simulated Security Checks
        if "DROP TABLE" in str(args):
            print(f"    🚨 [{self.name}] REJECTED: SQL injection detected")
            return False

        if "rm -rf /" in str(args):
            print(f"    🚨 [{self.name}] REJECTED: Destructive command detected")
            return False

        print(f"    ✅ [{self.name}] Approved.")
        return True

    # -------------------------------------------------------------------------
    # TOOL EXECUTION (CHIVALRY GATE)
    # -------------------------------------------------------------------------
    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a tool through Chivalry Gate.

        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments

        Returns:
            Tool execution result
        """
        tool = self.tools.get(tool_name)
        if not tool:
            print(f"⚠️ [{self.name}] Tool '{tool_name}' not equipped.")
            return None

        # Chivalry Gate Authorization
        authorized = await self._authorize(tool, args)
        if not authorized:
            print(f"🛡️ [{self.name}] Execution BLOCKED by Chivalry Gate.")
            return None

        # Execute
        try:
            if asyncio.iscoroutinefunction(tool.func):
                result = await tool.func(**args)
            else:
                result = tool.func(**args)
            return result
        except Exception as e:
            print(f"⚠️ [{self.name}] Tool execution error: {e}")
            return None

    async def _authorize(self, tool: ToolDefinition, args: Dict[str, Any]) -> bool:
        """
        Internal authorization check via Chivalry Gate.

        Args:
            tool: Tool definition
            args: Tool arguments

        Returns:
            True if authorized, False otherwise
        """
        print(f"\n🛡️  [GATE] Intercepting: {tool.name} from {self.name}")

        if tool.level == SecurityLevel.RED:
            print(f"    🚨 [GATE] BLOCKED: {tool.name} is RED-flagged")
            return False

        if tool.level == SecurityLevel.BLUE:
            if not self.auditor:
                print("    ⚠️  [GATE] No auditor assigned. Defaulting to REJECT.")
                return False

            print(f"    ⚖️  [AUDIT] Requesting review from {self.auditor.name}...")
            approved = await self.auditor.review_action(self.name, tool.name, args)

            # Log deployment decisions
            if "deploy" in tool.name.lower():
                try:
                    from kernel.Data_Pipeline.storage import Ledger

                    status = "APPROVED" if approved else "REJECTED"
                    Ledger.record_deployment(args.get("version", "unknown"), status, self.auditor.name)
                except ImportError:
                    pass

            return approved

        # GREEN = Auto-approved
        return True

    # -------------------------------------------------------------------------
    # REPRESENTATION
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.name}' role='{self.role}' "
            f"vox_id='{self.voice_id}' texture='{self.sonic_texture}'>"
        )


# ==============================================================================
# MODULE EXPORTS
# ==============================================================================
__all__ = [
    "SecurityLevel",
    "ToolDefinition",
    "VoxCore",
    "VoxCoreError",
    "VoxCoreFactory",
    "UniversalKnight",
]