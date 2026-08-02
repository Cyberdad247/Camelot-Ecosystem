# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
OMEGA_HYBRID_CONDUCTOR: Intelligent Browser Orchestration (v1.0)
Routes missions between Phantoms (Playwright) and Knights (Extension).
"""

import asyncio
import os
import sys
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from connectivity.titanlink_server import TitanLinkServer

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nano_forge.phantom_grid import PhantomGrid


class BrowserType(Enum):
    PHANTOM = "PHANTOM"  # Playwright (Scalable, Headless)
    KNIGHT = "KNIGHT"  # Extension (Stealth, Persistent)
    AUTO = "AUTO"  # Heuristic/LLM routing


class HybridConductor:
    """
    The Orchestrator that decides WHERE a mission should run.
    """

    def __init__(self, titan_server: Optional["TitanLinkServer"] = None):
        self.titan_server = titan_server
        self.grid = PhantomGrid()

    async def route_mission(
        self, qfocus: str, preference: BrowserType = BrowserType.AUTO, profile_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Main entry point for browser research.
        """
        target = preference
        if target == BrowserType.AUTO:
            target = self._evaluate_need(qfocus)

        print(f"[CONDUCTOR] (NAV) Routing Mission to {target.value}: {qfocus[:60]}...")

        if target == BrowserType.KNIGHT:
            return await self._dispatch_to_knight(qfocus, profile_id)
        else:
            return await self._dispatch_to_phantom(qfocus, profile_id)

    def evaluate_risk(self, qfocus: str, profile_id: str = "default") -> str:
        """
        Determines the risk level of a mission, considering both intent and profile.
        """
        # 1. Profile Risk Tier
        try:
            from nano_forge.profile_manager import ProfileManager

            mgr = ProfileManager()
            profile = mgr.load_profile(profile_id)
            tier = profile.get("risk_tier", "STANDARD")
        except Exception:
            tier = "STANDARD"

        if tier == "MAXIMUM":
            return "HIGH"  # All missions on Max Tiers are high risk

        lower = qfocus.lower()
        high_risk_triggers = [
            "login",
            "sign in",
            "password",
            "bank",
            "purchase",
            "social media",
            "twitter",
            "facebook",
            "linkedin",
            "personal",
            "private",
            "account",
            "secure",
        ]

        # Elevated tier has more broad triggers
        if tier == "ELEVATED":
            high_risk_triggers += ["order", "payment", "checkout", "address"]

        if any(trigger in lower for trigger in high_risk_triggers):
            return "HIGH"
        return "LOW"

    def _evaluate_need(self, qfocus: str) -> BrowserType:
        """
        Decision engine for routing.
        """
        lower = qfocus.lower()

        # 1. Stealth/Social/Security Triggers -> KNIGHT
        stealth_triggers = [
            "login",
            "sign in",
            "account",
            "bank",
            "password",
            "social media",
            "twitter",
            "facebook",
            "linkedin",
            "private",
            "secure",
            "bypass",
            "captcha",
        ]
        if any(trigger in lower for trigger in stealth_triggers):
            return BrowserType.KNIGHT

        # 2. Performance/Scalability Triggers -> PHANTOM
        bulk_triggers = [
            "scrape",
            "crawl",
            "bulk",
            "background",
            "batch",
            "mass extraction",
            "thousands",
            "hundreds",
            "rapid",
        ]
        if any(trigger in lower for trigger in bulk_triggers):
            return BrowserType.PHANTOM

        # 3. Default to Browser Extension (Knight) for high-fidelity research
        return BrowserType.KNIGHT

    async def _dispatch_to_knight(self, qfocus: str, profile_id: str) -> Dict[str, Any]:
        """Relays mission to the Extension via TitanLink."""
        if not self.titan_server:
            # Try to find a global instance or return fail
            return {"status": "ERROR", "msg": "TitanLink Server not attached to Conductor."}

        # Broadcast mission
        await self.titan_server.broadcast(
            "dispatch_mission", {"qfocus": qfocus, "profile_id": profile_id, "device": "DESKTOP"}
        )

        return {
            "status": "SUCCESS",
            "target": "KNIGHT",
            "summary": "Mission broadcast to the Swarm via TitanLink. Check extension console.",
        }

    async def _dispatch_to_phantom(self, qfocus: str, profile_id: str) -> Dict[str, Any]:
        """Starts a Playwright session via PhantomGrid."""
        print(f"[CONDUCTOR] Spawning Phantom Session for profile: {profile_id}")

        # In v1.0, we just trigger the session spawn.
        # In v1.1, we would pass the mission script to PhantomEngine.
        try:
            await self.grid.spawn_session(profile_id)
            return {
                "status": "SUCCESS",
                "target": "PHANTOM",
                "summary": f"Phantom session {profile_id} activated. Headless automation initiated.",
            }
        except Exception as e:
            return {"status": "ERROR", "msg": f"Phantom Spawn Failed: {str(e)}"}


if __name__ == "__main__":

    async def test():
        conductor = HybridConductor()

        print("\n[TEST 1] Testing AUTO Routing (Stealth)...")
        res1 = await conductor.route_mission("Login to Amazon and check last order.")
        print(f"Result: {res1['target']}")

        print("\n[TEST 2] Testing AUTO Routing (Bulk)...")
        res2 = await conductor.route_mission("Scrape all product titles from ebay.")
        print(f"Result: {res2['target']}")

        print("\n[TEST 3] Testing Manual Routing...")
        res3 = await conductor.route_mission("Find news", preference=BrowserType.PHANTOM)
        print(f"Result: {res3['target']}")

    asyncio.run(test())