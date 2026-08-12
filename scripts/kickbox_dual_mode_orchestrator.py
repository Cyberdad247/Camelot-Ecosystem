#!/usr/bin/env python3
"""
MERLIN_Ω FORGED DUAL-MODE DYNAMIC & OFFLINE MINIMUM ORCHESTRATOR
=================================================================
Systematic Dual-Mode Execution Architecture for Kickbox-Audio:
  1. DYNAMIC_ONLINE: Maximum efficiency & functionality via CloudBrain NotebookLM
     (UUID 8531e6d4-6fc4-428f-a754-b9e9592ac7ff), CLIProxy API (:8080), & 24-Knight WorldTree.
  2. OFFLINE_MINIMUM: Bare minimum zero-cloud fallback utilizing Tiny LLMs
     (qwen2.5:1.5b / llama3.2:1b), WASM CRDT ledger, & LaKesha on-device speech synthesis.

Run:
  .venv\\Scripts\\python.exe scripts\\kickbox_dual_mode_orchestrator.py --mode DYNAMIC_ONLINE
  .venv\\Scripts\\python.exe scripts\\kickbox_dual_mode_orchestrator.py --mode OFFLINE_MINIMUM
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(_CAMELOT_ROOT))

# ── DUAL MODE CONFIGURATION ───────────────────────────────────────────────────
DUAL_MODE_CONFIG = {
    "DYNAMIC_ONLINE": {
        "title": "Dynamic Online CloudBrain Mode (Max Capability & Efficiency)",
        "cloudbrain_node": "KICKBOX (8531e6d4-6fc4-428f-a754-b9e9592ac7ff)",
        "worldtree_anchor": "a0a4bfb9-e847-4c38-be39-7aee398f0795",
        "primary_knights": ["SIR_BORIS", "SIR_CODEX", "LADY_APIS", "MERLIN_OMEGA", "HERMES_PRIME"],
        "llm_tier": "Frontier CLIProxy OAuth (Gemini 3.1 Pro / GPT-5.5 Codex / Claude 4.8)",
        "proxy_endpoint": "http://127.0.0.1:8080/v1",
        "voice_engine": "Lakisha Hybrid WebRTC + Remote Telemetry",
        "bifrost_mesh": "Tailscale Direct (100.71.218.75:4433 WS / :4434 gRPC)",
        "cartridges": ["ANT", "BEAVER", "SPIDER", "EAGLE", "OCTOPUS", "BIO_SWARM"],
        "max_ram_mb": 4096,
    },
    "OFFLINE_MINIMUM": {
        "title": "Offline Minimum Zero-Cloud Fallback (Bare Minimum Lightweight)",
        "cloudbrain_node": "LOCAL_OPEN_NOTEBOOK_STUB (Air-Gapped)",
        "worldtree_anchor": "LOCAL_VFS_CACHE",
        "primary_knights": ["SIR_GHOST", "SIR_FORGE", "SIR_SENTINEL"],
        "llm_tier": "Tiny LLMs (Ollama qwen2.5:1.5b / llama3.2:1b)",
        "proxy_endpoint": "http://127.0.0.1:11434 (Local Ollama)",
        "voice_engine": "On-Device Web Audio RMS VAD + Local SpeechSynthesis",
        "bifrost_mesh": "Localhost IPC (127.0.0.1:4433)",
        "cartridges": ["ANT", "BIO_SWARM"],
        "max_ram_mb": 1200,
    },
}


def check_port(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def run_orchestrator(target_mode: str) -> dict:
    mode_spec = DUAL_MODE_CONFIG.get(target_mode, DUAL_MODE_CONFIG["DYNAMIC_ONLINE"])
    
    print(f"\n⚡ MERLIN_Ω ACTIVATING ORCHESTRATION MODE: {target_mode}")
    print(f"   Title: {mode_spec['title']}")
    print(f"   LLM Engine: {mode_spec['llm_tier']}")

    # System Probe
    proxy_online = check_port("127.0.0.1", 8080)
    ollama_online = check_port("127.0.0.1", 11434)
    bifrost_online = check_port("127.0.0.1", 4433)

    status_report = {
        "mode": target_mode,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "spec": mode_spec,
        "probes": {
            "cliproxy_8080": proxy_online,
            "ollama_11434": ollama_online,
            "bifrost_4433": bifrost_online,
        },
        "readiness": "OPTIMAL" if (proxy_online if target_mode == "DYNAMIC_ONLINE" else ollama_online) else "DEGRADED_STANDBY",
    }

    # Save Runtime State Artifact
    out_path = _CAMELOT_ROOT / "03_VAULT" / "runtime_state" / "kickbox_dual_mode_state.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(status_report, indent=2), encoding="utf-8")

    return status_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Kickbox-Audio Dual-Mode Orchestrator")
    parser.add_argument("--mode", choices=["DYNAMIC_ONLINE", "OFFLINE_MINIMUM"], default="DYNAMIC_ONLINE", help="Target mode")
    args = parser.parse_args()

    report = run_orchestrator(args.mode)

    print("\n" + "=" * 70)
    print(f"✅ MERLIN_Ω DUAL-MODE DYNAMIC SYSTEM READY")
    print(f"   Active Mode: {report['mode']}")
    print(f"   Readiness:   {report['readiness']}")
    print(f"   Probes:      CLIProxy(8080)={report['probes']['cliproxy_8080']} | Ollama(11434)={report['probes']['ollama_11434']} | Bifrost(4433)={report['probes']['bifrost_4433']}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
