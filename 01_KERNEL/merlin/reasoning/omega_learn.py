# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os
import re


def mine_ledger(ledger_path="PROVENANCE_LEDGER.md"):
    """
    OMEGA LEARN: Ledger Mining Protocol
    Extracts successful (Intent, Result) pairs for system self-improvement.
    """
    print(f"🎓 [OMEGA LEARN] Mining Golden Samples from {ledger_path}...")

    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to find Merlin_Omega SUCCESS entries
    # | Timestamp | Merlin_Omega | Intent | SUCCESS |
    pattern = r"\| (.*?) \| Merlin_Omega \| (.*?) \| SUCCESS (.*?)\|"
    matches = re.findall(pattern, content)

    golden_dataset = []
    for match in matches:
        timestamp, intent, mode = match
        golden_dataset.append(
            {
                "instruction": intent.strip(),
                "context": f"Camelot OS v100.x | Mode: {mode.strip()}",
                "response": "SUCCESS",  # In a real system, we'd grab the next Antigravity Write as the 'Response'
            }
        )

    output_path = "03_VAULT/training/golden_samples.jsonl"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        for entry in golden_dataset:
            f.write(json.dumps(entry) + "\n")

    print(f"✅ [OMEGA LEARN] Dataset generated: {len(golden_dataset)} samples.")
    return output_path


if __name__ == "__main__":
    import os

    mine_ledger()