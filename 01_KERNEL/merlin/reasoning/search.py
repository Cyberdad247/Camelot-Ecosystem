# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from typing import List, Optional

from pydantic import BaseModel


class ReasoningStep(BaseModel):
    """
    A single step in the Chain of Thought.
    """

    step_id: int
    thought: str
    is_valid: bool = True
    critique: Optional[str] = None

    def __str__(self):
        status = "✅" if self.is_valid else "❌"
        return f"{status} [Step {self.step_id}] {self.thought}"


class DepthFirstSearch:
    """
    A simple reasoning structure.
    It doesn't actually search a tree in this v1 implementation,
    but it structures the sequential thinking process.
    """

    def __init__(self, depth: int = 3):
        self.depth = depth
        self.trace: List[ReasoningStep] = []

    def add_step(self, thought: str, is_valid: bool = True, critique: str = None):
        step = ReasoningStep(step_id=len(self.trace) + 1, thought=thought, is_valid=is_valid, critique=critique)
        self.trace.append(step)

    def get_trace(self) -> str:
        return "\n".join([str(s) for s in self.trace])