"""Split-Brain OS — Self-Healing Test Runner

Sends synthetic tasks to the Pydantic AI Control Plane,
validates output structure, and reports integrity violations.
"""

from __future__ import annotations

import asyncio
import sys
import uuid

from control_plane.main import (
    A2AMessage,
    MessageType,
    StatusMessage,
    TaskMessage,
    process_task,
)

# --- Test Cases ---

SYNTHETIC_TASKS = [
    TaskMessage(
        sender="test_runner",
        receiver="control_plane",
        task_name="list_directory",
        parameters={"path": "."},
        correlation_id=str(uuid.uuid4()),
    ),
    TaskMessage(
        sender="test_runner",
        receiver="control_plane",
        task_name="unknown_task",
        parameters={},
        correlation_id=str(uuid.uuid4()),
    ),
]


# --- Validation ---

def validate_response(resp: A2AMessage) -> list[str]:
    """Validate A2A response structure. Returns list of violations."""
    violations = []

    if not isinstance(resp, StatusMessage):
        violations.append(f"Expected StatusMessage, got {type(resp).__name__}")
        return violations

    if resp.msg_type != MessageType.STATUS:
        violations.append(f"msg_type should be 'status', got '{resp.msg_type}'")

    if resp.status not in ("complete", "error", "pending"):
        violations.append(f"Unknown status: '{resp.status}'")

    if not resp.sender:
        violations.append("sender is empty")

    if not resp.receiver:
        violations.append("receiver is empty")

    return violations


# --- Self-Healing Loop ---

async def run_tests() -> bool:
    """Execute all synthetic tasks and validate responses."""
    all_passed = True

    for i, task in enumerate(SYNTHETIC_TASKS):
        print(f"[Test {i+1}/{len(SYNTHETIC_TASKS)}] task={task.task_name}")

        try:
            resp = await process_task(task)
        except Exception as exc:
            print(f"  FAIL: Exception — {exc}")
            all_passed = False
            continue

        violations = validate_response(resp)
        if violations:
            print(f"  FAIL: {violations}")
            all_passed = False
        else:
            print(f"  PASS: status={resp.status}")

    return all_passed


if __name__ == "__main__":
    passed = asyncio.run(run_tests())
    print("\n" + ("ALL TESTS PASSED" if passed else "SOME TESTS FAILED"))
    sys.exit(0 if passed else 1)
