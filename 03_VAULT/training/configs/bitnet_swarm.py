# -*- coding: utf-8 -*-
"""
bitnet_swarm.py — BitNet 1.58-bit Nano-Knight Inference Layer
==============================================================
P2-B. Assigns ternary {-1, 0, 1} quantized models to Bio-Swarm species.

BitNet 1.58-bit: model weights constrained to {-1, 0, +1}
  - 8× memory reduction vs FP32, 16× vs BF16
  - ~3.5 bits effective precision with AbsMax quantization
  - Enables on-device inference within 8GB RAM ceiling

Integration:
  swarm_spawner (Rust) → exec bitnet-cpp binary → token stream → knight response
  harness _run_knight() → BitNetSwarm.infer(species, prompt) → result

Reference: microsoft/bitnet (github) — bitnet.cpp inference engine
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

CAMELOT_HOME  = Path(__file__).parent.parent.parent.parent  # up to CAMELOT_OS root
BITNET_BIN    = CAMELOT_HOME / "bin" / "bitnet.cpp"         # compiled bitnet binary
MODELS_DIR    = CAMELOT_HOME / "03_VAULT" / "models" / "bitnet"
BITNET_LOG    = CAMELOT_HOME / "logs" / "bitnet_swarm.log"

# ── Species → Model assignment ────────────────────────────────────────────────
# Each Nano-Knight species gets a BitNet model matched to its token budget.
# Smaller = faster; Formica/Strigiform use 1B, Pongid uses 3B.

SPECIES_MODEL_MAP: dict[str, dict] = {
    "formica": {
        "model": "BitNet-b1.58-1B",
        "gguf":  "bitnet-b1.58-1b-q1_5.gguf",
        "ctx":   512,
        "token_budget": 150,
        "n_threads": 4,
        "description": "1B ternary — map-reduce file ops, low latency",
    },
    "pongid": {
        "model": "BitNet-b1.58-3B",
        "gguf":  "bitnet-b1.58-3b-q1_5.gguf",
        "ctx":   1024,
        "token_budget": 300,
        "n_threads": 8,
        "description": "3B ternary — heavy API integration, richer reasoning",
    },
    "castor": {
        "model": "BitNet-b1.58-2B",
        "gguf":  "bitnet-b1.58-2b-q1_5.gguf",
        "ctx":   768,
        "token_budget": 200,
        "n_threads": 6,
        "description": "2B ternary — infra builds, structured output",
    },
    "arachne": {
        "model": "BitNet-b1.58-2B",
        "gguf":  "bitnet-b1.58-2b-q1_5.gguf",
        "ctx":   768,
        "token_budget": 200,
        "n_threads": 6,
        "description": "2B ternary — browser/MCP scraping, HTML parsing",
    },
    "simian": {
        "model": "BitNet-b1.58-1B",
        "gguf":  "bitnet-b1.58-1b-q1_5.gguf",
        "ctx":   512,
        "token_budget": 150,
        "n_threads": 4,
        "description": "1B ternary — chaos injection, fast adversarial probes",
    },
    "strigiform": {
        "model": "BitNet-b1.58-1B",
        "gguf":  "bitnet-b1.58-1b-q1_5.gguf",
        "ctx":   256,
        "token_budget": 100,
        "n_threads": 2,
        "description": "1B ternary — oversight, conflict detection, inline only",
    },
}

# RAM budget per species (8GB ceiling enforcement)
SPECIES_RAM_MB: dict[str, int] = {
    "formica":    512,
    "pongid":    1024,
    "castor":     768,
    "arachne":    768,
    "simian":     512,
    "strigiform": 256,
}


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class BitNetResult:
    species: str
    model: str
    output: str
    tokens_generated: int
    duration_ms: float
    ram_mb_used: int
    error: Optional[str] = None


# ── RAM ceiling guard ─────────────────────────────────────────────────────────

def _estimate_total_ram_mb(active_species: list[str]) -> int:
    return sum(SPECIES_RAM_MB.get(s, 512) for s in active_species)


def _check_ram_ceiling(species: str, active: list[str]) -> tuple[bool, str]:
    current = _estimate_total_ram_mb(active)
    additional = SPECIES_RAM_MB.get(species, 512)
    total = current + additional
    if total > 7_800:
        return False, f"RAM ceiling: {total}MB > 7800MB — defer {species} until cell frees"
    return True, f"RAM OK: {total}MB / 7800MB"


# ── BitNet inference ──────────────────────────────────────────────────────────

class BitNetSwarm:
    """Manages BitNet 1.58-bit inference for all Bio-Swarm Nano-Knight species."""

    def __init__(self) -> None:
        self._active_species: list[str] = []
        self._bin_available = BITNET_BIN.exists()

    def available(self) -> bool:
        return self._bin_available

    def infer(
        self,
        species: str,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> BitNetResult:
        t0 = time.perf_counter()
        cfg = SPECIES_MODEL_MAP.get(species.lower(), SPECIES_MODEL_MAP["strigiform"])
        model_path = MODELS_DIR / cfg["gguf"]

        # RAM ceiling check
        ok, ram_msg = _check_ram_ceiling(species, self._active_species)
        if not ok:
            return BitNetResult(
                species=species, model=cfg["model"],
                output="", tokens_generated=0,
                duration_ms=0, ram_mb_used=0,
                error=ram_msg,
            )

        if not self._bin_available or not model_path.exists():
            return self._simulate(species, prompt, cfg, t0)

        # Build bitnet.cpp CLI args
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        cmd = [
            str(BITNET_BIN),
            "-m", str(model_path),
            "-p", full_prompt,
            "-n", str(cfg["token_budget"]),
            "-c", str(cfg["ctx"]),
            "-t", str(cfg["n_threads"]),
            "--no-display-prompt",
            "-f", "json",
        ]

        self._active_species.append(species)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                timeout=30,
                cwd=str(CAMELOT_HOME),
            )
            output = result.stdout.strip()
            tokens = len(output.split())
            ms = (time.perf_counter() - t0) * 1000
            return BitNetResult(
                species=species, model=cfg["model"],
                output=output, tokens_generated=tokens,
                duration_ms=ms, ram_mb_used=SPECIES_RAM_MB.get(species, 512),
            )
        except subprocess.TimeoutExpired:
            err = f"BitNet timeout (30s) for species={species}"
            return BitNetResult(species=species, model=cfg["model"],
                                output="", tokens_generated=0,
                                duration_ms=30_000, ram_mb_used=0, error=err)
        except Exception as e:
            return BitNetResult(species=species, model=cfg["model"],
                                output="", tokens_generated=0,
                                duration_ms=0, ram_mb_used=0, error=str(e))
        finally:
            if species in self._active_species:
                self._active_species.remove(species)

    def _simulate(self, species: str, prompt: str, cfg: dict, t0: float) -> BitNetResult:
        """Fallback: route to Ollama when bitnet.cpp binary or model not yet downloaded."""
        ollama_map = {
            "formica":    "qwen3:1.7b",
            "pongid":     "gemma4:latest",
            "castor":     "qwen2.5-coder:3b",
            "arachne":    "qwen3:4b",
            "simian":     "qwen3:1.7b",
            "strigiform": "qwen3.5:0.8b",
        }
        ollama_model = ollama_map.get(species.lower(), "qwen3:1.7b")
        try:
            result = subprocess.run(
                ["ollama", "run", ollama_model, prompt[:cfg["token_budget"] * 4]],
                capture_output=True, text=True, timeout=60,
                cwd=str(CAMELOT_HOME),
            )
            output = result.stdout.strip()
            if output:
                ms = (time.perf_counter() - t0) * 1000
                return BitNetResult(
                    species=species, model=f"ollama/{ollama_model}",
                    output=output, tokens_generated=len(output.split()),
                    duration_ms=ms, ram_mb_used=SPECIES_RAM_MB.get(species, 512),
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        ms = (time.perf_counter() - t0) * 1000
        return BitNetResult(
            species=species, model=cfg["model"],
            output=f"[STUB] bitnet.cpp + ollama both unavailable. species={species} prompt_preview={prompt[:60]}",
            tokens_generated=0, duration_ms=ms, ram_mb_used=0,
        )

    def status(self) -> dict:
        total_models = sum(1 for cfg in SPECIES_MODEL_MAP.values()
                          if (MODELS_DIR / cfg["gguf"]).exists())
        return {
            "binary_available": self._bin_available,
            "binary_path": str(BITNET_BIN),
            "models_dir": str(MODELS_DIR),
            "models_found": total_models,
            "models_total": len(set(c["gguf"] for c in SPECIES_MODEL_MAP.values())),
            "active_species": self._active_species,
            "ram_estimated_mb": _estimate_total_ram_mb(self._active_species),
            "ram_ceiling_mb": 7_800,
            "species": {
                k: {"model": v["model"], "token_budget": v["token_budget"],
                    "ram_mb": SPECIES_RAM_MB.get(k, 512)}
                for k, v in SPECIES_MODEL_MAP.items()
            },
        }


# ── Install helper ────────────────────────────────────────────────────────────

INSTALL_STEPS = """
# BitNet 1.58-bit Install Guide — CAMELOT Apex OS

