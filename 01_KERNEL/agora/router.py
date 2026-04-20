# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from typing import List

from .node import AgentNode
from .protocol import ANPEnvelope


class AgoraRouter:
    """
    The Central Nervous System of the local swarm.
    Routes messages between registered AgentNodes in memory.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgoraRouter, cls).__new__(cls)
            cls._instance.registry = {}  # Dict[str, AgentNode]
            cls._instance.logs = []
        return cls._instance

    def register(self, agent: AgentNode):
        """Register an agent to the local bus."""
        if agent.agent_id in self.registry:
            print(f"! [AGORA] Agent {agent.agent_id} re-registered.")
        self.registry[agent.agent_id] = agent
        print(f"[OK] [AGORA] Registered Node: {agent.agent_id}")

    async def route(self, envelope: ANPEnvelope) -> str:
        """
        Route an envelope to its recipient.
        Returns "ACK" if successful, "ERR" if failed.
        """
        recipient_id = envelope.recipient

        # Log traffic (In-Memory for now, could be DB)
        self.logs.append(envelope)

        if recipient_id not in self.registry:
            print(f"❌ [AGORA] Delivery Failed. Unknown Recipient: {recipient_id}")
            return "ERR_UNKNOWN_RECIPIENT"

        target_node = self.registry[recipient_id]

        # Async delivery - Fire and Forget logic, or await processing?
        # Awaiting processing to ensure "Handshake" completes instantly for now.
        try:
            await target_node.receive(envelope)
            return "ACK"
        except Exception as e:
            print(f"🔥 [AGORA] Node Crashed handling message: {e}")
            return f"ERR_NODE_CRASH: {str(e)}"

    async def broadcast(self, envelope: ANPEnvelope) -> List[str]:
        """
        Send an envelope to ALL registered agents.
        Returns a list of status codes.
        """
        results = []
        # Log traffic
        self.logs.append(envelope)

        print(f"[AGORA] Broadcasting {envelope.protocol} from {envelope.sender}...")

        for agent_id, agent in self.registry.items():
            try:
                # We deliver to everyone, even the sender, unless we want to filter.
                # For Telemetry, it's fine.
                await agent.receive(envelope)
                results.append("ACK")
            except Exception as e:
                print(f"🔥 [AGORA] Broadcast delivery to {agent_id} failed: {e}")
                results.append(f"ERR_NODE_CRASH: {str(e)}")

        return results