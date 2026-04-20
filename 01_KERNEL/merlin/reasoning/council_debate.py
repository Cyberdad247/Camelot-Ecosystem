# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os
from typing import Dict, Optional, Protocol, runtime_checkable

from agora.context import SovereignContext


@runtime_checkable
class LLMBackend(Protocol):
    """Protocol for any LLM backend that council_debate can use."""
    async def process_request(self, prompt: str) -> str: ...


class _LocalFallback:
    """Zero-cost local fallback when no LLM is available.
    Generates structured perspectives from peer config alone."""

    async def process_request(self, prompt: str) -> str:
        if "flaw" in prompt.lower() or "compromise" in prompt.lower():
            return "[LOCAL] Acknowledged. No external reasoning available — deferring to Sovereign."
        if "synthesize" in prompt.lower() or "resolution" in prompt.lower():
            return "[LOCAL] Resolution requires LLM adjudication. Presenting raw debate for Sovereign review."
        return f"[LOCAL] Perspective registered. Bias-driven heuristic applied."


# Resolve config path relative to this file, not cwd
_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
_PEERS_PATH = os.path.join(_CONFIG_DIR, "council_peers.json")


class CouncilDebate:
    """
    THE COUNCIL OF PEERS: Simulated Debate Engine
    Fuses multi-perspective reasoning with pluralistic critique for deeper analysis.
    Operates with or without an LLM backend (graceful degradation).
    """

    def __init__(self, merlin: Optional[LLMBackend] = None):
        self.merlin = merlin if merlin and isinstance(merlin, LLMBackend) else _LocalFallback()
        self.peers_data = self._load_peers()

    def _load_peers(self):
        try:
            with open(_PEERS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)["peers"]
        except FileNotFoundError:
            return [
                {"id": "FALLBACK_ARCH", "name": "The Architect", "persona": "Clean code purist", "bias": "Maintenance over Speed", "capabilities": []},
                {"id": "FALLBACK_OPT", "name": "The Optimizer", "persona": "Performance maximizer", "bias": "Performance over Features", "capabilities": []},
                {"id": "FALLBACK_SEC", "name": "The Justicar", "persona": "Security enforcer", "bias": "Security over Functionality", "capabilities": []},
                {"id": "FALLBACK_UX", "name": "The User Voice", "persona": "UX advocate", "bias": "Usability over Purity", "capabilities": []},
            ]

    async def facilitate_debate(self, sovereign_intent: str, context: SovereignContext) -> str:
        """
        Moderates a 3-turn debate between council peers.
        Turn 1: Statements of Priority
        Turn 2: Rebuttal / Cross-Pollination
        Turn 3: Resolution & Kinetic Hand-off
        """
        print(f"\u2693 [COUNCIL] Summoning the Peers for intent: '{sovereign_intent}'")

        # Turn 1: Perspectives
        perspectives = []
        for peer in self.peers_data:
            perspective = await self._get_peer_opinion(peer, sovereign_intent, context)
            perspectives.append(f"**{peer['name']}**: {perspective}")
            print(f"  - {peer['name']} has spoken.")

        # Turn 2: Rebuttal (Peers see each other's opinions)
        rebuttals = []
        combined_perspectives = "\n".join(perspectives)
        for peer in self.peers_data:
            rebuttal = await self._get_peer_rebuttal(peer, combined_perspectives, context)
            rebuttals.append(f"**{peer['name']} (Counter)**: {rebuttal}")
            print(f"  - {peer['name']} has rebutted.")

        # Turn 3: Resolution (Merlin compiles)
        resolution_prompt = (
            f"[DEBATE MODERATION]\n"
            f"SOVEREIGN INTENT: {sovereign_intent}\n\n"
            f"OPENING PERSPECTIVES:\n{combined_perspectives}\n\n"
            f"REBUTTALS:\n{' '.join(rebuttals)}\n\n"
            f"[TASK] Synthesize into a single RESOLUTION. "
            f"Include a KINETIC PAYLOAD starting with 'Omega_OPEN:' if a physical change is required."
        )

        final_decision = await self.merlin.process_request(resolution_prompt)
        return self._format_output(combined_perspectives, rebuttals, final_decision)

    async def _get_peer_opinion(self, peer: Dict, intent: str, context: SovereignContext) -> str:
        tension = context.world_state.get("global_tension", 0.5)
        prompt = (
            f"As {peer['name']}, with bias toward {peer['bias']}. "
            f"Persona: {peer['persona']}. "
            f"What is your stance on: '{intent}'? World State: Tension {tension}"
        )
        return await self.merlin.process_request(prompt)

    async def _get_peer_rebuttal(self, peer: Dict, other_perspectives: str, context: SovereignContext) -> str:
        prompt = (
            f"As {peer['name']}, identify one flaw in the other perspectives "
            f"and suggest a compromise. Perspectives:\n{other_perspectives}"
        )
        return await self.merlin.process_request(prompt)

    def _format_output(self, perspectives: str, rebuttals: list, decision: str) -> str:
        rebuttal_block = "\n".join(rebuttals)
        return (
            f"# THE COUNCIL OF PEERS: DEBATE RESOLUTION\n\n"
            f"## THE DIALOGUE\n{perspectives}\n\n"
            f"## THE CROSS-POLLINATION\n{rebuttal_block}\n\n"
            f"## THE SOVEREIGN RESOLUTION\n{decision}"
        )