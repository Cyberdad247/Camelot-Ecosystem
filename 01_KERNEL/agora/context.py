# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import time
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SovereignContext(BaseModel):
    """
    The Unified Execution Context for the Camelot Swarm.
    Assimilated from WilmerAI's 'ExecutionContext'.

    Carries the full intent, history, and variable state across the Agora Graph.
    """

    # IDENTITY
    session_id: str
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # STATE
    intent: str
    variables: Dict[str, Any] = Field(default_factory=dict)  # The "Variable Bus" e.g., {"agent#Output": "..."}

    # MEMORY
    message_history: List[Dict[str, str]] = Field(default_factory=list)  # [{"role": "user", "content": "..."}]

    # METADATA
    start_time: float = Field(default_factory=time.time)
    active_cartridge: Optional[str] = None

    # HYPERVISOR STATE (Oracle Protocol)
    world_state: Dict[str, Any] = Field(
        default_factory=lambda: {
            "epoch": 0,
            "global_tension": 0.5,
            "active_factions": [],
            "dead_actors": [],
            "resources": {},
        }
    )

    def set_var(self, key: str, value: Any):
        """Sets a variable in the global bus."""
        self.variables[key] = value

    def get_var(self, key: str, default: Any = None) -> Any:
        """Retrieves a variable, supporting resolution."""
        return self.variables.get(key, default)

    def add_message(self, role: str, content: str):
        """Appends to the conversation history."""
        self.message_history.append({"role": role, "content": content})