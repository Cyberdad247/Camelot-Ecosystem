# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Omega_PHANTOM_GRID: Multi-Account Orchestration System
Clones Multi-Login capabilities within Camelot Sovereign OS.
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Local imports
# Local imports
try:
    from nano_forge.phantom_engine import PhantomEngine
    from nano_forge.profile_manager import ProfileManager
except ImportError:
    from phantom_engine import PhantomEngine
    from profile_manager import ProfileManager


class RiskTier(Enum):
    GREEN = "GREEN"  # View-only, no interactions
    BLUE = "BLUE"  # Light interaction
    RED = "RED"  # Login/transactions - requires approval


class SessionStatus(Enum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    ERROR = "ERROR"


@dataclass
class PhantomSession:
    """Represents an active AIONUI session for a profile."""

    profile_id: str
    status: SessionStatus = SessionStatus.IDLE
    proxy_config: Optional[Dict] = None
    context: Any = None  # Playwright BrowserContext
    pages: List[Any] = field(default_factory=list)
    fingerprint_score: float = 100.0
    last_activity: datetime = field(default_factory=datetime.now)


class PhantomGrid:
    """
    Omega_PHANTOM_GRID: Multi-Account Orchestration Controller
    Manages Nano-Knights across isolated browser sessions.
    """

    def __init__(self, hive_root: str = ".hive"):
        self.hive_root = Path(hive_root)
        self.profiles_path = self.hive_root / "profiles"
        self.profiles_path.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self.profile_manager = ProfileManager(str(self.profiles_path))
        self.phantom_engine = PhantomEngine(self.profile_manager)

        # Session registry
        self.sessions: Dict[str, PhantomSession] = {}

        # Proxy pool (from saltare config)
        self.proxy_pool: Dict[str, Dict] = {}
        self._load_proxy_pool()

        print("[OMEGA_PHANTOM_GRID] Grid initialized. Phantoms await.")

    def _load_proxy_pool(self):
        """Load proxy configurations from Saltare."""
        saltare_config = self.hive_root / "saltare_proxies.json"
        if saltare_config.exists():
            with open(saltare_config, "r") as f:
                self.proxy_pool = json.load(f)
        else:
            # Default empty pool
            self.proxy_pool = {}
            self._save_proxy_pool()

    def _save_proxy_pool(self):
        """Persist proxy pool configuration."""
        saltare_config = self.hive_root / "saltare_proxies.json"
        with open(saltare_config, "w") as f:
            json.dump(self.proxy_pool, f, indent=2)

    def add_proxy(self, proxy_id: str, config: Dict):
        """
        Add a proxy to the Saltare pool.
        Config: {server, username?, password?, profile_ids?: []}
        """
        self.proxy_pool[proxy_id] = config
        self._save_proxy_pool()
        print(f"[SALTARE] Proxy added: {proxy_id}")

    def assign_proxy_to_profile(self, profile_id: str, proxy_id: str):
        """Bind a static proxy to a profile for consistency."""
        if proxy_id not in self.proxy_pool:
            raise ValueError(f"Proxy {proxy_id} not found in pool")

        # Update proxy config to track assignment
        if "profile_ids" not in self.proxy_pool[proxy_id]:
            self.proxy_pool[proxy_id]["profile_ids"] = []

        if profile_id not in self.proxy_pool[proxy_id]["profile_ids"]:
            self.proxy_pool[proxy_id]["profile_ids"].append(profile_id)
            self._save_proxy_pool()

        print(f"[SALTARE] Profile {profile_id} -> Proxy {proxy_id}")

    def get_proxy_for_profile(self, profile_id: str) -> Optional[Dict]:
        """Retrieve the assigned proxy for a profile."""
        for _proxy_id, config in self.proxy_pool.items():
            if profile_id in config.get("profile_ids", []):
                return {
                    "server": config["server"],
                    "username": config.get("username"),
                    "password": config.get("password"),
                }
        return None

    async def spawn_session(
        self, profile_id: str, risk_tier: RiskTier = RiskTier.BLUE, headless: bool = True
    ) -> PhantomSession:
        """
        Spawn an AIONUI session for a profile.
        Law of Isolation: Each Knight runs in dedicated context.
        """
        if profile_id in self.sessions and self.sessions[profile_id].status == SessionStatus.ACTIVE:
            print(f"[AIONUI] Session already active: {profile_id}")
            return self.sessions[profile_id]

        print(f"[AIONUI] Spawning session: {profile_id} (Risk: {risk_tier.value})")

        # Get assigned proxy
        proxy = self.get_proxy_for_profile(profile_id)
        if proxy:
            print(f"[SALTARE] Routing through: {proxy['server']}")

        # Create session record
        session = PhantomSession(profile_id=profile_id, proxy_config=proxy, status=SessionStatus.ACTIVE)

        self.sessions[profile_id] = session
        return session

    async def launch_context(self, p, session: PhantomSession) -> Any:
        """Launch Playwright context for a session."""
        context = await self.phantom_engine.launch_context(
            p, profile_id=session.profile_id, headless=True, proxy=session.proxy_config
        )
        session.context = context
        return context

    async def freeze_session(self, profile_id: str):
        """
        Omega_SILENCE: Freeze session immediately.
        Triggered when fingerprint consistency drops < 97%.
        """
        if profile_id not in self.sessions:
            return

        session = self.sessions[profile_id]
        print(f"[Omega_SILENCE] Freezing session: {profile_id}")

        # Save state before closing
        if session.context:
            await self.phantom_engine.save_session(session.context, profile_id)
            await session.context.close()

        session.status = SessionStatus.FROZEN
        session.context = None

    async def resume_session(self, profile_id: str, p) -> PhantomSession:
        """Resume a frozen session with Omega_SYNC hydration."""
        session = await self.spawn_session(profile_id)
        await self.launch_context(p, session)
        print(f"[Omega_SYNC] Session hydrated: {profile_id}")
        return session

    def check_fingerprint_consistency(self, session: PhantomSession) -> float:
        """
        Verify fingerprint hasn't been corrupted.
        Returns score 0-100. Below 97 triggers kill switch.
        """
        # In production, compare runtime fingerprint with stored baseline
        # For now, return stored score
        return session.fingerprint_score

    def iron_gate_check(self, profile_id: str, domain: str, whitelist: List[str]) -> bool:
        """
        HITL Iron Gate security check.
        Returns True if domain is allowed, False triggers approval flow.
        """
        for allowed in whitelist:
            if domain.endswith(allowed) or domain == allowed:
                return True

        print(f"[IRON_GATE] ⚠️ Domain not whitelisted: {domain}")
        print(f"[IRON_GATE] Profile: {profile_id} requires BLUE approval")
        return False

    def list_sessions(self) -> Dict[str, Dict]:
        """List all sessions and their status."""
        return {
            pid: {
                "status": s.status.value,
                "proxy": s.proxy_config["server"] if s.proxy_config else None,
                "score": s.fingerprint_score,
                "last_activity": s.last_activity.isoformat(),
            }
            for pid, s in self.sessions.items()
        }


# === MCP PHONE BRIDGE ===
class MCPPhoneBridge:
    """
    MCP Tool wrapper for cloud phone providers.
    Used for 2FA code retrieval.
    """

    def __init__(self, provider: str = "twilio"):
        self.provider = provider
        self.api_key = os.environ.get(f"{provider.upper()}_API_KEY")

    async def get_code(self, phone_number: str, timeout: int = 60) -> Optional[str]:
        """
        Fetch 2FA code from cloud phone provider.
        In production, calls actual API via MCP.
        """
        print(f"[MCP_PHONE] Fetching code for: {phone_number}")
        # Simulated - in production uses mcp-cli
        await asyncio.sleep(1)
        return "123456"  # Mock code


if __name__ == "__main__":

    async def demo():
        # Initialize Grid
        grid = PhantomGrid()

        # Create test profile
        try:
            grid.profile_manager.create_profile("demo_phantom_01")
        except ValueError:
            print("[DEMO] Profile already exists")

        # Add proxy to pool
        grid.add_proxy(
            "us_residential_01", {"server": "http://proxy.example.com:8080", "username": "user", "password": "pass"}
        )

        # Assign proxy to profile
        grid.assign_proxy_to_profile("demo_phantom_01", "us_residential_01")

        # Spawn session
        await grid.spawn_session("demo_phantom_01", RiskTier.BLUE)

        # Check Iron Gate
        allowed = grid.iron_gate_check("demo_phantom_01", "facebook.com", ["google.com", "example.com"])
        print(f"[DEMO] Domain allowed: {allowed}")

        # List sessions
        print(f"[DEMO] Sessions: {json.dumps(grid.list_sessions(), indent=2)}")

    asyncio.run(demo())