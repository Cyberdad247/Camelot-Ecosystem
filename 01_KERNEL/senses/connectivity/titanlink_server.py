# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# TITAN LINK SERVER (v2.0)
# Handles WebSocket comms with Mobile Bridge

import json
import sys
import time

# Windows cp1252 can't print emoji — safe print wrapper
def _print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", errors="replace").decode("ascii", errors="replace"))


class TitanLinkServer:
    def send_challenge(self, action_type):
        """
        Sends an Iron Gate Biometric Challenge to the Mobile App.
        """
        payload = {
            "kind": "rustdesk_approval_request",
            "id": f"req_{int(time.time())}",
            "action": action_type,
            "severity": "HIGH",
            "timestamp": time.time(),
        }
        _print(f"[TITAN_LINK] Transmitting Challenge -> {json.dumps(payload)}")
        # In real impl, this pushes to the WS client
        return payload

    def broadcast_event(self, event):
        """Broadcasts an event to all connected clients.
        If it has a 'vocal_cue', it triggers Sir Sonus.
        """
        _print(f"[TITAN_LINK] Broadcast -> {event['type']}")
        if "vocal_cue" in event:
            _print(f"[SIR_SONUS] Queueing Speech -> '{event['vocal_cue']}'")
        return True