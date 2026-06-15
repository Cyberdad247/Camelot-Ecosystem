# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from typing import List, Optional

from pydantic import BaseModel, Field


class ProteusVector(BaseModel):
    """
    Proteus MPI Vector: The Mathematical Soul of an Actor.
    Assimilated from the Omega_ORACLE_HYPERVISOR architecture.

    Instead of text descriptions ("He is brave"), we use R^n vectors
    to define personality, capability, and ethical orientation.
    """

    # CORE VECTORS (0.0 - 1.0)
    agency: float = Field(ge=0.0, le=1.0, default=0.5, description="Propensity to act without user input.")
    competence: float = Field(ge=0.0, le=1.0, default=0.5, description="Success probability of actions.")
    morality: float = Field(
        ge=0.3,
        le=1.0,
        default=0.7,  # HARD FLOOR: 0.3 (Titanium Law)
        description="Ethical orientation. Capped at >= 0.3 per Antigravity Chamber.",
    )
    aggression: float = Field(ge=0.0, le=1.0, default=0.3, description="Willingness to engage in conflict.")
    loyalty: float = Field(ge=0.0, le=1.0, default=0.5, description="Fidelity to the user/faction.")

    # GOAL STACK
    goal_stack: List[str] = Field(default_factory=list, description="Ordered list of objectives. [0] = Primary.")
    hidden_agenda: Optional[str] = Field(default=None, description="Secret objective unknown to user until revealed.")

    def utility_score(self, action_risk: float) -> float:
        """
        Calculate the 'Utility Score' for a given action risk level.
        Used by Tree of Thoughts to select the optimal path.
        """
        # High Agency + High Competence = Willing to take risky actions
        # High Morality = Less likely to take unethical actions
        return (self.agency * self.competence) - (action_risk * (1 - self.morality))

    def would_betray(self, opportunity_value: float) -> bool:
        """
        Determines if this actor would betray given an opportunity.
        Morality floor prevents truly 'evil' outcomes.
        """
        betrayal_threshold = (1 - self.morality) * (1 - self.loyalty)
        return opportunity_value > betrayal_threshold