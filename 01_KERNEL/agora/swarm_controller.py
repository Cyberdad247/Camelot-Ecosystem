# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import asyncio
import json
from typing import Any, Dict, List

import httpx


class SwarmController:
    """
    CAMELOT_OS Swarm Controller (Phase 5)
    Bridges Merlin_Ω (L3) to the Hivemind Orchestrator (L5/Go).
    """

    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def check_health(self) -> bool:
        """Verify Hivemind is alive."""
        try:
            resp = await self.client.get(f"{self.base_url}/health")
            return resp.text == "HIVEMIND_ONLINE"
        except Exception:
            return False

    async def execute_crusade(self, objective: str, phases: List[str] = ["build", "audit", "lint"]) -> Dict[str, Any]:
        """
        Broadcast an objective to the Swarm for parallel execution.
        """
        print(f"⚔️  [SWARM] Broadcasting Objective: {objective}")
        print(f"📡 [SWARM] Activating Phases: {', '.join(phases)}")

        payload = {"objective": objective, "phases": phases}

        try:
            resp = await self.client.post(f"{self.base_url}/dispatch", json=payload)
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ [SWARM] Crusade Complete ({result['total_ms']}ms)")
                return result
            else:
                return {"status": "ERROR", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def close(self):
        await self.client.aclose()


# Singleton for system-wide access
swarm = SwarmController()


async def test_swarm():
    """Diagnostic check for Phase 5 ignition."""
    is_alive = await swarm.check_health()
    if is_alive:
        print("🟢 HIVEMIND: ONLINE")
        result = await swarm.execute_crusade("Build a secure Rotel CPU monitor")
        print(json.dumps(result, indent=2))
    else:
        print("🔴 HIVEMIND: OFFLINE (Run hivemind.exe first)")


if __name__ == "__main__":
    asyncio.run(test_swarm())