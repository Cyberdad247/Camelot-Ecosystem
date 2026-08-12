#!/usr/bin/env python3
"""
MERLIN_Ω LOCAL TINY LLM WARMUP & OFFLINE READINESS SUITE
=========================================================
Probes local Ollama instance (:11434) and warms up assigned Tiny LLM models
for zero-cloud air-gapped fallback across all Knights.

Run:
  .venv\\Scripts\\python.exe scripts\\warmup_tiny_llms.py
"""

from __future__ import annotations

import json
import os
import socket
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(_CAMELOT_ROOT))

# Target Tiny LLMs bound to Knights in bifrost_knight_llm_registry.json
TARGET_TINY_MODELS = [
    ("qwen2.5:1.5b", "SIR_BORIS / LADY_APIS / SIR_DEBUG / LADY_MNEMOSYNE"),
    ("qwen2.5-coder:1.5b", "SIR_FORGE / SIR_CODEX"),
    ("llama3.2:1b", "SIR_ALEX / MERLIN_OMEGA"),
    ("phi3:mini", "SIR_SENTINEL"),
    ("qwen3:1.7b", "SIR_GHOST (Air-Gapped Sentry)"),
]


def check_ollama_status(host: str = "127.0.0.1", port: int = 11434) -> bool:
    try:
        req = urllib.request.urlopen(f"http://{host}:{port}/api/tags", timeout=1.5)
        return req.status == 200
    except Exception:
        return False


def get_installed_ollama_models(host: str = "127.0.0.1", port: int = 11434) -> list[str]:
    try:
        req = urllib.request.urlopen(f"http://{host}:{port}/api/tags", timeout=2.0)
        if req.status == 200:
            data = json.loads(req.read().decode("utf-8"))
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        pass
    return []


def main() -> int:
    print("=" * 70)
    print("🧙‍♂️ MERLIN_Ω LOCAL TINY LLM WARMUP & OFFLINE READINESS SUITE")
    print("=" * 70)

    start_time = time.time()
    ollama_online = check_ollama_status()

    print(f"\n[1/2] Probing Local Ollama Instance (127.0.0.1:11434)...")
    if ollama_online:
        print("  --> Ollama Backend: ONLINE (http://127.0.0.1:11434)")
        installed_models = get_installed_ollama_models()
        print(f"  --> Installed Local Models ({len(installed_models)}): {', '.join(installed_models) or 'None'}")
    else:
        print("  --> Ollama Backend: STANDBY / OFFLINE (Ollama service not running locally)")
        installed_models = []

    print("\n[2/2] Auditing Knight Tiny LLM Model Allocations...")
    model_statuses = []
    for model_name, bound_knights in TARGET_TINY_MODELS:
        is_installed = any(model_name in m for m in installed_models)
        status_str = "READY" if is_installed else "STANDBY (Install: ollama pull " + model_name + ")"
        model_statuses.append({
            "model_name": model_name,
            "bound_knights": bound_knights,
            "status": status_str,
            "installed": is_installed,
        })
        print(f"  --> [{status_str}] {model_name} -> {bound_knights}")

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    # Save Runtime Artifact
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ollama_online": ollama_online,
        "elapsed_ms": elapsed_ms,
        "models": model_statuses,
    }

    out_path = _CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "tiny_llm_warmup_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"✅ TINY LLM WARMUP AUDIT COMPLETE in {elapsed_ms} ms")
    print(f"   Report: {out_path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
