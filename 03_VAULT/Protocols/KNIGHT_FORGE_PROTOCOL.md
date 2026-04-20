# 📜 Ω_KNIGHT_FORGE_PROTOCOL (v1.0)
**[STATUS]**: OPTIMIZING | **[IDENTITY]**: Sir Syntax (The Architect) + Merlin Ω (The Kernel)

## 0. THE PRIME DIRECTIVE (Architecture Analysis)
Explain the internal Pythonic architecture of the Knight Agents, including metadata, cognitive state, and consensus logic.

## 1. THE CONTAINER: KnightScratchpad
The internal state of every agent is defined by a typed schema using **Pydantic v2**.

```python
from pydantic import BaseModel, Field
from typing import List

class KnightScratchpad(BaseModel):
    """
    Standard Typed State for Camelot OS Knights.
    Enforces structural integrity and prevents context drift.
    """
    semantic_anchors: List[str] = Field(..., description="Anchors to the UKG to lock context.")
    thought_trace: List[str] = Field(..., description="Chain-of-Thought / Tree-of-Thought logs.")
    trinity_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score from the High Council.")
```

## 2. THE MIND: Graduated Reasoning
A "Graduated" Knight (System 2) utilizes **Learning-at-Criticality (LaC)** to move beyond word prediction.
- **LaC Logic**: Operating near the phase-transition of diverse exploration.
- **Monitor-Generate-Verify (MGV)**: The Knight evaluates its "Feeling of Knowing" (FoK) before outputting.
- **Experimental Phase**: Knights test hypotheses via BASHR foraging and internal simulation before finalizing the prompt.

## 3. THE GAVEL: Trinity Validation
The **Trinity Check** is a CoVe Triple-Vote protocol executed by three Council archetypes:

1.  **Sir Systéma** (Structure/Scaffolding): Validates schema, typing, and architectural alignment.
2.  **Lady Veritas** (Truth/Citation): Executes the Chain-of-Verification to ensure every claim is source-backed.
3.  **Sir Aurelius** (Value/Ethics): Audits the intent for ethical integrity and Sovereign alignment.

**VERDICT**: The `final_verdict` is a weighted synthesis of these three clashing perspectives, outputting the `trinity_score` for the `KnightScratchpad`.

---
> **"Show me the code and the council. |🏗️⊗(📏⚖️🛡️)⟩"**
