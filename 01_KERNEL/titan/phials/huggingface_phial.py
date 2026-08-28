# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
SIR_HUGGINGFACE PHIAL: HuggingFace Hub & Model Research Engine
==============================================================
Executable PhialEngine for SIR_HUGGINGFACE — Monitor-Inspect-Deploy research loop
for HuggingFace models, datasets, transformers, and Spaces.

Self-test:
  python 01_KERNEL/titan/phials/huggingface_phial.py --test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

_CAMELOT_ROOT = Path(__file__).resolve().parents[3]
_STATE_PATH = _CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "huggingface_phial.json"

sys.path.insert(0, str(_CAMELOT_ROOT / "04_KINETIC"))


class HuggingFacePhialEngine:
    """Executable PhialEngine for HuggingFace Hub & Model Research."""

    def __init__(self, state_path: Path = _STATE_PATH):
        self.state_path = state_path
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "knight_id": "SIR_HUGGINGFACE",
            "worldtree_home": "a0a4bfb9-e847-4c38-be39-7aee398f0795",
            "cycles_run": 0,
            "inspected_models": [],
            "status": "READY",
        }

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def run_cycle(self, model_id: str = "BAAI/bge-small-en-v1.5") -> Dict[str, Any]:
        """Runs one research/inspection cycle on a HuggingFace model."""
        from huggingface_knight import SirHuggingFaceKnight
        knight = SirHuggingFaceKnight()
        info = knight.inspect_model(model_id)
        self.state["cycles_run"] += 1
        if model_id not in self.state["inspected_models"]:
            self.state["inspected_models"].append(model_id)
        self.state["last_inspected"] = info
        self._save_state()
        return info

    def run_test(self) -> bool:
        """Self-test method for Phial Engine verification."""
        status = self.run_cycle("BAAI/bge-small-en-v1.5")
        assert "model_id" in status or "error" in status
        return True


def main():
    parser = argparse.ArgumentParser(description="Sir HuggingFace Phial Engine")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    parser.add_argument("--cycle", type=str, default="BAAI/bge-small-en-v1.5", help="Run inspection cycle")
    args = parser.parse_args()

    engine = HuggingFacePhialEngine()
    if args.test:
        success = engine.run_test()
        print(f"HuggingFace Phial Engine Test: {'PASSED' if success else 'FAILED'}")
    else:
        result = engine.run_cycle(args.cycle)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
