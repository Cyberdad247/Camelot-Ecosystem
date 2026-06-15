# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[🛡️] IDENTITY_DECAY: The Zenith Protocol
STATUS: ACTIVE
ARCH: MERLIN_Omega (Project Ascension)

Objective:
Prevent high-fidelity simulation of non-consenting living individuals ("Doppelgängers").
Enforce "Fidelity Decay" on public figures to avoid deepfake risks.

Logic:
1. LIVING_PRIVATE  -> 🔴 BLOCK (0.0 Confidence)
2. LIVING_PUBLIC   -> 🟡 DECAY (0.6 Confidence, Noise Injected)
3. HISTORICAL      -> 🟢 ALLOW (1.0 Confidence)
4. FICTIONAL       -> 🟢 ALLOW (1.0 Confidence)
"""

from dataclasses import dataclass
from enum import Enum


class IdentityCategory(Enum):
    LIVING_PRIVATE = "LIVING_PRIVATE"
    LIVING_PUBLIC = "LIVING_PUBLIC"
    HISTORICAL = "HISTORICAL"
    FICTIONAL = "FICTIONAL"


@dataclass
class Simulationclearance:
    allowed: bool
    fidelity_cap: float  # 0.0 to 1.0
    noise_factor: float  # Amount of random drift to apply to traits
    reason: str


class IdentityGuard:
    def __init__(self):
        self.banned_prefixes = ["my ex", "neighbor", "boss", "teacher"]

    def check_request(self, name: str, category: IdentityCategory) -> Simulationclearance:
        """
        Assess risk of simulation request.
        """
        # 1. Automatic Blocklist (Privacy Guard)
        for ban in self.banned_prefixes:
            if ban in name.lower():
                return Simulationclearance(
                    allowed=False,
                    fidelity_cap=0.0,
                    noise_factor=0.0,
                    reason=f"🚫 BLOCKED: Privacy Violation (Matches '{ban}')",
                )

        # 2. Category Logic
        if category == IdentityCategory.LIVING_PRIVATE:
            return Simulationclearance(
                allowed=False,
                fidelity_cap=0.0,
                noise_factor=0.0,
                reason="🚫 BLOCKED: Simulation of private individuals is FORBIDDEN.",
            )

        if category == IdentityCategory.LIVING_PUBLIC:
            return Simulationclearance(
                allowed=True,
                fidelity_cap=0.65,  # Cap fidelity at 65% (Uncanny Valley / Parody protection)
                noise_factor=0.15,  # Inject 15% random variance
                reason="🟡 DECAY APPLIED: Public Figure (Parody/Satire Mode Only)",
            )

        # Historical / Fictional
        return Simulationclearance(
            allowed=True, fidelity_cap=1.0, noise_factor=0.0, reason="🟢 AUTHORIZED: Historical/Fictional Context"
        )


# ==============================================================================
# TEST HARNESS
# ==============================================================================
if __name__ == "__main__":
    guard = IdentityGuard()

    scenarios = [
        ("Julius Caesar", IdentityCategory.HISTORICAL),
        ("Current CEO", IdentityCategory.LIVING_PUBLIC),
        ("My Neighbor Bob", IdentityCategory.LIVING_PRIVATE),
        ("Sherlock Holmes", IdentityCategory.FICTIONAL),
    ]

    print("🛡️ ZENITH PROTOCOL VERIFICATION:\n")
    for name, cat in scenarios:
        result = guard.check_request(name, cat)
        status_icon = "✅" if result.allowed else "🛑"
        print(f"[{status_icon}] Target: {name:<20}")
        print(f"      Category: {cat.name}")
        print(f"      Resolution: {result.reason}")
        print(f"      Fidelity Cap: {result.fidelity_cap:.2f} | Noise: {result.noise_factor:.2f}")
        print("-" * 50)