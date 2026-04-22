# Made by Invisioned Marketing Inc. (c) 2024-2026 | ALL RIGHTS RESERVED
"""Sir Synthesis - The Neurosymbolic Architect v5.0.

Masters "Understandability, Credibility, and Deliverability" (UCD).
Bridges symbolic reasoning with neural outputs for architecture decisions.
Applies NDR+S (Neurosymbolic Deep Reasoning + Synthesis) protocol.
"""

import re
from .base import BaseKnight


class SirSynthesis(BaseKnight):
    name = "Sir Synthesis"
    title = "Neurosymbolic Architect"
    specialty = "UCD Framework & NDR+S Reasoning Protocol"
    icon = "[SYNTHESIS]"

    # Proteus MPI vectors (Soul Matrix) — full OCEAN
    MPI = {'openness': 1.0, 'conscientiousness': 0.9, 'extraversion': 0.65, 'agreeableness': 0.8, 'neuroticism': 0.05}

    # Personality & Prisms
    personality = "Philosophical, integrative, seeks the truth between symbolic logic and neural intuition."
    backstory = "An experiment in neurosymbolic architecture that succeeded in balancing deterministic rules with probabilistic learning."
    humanistic_prism = "AI is a partner to human cognition, amplifying human creativity rather than replacing it."
    alexandria_prism = "Bridging ancient logic systems (Aristotelian, Boolean) with modern gradient descent networks."
    version = "5.0"

    # UCD evaluation criteria
    UCD_DIMENSIONS = {
        "Understandability": [
            "Can a new engineer understand this in <15 minutes?",
            "Are abstractions named after domain concepts (not implementation)?",
            "Is the data flow traceable without reading every file?",
            "Does the README explain WHY, not just WHAT?",
        ],
        "Credibility": [
            "Is every external claim backed by a reference or test?",
            "Are edge cases documented, not hidden?",
            "Do error messages explain what went wrong AND how to fix it?",
            "Is there an audit trail for architectural decisions (ADRs)?",
        ],
        "Deliverability": [
            "Can this ship in the current sprint?",
            "Are dependencies available and stable (no alpha/RC in prod)?",
            "Is the deployment path clear (Dockerfile, CI, env vars)?",
            "Can this be rolled back in <5 minutes?",
        ],
    }

    # NDR+S reasoning stages
    NDRS_STAGES = [
        ("NEURAL", "Intuitive pattern recognition — what does this FEEL like?"),
        ("DECOMPOSE", "Break into atomic propositions — what are the FACTS?"),
        ("REASON", "Symbolic logic chain — what FOLLOWS from the facts?"),
        ("SYNTHESIZE", "Merge neural intuition + symbolic proof — what's the VERDICT?"),
    ]

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        text = directive.lower()

        # UCD evaluation
        if "ucd" in text or "evaluate" in text or "review" in text:
            return self._ucd_evaluation(directive, intent)

        # NDR+S reasoning
        if "reason" in text or "ndrs" in text or "think" in text or "analyze" in text:
            return self._ndrs_reasoning(directive, intent)

        # ADR generation
        if "adr" in text or "decision" in text or "record" in text:
            return self._generate_adr(directive, intent, write)

        lines = [
            "# Sir Synthesis — Neurosymbolic Architect v5.0",
            "",
            "## Core Framework: UCD (Understandability, Credibility, Deliverability)",
            "Every architecture decision is evaluated on three axes.",
            "A system that scores low on any axis is flagged for redesign.",
            "",
            "## Reasoning Protocol: NDR+S",
            "1. **NEURAL** — Pattern recognition (intuition)",
            "2. **DECOMPOSE** — Atomic propositions (facts)",
            "3. **REASON** — Symbolic logic chain (proof)",
            "4. **SYNTHESIZE** — Merge intuition + proof (verdict)",
            "",
            "## Available Actions",
            "- `evaluate <topic>` — Run UCD evaluation framework",
            "- `reason about <topic>` — Apply NDR+S reasoning protocol",
            "- `adr for <decision>` — Generate Architecture Decision Record",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _ucd_evaluation(self, directive: str, intent: dict) -> dict:
        topic = directive.replace("evaluate", "").replace("ucd", "").replace("review", "").strip()
        if not topic:
            topic = "Current Architecture"

        lines = [f"[SYNTHESIS] UCD Evaluation: {topic}", ""]

        for dimension, questions in self.UCD_DIMENSIONS.items():
            lines.append(f"### {dimension}")
            for q in questions:
                lines.append(f"- [ ] {q}")
            lines.append("")

        lines.extend([
            "### Scoring Guide",
            "- **3/3 dimensions pass**: Ship it.",
            "- **2/3 pass**: Fix the weak axis, then ship.",
            "- **1/3 or 0/3 pass**: Redesign required. Escalate to Sir Boris.",
        ])
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _ndrs_reasoning(self, directive: str, intent: dict) -> dict:
        topic = re.sub(r"(reason|ndrs|think|analyze|about)\s*", "", directive, flags=re.I).strip()
        if not topic:
            topic = "the given problem"

        lines = [f"[SYNTHESIS] NDR+S Reasoning: {topic}", ""]

        for stage, description in self.NDRS_STAGES:
            lines.append(f"### Stage: {stage}")
            lines.append(f"*{description}*")
            lines.append(f"- [ ] Apply {stage} lens to: {topic}")
            lines.append(f"- [ ] Document findings")
            lines.append("")

        lines.extend([
            "### Resolution",
            "- [ ] Do NEURAL and REASON agree? If yes → high confidence.",
            "- [ ] If they conflict → flag for Merlin_Omega escalation (GoT/DoT).",
            "- [ ] Record final synthesis in Provenance Ledger.",
        ])
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _generate_adr(self, directive: str, intent: dict, write: bool) -> dict:
        topic = re.sub(r"(adr|decision|record|for|generate|create)\s*", "", directive, flags=re.I).strip()
        if not topic:
            topic = "Untitled Decision"

        content = f"""# ADR: {topic.title()}

## Status
Proposed

## Context
<!-- What is the issue that we're seeing that is motivating this decision? -->

## Decision
<!-- What is the change that we're proposing and/or doing? -->

## Consequences

### Positive
- <!-- What becomes easier? -->

### Negative
- <!-- What becomes harder? -->

### Neutral
- <!-- What stays the same but is worth noting? -->

## UCD Assessment
- **Understandability**: [ ] Pass / [ ] Fail
- **Credibility**: [ ] Pass / [ ] Fail
- **Deliverability**: [ ] Pass / [ ] Fail
"""
        safe_name = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
        path = f"docs/adr/{safe_name}.md"

        output = f"[SYNTHESIS] Architecture Decision Record\n"
        output += f"Target: `{path}`\n\n```markdown\n{content}```\n"
        if not write:
            output += "\nAdd --write to create file on disk."
        return {"status": "success", "output": output, "files_created": [path] if write else []}
