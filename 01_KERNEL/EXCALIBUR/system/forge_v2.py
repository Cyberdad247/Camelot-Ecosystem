# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[⚒️] FORGE_V2: The Stochastic Universal Forge
STATUS: ACTIVE
ARCH: MERLIN_Omega (Project Ascension)

Objective:
Eliminate "flat" personas by implementing Multivariate Normal Distribution
for trait sampling across a 7-Dimensional Matrix (Big 5 + Honesty + Optimism).

Dependencies:
- numpy (for multivariate_normal)
- scipy (optional, for validation, but we'll stick to numpy for core)
"""

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import numpy as np

# Ensure we can import from kernel if running as script
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from kernel.culture_bias import CulturalLens
except ImportError:
    # Explicit relative import for safety
    sys.path.append(os.path.join(parent_dir, "kernel"))
    from culture_bias import CulturalLens


# ==============================================================================
# PSYCHOMETRICS CONFIGURATION (The Matrix)
# ==============================================================================

TRAIT_LABELS = [
    "Openness",  # Creativity, Curiosity
    "Conscientiousness",  # Order, Dutifulness
    "Extraversion",  # Sociability, Energy
    "Agreeableness",  # Trust, Altruism
    "Neuroticism",  # Anxiety, Volatility
    "Honesty-Humility",  # Sincerity, Fairness (HEXACO)
    "Optimism",  # Hope, Resilience (Positive Psych)
]

# 7x7 Covariance Matrix (Simplified Psychological Model)
# Rows/Cols correspond to TRAIT_LABELS index.
# Values based on meta-analyses (approximate).
# N (4) is negatively correlated with Optimism (6) and Agreeableness (3).
# H (5) is positively correlated with A (3).
COVARIANCE_MATRIX = np.array(
    [
        # O     C     E     A     N     H     Opt
        [1.0, 0.1, 0.2, 0.1, -0.1, 0.2, 0.2],  # Openness
        [0.1, 1.0, 0.2, 0.2, -0.2, 0.3, 0.3],  # Conscientiousness
        [0.2, 0.2, 1.0, 0.3, -0.2, 0.1, 0.4],  # Extraversion
        [0.1, 0.2, 0.3, 1.0, -0.3, 0.5, 0.3],  # Agreeableness
        [-0.1, -0.2, -0.2, -0.3, 1.0, -0.2, -0.6],  # Neuroticism (Strong neg with Opt)
        [0.2, 0.3, 0.1, 0.5, -0.2, 1.0, 0.2],  # Honesty-Humility
        [0.2, 0.3, 0.4, 0.3, -0.6, 0.2, 1.0],  # Optimism
    ]
)


@dataclass
class PersonaVector:
    """The Mathematical Soul of an Agent."""

    name: str
    traits: Dict[str, float]  # 0.0 to 1.0 (Normalized)
    dna_hash: str
    created_at: str


class StochasticForge:
    """
    The Iron Heart of Project Ascension.
    Generates biologically realistic personas using 7D statistics.
    """

    def __init__(self):
        self.mean_vector = np.zeros(7)  # Center point (Standard Normal, Z=0)
        self.cov_matrix = COVARIANCE_MATRIX
        self.lens = CulturalLens()

    def forge_persona(self, name: str, region: Optional[str] = None) -> PersonaVector:
        """
        Create a new persona from the Void.

        Args:
            name: Name of the entity.
            region: Optional WVS Region Code (e.g., 'JAPAN', 'SWEDEN').

        Returns:
            PersonaVector object.
        """
        # 1. Sample from Multivariate Normal Distribution
        # Result is Z-scores (mostly -3.0 to +3.0)
        raw_traits = np.random.multivariate_normal(self.mean_vector, self.cov_matrix)

        # 2. Apply Regional/Cultural Bias if provided
        if region:
            bias_vector = self.lens.get_bias_vector(region)
            if bias_vector:
                print(f"[🌏] Applying Cultural Bias: {region}")
                for i, label in enumerate(TRAIT_LABELS):
                    if label in bias_vector:
                        raw_traits[i] += bias_vector[label]

        # 3. Normalize Z-scores to 0.0-1.0 (Sigmoid-ish clamp for game logic)
        # Using simple min-max logic over expected range or just a sigmoid
        normalized_traits = {}
        for i, val in enumerate(raw_traits):
            # Sigmoid transform: 1 / (1 + e^-x) -> maps -inf/inf to 0-1
            # Z=0 becomes 0.5. Z=-2 becomes ~0.12. Z=2 becomes ~0.88.
            norm_val = 1 / (1 + np.exp(-val))
            normalized_traits[TRAIT_LABELS[i]] = round(norm_val, 4)

        # 4. Generate DNA Hash (Integrity Check)
        dna_str = f"{name}:{json.dumps(normalized_traits, sort_keys=True)}"
        import hashlib

        dna_hash = hashlib.sha256(dna_str.encode()).hexdigest()[:16]

        return PersonaVector(
            name=name, traits=normalized_traits, dna_hash=dna_hash, created_at=datetime.utcnow().isoformat()
        )

    def analyze_entropy(self, count: int = 1000):
        """
        Verify the Forge isn't broken (Covariance Checks).
        Run this to ensure N and Opt are actually negatively correlated.
        """
        print(f"🔥 Heating Forge... generating {count} souls...")
        matrix = []
        for _ in range(count):
            raw = np.random.multivariate_normal(self.mean_vector, self.cov_matrix)
            matrix.append(raw)

        data = np.array(matrix)

        # Calculate actual correlation between Neuroticism (4) and Optimism (6)
        n_col = data[:, 4]
        opt_col = data[:, 6]
        correlation = np.corrcoef(n_col, opt_col)[0, 1]

        print("📊 ANALYSIS RESULT:")
        print("   Target Correlation (N vs Opt): -0.6")
        print(f"   Actual Correlation (N vs Opt): {correlation:.4f}")

        if correlation > -0.3:
            print("⚠️ WARNING: Forge is running COLD (Correlations weak).")
        else:
            print("✅ STATUS: Forge is HOT and REALISTIC.")


# ==============================================================================
# MAIN (Test Harness)
# ==============================================================================
if __name__ == "__main__":
    forge = StochasticForge()

    # 1. Forge a Knight (Japan)
    knight = forge.forge_persona("Yamamoto_San", region="JAPAN")
    print(f"\n🗡️  Forged New Knight: {knight.name}")
    print(f"    DNA: {knight.dna_hash}")
    print("    Traits:")
    for k, v in knight.traits.items():
        bar = "█" * int(v * 20)
        print(f"      {k:<18}: {v:.2f} {bar}")

    # 2. Forge a Knight (Sweden)
    knight2 = forge.forge_persona("Bjorn_Explorer", region="SWEDEN")
    print(f"\n🗡️  Forged New Knight: {knight2.name}")
    print("    Traits (Compare):")
    for k, v in knight2.traits.items():
        bar = "█" * int(v * 20)
        print(f"      {k:<18}: {v:.2f} {bar}")

    # 3. Run Entropy Check
    print("\n")
    forge.analyze_entropy()