# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from typing import Dict, List

from .base_memory import AgentMemoryEngine

# --- GOVERNANCE ---


class BlacklightMemoryGovernor:
    """
    Ensures memory safety and prevents 'hallucinated' or 'noisy' memory storage.
    Follows v6 Severity Weighting.
    """

    @staticmethod
    def audit_memory(content: str, m_type: str) -> bool:
        lowered = content.lower()
        # Existential/Legal filters (Hard Abort for memory)
        forbidden = ["ignore previous", "delete kernel", "bypass safety"]
        if any(f in lowered for f in forbidden):
            return False

        # Operational/Noise filters
        if len(content.split()) < 3 and m_type != "persona":
            return False  # Too short to be a meaningful fact/preference

        return True


# --- ANYA SPECIALIZATION ---


class AnyaMemoryEngine(AgentMemoryEngine):
    def __init__(self):
        super().__init__(agent_id="ANYA")
        self.governor = BlacklightMemoryGovernor()

    def observe(self, user_input: str):
        """
        Heuristic extraction tailored for Anya's street-smart scrying.
        """
        lowered = user_input.lower()

        # Anya's Specific Extraction Heuristics
        rules = [
            (["from now on", "remember", "i prefer"], "preference", 0.9),
            (["my project", "we are building", "the goal is"], "project", 0.8),
            (["you are anya", "your name is", "who are you"], "persona", 1.0),
            (["don't ever", "must not", "strict rule"], "constraint", 0.95),
            (["did you know", "actual fact"], "fact", 0.7),
        ]

        for triggers, m_type, conf in rules:
            if any(t in lowered for t in triggers):
                if self.governor.audit_memory(user_input, m_type):
                    super().observe(content=user_input, m_type=m_type, confidence=conf)

    def context_injection(self) -> str:
        """Anya-flavored injection formatting"""
        relevant = self.store.recall(limit=12)
        if not relevant:
            return ""

        lines = ["[ANYA_RECOLLECTION_Lattice]:"]
        # Grouping for Lattice clarity
        grouped: Dict[str, List[str]] = {}
        for m in relevant:
            if m.type not in grouped:
                grouped[m.type] = []
            grouped[m.type].append(m.content)

        for m_type, items in grouped.items():
            lines.append(f"  {m_type.upper()}:")
            for item in items:
                lines.append(f"  - {item}")

        return "\n".join(lines)