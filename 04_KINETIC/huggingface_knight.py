# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Sir HuggingFace (Valkyrie HF) Kinetic Integration
r"""
Sir HuggingFace (SIR_HUGGINGFACE) — Specialized Knight for HuggingFace CLI,
transformers, datasets, model hub, and Spaces integration.

Features:
  1. HuggingFace CLI integration (login, whoami, repo creation, Space status).
  2. Transformers library model/tokenizer loading & inspection.
  3. Spaces API integration (querying, uploading, and managing HuggingFace Spaces).
  4. WorldTree CloudBrain tethering & dynamic Open-Notebook local counterpart sync.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "01_KERNEL"))
sys.path.insert(0, str(_REPO_ROOT / "vfs"))

try:
    from memory.cloudbrain_connector import CloudBrainConnector
except ImportError:
    CloudBrainConnector = None

try:
    from vfs.open_notebook_bridge import OpenNotebookBridge
except ImportError:
    OpenNotebookBridge = None

LOG = logging.getLogger("sir_huggingface")


class SirHuggingFaceKnight:
    """Specialized Knight for HuggingFace CLI, Transformers, and Spaces management."""

    def __init__(self):
        self.knight_id = "SIR_HUGGINGFACE"
        self.spark_id = "0xHFHUB777000000000000000000007777"
        self.name = "Sir HuggingFace (Valkyrie HF)"
        self.title = "HuggingFace Hub & Spaces Conductor"
        self.summoning_rune = "Omega_HuggingFace"
        self.cloudbrain = CloudBrainConnector(knight_id=self.knight_id) if CloudBrainConnector else None
        self.bridge = OpenNotebookBridge(knight_id=self.knight_id) if OpenNotebookBridge else None

    def whoami(self) -> Dict[str, Any]:
        """Runs hf CLI to inspect authenticated identity."""
        for cmd in [["hf", "auth", "whoami"], ["hf", "whoami"], ["huggingface-cli", "whoami"]]:
            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if res.returncode == 0:
                    user_info = res.stdout.strip()
                    return {"authenticated": True, "identity": user_info, "status": "LIVE", "cli": cmd[0]}
            except Exception:
                continue
        return {"authenticated": False, "status": "UNAUTHENTICATED", "cli": "hf"}

    def inspect_model(self, model_id: str = "BAAI/bge-small-en-v1.5") -> Dict[str, Any]:
        """Inspects model metadata on HuggingFace Hub."""
        try:
            import huggingface_hub
            info = huggingface_hub.model_info(model_id)
            details = {
                "model_id": info.id,
                "author": info.author,
                "sha": info.sha,
                "downloads": getattr(info, "downloads", 0),
                "likes": getattr(info, "likes", 0),
                "tags": getattr(info, "tags", []),
                "pipeline_tag": getattr(info, "pipeline_tag", None),
            }
            if self.bridge:
                self.bridge.sync_local_tissue(f"Inspect Model {model_id}", details)
            return details
        except Exception as exc:
            return {"model_id": model_id, "error": str(exc), "status": "FAILED"}

    def get_integrated_catalog(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns the master catalog of integrated quantization models for Camelot-OS."""
        return {
            "1.58_bit_ternary": [
                {"model_id": "microsoft/bitnet-b1.58-2B-4T-gguf", "vram_mb": 1200, "engine": "bitnet.cpp / Ouroboros"},
                {"model_id": "microsoft/bitnet-b1.58-3B", "vram_mb": 1800, "engine": "bitnet.cpp"},
                {"model_id": "Ouroboros-1.58bit-SSM-v1", "vram_mb": 1100, "engine": "Ouroboros 0.8ms SSM"}
            ],
            "gguf_importance_matrix": [
                {"model_id": "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF", "vram_mb": 3200, "engine": "llama.cpp / OmniRoute"},
                {"model_id": "unsloth/gemma-2-2b-it-GGUF", "vram_mb": 1600, "engine": "llama.cpp"},
                {"model_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF", "vram_mb": 1100, "engine": "llama.cpp"},
                {"model_id": "HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF", "vram_mb": 1200, "engine": "llama.cpp"},
                {"model_id": "microsoft/Phi-3.5-mini-instruct-GGUF", "vram_mb": 2400, "engine": "llama.cpp"}
            ],
            "heavy_reasoning_llms": [
                {"model_id": "Qwen/Qwen2.5-Coder-32B-Instruct", "vram_mb": "Cloud / API", "engine": "CLIProxyAPI / OmniRoute"},
                {"model_id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", "vram_mb": "Cloud / API", "engine": "CLIProxyAPI / GoT"}
            ],
            "stt_ingress": [
                {"model_id": "UsefulSensors/moonshine-tiny", "vram_mb": 150, "engine": "ONNX Edge Speech"},
                {"model_id": "openai/whisper-tiny.en", "vram_mb": 200, "engine": "Whisper ONNX"}
            ],
            "tts_egress": [
                {"model_id": "OuteAI/OuteTTS-0.2-500M", "vram_mb": 500, "engine": "PyTorch Stream"},
                {"model_id": "parler-tts/parler-tts-mini-v1", "vram_mb": 600, "engine": "Parler Synthesizer"},
                {"model_id": "rhasspy/piper-voices", "vram_mb": 100, "engine": "Piper ONNX TTS"}
            ]
        }

    def list_user_spaces(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists accessible HuggingFace Spaces for a user or organization."""
        try:
            import huggingface_hub
            api = huggingface_hub.HfApi()
            spaces = api.list_spaces(author=username)
            results = []
            for s in spaces:
                results.append({
                    "id": s.id,
                    "author": s.author,
                    "sdk": getattr(s, "sdk", None),
                    "likes": getattr(s, "likes", 0),
                    "private": getattr(s, "private", False),
                })
            return results
        except Exception as exc:
            LOG.error(f"[HF_KNIGHT] Failed to list spaces: {exc}")
            return []

    def get_full_character_sheet(self) -> Dict[str, Any]:
        """Returns Sir HuggingFace full character sheet."""
        tether_info = self.cloudbrain.get_tether_status() if self.cloudbrain else {}
        return {
            "knight_id": self.knight_id,
            "spark_id": self.spark_id,
            "name": self.name,
            "title": self.title,
            "layer": "L4 Kinetic",
            "role": "HuggingFace CLI, Transformers, Datasets & Spaces Management",
            "summoning_rune": self.summoning_rune,
            "primary_engine": "HuggingFace Hub / Transformers / Gradio Spaces",
            "skill_tier": "S4 Strategic",
            "ocean_vector": {"O": 0.95, "C": 0.96, "E": 0.50, "A": 0.70, "N": 0.02},
            "tether": tether_info,
        }


if __name__ == "__main__":
    knight = SirHuggingFaceKnight()
    sheet = knight.get_full_character_sheet()
    print("=== SIR HUGGINGFACE CHARACTER SHEET ===")
    print(json.dumps(sheet, indent=2))
    print("\n=== HUGGINGFACE CLI IDENTITY CHECK ===")
    print(json.dumps(knight.whoami(), indent=2))
