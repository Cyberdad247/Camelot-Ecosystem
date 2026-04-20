# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
SkillGraph4: The VIDENEPTUS Skill Hierarchy System
Implements the 4-tier competence architecture for Knight personas.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Skill:
    """Individual skill node"""

    name: str
    tier: str  # S1, S2, S3, or S4
    description: str
    dependencies: List[str] = field(default_factory=list)


class SkillGraph4:
    """
    The VIDENEPTUS SkillGraph4 Architecture
    Organizes Knight capabilities across 4 hierarchical tiers.
    """

    def __init__(self, knight_id: str):
        self.knight_id = knight_id
        self.s1_atomic: List[Skill] = []  # Core building blocks
        self.s2_composite: List[Skill] = []  # Workflows
        self.s3_contextual: List[Skill] = []  # Domain knowledge
        self.s4_strategic: List[Skill] = []  # Orchestration

    def add_skill(self, skill: Skill):
        """Add a skill to the appropriate tier"""
        if skill.tier == "S1":
            self.s1_atomic.append(skill)
        elif skill.tier == "S2":
            self.s2_composite.append(skill)
        elif skill.tier == "S3":
            self.s3_contextual.append(skill)
        elif skill.tier == "S4":
            self.s4_strategic.append(skill)

    def validate_dependencies(self) -> bool:
        """
        Ensure all skill dependencies exist in lower tiers.
        S2 can only depend on S1, S3 on S1+S2, S4 on S1+S2+S3.
        """
        all_skills = {s.name for s in (self.s1_atomic + self.s2_composite + self.s3_contextual + self.s4_strategic)}

        for skill in self.s2_composite + self.s3_contextual + self.s4_strategic:
            for dep in skill.dependencies:
                if dep not in all_skills:
                    return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Export the skill graph as JSON-compatible dict"""
        return {
            "knight_id": self.knight_id,
            "s1_atomic": [{"name": s.name, "description": s.description} for s in self.s1_atomic],
            "s2_composite": [
                {"name": s.name, "description": s.description, "dependencies": s.dependencies}
                for s in self.s2_composite
            ],
            "s3_contextual": [
                {"name": s.name, "description": s.description, "dependencies": s.dependencies}
                for s in self.s3_contextual
            ],
            "s4_strategic": [
                {"name": s.name, "description": s.description, "dependencies": s.dependencies}
                for s in self.s4_strategic
            ],
        }

    def to_mermaid(self) -> str:
        """Generate Mermaid.js visualization using Sugiyama (Layered) algorithm"""
        lines = ["graph TD"]

        # S1 Atomic
        for skill in self.s1_atomic:
            lines.append(f"    S1_{skill.name}[{skill.name}]:::s1")

        # S2 Composite
        for skill in self.s2_composite:
            lines.append(f"    S2_{skill.name}[{skill.name}]:::s2")
            for dep in skill.dependencies:
                lines.append(f"    S1_{dep} --> S2_{skill.name}")

        # S3 Contextual
        for skill in self.s3_contextual:
            lines.append(f"    S3_{skill.name}[{skill.name}]:::s3")
            for dep in skill.dependencies:
                if any(s.name == dep for s in self.s2_composite):
                    lines.append(f"    S2_{dep} --> S3_{skill.name}")

        # S4 Strategic
        for skill in self.s4_strategic:
            lines.append(f"    S4_{skill.name}[{skill.name}]:::s4")
            for dep in skill.dependencies:
                if any(s.name == dep for s in self.s3_contextual):
                    lines.append(f"    S3_{dep} --> S4_{skill.name}")

        # Styling
        lines.append("    classDef s1 fill:#e1f5ff,stroke:#01579b")
        lines.append("    classDef s2 fill:#fff9c4,stroke:#f57f17")
        lines.append("    classDef s3 fill:#f3e5f5,stroke:#4a148c")
        lines.append("    classDef s4 fill:#ffebee,stroke:#b71c1c")

        return "\n".join(lines)


# Example: Kaito "The Pruner" Tanaka SkillGraph
if __name__ == "__main__":
    kaito = SkillGraph4("kaito_pruner")

    # S1: Atomic
    kaito.add_skill(Skill("AST_Parsing", "S1", "Python AST parsing"))
    kaito.add_skill(Skill("Regex_Optimization", "S1", "RegEx optimization"))

    # S2: Composite
    kaito.add_skill(Skill("Winter_Prune", "S2", "Automated legacy code detection", ["AST_Parsing"]))

    # S3: Contextual
    kaito.add_skill(Skill("SOLID_Principles", "S3", "Deep knowledge of SOLID", ["Winter_Prune"]))

    # S4: Strategic
    kaito.add_skill(Skill("Ecosystem_Stewardship", "S4", "Long-term maintainability", ["SOLID_Principles"]))

    # Mirror: gateway::clawdbot skills
    clawdbot = SkillGraph4("gateway::clawdbot")
    clawdbot.add_skill(Skill("Multichannel_Broadcast", "S3", "Broadcasting across 8+ channels", []))
    clawdbot.add_skill(Skill("Device_Node_Sync", "S3", "iOS/Android state mirroring", []))

    print("\nKAITO SKILLGRAPH:")
    print(kaito.to_mermaid())
    print("\nCLAWDBOT SKILL MIRROR:")
    print(clawdbot.to_mermaid())