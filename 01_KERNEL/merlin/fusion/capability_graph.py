# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Agent Capability Graph (Node 5.1)

Maps agents and cartridges into a queryable capability lattice.
Used by the Merger Engine to identify the best agents for a specific goal.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AgentCapability(BaseModel):
    agent_id: str
    cartridge_id: str
    capabilities: List[str]
    risk_profile: str

class CapabilityGraph:
    """
    Management layer for discovering and indexing agent capabilities 
    from the Cartridge Matrix (CMX).
    """
    
    def __init__(self, packages_dir: str):
        self.packages_dir = os.path.abspath(packages_dir)
        self.capability_map: Dict[str, Set[str]] = {} # capability -> {agent_ids}
        self.agent_map: Dict[str, AgentCapability] = {} # agent_id -> capability_data
        
    def refresh(self):
        """Scans the packages directory and rebuilds the capability index."""
        self.capability_map.clear()
        self.agent_map.clear()
        
        if not os.path.exists(self.packages_dir):
            logger.warning(
                "[Cap-Graph] Packages directory %s not found.",
                self.packages_dir,
            )
            return

        for entry in os.scandir(self.packages_dir):
            if entry.is_dir():
                manifest_path = os.path.join(entry.path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)
                            self._index_manifest(manifest)
                    except Exception as e:
                        logger.warning(
                            "[Cap-Graph] Error indexing %s: %s",
                            manifest_path,
                            e,
                        )
        
        logger.info(
            "[Cap-Graph] Index rebuilt. Found %d agents across %d capabilities.",
            len(self.agent_map),
            len(self.capability_map),
        )

    def _index_manifest(self, manifest: Dict[str, Any]):
        """Internal helper to parse and index a manifest."""
        cart_id = manifest.get("cartridge_id")
        caps = manifest.get("capabilities", [])
        risk = manifest.get("risk_profile", "low")
        
        for agent_id in manifest.get("agents", []):
            self.agent_map[agent_id] = AgentCapability(
                agent_id=agent_id,
                cartridge_id=cart_id,
                capabilities=caps,
                risk_profile=risk
            )
            for cap in caps:
                if cap not in self.capability_map:
                    self.capability_map[cap] = set()
                self.capability_map[cap].add(agent_id)

    def find_agents_for_goal(self, required_caps: List[str]) -> List[str]:
        """Returns agents that match at least one of the required capabilities."""
        matches = set()
        for cap in required_caps:
            if cap in self.capability_map:
                matches.update(self.capability_map[cap])
        return list(matches)

    def get_agent_details(self, agent_id: str) -> Optional[AgentCapability]:
        """Retrieve full capability record for a specific agent."""
        return self.agent_map.get(agent_id)

if __name__ == "__main__":
    # Test Graph
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "02_FORGE", "cartridge", "packages")
    graph = CapabilityGraph(base_path)
    graph.refresh()
    
    # Test query
    engineers = graph.find_agents_for_goal(["backend", "systems_engineering"])
    print(f"Agents with 'backend' capability: {engineers}")