## Step 1: Clone bitnet.cpp
git clone https://github.com/microsoft/BitNet.git C:/Users/vizio/CAMELOT_OS/build/bitnet
cd C:/Users/vizio/CAMELOT_OS/build/bitnet
pip install -r requirements.txt

## Step 2: Download models (HuggingFace)
python utils/install_bitnet.py -m microsoft/bitnet_b1.58-2B-4T -q i2_s
# Model lands in: ./models/bitnet_b1.58-2B-4T/

## Step 3: Build (requires CMake + MSVC or MinGW)
cmake -B build -DLLAMA_NATIVE=ON
cmake --build build --config Release

## Step 4: Copy binary
cp build/bin/Release/llama-cli.exe C:/Users/vizio/CAMELOT_OS/bin/bitnet.cpp

## Step 5: Copy models
mkdir -p C:/Users/vizio/CAMELOT_OS/03_VAULT/models/bitnet/
cp models/bitnet_b1.58-2B-4T/*.gguf C:/Users/vizio/CAMELOT_OS/03_VAULT/models/bitnet/

## Verification
C:/Users/vizio/CAMELOT_OS/bin/bitnet.cpp --version
python 03_VAULT/training/configs/bitnet_swarm.py
"""


if __name__ == "__main__":
    swarm = BitNetSwarm()
    print(json.dumps(swarm.status(), indent=2))
    if not swarm.available():
        print("\n--- Install Steps ---")
        print(INSTALL_STEPS)
    else:
        result = swarm.infer("formica", "List files in /tmp sorted by size")
        print(f"\nTest inference: {result}")
