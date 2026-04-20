# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import time
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

# 🛡️ ANTIGRAVITY SAFETY CHECKS
# ALL MESSAGES MUST BE TYPED AND SIGNED


class ANPEnvelope(BaseModel):
    """
    ANP (Agent Network Protocol) Envelope.
    The standardized container for all Inter-Agent Communication within the Agora.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    recipient: str
    timestamp: float = Field(default_factory=time.time)

    # "HANDSHAKE", "QUERY", "TASK", "ACK", "ERROR"
    protocol: str

    payload: Dict[str, Any]
    signature: Optional[str] = None  # Hash(payload + sender_secret) for verification

    model_config = ConfigDict(frozen=True)  # Immutable messages


class ProtocolDocument(BaseModel):
    """
    Defines the capabilities and "Contract" of an Agent.
    """

    agent_id: str
    role: str  # e.g. "ARCHITECT", "FORGE"
    capabilities: list[str]
    ver: str = "1.0"
