"""
Phase G Week 2 Tests — Distributed Agent Network & Cross-Instance Routing

Tests for:
1. Distributed Agent Registry (cross-instance discovery)
2. Agent Health Checking (heartbeat timeout detection)
3. Agent Selection Strategies (least-loaded, geographically-closest)
4. Distributed Agent Router (consensus routing)

Status: 12 tests total
"""

import asyncio
import sys
import time
from control_plane.distributed_agent_registry import (
    DistributedAgentRegistry, DistributedAgentRouter, AgentInfo, AgentStatus,
    AgentScope
)


class Phase_G_Week2_TestSuite:
    """Week 2 tests for Phase G distributed agents"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    async def test_agent_registry_initialization(self):
        """Test: Agent registry initialization"""
        try:
            registry = DistributedAgentRegistry("node_1", ["node_2", "node_3"])

            assert registry.node_id == "node_1"
            assert len(registry.peers) == 2
            assert len(registry.all_nodes) == 3
            assert len(registry.local_agents) == 0
            assert len(registry.global_agents) == 0

            print("✅ test_agent_registry_initialization")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_agent_registry_initialization: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_register_local_agent(self):
        """Test: Register local agent"""
        try:
            registry = DistributedAgentRegistry("node_1", [])

            agent = registry.register_local_agent(
                "hermes_1",
                8401,
                "forge",
                {"dispatch", "execution"}
            )

            assert agent.agent_id == "hermes_1"
            assert agent.node_id == "node_1"
            assert agent.port == 8401
            assert agent.role == "forge"
            assert agent.status == AgentStatus.HEALTHY
            assert "dispatch" in agent.capabilities

            assert agent.agent_id in registry.local_agents
            assert agent.agent_id in registry.global_agents

            print("✅ test_register_local_agent")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_register_local_agent: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_discover_agents_local(self):
        """Test: Discover local agents"""
        try:
            registry = DistributedAgentRegistry("node_1", [])

            registry.register_local_agent("agent_1", 8401, "role_1", {"cap_1"})
            registry.register_local_agent("agent_2", 8402, "role_2", {"cap_2"})

            local_agents = await registry.discover_agents(AgentScope.LOCAL)
            assert len(local_agents) == 2

            print("✅ test_discover_agents_local")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_discover_agents_local: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_discover_agents_global(self):
        """Test: Discover global agents (multi-node)"""
        try:
            registry = DistributedAgentRegistry("node_1", ["node_2"])

            # Register on node 1
            registry.register_local_agent("agent_1", 8401, "forge", {"execution"})

            # Simulate agent on node 2
            agent_2 = AgentInfo(
                agent_id="agent_2",
                node_id="node_2",
                port=8401,
                role="coordinator",
                scope=AgentScope.GLOBAL,
                status=AgentStatus.HEALTHY,
                last_heartbeat=time.time(),
                capabilities={"routing"}
            )
            registry.global_agents["agent_2"] = agent_2

            global_agents = await registry.discover_agents(AgentScope.GLOBAL)
            assert len(global_agents) == 2

            print("✅ test_discover_agents_global")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_discover_agents_global: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_discover_agents_by_role(self):
        """Test: Discover agents by role"""
        try:
            registry = DistributedAgentRegistry("node_1", [])

            registry.register_local_agent("forge_1", 8401, "forge", {"execution"})
            registry.register_local_agent("forge_2", 8402, "forge", {"execution"})
            registry.register_local_agent("coordinator_1", 8403, "coordinator", {"routing"})

            forges = await registry.discover_agents_by_role("forge")
            assert len(forges) == 2

            coordinators = await registry.discover_agents_by_role("coordinator")
            assert len(coordinators) == 1

            print("✅ test_discover_agents_by_role")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_discover_agents_by_role: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_discover_agents_by_capability(self):
        """Test: Discover agents by capability"""
        try:
            registry = DistributedAgentRegistry("node_1", [])

            registry.register_local_agent("agent_1", 8401, "role_1", {"dispatch", "execution"})
            registry.register_local_agent("agent_2", 8402, "role_2", {"execution", "routing"})
            registry.register_local_agent("agent_3", 8403, "role_3", {"routing"})

            dispatch_agents = await registry.discover_agents_by_capability("dispatch")
            assert len(dispatch_agents) == 1

            execution_agents = await registry.discover_agents_by_capability("execution")
            assert len(execution_agents) == 2

            routing_agents = await registry.discover_agents_by_capability("routing")
            assert len(routing_agents) == 2

            print("✅ test_discover_agents_by_capability")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_discover_agents_by_capability: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_agent_health_checking(self):
        """Test: Agent health check (heartbeat timeout detection)"""
        try:
            registry = DistributedAgentRegistry("node_1", [])
            registry.heartbeat_timeout = 2  # 2 second timeout for test

            agent = registry.register_local_agent("agent_1", 8401, "role_1", {"cap"})

            # Initially healthy
            assert agent.status == AgentStatus.HEALTHY

            # Simulate time passing
            agent.last_heartbeat = time.time() - 3  # 3 seconds ago

            # Check health
            health = await registry.check_agent_health()
            assert health["agent_1"] == AgentStatus.DARK

            print("✅ test_agent_health_checking")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_agent_health_checking: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_select_least_loaded_agent(self):
        """Test: Select least-loaded agent"""
        try:
            registry = DistributedAgentRegistry("node_1", [])

            agent1 = registry.register_local_agent("agent_1", 8401, "forge", {"execution"})
            agent1.load = 0.8

            agent2 = registry.register_local_agent("agent_2", 8402, "forge", {"execution"})
            agent2.load = 0.2

            selected = await registry.select_least_loaded_agent("forge")
            assert selected.agent_id == "agent_2"

            print("✅ test_select_least_loaded_agent")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_select_least_loaded_agent: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_select_geographically_closest_agent(self):
        """Test: Select geographically closest agent"""
        try:
            registry = DistributedAgentRegistry("node_1", ["node_2", "node_3"])

            # Register on local node
            local_agent = registry.register_local_agent("forge_1", 8401, "forge", {"execution"})

            # Simulate agents on remote nodes
            remote_agent = AgentInfo(
                agent_id="forge_2",
                node_id="node_2",
                port=8401,
                role="forge",
                scope=AgentScope.GLOBAL,
                status=AgentStatus.HEALTHY,
                last_heartbeat=time.time(),
                capabilities={"execution"}
            )
            registry.global_agents["forge_2"] = remote_agent

            # Should select local agent first
            selected = await registry.select_geographically_closest_agent("forge")
            assert selected.node_id == "node_1"

            print("✅ test_select_geographically_closest_agent")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_select_geographically_closest_agent: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_agent_router_route_to_role(self):
        """Test: Route request to agent by role"""
        try:
            registry = DistributedAgentRegistry("node_1", [])
            registry.register_local_agent("forge_1", 8401, "forge", {"execution"})

            router = DistributedAgentRouter(registry)

            agent, result = await router.route_to_role("forge", {"operation": "test"})

            assert agent is not None
            assert agent.role == "forge"
            assert result['status'] == 'success'

            print("✅ test_agent_router_route_to_role")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_agent_router_route_to_role: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_agent_router_route_with_consensus(self):
        """Test: Route request with consensus across agents"""
        try:
            registry = DistributedAgentRegistry("node_1", [])
            registry.register_local_agent("forge_1", 8401, "forge", {"execution"})
            registry.register_local_agent("forge_2", 8402, "forge", {"execution"})

            router = DistributedAgentRouter(registry)

            agents, result = await router.route_with_consensus("forge", {"operation": "test"}, quorum=2)

            assert len(agents) == 2
            assert result.get('consensus') is not None
            assert result.get('agreement') == 2

            print("✅ test_agent_router_route_with_consensus")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_agent_router_route_with_consensus: {str(e)[:50]}")
            self.failed += 1
            return False

    async def test_registry_status(self):
        """Test: Get registry status"""
        try:
            registry = DistributedAgentRegistry("node_1", ["node_2"])
            registry.register_local_agent("agent_1", 8401, "forge", {"execution"})
            registry.register_local_agent("agent_2", 8402, "coordinator", {"routing"})

            status = await registry.get_registry_status()

            assert status['node_id'] == "node_1"
            assert status['local_agents'] == 2
            assert status['global_agents'] == 2
            assert status['healthy'] == 2
            assert 'forge' in status['agents_by_role']
            assert 'node_1' in status['agents_by_node']

            print("✅ test_registry_status")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ test_registry_status: {str(e)[:50]}")
            self.failed += 1
            return False

    async def run_all_tests(self):
        """Run complete Week 2 test suite"""
        print("\n" + "=" * 70)
        print("PHASE G WEEK 2: DISTRIBUTED AGENT NETWORK")
        print("=" * 70)

        tests = [
            self.test_agent_registry_initialization(),
            self.test_register_local_agent(),
            self.test_discover_agents_local(),
            self.test_discover_agents_global(),
            self.test_discover_agents_by_role(),
            self.test_discover_agents_by_capability(),
            self.test_agent_health_checking(),
            self.test_select_least_loaded_agent(),
            self.test_select_geographically_closest_agent(),
            self.test_agent_router_route_to_role(),
            self.test_agent_router_route_with_consensus(),
            self.test_registry_status(),
        ]

        results = await asyncio.gather(*tests)

        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Passed: {self.passed}/{self.passed + self.failed}")
        print(f"Failed: {self.failed}/{self.passed + self.failed}")

        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")

        print("\nModules Tested:")
        print("  ✅ distributed_agent_registry.py (agent discovery, routing)")

        return all(results)


async def main():
    """Run Week 2 tests"""
    suite = Phase_G_Week2_TestSuite()
    success = await suite.run_all_tests()
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
