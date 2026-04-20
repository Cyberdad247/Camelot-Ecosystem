# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import json
from typing import Any, Dict, Optional

import aiohttp
import websockets


class ClawdbotClient:
    """
    Clawdbot Gateway Bridge Client
    Connects Anya to multi-channel messaging (WhatsApp, Signal, etc.)
    """

    def __init__(self, ws_url: str = "ws://127.0.0.1:18789", http_url: str = "http://127.0.0.1:18789"):
        self.ws_url = ws_url
        self.http_url = http_url
        self.session: Optional[aiohttp.ClientSession] = None
        self._connected = False

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def send_message(self, text: str, channel: str = "webchat", recipient: str = "default") -> Dict[str, Any]:
        """
        Sends a message through a Clawdbot channel.
        """
        payload = {"kind": "send_message", "text": text, "channel": channel, "recipient": recipient}

        # Try HTTP POST first
        try:
            await self._ensure_session()
            async with self.session.post(f"{self.http_url}/api/message", json=payload) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print(f"[CLAWDBOT] HTTP send failed: {e}")

        # Fallback to WebSocket if needed or if preferred by protocol
        return {"status": "FAILED", "reason": "No connectivity to Gateway"}

    async def call_skill(self, skill_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invokes a Clawdbot Skill via RPC.
        """
        payload = {"kind": "call_skill", "skill": skill_name, "args": args}

        try:
            async with websockets.connect(self.ws_url) as ws:
                await ws.send(json.dumps(payload))
                response = await ws.recv()
                return json.loads(response)
        except Exception as e:
            print(f"[CLAWDBOT] WS skill call failed: {e}")
            return {"status": "ERROR", "message": str(e)}

    async def close(self):
        if self.session:
            await self.session.close()


# Global Client Instance
_clawdbot_client = ClawdbotClient()


async def get_clawdbot_client():
    return _clawdbot_client


def call_clawdbot_sync(text: str, channel: str = "webchat") -> Dict[str, Any]:
    """Synchronous wrapper for Aether integration."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we are inside an async context (like TitanLink), we should use the existing loop
            # This is tricky in a sync wrapper.
            return {"status": "DEFERRED", "msg": "Async context detected. Use async_call."}
        return loop.run_until_complete(_clawdbot_client.send_message(text, channel))
    except Exception:
        return {"status": "ERROR", "msg": "Sync bridge failure."}