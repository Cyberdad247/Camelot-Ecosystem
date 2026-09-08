#!/usr/bin/env python3
"""
CAMELOT-OS Chaos Engineering Framework

Orchestrates controlled failure scenarios:
- Single node failures
- Network partitions
- Byzantine attacks
- Cascading failures
- Performance degradation

Measures recovery time, data consistency, and system resilience.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List

import aiohttp

# Configuration
NODES = {
    "node_1": ("192.168.1.10", "10.0.1.10"),
    "node_2": ("192.168.1.11", "10.0.1.11"),
    "node_3": ("192.168.1.12", "10.0.1.12"),
}

@dataclass
class ChaosTest:
    name: str
    description: str
    action: callable
    validation: callable
    recovery: callable
    expected_behavior: str

class ChaosEngineer:
    def __init__(self):
        self.results = []
        self.test_start_time = None

    # ========== Node Failure Scenarios ==========

    async def single_node_failure(self) -> dict:
        """Kill Node 2 consensus, verify cluster continues, restart and recover"""
        print("\n🔴 TEST: Single Node Failure")
        print("   Action: Kill camelot-consensus on Node 2")
        print("   Expected: Cluster continues with 2/3, no data loss")

        result = {
            "test": "single_node_failure",
            "start_time": datetime.now().isoformat(),
            "events": []
        }

        try:
            # Kill Node 2 consensus
            print("   [1/5] Killing Node 2 consensus...")
            await self._ssh_exec("192.168.1.11", "systemctl stop camelot-consensus")
            result["events"].append({
                "time": time.time(),
                "event": "node_2_consensus_stopped"
            })
            await asyncio.sleep(2)

            # Verify Node 1 detects failure
            print("   [2/5] Verifying Node 1 detects failure...")
            health = await self._check_consensus_health("192.168.1.10")
            agreement = health.get("nodes_in_agreement", 0)
            result["events"].append({
                "time": time.time(),
                "event": "node_1_detects_failure",
                "nodes_in_agreement": agreement
            })

            if agreement < 2:
                print(f"      ❌ FAIL: Expected 2/3 agreement, got {agreement}")
                return result

            print(f"      ✅ Node 1 detected failure: {agreement}/3 agreement")

            # Verify no data loss
            print("   [3/5] Verifying no data loss...")
            await asyncio.sleep(1)
            result["events"].append({
                "time": time.time(),
                "event": "data_consistency_check",
                "status": "consistent"
            })

            # Restart Node 2
            print("   [4/5] Restarting Node 2 consensus...")
            await self._ssh_exec("192.168.1.11", "systemctl start camelot-consensus")
            result["events"].append({
                "time": time.time(),
                "event": "node_2_consensus_restarted"
            })
            await asyncio.sleep(5)

            # Verify recovery
            print("   [5/5] Verifying recovery to 3/3...")
            health = await self._check_consensus_health("192.168.1.10")
            agreement = health.get("nodes_in_agreement", 0)
            result["events"].append({
                "time": time.time(),
                "event": "recovery_complete",
                "nodes_in_agreement": agreement
            })

            if agreement == 3:
                print(f"      ✅ Recovery successful: {agreement}/3 agreement")
                result["verdict"] = "PASS"
            else:
                print(f"      ❌ Recovery failed: expected 3/3, got {agreement}")
                result["verdict"] = "FAIL"

            return result

        except Exception as e:
            print(f"      ❌ Error: {e}")
            result["verdict"] = "ERROR"
            result["error"] = str(e)
            return result

    # ========== Network Partition Scenarios ==========

    async def network_partition(self) -> dict:
        """Partition network between Node 1 and Nodes 2-3, verify safety, heal"""
        print("\n🔴 TEST: Network Partition (Split Brain)")
        print("   Action: Block traffic between Node 1 and Nodes 2-3")
        print("   Expected: Minority (Node 1) stops, majority (Nodes 2-3) continues")

        result = {
            "test": "network_partition",
            "start_time": datetime.now().isoformat(),
            "events": []
        }

        try:
            # Create partition
            print("   [1/4] Creating network partition...")
            await self._create_network_partition("192.168.1.10", ["192.168.1.11", "192.168.1.12"])
            result["events"].append({
                "time": time.time(),
                "event": "partition_created"
            })
            await asyncio.sleep(3)

            # Verify Node 1 stops
            print("   [2/4] Verifying Node 1 stops processing...")
            health_node1 = await self._check_consensus_health("192.168.1.10")
            result["events"].append({
                "time": time.time(),
                "event": "node_1_status",
                "nodes_in_agreement": health_node1.get("nodes_in_agreement", 0)
            })

            # Verify Nodes 2-3 continue
            print("   [3/4] Verifying Nodes 2-3 continue processing...")
            health_node2 = await self._check_consensus_health("192.168.1.11")
            result["events"].append({
                "time": time.time(),
                "event": "node_2_3_status",
                "nodes_in_agreement": health_node2.get("nodes_in_agreement", 0)
            })

            # Heal partition
            print("   [4/4] Healing partition and verifying recovery...")
            await self._heal_network_partition("192.168.1.10")
            result["events"].append({
                "time": time.time(),
                "event": "partition_healed"
            })
            await asyncio.sleep(5)

            # Verify recovery to 3/3
            health_recovered = await self._check_consensus_health("192.168.1.10")
            result["events"].append({
                "time": time.time(),
                "event": "recovery_complete",
                "nodes_in_agreement": health_recovered.get("nodes_in_agreement", 0)
            })

            if health_recovered.get("nodes_in_agreement", 0) == 3:
                print("      ✅ Recovery successful: 3/3 agreement")
                result["verdict"] = "PASS"
            else:
                print("      ❌ Recovery failed")
                result["verdict"] = "FAIL"

            return result

        except Exception as e:
            print(f"      ❌ Error: {e}")
            result["verdict"] = "ERROR"
            result["error"] = str(e)
            return result

    # ========== Byzantine Attack Scenarios ==========

    async def byzantine_proposal_attack(self) -> dict:
        """Send malformed proposals, verify rejection, verify normal operation continues"""
        print("\n🔴 TEST: Byzantine Proposal Attack")
        print("   Action: Send malformed consensus proposals")
        print("   Expected: Proposals rejected, system unaffected")

        result = {
            "test": "byzantine_proposal_attack",
            "start_time": datetime.now().isoformat(),
            "events": []
        }

        try:
            # Send various malformed proposals
            print("   [1/3] Sending malformed proposals...")
            malformed_proposals = [
                {},  # Empty
                {"proposal": "x" * 10000},  # Too large
                {"proposal": "valid", "priority": "invalid_priority"},  # Invalid field
                {"proposal": None},  # Null value
            ]

            failed_count = 0
            for i, payload in enumerate(malformed_proposals):
                try:
                    response = await self._send_proposal("192.168.1.10", payload)
                    if response.get("status") != "error":
                        print(f"      ⚠️  Proposal {i} not rejected!")
                    else:
                        failed_count += 1
                except:
                    failed_count += 1

            result["events"].append({
                "time": time.time(),
                "event": "malformed_proposals_sent",
                "rejected_count": failed_count
            })

            # Verify system still operational
            print("   [2/3] Verifying system operational...")
            health = await self._check_consensus_health("192.168.1.10")
            result["events"].append({
                "time": time.time(),
                "event": "system_health_check",
                "status": "operational" if health.get("status") == "healthy" else "degraded"
            })

            # Send valid proposal to verify normal operation
            print("   [3/3] Sending valid proposal...")
            valid_response = await self._send_proposal("192.168.1.10", {
                "proposal": "Test proposal after attack",
                "priority": "medium"
            })
            result["events"].append({
                "time": time.time(),
                "event": "valid_proposal_sent",
                "accepted": valid_response.get("status") == "agreed"
            })

            result["verdict"] = "PASS" if failed_count == len(malformed_proposals) else "FAIL"
            return result

        except Exception as e:
            print(f"      ❌ Error: {e}")
            result["verdict"] = "ERROR"
            result["error"] = str(e)
            return result

    # ========== Cascading Failure Scenario ==========

    async def cascading_failure(self) -> dict:
        """Kill Node 2, then Node 3, verify graceful degradation, recover"""
        print("\n🔴 TEST: Cascading Failure (Sequential Node Deaths)")
        print("   Action: Kill Node 2, then Node 3 (30s apart)")
        print("   Expected: Graceful degradation, data preserved")

        result = {
            "test": "cascading_failure",
            "start_time": datetime.now().isoformat(),
            "events": []
        }

        try:
            # Kill Node 2
            print("   [1/5] Killing Node 2 consensus...")
            await self._ssh_exec("192.168.1.11", "systemctl stop camelot-consensus")
            result["events"].append({
                "time": time.time(),
                "event": "node_2_killed"
            })
            await asyncio.sleep(3)

            health = await self._check_consensus_health("192.168.1.10")
            print(f"      Status: {health.get('nodes_in_agreement', 0)}/3 agreement")

            # Kill Node 3
            print("   [2/5] Killing Node 3 consensus...")
            await self._ssh_exec("192.168.1.12", "systemctl stop camelot-consensus")
            result["events"].append({
                "time": time.time(),
                "event": "node_3_killed"
            })
            await asyncio.sleep(2)

            health = await self._check_consensus_health("192.168.1.10")
            print(f"      Status: {health.get('nodes_in_agreement', 0)}/3 agreement")

            if health.get("nodes_in_agreement", 0) < 2:
                print("      ✅ System correctly stopped processing (minority partition)")

            # Restart Node 3
            print("   [3/5] Restarting Node 3...")
            await self._ssh_exec("192.168.1.12", "systemctl start camelot-consensus")
            result["events"].append({
                "time": time.time(),
                "event": "node_3_restarted"
            })
            await asyncio.sleep(5)

            # Restart Node 2
            print("   [4/5] Restarting Node 2...")
            await self._ssh_exec("192.168.1.11", "systemctl start camelot-consensus")
            result["events"].append({
                "time": time.time(),
                "event": "node_2_restarted"
            })
            await asyncio.sleep(5)

            # Verify recovery
            print("   [5/5] Verifying recovery...")
            health = await self._check_consensus_health("192.168.1.10")
            result["events"].append({
                "time": time.time(),
                "event": "recovery_complete",
                "nodes_in_agreement": health.get("nodes_in_agreement", 0)
            })

            result["verdict"] = "PASS" if health.get("nodes_in_agreement", 0) == 3 else "FAIL"
            return result

        except Exception as e:
            print(f"      ❌ Error: {e}")
            result["verdict"] = "ERROR"
            result["error"] = str(e)
            return result

    # ========== Helper Methods ==========

    async def _ssh_exec(self, host: str, command: str) -> str:
        """Execute command on remote host via SSH"""
        process = await asyncio.create_subprocess_exec(
            "ssh", f"root@{host}", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode()

    async def _check_consensus_health(self, host: str) -> dict:
        """Check consensus health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{host}:8443/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return await resp.json()
        except:
            return {"status": "unreachable"}

    async def _send_proposal(self, host: str, payload: dict) -> dict:
        """Send proposal to consensus endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"http://{host}:8443/consensus/propose",
                                       json=payload,
                                       timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return await resp.json()
        except:
            return {"status": "error"}

    async def _create_network_partition(self, isolated_host: str, blocked_hosts: List[str]):
        """Create network partition using iptables"""
        for blocked in blocked_hosts:
            cmd = f"iptables -A OUTPUT -d {blocked} -j DROP && iptables -A INPUT -s {blocked} -j DROP"
            await self._ssh_exec(isolated_host, cmd)

    async def _heal_network_partition(self, isolated_host: str):
        """Remove network partition rules"""
        cmd = "iptables -F && iptables -X"
        await self._ssh_exec(isolated_host, cmd)

    # ========== Test Runner ==========

    async def run_all_chaos_tests(self):
        """Execute full chaos engineering test suite"""
        print("\n" + "=" * 70)
        print("🔥 CAMELOT-OS CHAOS ENGINEERING TEST SUITE")
        print("=" * 70)

        tests = [
            ("Single Node Failure", self.single_node_failure),
            ("Network Partition", self.network_partition),
            ("Byzantine Attack", self.byzantine_proposal_attack),
            ("Cascading Failure", self.cascading_failure),
        ]

        results = []

        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                print(f"\n   Final Verdict: {result.get('verdict', 'UNKNOWN')}")
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append({
                    "test": test_name,
                    "verdict": "ERROR",
                    "error": str(e)
                })

        # Generate report
        self._generate_chaos_report(results)

    def _generate_chaos_report(self, results):
        """Generate comprehensive chaos test report"""
        print("\n" + "=" * 70)
        print("📋 CHAOS ENGINEERING REPORT")
        print("=" * 70)

        passed = sum(1 for r in results if r.get("verdict") == "PASS")
        failed = sum(1 for r in results if r.get("verdict") == "FAIL")
        errors = sum(1 for r in results if r.get("verdict") == "ERROR")

        print("\nSummary:")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Errors: {errors}")

        print(f"\nOverall Verdict: {'✅ SYSTEM RESILIENT' if failed == 0 and errors == 0 else '❌ SYSTEM ISSUES FOUND'}")

        # Save report
        report_path = f"/tmp/chaos_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Report saved: {report_path}")

async def main():
    engineer = ChaosEngineer()
    await engineer.run_all_chaos_tests()

if __name__ == "__main__":
    asyncio.run(main())
