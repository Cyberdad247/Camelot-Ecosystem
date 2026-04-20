# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import re
from datetime import datetime

from src.tools.antigravity import gravity


class OmegaDatasetGenerator:
    """
    👻 OMEGA LEARN: DATA COLLECTOR
    Extracts SFT (Supervised Fine-Tuning) pairs from the PROVENANCE_LEDGER.
    Converts historical actions into 'Command -> Result' training data.
    """

    def __init__(self, ledger_path="PROVENANCE_LEDGER.md"):
        self.ledger_path = ledger_path
        self.output_dir = "01_KERNEL/learning/training_data"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_sft_pairs(self):
        """
        Parses the ledger and generates a JSONL file for training.
        """
        print("🎓 [OMEGA_LEARN] Scraping Provenance Ledger for intelligence...")

        try:
            content = gravity.read(self.ledger_path)
            # Find entries: | timestamp | actor | event | status |
            # We look for successful events
            pattern = r"\| (.*?) \| (.*?) \| (.*?) \| SUCCESS (.*?)\|"
            matches = re.findall(pattern, content)

            dataset = []
            for m in matches:
                timestamp, actor, event, details = m
                # Construct training pair
                dataset.append(
                    {
                        "instruction": f"As {actor}, perform the following task: {event}",
                        "context": f"System status was OMEGA_ACTIVE. Timestamp: {timestamp}",
                        "response": f"Action successfully executed. Result: {details.strip()}",
                    }
                )

            # Save to JSONL
            output_path = os.path.join(self.output_dir, f"ledger_sft_{datetime.now().strftime('%Y%m%d')}.jsonl")
            with open(output_path, "w", encoding="utf-8") as f:
                import json

                for entry in dataset:
                    f.write(json.dumps(entry) + "\n")

            return len(dataset), output_path

        except Exception as e:
            print(f"❌ [OMEGA_LEARN] Collection Error: {e}")
            return 0, str(e)


# Singleton logic for the command
generator = OmegaDatasetGenerator()