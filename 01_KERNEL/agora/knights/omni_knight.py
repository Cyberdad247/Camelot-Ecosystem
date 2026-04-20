# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

from kernel.agora.node import AgentNode
from kernel.agora.protocol import ANPEnvelope


class OmniKnight(AgentNode):
    """
    THE OMNI-KNIGHT (Template Node)

    A polymorphic agent shell that reshapes its persona and capabilities
    based on the 'SovereignContext' it receives.

    It is not hardcoded. It hydrates its personality from the 'role'
    variable injected by Merlin/Videneptus at runtime.
    """

    def __init__(self, agent_id: str, default_role: str = "Standard Unit"):
        super().__init__(agent_id)
        self.default_role = default_role
        self.current_config = {}

    async def receive(self, envelope: ANPEnvelope) -> None:
        """
        Receives a task, hydrates persona from docs/KNIGHTS, and executes mission.
        """
        if envelope.protocol != "TASK_ASSIGNMENT":
            return

        payload = envelope.payload
        context_data = payload.get("context", {})

        # 1. HYDRATE PERSONA
        # Heuristic: Match agent_id to knights directory
        role_map = {
            "LANCELOT": "LANCELOT_ARCHITECT.md",
            "GALAHAD": "GALAHAD_CODER.md",
            "PERCIVAL": "PERCIVAL_AUDITOR.md",
            "TRISTAN": "TRISTAN_RESEARCHER.md",
            "MORDRED": "MORDRED_EXECUTOR.md",
        }

        spec_file = role_map.get(self.agent_id, "Standard_Knight.md")
        spec_path = f"docs/KNIGHTS/{spec_file}"

        # Simulation of loading the Markdown as the system prompt
        if os.path.exists(spec_path):
            with open(spec_path, "r", encoding="utf-8") as f:
                self.current_config["system_prompt"] = f.read()
                print(f"📖 [{self.agent_id}] Persona Hydrated from: {spec_path}")
        else:
            self.current_config["system_prompt"] = f"You are {self.agent_id}."

        # 2. EXECUTE MISSION
        intent = context_data.get("intent", "")
        print(f"⚔️ [{self.agent_id}] Order Received: '{intent[:50]}...'")

        # Simulation of LLM reasoning based on the prompt
        result = self._simulate_reasoning(intent)

        # 3. REPORT BACK
        print(f"✅ [{self.agent_id}] Mission Complete.")
        # In a full ANP implementation, we'd send an 'ORDER_COMPLETED' envelope back.

    def _simulate_reasoning(self, intent: str) -> str:
        """
        Simulates the 'Voice' of the knight based on its profile.
        """
        voices = {
            "LANCELOT": "By the SIT-Loop! I have validated the symmetry of this design.",
            "GALAHAD": "I have forged the code with type-safe precision. No 'any' shall pass.",
            "PERCIVAL": "Audit complete. No vulnerabilities detected in the Iron Vault.",
            "TRISTAN": "I have found the threads of knowledge in the Great Archive.",
            "MORDRED": "The target is purged. I await the next consequence.",
        }
        voice = voices.get(self.agent_id, "I obey the Sovereign.")
        print(f"💬 [{self.agent_id}] {voice}")
        return voice