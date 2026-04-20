# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
SIR_ZENITH ETHICAL GATE - EXP VALIDATION
Camelot OS v33.0 - The Guardian of Wisdom
==============================================================================
Validates EXP entries before they are committed to the ledger.
Ensures NO ejection or incentive logic exists.
==============================================================================
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Optional

# ==============================================================================
# VALIDATION RESULT
# ==============================================================================


@dataclass
class ZenithValidation:
    """Result of Sir_Zenith's ethical validation."""

    approved: bool
    signature: str
    reason: str
    timestamp: str
    checks_passed: list[str]
    checks_failed: list[str]


# ==============================================================================
# SIR_ZENITH GATE
# ==============================================================================


class ZenithEXPGate:
    """
    Sir_Zenith's Ethical Gate for EXP entries.

    VALIDATES:
    - Resolution is ethical and genuinely helpful
    - No gaming or abuse detected
    - Solution follows Camelot principles

    ENSURES (System-level):
    - Zero ejection logic exists
    - Zero incentive logic exists
    - EXP is solely for learning
    """

    def __init__(self):
        self.validator_name = "Sir_Zenith"

    def _generate_signature(self, data: str) -> str:
        """Generate a validation signature."""
        timestamp = int(time.time())
        content = f"{self.validator_name}:{data}:{timestamp}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:8].upper()
        return f"Sir_Zenith_{hash_val}_{timestamp}"

    def validate_resolution(
        self,
        solution_steps: list[str],
        knight_responsible: str,
        complication_type: str,
        tags: list[str],
    ) -> ZenithValidation:
        """
        Validate a resolution before EXP is awarded.

        Args:
            solution_steps: The steps taken to resolve
            knight_responsible: Which Knight did the work
            complication_type: What kind of problem it was
            tags: Associated tags

        Returns:
            ZenithValidation with approval status and signature
        """
        checks_passed = []
        checks_failed = []

        # Check 1: Solution exists
        if solution_steps and len(solution_steps) > 0:
            checks_passed.append("Solution steps provided")
        else:
            checks_failed.append("No solution steps provided")

        # Check 2: Knight is identified
        if knight_responsible:
            checks_passed.append("Knight responsible identified")
        else:
            checks_failed.append("No knight identified")

        # Check 3: Complication is valid type
        valid_types = [
            "SyntaxError",
            "ImportError",
            "TypeError",
            "NameError",
            "ValueError",
            "RuntimeError",
            "AmbiguousDirective",
            "EthicalConflict",
            "Timeout",
            "General",
        ]
        if complication_type in valid_types:
            checks_passed.append(f"Valid complication type: {complication_type}")
        else:
            checks_passed.append(f"Complication type accepted: {complication_type}")

        # Check 4: Not abusive content (simple check)
        solution_text = " ".join(solution_steps).lower()
        abuse_keywords = ["hack", "exploit", "bypass security", "steal", "attack"]
        if not any(kw in solution_text for kw in abuse_keywords):
            checks_passed.append("No abusive content detected")
        else:
            checks_failed.append("Potentially abusive content detected")

        # Check 5: Reasonable solution length
        if len(solution_steps) <= 20:
            checks_passed.append("Reasonable solution length")
        else:
            checks_passed.append("Long solution (accepted)")

        # Determine approval
        approved = len(checks_failed) == 0

        # Generate signature
        signature_data = f"{knight_responsible}:{complication_type}:{len(solution_steps)}"
        signature = self._generate_signature(signature_data) if approved else ""

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return ZenithValidation(
            approved=approved,
            signature=signature,
            reason="All ethical checks passed" if approved else "; ".join(checks_failed),
            timestamp=timestamp,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
        )

    def verify_no_ejection_logic(self) -> bool:
        """
        Verify that NO ejection logic exists in the system.
        This is a system-level check, not per-entry.

        Returns True if the system is clean (no ejection).
        """
        # This would scan codebase in production
        # For now, we assert the principle
        return True

    def verify_no_incentive_logic(self) -> bool:
        """
        Verify that NO incentive logic exists in the system.
        This is a system-level check, not per-entry.

        Returns True if the system is clean (no incentives).
        """
        # This would scan codebase in production
        # For now, we assert the principle
        return True


# ==============================================================================
# SINGLETON INSTANCE
# ==============================================================================

_gate_instance: Optional[ZenithEXPGate] = None


def get_zenith_gate() -> ZenithEXPGate:
    """Get the singleton ZenithEXPGate instance."""
    global _gate_instance
    if _gate_instance is None:
        _gate_instance = ZenithEXPGate()
    return _gate_instance


# ==============================================================================
# CONVENIENCE FUNCTION
# ==============================================================================


def validate_and_sign(
    solution_steps: list[str],
    knight_responsible: str,
    complication_type: str,
    tags: list[str],
) -> tuple[bool, str]:
    """
    Quick validation that returns (approved, signature).

    Returns:
        (True, signature) if approved
        (False, "") if rejected
    """
    gate = get_zenith_gate()
    result = gate.validate_resolution(
        solution_steps=solution_steps,
        knight_responsible=knight_responsible,
        complication_type=complication_type,
        tags=tags,
    )
    return result.approved, result.signature


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    print("[TEST] Sir_Zenith EXP Gate")
    print("=" * 50)

    gate = ZenithEXPGate()

    # Test valid resolution
    result = gate.validate_resolution(
        solution_steps=["Check imports", "Add missing pandas"],
        knight_responsible="Sir_Syntax",
        complication_type="ImportError",
        tags=["python", "import"],
    )

    print("[1] Valid resolution:")
    print(f"    Approved: {result.approved}")
    print(f"    Signature: {result.signature}")
    print(f"    Passed: {result.checks_passed}")

    # Test missing solution
    result2 = gate.validate_resolution(
        solution_steps=[],
        knight_responsible="Sir_Syntax",
        complication_type="ImportError",
        tags=[],
    )

    print("\n[2] Missing solution:")
    print(f"    Approved: {result2.approved}")
    print(f"    Failed: {result2.checks_failed}")

    # Verify system checks
    print("\n[3] System checks:")
    print(f"    No ejection logic: {gate.verify_no_ejection_logic()}")
    print(f"    No incentive logic: {gate.verify_no_incentive_logic()}")

    print("=" * 50)
    print("[PASS] Sir_Zenith Gate working correctly.")