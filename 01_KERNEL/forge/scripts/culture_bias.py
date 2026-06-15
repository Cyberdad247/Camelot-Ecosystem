# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[🌏] CULTURE_BIAS: The Cultural Lens
STATUS: ACTIVE
ARCH: MERLIN_Omega

Objective:
Translate 2D Inglehart-Welzel Coordinates into 7D Psychometric Shifts.

Mapping Logic (Hypothetical Heuristics):
1. Self-Expression (Y-Axis):
   - (+) Increases Openness, Extraversion.
   - (-) Increases Conscientiousness (Conformity), Neuroticism (Threat sensitivity).

2. Secular-Rational (X-Axis):
   - (+) Increases Openness (Intellectualism), DECREASES Traditionalism (proxy for low O).
   - (-) Increases Agreeableness (In-group loyalty/Tradition).
"""

import json
from pathlib import Path
from typing import Dict


class CulturalLens:
    def __init__(self, data_path: str = "kernel/data/wvs_map.json"):
        self.data_path = Path(data_path)
        self.wvs_data = self._load_data()

    def _load_data(self) -> Dict:
        if not self.data_path.exists():
            return {}
        with open(self.data_path, "r") as f:
            return json.load(f).get("REGIONS", {})

    def get_bias_vector(self, region_name: str) -> Dict[str, float]:
        """
        Convert WVS coords to Trait Bias (Shift in Mean).
        """
        region = self.wvs_data.get(region_name.upper())
        if not region:
            print(f"⚠️ Region '{region_name}' not found in WVS Map.")
            return {}

        x, y = region["coords"]  # X=Secular, Y=Expression

        # BIAS MAPPING (Heuristic Helpers)
        # Scale: Coords range roughly -2.0 to +2.0.
        # Impact: We want max shift of maybe +/- 0.5 Z-score.
        scale = 0.25

        bias = {}

        # 1. Openness (Correlated with Secular + Self-Expression)
        bias["Openness"] = (x * 0.5 + y * 0.5) * scale

        # 2. Conscientiousness (Correlated with Survival/Order -> Low Y)
        bias["Conscientiousness"] = (y * -1.0) * scale

        # 3. Extraversion (Correlated with Self-Expression)
        bias["Extraversion"] = (y * 0.8) * scale

        # 4. Agreeableness (Complex: Traditional (Low X) often implies higher in-group A)
        bias["Agreeableness"] = (x * -0.3) * scale

        # 5. Neuroticism (Survival (Low Y) implies higher threat sensitivity)
        bias["Neuroticism"] = (y * -0.5) * scale

        # 6. Honesty-Humility (Hard to map, assumed neutral or slight correlation to Traditional)
        bias["Honesty-Humility"] = 0.0

        # 7. Optimism (Correlated strongly with Self-Expression)
        bias["Optimism"] = (y * 0.6) * scale

        return bias


if __name__ == "__main__":
    lens = CulturalLens()
    print("🌏 CULTURAL LENS CALIBRATION:")

    test_regions = ["JAPAN", "SWEDEN", "EGYPT"]

    for r in test_regions:
        print(f"\n[{r}] Trait Shifts:")
        shifts = lens.get_bias_vector(r)
        for k, v in shifts.items():
            if abs(v) > 0.01:
                direction = "+" if v > 0 else ""
                print(f"  {k:<18}: {direction}{v:.2f}")