# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os
from typing import Any, Dict, List


class OmegaTrainer:
    """
    Omega Learn (Phase 45)
    Processes Ouroboros datasets to extract 'Golden Paths' (high-success sequences).
    """

    def __init__(self, data_dir: str = "01_KERNEL/learning/datasets"):
        self.data_dir = data_dir

    def extract_golden_paths(self) -> List[Dict[str, Any]]:
        """Scans all dataset files for successful interactions."""
        golden_paths = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".jsonl"):
                with open(os.path.join(self.data_dir, filename), "r", encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        # We prioritize successful, unhealed actions as 'pure' targets
                        # Or healed actions as 're-labeled' targets
                        if entry["type"] == "action" and entry["data"]["status"] == "SUCCESS":
                            golden_paths.append(entry["data"])
        return golden_paths

    def generate_few_shot_context(self) -> str:
        """Converts golden paths into a string suitable for LLM context injection."""
        paths = self.extract_golden_paths()
        if not paths:
            return ""

        context = "[SYSTEM: FEW_SHOT_LEARNING]\nHistorical Successes:\n"
        for p in paths[:10]:  # Limit to top 10 for context window safety
            context += f"- Goal: {p.get('target')} | Action: {p.get('action')} | Healed: {p.get('healed')}\n"
        return context


# Singleton
trainer = OmegaTrainer()

if __name__ == "__main__":
    print("🎓 [OMEGA] Generating Few-Shot Context...")
    print(trainer.generate_few_shot_context())