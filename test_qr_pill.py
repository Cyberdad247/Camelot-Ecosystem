#!/usr/bin/env python
"""
QR Pill Test Suite — Verify bootstrap and self-healing.

Tests:
  1. Sovereign Commander initialization
  2. QR Pill activation
  3. Bootstrap task execution
  4. Health checks
  5. Self-healing capability
  6. Ledger audit trail
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class QRPillTestSuite:
    """Test suite for QR Pill system."""

    def __init__(self):
        self.results = {}
        self.passed = 0
        self.failed = 0

    async def run_all_tests(self) -> dict:
        """Run all tests."""
        print("╔════════════════════════════════════════╗")
        print("║  QR Pill Verification Test Suite      ║")
        print("╚════════════════════════════════════════╝\n")

        tests = [
            ("Sovereign Commander", self.test_sovereign_commander),
            ("QR Pill Initialization", self.test_pill_initialization),
            ("Bootstrap Tasks", self.test_bootstrap_tasks),
            ("Health Checks", self.test_health_checks),
            ("Self-Healing", self.test_self_healing),
            ("Ledger Audit Trail", self.test_ledger_audit),
            ("Approval Gates", self.test_approval_gates),
        ]

        for test_name, test_fn in tests:
            try:
                result = await test_fn()
                status = "✓" if result else "✗"
                self.results[test_name] = result
                if result:
                    self.passed += 1
                else:
                    self.failed += 1
                print(f"{status} {test_name}")
            except Exception as e:
                print(f"✗ {test_name}: {str(e)[:80]}")
                self.results[test_name] = False
                self.failed += 1

        # Summary
        total = len(self.results)
        print(f"\n{'='*44}")
        print(f"Result: {self.passed}/{total} tests passed")
        print(f"{'='*44}\n")

        if self.passed == total:
            print("✓ QR Pill system ready for deployment")
        else:
            print(f"✗ {self.failed} tests failed, review required")

        return self.results

    async def test_sovereign_commander(self) -> bool:
        """Test Sovereign Commander initialization."""
        try:
            from control_plane.sovereign_commander import (
                get_sovereign_commander,
                OperationType,
                ApprovalLevel,
            )

            commander = get_sovereign_commander()

            # Test 1: Commander initialized
            if commander.commander_name != "Vizion":
                print(f"  ERROR: Expected commander name 'Vizion', got '{commander.commander_name}'")
                return False

            # Test 2: Approval gates configured
            if len(commander.approval_gates) == 0:
                print("  ERROR: No approval gates configured")
                return False

            # Test 3: Gate configuration for QR Pill activation
            if OperationType.QR_PILL_ACTIVATION not in commander.approval_gates:
                print("  ERROR: No gate for QR_PILL_ACTIVATION")
                return False

            gate = commander.approval_gates[OperationType.QR_PILL_ACTIVATION]
            if gate.default_level != ApprovalLevel.APPROVAL:
                print("  ERROR: QR_PILL_ACTIVATION should require APPROVAL level")
                return False

            print(f"  Commander: {commander.commander_name}")
            print(f"  Gates: {len(commander.approval_gates)}")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_pill_initialization(self) -> bool:
        """Test QR Pill initialization."""
        try:
            from control_plane.qr_pill import get_qr_pill, PillState

            pill = get_qr_pill("test_pill")

            # Test 1: Pill initialized
            if pill.state != PillState.DORMANT:
                print(f"  ERROR: Expected DORMANT state, got {pill.state}")
                return False

            # Test 2: Bifrost bridge status
            if pill.bifrost_bridge_active:
                print("  ERROR: Bifrost should not be active before activation")
                return False

            # Test 3: Knight brain status
            if pill.knight_brain_connected:
                print("  ERROR: Knight brain should not be connected before activation")
                return False

            # Test 4: Status method works
            status = pill.get_status()
            if status["pill_id"] != "test_pill":
                print("  ERROR: Pill ID mismatch")
                return False

            print(f"  Pill ID: {pill.pill_id}")
            print(f"  State: {pill.state.value}")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_bootstrap_tasks(self) -> bool:
        """Test bootstrap task execution."""
        try:
            from control_plane.qr_pill import get_qr_pill

            pill = get_qr_pill("test_bootstrap")

            # Test 1: Load manifest
            manifest_loaded = await pill._load_manifest()
            if not manifest_loaded:
                print("  ERROR: Failed to load manifest")
                return False

            if not pill.manifest:
                print("  ERROR: Manifest not loaded")
                return False

            # Test 2: Manifest has required fields
            if not hasattr(pill.manifest, "pill_id"):
                print("  ERROR: Manifest missing pill_id")
                return False

            if not hasattr(pill.manifest, "blueprint"):
                print("  ERROR: Manifest missing blueprint")
                return False

            # Test 3: Task structure valid
            if not isinstance(pill.manifest.tasks, list):
                print("  ERROR: Tasks should be a list")
                return False

            print(f"  Manifest loaded: {pill.manifest.pill_id}")
            print(f"  Version: {pill.manifest.version}")
            print(f"  Tasks: {len(pill.manifest.tasks)}")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_health_checks(self) -> bool:
        """Test health check system."""
        try:
            from control_plane.qr_pill import get_qr_pill, HealthStatus

            pill = get_qr_pill("test_health")

            # Simulate activation
            pill.bifrost_bridge_active = True
            pill.knight_brain_connected = True

            # Test 1: Run health check
            health = await pill._health_check()
            if not health:
                print("  ERROR: Health check failed")
                return False

            # Test 2: Health check has required fields
            if not hasattr(health, "status"):
                print("  ERROR: Health check missing status")
                return False

            # Test 3: Check status values
            if health.status not in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.CRITICAL]:
                print(f"  ERROR: Invalid health status {health.status}")
                return False

            # Test 4: Health history recorded
            if len(pill.health_history) == 0:
                print("  ERROR: Health check not recorded")
                return False

            print(f"  Health status: {health.status.value}")
            print(f"  Checks passed: {health.checks_passed}")
            print(f"  Checks failed: {health.checks_failed}")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_self_healing(self) -> bool:
        """Test self-healing capability."""
        try:
            from control_plane.qr_pill import get_qr_pill, PillState

            pill = get_qr_pill("test_healing")

            # Set up degraded state
            pill.bifrost_bridge_active = False
            pill.knight_brain_connected = False
            pill.state = PillState.LIVE

            # Test 1: Detect degradation
            health = await pill._health_check()
            if health.checks_failed == 0:
                print("  ERROR: Should detect degradation")
                return False

            # Test 2: Attempt self-heal
            healed = await pill._self_heal(health)
            if not healed:
                print("  ERROR: Self-heal failed")
                return False

            # Test 3: Health improved after healing
            if not health.self_healed:
                print("  ERROR: Healing not marked as executed")
                return False

            print(f"  Degraded state detected: {health.checks_failed} failures")
            print(f"  Self-healed: {health.self_healed}")
            print(f"  Healing actions: {len(health.healing_actions)}")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_ledger_audit(self) -> bool:
        """Test ledger audit trail."""
        try:
            from control_plane.sovereign_commander import get_sovereign_commander

            commander = get_sovereign_commander()

            # Test 1: Ledger path configured
            if not commander.ledger_path:
                print("  ERROR: Ledger path not configured")
                return False

            # Test 2: Approval history works
            history = commander.get_approval_history()
            if not isinstance(history, list):
                print("  ERROR: Approval history should be a list")
                return False

            # Test 3: Status method works
            status = commander.status()
            if not status:
                print("  ERROR: Status method failed")
                return False

            if status["commander"] != "Vizion":
                print("  ERROR: Commander name mismatch")
                return False

            print(f"  Ledger path: {commander.ledger_path}")
            print(f"  History entries: {len(history)}")
            print(f"  Pending approvals: {status['pending_approvals']}")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

    async def test_approval_gates(self) -> bool:
        """Test approval gate system."""
        try:
            from control_plane.sovereign_commander import (
                get_sovereign_commander,
                ApprovalRequest,
                OperationType,
            )

            commander = get_sovereign_commander()

            # Test 1: Request approval
            request = ApprovalRequest(
                operation_id="test_op_1",
                operation_type=OperationType.TASK_EXECUTION,
                description="Test task execution",
                risk_level="low",
            )

            approved = await commander.request_approval(request)
            if not approved:
                print("  ERROR: Low-risk operation should auto-approve")
                return False

            # Test 2: Check approval in history
            history = commander.get_approval_history()
            if len(history) == 0:
                print("  ERROR: Approval not in history")
                return False

            # Test 3: Critical operation requires approval
            critical_request = ApprovalRequest(
                operation_id="test_critical_1",
                operation_type=OperationType.QR_PILL_ACTIVATION,
                description="Test pill activation",
                risk_level="critical",
            )

            approved = await commander.request_approval(critical_request)
            if not approved:
                print("  ERROR: Critical operation approval failed")
                return False

            print(f"  Low-risk auto-approved: ✓")
            print(f"  Critical approved: ✓")
            print(f"  Total approvals: {len(history)}")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False


async def main():
    """Run all tests."""
    tester = QRPillTestSuite()
    results = await tester.run_all_tests()

    # Exit code based on pass/fail
    sys.exit(0 if tester.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
