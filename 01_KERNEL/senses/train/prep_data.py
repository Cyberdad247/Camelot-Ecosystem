# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json

LEDGER_PATH = "PROVENANCE_LEDGER.md"
OUTPUT_PATH = "01_KERNEL/train/camelot_dataset.jsonl"


def extract_training_data():
    print("🎓 [OMEGA_LEARN] Scanning Ledger for Wisdom...")

    dataset = []

    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if "| SUCCESS" in line:
                # Parse the log line
                # Format: | Timestamp | Actor | Event | Status |
                try:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) < 5:
                        continue

                    event = parts[3]  # e.g. "POST /agent/dispatch"

                    # Heuristic: We only want high-value actions
                    if "POST /agent/dispatch" in event:
                        # In a real scenario, we would link this log to the actual request/response payload
                        # stored in a DB. Since we only have the log line here, we create a
                        # "Synthetic" training example based on the event type.

                        example = {
                            "instruction": "Execute a Sovereign Dispatch.",
                            "input": event,
                            "output": "Action executed successfully and logged to Provenance Ledger.",
                        }
                        dataset.append(example)
                except:
                    continue

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ [OMEGA_LEARN] Extracted {len(dataset)} Golden Vectors.")


if __name__ == "__main__":
    extract_training_data()