#!/usr/bin/env python
"""
Distance Travel Simple Test — Core functionality verification (no external deps).

Tests:
  1. Agent registry
  2. Consensus layer
  3. Gateway coordination
  4. Network orchestration

Usage:
    python test_distance_travel_simple.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class SimpleDistanceTravelTest:
    """Simplified distance travel test (no Redis/Qdrant required)."""

    def __init__(self):
        self.results = {}

    async def run_all_tests(self) -> dict:
        """Run all tests."""
        print("╔════════════════════════════════════════════╗")
        print("║  Distance Travel Core Functionality Test   ║")
        print("╚════════════════════════════════════════════╝\n")

        tests = [
            ("Agent Registry", self.test_agent_registry),
            ("Agent Capabilities", self.test_agent_capabilities),
            ("Consensus Selection", self.test_consensus_selection),
            ("Gateway Mapping", self.test_gateway_mapping),
            ("Network Orchestration", self.test_network_orchestration),
        ]

        for test_name, test_fn in tests:
            try:
                result = await test_fn()
                status = "✓" if result else "✗"
                self.results[test_name] = result
                print(f"{status} {test_name}")
            except Exception as e:
                print(f"✗ {test_name}: {str(e)[:100]}")
                self.results[test_name] = False

        # Summary
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        print(f"\n{'='*44}")
        print(f"Result: {passed}/{total} tests passed")
        print(f"{'='*44}\n")

        if passed == total:
            print("✓ Distance Travel system core is operational")
            print("  (Redis/Qdrant not required for core logic)")
        return self.results

    async def test_agent_registry(self) -> bool:
        """Verify agent registry and definitions."""
        try:
            from control_plane.agent_registry import (
                get_agent_registry,
                get_agent,
                list_agents,
            )

            registry = get_agent_registry()
            agents = list_agents()

            # Test: Exact 5 agents
            if len(agents) != 5:
                print(f"  ERROR: Expected 5 agents, got {len(agents)}")
                return False

            # Test: All agents have required fields
            expected_ids = ["hermes", "openclaw", "nanobot", "zeroclaw", "rustclaw"]
            actual_ids = [a.agent_id for a in agents]

            if set(expected_ids) != set(actual_ids):
                print(f"  ERROR: Agent mismatch")
                return False

            # Print summary
            print(f"  Registered agents: {len(agents)}")
            for agent in agents:
                print(
                    f"    - {agent.agent_id:15} port={agent.port:5} "
                    f"capabilities={len(agent.capabilities)}"
                )

            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_agent_capabilities(self) -> bool:
        """Verify agent capabilities mapping."""
        try:
            from control_plane.agent_registry import get_agent_registry

            registry = get_agent_registry()

            # Test: Each agent has at least 4 capabilities
            for agent in registry.list_agents():
                if len(agent.capabilities) < 4:
                    print(f"  ERROR: {agent.agent_id} has only {len(agent.capabilities)} capabilities")
                    return False

            # Test: Get agents by capability
            reasoning_agents = registry.get_agents_with_capability("reasoning")
            if len(reasoning_agents) == 0:
                print("  ERROR: No agents with 'reasoning' capability")
                return False

            security_agents = registry.get_agents_with_capability("security")
            if len(security_agents) == 0:
                print("  ERROR: No agents with 'security' capability")
                return False

            print(f"  Reasoning agents: {[a.agent_id for a in reasoning_agents]}")
            print(f"  Security agents: {[a.agent_id for a in security_agents]}")

            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_consensus_selection(self) -> bool:
        """Verify consensus layer agent selection."""
        try:
            from control_plane.consensus_layer import get_consensus_layer

            consensus = get_consensus_layer()

            # Test: Select agent for capability
            selected_reasoning = await consensus.select_agent_for_capability("reasoning")
            if not selected_reasoning:
                print("  ERROR: Could not select agent for reasoning")
                return False

            selected_security = await consensus.select_agent_for_capability("security")
            if not selected_security:
                print("  ERROR: Could not select agent for security")
                return False

            selected_performance = await consensus.select_agent_for_capability("performance")
            if not selected_performance:
                print("  ERROR: Could not select agent for performance")
                return False

            print(f"  Reasoning → {selected_reasoning}")
            print(f"  Security → {selected_security}")
            print(f"  Performance → {selected_performance}")

            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_gateway_mapping(self) -> bool:
        """Verify agent-to-knight mapping."""
        try:
            # Test: Verify gateway mapping logic
            agent_to_knight_map = {
                "hermes": "sir_hermes",
                "openclaw": "sir_boris",
                "nanobot": "sir_ghost",
                "zeroclaw": "sir_sentinel",
                "rustclaw": "sir_ghost",
            }

            from control_plane.agent_registry import list_agents

            all_agents = [a.agent_id for a in list_agents()]

            # Verify mapping covers all agents
            for agent_id in all_agents:
                if agent_id not in agent_to_knight_map:
                    print(f"  ERROR: No knight mapping for {agent_id}")
                    return False

            print(f"  Agent-to-knight mappings: {len(agent_to_knight_map)}")
            for agent, knight in agent_to_knight_map.items():
                print(f"    {agent:15} → {knight}")

            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_network_orchestration(self) -> bool:
        """Verify distance travel orchestration logic."""
        try:
            from control_plane.distance_travel import get_distance_travel
            from control_plane.agent_registry import get_agent_registry

            # Initialize
            dt = get_distance_travel()
            registry = get_agent_registry()

            # Test: Verify all components initialized
            if not dt.gateway:
                print("  ERROR: Gateway not initialized")
                return False

            if not dt.consensus:
                print("  ERROR: Consensus layer not initialized")
                return False

            if not dt.memory_syncer:
                print("  ERROR: Memory syncer not initialized")
                return False

            if not dt.distributed_memory:
                print("  ERROR: Distributed memory not initialized")
                return False

            # Test: Verify agent registry accessible
            agents = registry.list_agents()
            if len(agents) != 5:
                print(f"  ERROR: Expected 5 agents, got {len(agents)}")
                return False

            print(f"  Distance Travel initialized:")
            print(f"    - Gateway: ✓")
            print(f"    - Consensus: ✓")
            print(f"    - Memory Syncer: ✓")
            print(f"    - Distributed Memory: ✓ (Redis optional)")
            print(f"    - Agent Registry: ✓ ({len(agents)} agents)")

            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False


async def main():
    """Run all tests."""
    tester = SimpleDistanceTravelTest()
    results = await tester.run_all_tests()

    # Exit code based on pass/fail
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
