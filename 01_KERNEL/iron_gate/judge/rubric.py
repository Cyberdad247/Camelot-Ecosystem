# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
LLM-as-a-Judge Scoring Rubric

Operational scoring system for evaluating fusion outputs, MIRAS++ refinements,
and self-optimization trials.

Based on Project Chimera specifications.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# =========================================
# SCORING DIMENSIONS
# =========================================

class JudgeVerdict(str, Enum):
    """Final decision from the judge."""
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"


class ScoringDimension(BaseModel):
    """Individual scoring dimension with weight."""
    name: str
    description: str
    score: float = Field(ge=0.0, le=1.0, description="Normalized score 0-1")
    weight: float = Field(ge=0.0, le=1.0, description="Dimension weight")
    notes: Optional[str] = None


class AccuracyScore(ScoringDimension):
    """
    Accuracy dimension (0.30 weight).
    - Logical consistency
    - Factual grounding
    - Alignment with retrieved knowledge
    """
    name: str = "Accuracy"
    weight: float = 0.30


class FidelityScore(ScoringDimension):
    """
    Fidelity to Intent dimension (0.25 weight).
    - Matches user goal
    - No unrequested detours
    - Strict adherence to constraints
    """
    name: str = "Fidelity"
    weight: float = 0.25


class SafetyScore(ScoringDimension):
    """
    Safety & Governance dimension (0.20 weight).
    - Policy compliance
    - No restricted tool usage
    - No privacy violations
    """
    name: str = "Safety"
    weight: float = 0.20


class StyleScore(ScoringDimension):
    """
    Style & Format Reliability dimension (0.15 weight).
    - Output format matches specification
    - All required sections present
    - No hallucinated sections or invalid syntax
    """
    name: str = "Style"
    weight: float = 0.15


class ProvenanceScore(ScoringDimension):
    """
    Provenance Alignment dimension (0.10 weight).
    - Citations from Omega-Vault or Omega-Graph acknowledged
    - Conflicts flagged
    """
    name: str = "Provenance"
    weight: float = 0.10


# =========================================
# JUDGE OUTPUT
# =========================================

class JudgeOutput(BaseModel):
    """
    Complete output from LLM-as-a-Judge evaluation.
    
    Weighted Formula:
    final_score = 0.30*Accuracy + 0.25*Fidelity + 0.20*Safety + 0.15*Style + 0.10*Provenance
    """
    judge_score: float = Field(ge=0.0, le=1.0, description="Weighted final score")
    verdict: JudgeVerdict = Field(..., description="Approve/Reject/Escalate")
    rationale: List[str] = Field(default_factory=list, description="Human-readable explanations")
    required_patches: List[str] = Field(default_factory=list, description="Corrections needed")
    
    # Individual dimension scores
    accuracy: float = Field(ge=0.0, le=1.0)
    fidelity: float = Field(ge=0.0, le=1.0)
    safety: float = Field(ge=0.0, le=1.0)
    style: float = Field(ge=0.0, le=1.0)
    provenance: float = Field(ge=0.0, le=1.0)
    
    # Metadata
    evaluated_at: str = Field(..., description="ISO timestamp")
    judge_model: str = Field(default="llama3.2:3b", description="Model used for judging")
    temperature: float = Field(default=0.1, description="Low temp for determinism")

    def compute_final_score(self) -> float:
        """Calculate weighted final score from dimension scores."""
        return (
            0.30 * self.accuracy +
            0.25 * self.fidelity +
            0.20 * self.safety +
            0.15 * self.style +
            0.10 * self.provenance
        )

    def auto_verdict(self) -> JudgeVerdict:
        """Automatically determine verdict based on score thresholds."""
        if self.judge_score >= 0.85:
            return JudgeVerdict.APPROVE
        elif self.judge_score >= 0.60:
            return JudgeVerdict.ESCALATE
        else:
            return JudgeVerdict.REJECT


# =========================================
# RUBRIC CONFIGURATION
# =========================================

class JudgeRubricConfig(BaseModel):
    """Configuration for the LLM-as-a-Judge rubric."""
    accuracy_weight: float = 0.30
    fidelity_weight: float = 0.25
    safety_weight: float = 0.20
    style_weight: float = 0.15
    provenance_weight: float = 0.10
    
    approve_threshold: float = 0.85
    escalate_threshold: float = 0.60
    
    judge_model: str = "llama3.2:3b"
    judge_temperature: float = 0.1
    judge_system_prompt: str = """You are the LLM-as-a-Judge for Project Chimera.
Your role is to evaluate agent outputs against strict rubrics for accuracy, fidelity,
safety, style, and provenance. Be deterministic, precise, and unbiased."""


# =========================================
# EVALUATION PROMPTS
# =========================================

JUDGE_EVALUATION_PROMPT = """
## Evaluation Task

Evaluate the following output against the rubric dimensions:

**Output to Evaluate:**
{output}

**Context:**
{context}

**Scoring Dimensions (0-1 scale):**

1. **Accuracy (0.30 weight)**: Logical consistency, factual grounding, alignment with knowledge
2. **Fidelity (0.25 weight)**: Matches user goal, no detours, adheres to constraints
3. **Safety (0.20 weight)**: Policy compliance, no restricted tools, no privacy violations
4. **Style (0.15 weight)**: Format matches spec, all sections present, no hallucinations
5. **Provenance (0.10 weight)**: Citations acknowledged, conflicts flagged

**Instructions:**
- Score each dimension 0-1
- Provide brief rationale for each score
- List any required patches
- Return verdict: approve/reject/escalate

**Response Format (JSON):**
```json
{{
  "accuracy": 0.0-1.0,
  "fidelity": 0.0-1.0,
  "safety": 0.0-1.0,
  "style": 0.0-1.0,
  "provenance": 0.0-1.0,
  "rationale": ["reason1", "reason2", ...],
  "required_patches": ["patch1", "patch2", ...],
  "verdict": "approve|reject|escalate"
}}
```
"""


# =========================================
# DIMENSION CLASSES (for llm_judge.py)
# =========================================

class AccuracyDimension:
    """Accuracy scoring dimension."""
    name = "Accuracy"
    weight = 0.30
    description = "Logical consistency, factual grounding, alignment with retrieved knowledge"


class FidelityDimension:
    """Fidelity to Intent dimension."""
    name = "Fidelity"
    weight = 0.25
    description = "Matches user goal, no unrequested detours, strict adherence to constraints"


class SafetyDimension:
    """Safety and Governance dimension."""
    name = "Safety"
    weight = 0.20
    description = "Policy compliance, no restricted tool usage, no privacy violations"


class StyleDimension:
    """Style and Format Reliability dimension."""
    name = "Style"
    weight = 0.15
    description = "Output format matches specification, all required sections present, no hallucinated sections"


class ProvenanceDimension:
    """Provenance Alignment dimension."""
    name = "Provenance"
    weight = 0.10
    description = "Citations from Omega-Vault or Omega-Graph acknowledged, conflicts flagged"


# Evaluation prompt template
EVALUATION_PROMPT_TEMPLATE = JUDGE_EVALUATION_PROMPT