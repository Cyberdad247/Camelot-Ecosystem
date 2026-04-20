# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Sentinel Compressor v1.0
Domain: L4 Semantic / Context Optimization
Guardian: Merlin_Ω / Chronos

Provides high-speed context distillation using local TINY models
to reduce token pressure on Frontier APIs (Gemini/GPT).
"""

import re

from .prism_gateway import PrismAdapter


class SentinelCompressor:
    """
    Implements Context Distillation and Anchor Tokenization.
    Reduces context window size by identifying high-entropy 'Anchor Tokens'.
    """

    ANCHOR_MAP = {
        "PROVENANCE_LEDGER": "Ω_LEDGER",
        "UNIVERSAL_KNOWLEDGE_GLYPH": "Ω_UKG",
        "KINETIC_SYNC_IGNITION": "Ψ_KINETIC",
        "SUCCESS": "✅",
        "FAILED": "❌",
        "RUNNING": "⏳",
        "OMEGA_ARCHITECT": "Ω_ARCH",
        "SYSTEM_MANIFEST": "Ω_DNA",
        "KNOWLEDGE_ARTIFACT": "Ω_MEM",
    }

    SYMBOLECT_MAP = {
        "INTENT_ANALYSIS": "[🔮Scry]",
        "REASONING_LOOP": "[🔥Burn]",
        "KINETIC_EXECUTION": "[⚡Strike]",
        "DATA_SYNCHRONIZATION": "[💾Sync]",
        "SECURITY_AUDIT": "[🛡️Audit]",
        "LATTICE_ALIGNMENT": "[🌐Align]",
        "ETHEREAL_RESONANCE": "[✨Pulse]",
        "AURORA_VISION": "[👁️Scene]",
    }

    # Inspired by Unsloth Dynamic Context & Context Distillation protocols

    @staticmethod
    def encode_anchors(text: str) -> str:
        """Replaced common sovereign strings with high-density Anchor Tokens."""
        for key, glyph in SentinelCompressor.ANCHOR_MAP.items():
            text = text.replace(key, glyph)
        return text

    @staticmethod
    def glyphify_dialogue(dialogue: str) -> str:
        """Compresses agent dialogue using Symbolect glyphs."""
        for key, glyph in SentinelCompressor.SYMBOLECT_MAP.items():
            dialogue = dialogue.replace(key, glyph)
        return dialogue

    @staticmethod
    async def distill(context: str, objective: str) -> str:
        """
        Uses a TINY local model (Llama 3.2 1B) to distill a large context
        into only the facts strictly necessary for the objective.
        """
        if not context or len(context) < 300:
            return context  # Too small to distill

        distill_prompt = f"""
        DISTILLATION MISSION:
        Context: {context}
        Objective: {objective}
        
        TASK: Extract ONLY the technical facts, variable values, and paths relevant to the objective.
        Format: Bullet points. No pleasantries. Max 150 words.
        """

        # Force redirection to TINY tier (Local Llama 3.2 1B)
        summary = await PrismAdapter.transmit(
            model="llama3.2:1b",
            prompt=distill_prompt,
            system_persona="High-speed context distiller. Fact extraction only.",
        )

        return summary if summary else context[:500]  # Fallback to head-truncation

    @staticmethod
    def tree_shake_prompt(system_prompt: str, task_complexity: str) -> str:
        """
        Removes non-essential sections of the system prompt (e.g., historical lore)
        if the task complexity is 'LOW'.
        """
        if task_complexity != "LOW":
            return system_prompt

        # Regex to remove sections marked with [LORE] or [EXTENDED_DEFS]
        # For now, we simple-strip the lore block if it exists
        clean_prompt = re.sub(r"# LORE.*?(?=\n#|\Z)", "", system_prompt, flags=re.DOTALL)
        return clean_prompt