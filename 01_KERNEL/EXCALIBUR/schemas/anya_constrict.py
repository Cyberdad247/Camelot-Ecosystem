# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    KINETIC = "Kinetic"
    STRATEGY = "Strategy"


class ModelTier(str, Enum):
    HIGH = "High"
    MID = "Mid"
    TOOL = "Tool"


class InversionMode(str, Enum):
    SCAFFOLD = "Scaffold"
    SCULPT = "Sculpt"
    SCHEMA = "Schema"


class RiskLevel(str, Enum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Determinism(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    EXPLORATORY = "Exploratory"


class Anchors(BaseModel):
    concept: List[str] = Field(default_factory=list)
    constraint: List[str] = Field(default_factory=list)
    risk: List[str] = Field(default_factory=list)
    temporal: List[str] = Field(default_factory=list)


class Blacklight(BaseModel):
    money: RiskLevel = RiskLevel.NONE
    data: RiskLevel = RiskLevel.NONE
    rights: RiskLevel = RiskLevel.NONE
    hassle: RiskLevel = RiskLevel.NONE


class AnyaKGNode(BaseModel):
    """
    Representing the compiled state of a cognitive session in ANYA_v6.
    """

    q_focus: str = Field(..., description="The clarified intent stripped of noise.")
    task_type: TaskType
    model_tier: ModelTier = ModelTier.HIGH
    inversion: InversionMode = InversionMode.SCAFFOLD
    anchors: Anchors
    blacklight: Blacklight
    determinism: Determinism = Determinism.HIGH


class AnyaConstrict(BaseModel):
    """
    Root container for the ANYA Constrict DSL.
    """

    input_prompt: str
    compiled_glyph: Optional[AnyaKGNode] = None


# Example Usage:
# node = AnyaKGNode(
#     q_focus="Prevent unpaid consulting work",
#     task_type=TaskType.STRATEGY,
#     anchors=Anchors(concept=["Deliverables", "Payment Terms"], risk=["Scope Creep"]),
#     blacklight=Blacklight(money=RiskLevel.HIGH, rights=RiskLevel.MEDIUM)
# )