# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Root path additions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from security.iron_gate import iron_gate
from security.vault_keeper import keeper


class KillswitchController:
    """
    OMEGA_KILLSWITCH Protocol (Phase 51.5)
    The absolute safety mechanism for Camelot OS.
    Requires 2-Way Authentication:
    1. Mobile (Iron Gate Biometric Signature)
    2. Password (Vault-verified)
    """

    def __init__(self, titan_server=None):
        self.titan_server = titan_server
        self.is_active = False

    async def initiate_killswitch(self, password: str) -> Dict[str, Any]:
        """
        Triggers the 2-Way Authentication flow for OS shutdown.
        """
        print("[KILLSWITCH] (WARN) Emergency Shutdown Protocol Initiated.")

        # 1. Gate One: Password Verification
        # We check against the SOVEREIGN_PASSWORD stored in the vault
        stored_pass = keeper.get_secret("SOVEREIGN_PASSWORD")
        if not stored_pass:
            # If no password is set, we fallback to a strict fail-safe
            print("[KILLSWITCH] (FAIL) No Sovereign Password found in Vault.")
            return {"status": "FAILED", "reason": "UNSET_CREDENTIALS"}

        if password != stored_pass:
            print("[KILLSWITCH] (FAIL) Invalid Sovereign Password.")
            return {"status": "FAILED", "reason": "AUTH_FAILURE"}

        # 2. Gate Two: Mobile Approval (Iron Gate)
        print("[KILLSWITCH] (GATE) Requesting Mobile Biometric Signature...")
        action_id = iron_gate.request_approval(
            {
                "summary": "SYSTEM_KILLSWITCH: Immediate Swarm & Kernel Termination",
                "riskLevel": "CRITICAL",
                "agent": "OmegaWarden",
                "ttlSeconds": 120,
            }
        )

        return {
            "status": "PENDING_MOBILE",
            "actionId": action_id,
            "summary": "Password accepted. Awaiting secondary mobile biometric signature.",
        }

    async def execute_shutdown(self):
        """
        Performs the actual shutdown sequence.
        """
        print("[KILLSWITCH] (CRITICAL) SHUTDOWN SEQUENCE ENGAGED.")

        # Notify all connected swarm members
        if self.titan_server:
            await self.titan_server.broadcast(
                "emergency_shutdown", {"reason": "KILLSWITCH_ACTIVATED", "timestamp": datetime.now().isoformat()}
            )
            await asyncio.sleep(1)  # Allow broadcast to propagate

        print("[KILLSWITCH] (BYE) Camelot OS going dark.")
        # In a real environment, this might exit the process or trigger a system-level command
        os._exit(0)


# Singleton
killswitch = KillswitchController()