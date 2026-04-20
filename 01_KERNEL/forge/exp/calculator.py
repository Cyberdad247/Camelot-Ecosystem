# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
==============================================================================
EXP CALCULATOR
Camelot OS v33.0 - Pure Experience Tracking
==============================================================================
EXP value is ALWAYS 10. NO multipliers. NO bonuses. NO incentives.
==============================================================================
"""

from typing import NamedTuple

# ==============================================================================
# CONSTANTS
# ==============================================================================

BASE_EXP = 10  # The ONLY value. NEVER changes.

# These are EXPLICITLY not used (documented for verification):
# SEVERITY_MULTIPLIER = NOT_USED
# EFFICIENCY_BONUS = NOT_USED
# COLLABORATION_BONUS = NOT_USED
# PREVENTIVE_EXP = NOT_USED


# ==============================================================================
# RESULT TYPE
# ==============================================================================


class EXPResult(NamedTuple):
    """Result of EXP calculation."""

    awarded: bool
    exp_value: int
    reason: str


# ==============================================================================
# CALCULATOR
# ==============================================================================


def calculate_exp(
    complication_resolved: bool,
    is_novel: bool,
    zenith_approved: bool,
) -> EXPResult:
    """
    Calculate EXP for a resolved complication.

    CONDITIONS (ALL must be true):
    1. A genuine complication occurred and was resolved
    2. The solution is NOVEL (not already in ledger)
    3. Sir_Zenith approved the resolution

    RETURNS:
    - 10 EXP if all conditions met
    - 0 EXP otherwise

    NO multipliers. NO bonuses. NO exceptions.
    """

    # Check all conditions
    if not complication_resolved:
        return EXPResult(awarded=False, exp_value=0, reason="No complication to resolve")

    if not is_novel:
        return EXPResult(awarded=False, exp_value=0, reason="Solution already exists in ledger (not novel)")

    if not zenith_approved:
        return EXPResult(awarded=False, exp_value=0, reason="Resolution not approved by Sir_Zenith")

    # All conditions met - award BASE_EXP (always 10)
    return EXPResult(awarded=True, exp_value=BASE_EXP, reason="Novel complication resolved and approved")


# ==============================================================================
# WHAT THIS MODULE DOES NOT DO (Verification Checklist)
# ==============================================================================

"""
PURGED FEATURES - These do NOT exist in this module:

❌ Severity Multipliers
   - No multiplier based on error severity
   - No "critical" vs "minor" distinction for EXP

❌ Efficiency Bonus
   - No bonus for fast resolution
   - No penalty for slow resolution

❌ Collaboration Bonus
   - No extra EXP for team work
   - No cross-persona EXP sharing

❌ Preventive EXP
   - No EXP for "preventing" errors
   - No "just in case" awards

❌ GOLDEN Entries
   - No special high-value entries
   - All entries are equal (10 EXP)

❌ exp_level
   - No leveling system
   - No tiers or ranks based on EXP

❌ Ejection Logic
   - No threshold for removal
   - Knights NEVER get ejected

❌ Incentive System
   - No badges
   - No leaderboards
   - No gamification
"""


# ==============================================================================
# TESTING
# ==============================================================================


if __name__ == "__main__":
    print("[TEST] EXP Calculator")
    print("=" * 50)

    # Test 1: All conditions met
    result = calculate_exp(complication_resolved=True, is_novel=True, zenith_approved=True)
    print(f"[1] All conditions met: {result.exp_value} EXP - {result.reason}")
    assert result.exp_value == 10, "Should be 10"

    # Test 2: Not novel
    result = calculate_exp(complication_resolved=True, is_novel=False, zenith_approved=True)
    print(f"[2] Not novel: {result.exp_value} EXP - {result.reason}")
    assert result.exp_value == 0, "Should be 0"

    # Test 3: Not approved
    result = calculate_exp(complication_resolved=True, is_novel=True, zenith_approved=False)
    print(f"[3] Not approved: {result.exp_value} EXP - {result.reason}")
    assert result.exp_value == 0, "Should be 0"

    # Test 4: No complication
    result = calculate_exp(complication_resolved=False, is_novel=True, zenith_approved=True)
    print(f"[4] No complication: {result.exp_value} EXP - {result.reason}")
    assert result.exp_value == 0, "Should be 0"

    print("=" * 50)
    print("[PASS] All tests passed. EXP is ALWAYS 10 or 0.")