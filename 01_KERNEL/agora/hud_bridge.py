# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
from datetime import datetime

import httpx

from .node import AgentNode
from .protocol import ANPEnvelope


class HUDNode(AgentNode):
    """
    HUD Node: The Visual Cortex Bridge.
    Listens for 'Telemetry' broadcasts and forwards them to the OMEGA HUD backend.
    """

    def __init__(self):
        super().__init__("HUD_BRIDGE")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:3001")
        self.session_id = os.getenv("SESSION_ID", "OMEGA_SESSION_INIT")

    async def receive(self, envelope: ANPEnvelope) -> None:
        """
        Filter for Telemetry messages.
        """
        if envelope.protocol == "Telemetry":
            await self._forward_to_hud(envelope.payload)

    async def _forward_to_hud(self, payload: dict):
        """Bridge Agora -> HTTP HUD."""
        try:
            # Ensure timestamp and session info
            if "timestamp" not in payload:
                payload["timestamp"] = datetime.utcnow().isoformat()
            if "session_id" not in payload:
                payload["session_id"] = self.session_id

            async with httpx.AsyncClient() as client:
                await client.post(f"{self.backend_url}/api/hud/update/{self.session_id}", json=payload)
        except Exception:
            # Silent fail for the bridge if backend is down
            pass