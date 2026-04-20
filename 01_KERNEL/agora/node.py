# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from abc import ABC, abstractmethod
from typing import Any

from .protocol import ANPEnvelope


class AgentNode(ABC):
    """
    Abstract Base Class for all entities connected to the Agora.
    Must implement receive() to handle incoming ANPEnvelopes.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    @abstractmethod
    async def receive(self, envelope: ANPEnvelope) -> None:
        """
        Handle an incoming message.
        Must be implemented by the specific Agent subclass (e.g. Merlin, Bard).
        """
        pass

    async def send(self, router, recipient: str, protocol: str, payload: Any) -> str:
        """
        Convenience wrapper to construct and emit an envelope.
        """
        envelope = ANPEnvelope(sender=self.agent_id, recipient=recipient, protocol=protocol, payload=payload)

        if recipient == "BROADCAST":
            await router.broadcast(envelope)
            return "ACK"

        return await router.route(envelope)