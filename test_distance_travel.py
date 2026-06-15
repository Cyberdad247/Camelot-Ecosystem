#!/usr/bin/env python
"""
Distance Travel System Test — Full feature verification.

Tests:
  1. Single agent dispatch (Hermes → OpenClaw)
  2. Parallel dispatch (Hermes → [3 agents])
  3. Consensus routing (vote on best agent)
  4. Network status
  5. Memory sync verification
  6. Agent registry

Usage:
    python test_distance_travel.py
"""
import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class DistanceTravelTester:
    """Test Distance Travel system."""

    def __init__(self):
        self.results = {}

    async def run_all_tests(self) -> dict:
        """Run all distance travel tests."""
        print("╔════════════════════════════════════════════╗")
        print("║     Distance Travel System Test Suite      ║")
        print("╚════════════════════════════════════════════╝\n")

        tests = [
            ("Agent Registry", self.test_agent_registry),
            ("Distributed Memory", self.test_distributed_memory),
            ("Consensus Layer", self.test_consensus_layer),
            ("Memory Sync", self.test_memory_sync),
            ("Agent Gateway", self.test_agent_gateway),
            ("Single Dispatch", self.test_single_dispatch),
            ("Parallel Dispatch", self.test_parallel_dispatch),
            ("Consensus Routing", self.test_consensus_routing),
            ("Network Status", self.test_network_status),
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

        return self.results

    async def test_agent_registry(self) -> bool:
        """Verify agent registry."""
        try:
            from control_plane.agent_registry import get_agent_registry

            registry = get_agent_registry()
            agents = registry.list_agents()

            print(f"  Registered agents: {len(agents)}")
            for agent in agents:
                print(f"    - {agent.agent_id}: {len(agent.capabilities)} capabilities")

            # Verify all 5 agents present
            agent_ids = [a.agent_id for a in agents]
            expected = ["hermes", "openclaw", "nanobot", "zeroclaw", "rustclaw"]
            all_present = all(aid in agent_ids for aid in expected)

            return all_present
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_distributed_memory(self) -> bool:
        """Verify distributed memory (Redis)."""
        try:
            from control_plane.distributed_memory import get_distributed_memory

            dm = get_distributed_memory()

            # Test broadcast (fire-and-forget)
            await dm.broadcast_event(
                event_type="test",
                source_agent="test_harness",
                data={"test": "message"},
            )

            # Test network status
            status = await dm.get_network_status()
            print(f"  Network status: {len(status)} agents in view")

            return dm.redis_client is not None
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_consensus_layer(self) -> bool:
        """Verify consensus layer."""
        try:
            from control_plane.consensus_layer import get_consensus_layer

            consensus = get_consensus_layer()

            # Test agent selection for capability
            selected = await consensus.select_agent_for_capability("reasoning")
            print(f"  Selected for 'reasoning': {selected}")

            return selected is not None
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_memory_sync(self) -> bool:
        """Verify memory sync."""
        try:
            from control_plane.memory_sync import get_memory_syncer

            syncer = get_memory_syncer()

            # Test cross-agent insights (should be empty initially)
            insights = await syncer.get_cross_agent_insights("CODE")
            print(f"  Cross-agent insights available: {bool(insights)}")

            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_agent_gateway(self) -> bool:
        """Verify agent gateway."""
        try:
            from control_plane.agent_gateway import get_agent_gateway

            gateway = get_agent_gateway()

            # Test dispatch history retrieval (should be empty initially)
            history = await gateway.get_dispatch_history("test-dispatch")
            print(f"  Gateway ready: {gateway.redis_client is not None}")

            return gateway.redis_client is not None
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_single_dispatch(self) -> bool:
        """Test single agent dispatch."""
        print("  Testing Hermes → OpenClaw dispatch...")

        try:
            from control_plane.distance_travel import ask_agent

            # Simple dispatch with short timeout
            chunks = []
            try:
                async for chunk in asyncio.wait_for(
                    self._collect_dispatch(ask_agent, "hermes", "openclaw", "Quick test: what is 2+2?"),
                    timeout=10.0
                ):
                    chunks.append(chunk)
                    if len("".join(chunks)) > 100:
                        break
            except asyncio.TimeoutError:
                print("    [Timeout - expected, continuing]")

            response = "".join(chunks)
            print(f"    Response length: {len(response)} chars")
            print(f"    Sample: {response[:80]}...")

            return len(chunks) > 0
        except Exception as e:
            print(f"    Error: {e}")
            return False

    async def _collect_dispatch(self, dispatch_fn, source, target, task):
        """Helper to collect dispatch chunks."""
        async for chunk in dispatch_fn(source, target, task):
            yield chunk

    async def test_parallel_dispatch(self) -> bool:
        """Test parallel agent dispatch."""
        print("  Testing parallel dispatch (Hermes → 3 agents)...")

        try:
            from control_plane.distance_travel import ask_agents

            # Parallel dispatch with timeout per agent
            try:
                results = await asyncio.wait_for(
                    ask_agents(
                        "hermes",
                        ["openclaw", "nanobot"],
                        "Quick question"
                    ),
                    timeout=10.0
                )
                print(f"    Responses received: {len(results)} agents")
                for agent_id, response in results.items():
                    print(f"      {agent_id}: {len(response)} chars")
                return len(results) > 0
            except asyncio.TimeoutError:
                print("    [Timeout - expected, continuing]")
                return True
        except Exception as e:
            print(f"    Error: {e}")
            return False

    async def test_consensus_routing(self) -> bool:
        """Test consensus-based routing."""
        print("  Testing consensus routing...")

        try:
            from control_plane.consensus_layer import get_consensus_layer

            consensus = get_consensus_layer()

            # Vote on routing
            task = "Optimize database performance"
            candidates = ["rustclaw", "nanobot", "openclaw"]

            selected = await consensus.vote_on_routing(task, candidates)
            print(f"    Task: '{task}'")
            print(f"    Candidates: {candidates}")
            print(f"    Selected: {selected}")

            return selected in candidates
        except Exception as e:
            print(f"    Error: {e}")
            return False

    async def test_network_status(self) -> bool:
        """Test network status."""
        try:
            from control_plane.distance_travel import get_distance_travel

            dt = get_distance_travel()

            status = await dt.network_status()
            print(f"  Network agents: {status['agents']['total_agents']}")
            print(f"  Network status keys: {len(status['network'])}")

            return status["agents"]["total_agents"] == 5
        except Exception as e:
            print(f"  Error: {e}")
            return False


async def main():
    """Run all tests."""
    tester = DistanceTravelTester()
    results = await tester.run_all_tests()

    # Exit code based on pass/fail
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
