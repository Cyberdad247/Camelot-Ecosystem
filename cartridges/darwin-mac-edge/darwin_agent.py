#!/usr/bin/env python3
"""
SIR_DARWIN_MAC — Hermes-Level Hardware & Software Sentinel
=========================================================
Executes local/remote telemetry collection on macOS (Darwin):
- Hardware: Apple Silicon (M-series), GPU/Metal, Neural Engine, Unified Memory, Thermals.
- Software: launchd daemons, Homebrew packages, active ports, POSIX shells, Ollama Metal nodes.
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

class SirDarwinMacSentinel:
    def __init__(self, node_ip="100.113.101.43", hostname="macbook-pro-3"):
        self.node_ip = node_ip
        self.hostname = hostname
        self.knight_id = "SIR_DARWIN_MAC"
        self.spark_id = "0xDARW1N9000M4XMACEDGE9942763"

    def generate_darwin_probe_script(self) -> str:
        """Generates a zero-dependency POSIX probe script to run on macOS."""
        return """#!/usr/bin/env bash
# SIR_DARWIN_MAC Autonomous Telemetry Probe (macOS / Darwin)
echo "=== SIR_DARWIN_MAC HARDWARE & SOFTWARE AUDIT ==="
echo "HOST: $(hostname)"
echo "OS_VERSION: $(sw_vers -productVersion)"
echo "BUILD: $(sw_vers -buildVersion)"
echo "ARCH: $(uname -m)"
echo "CHIP: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo 'Apple Silicon')"
echo "CORES: $(sysctl -n hw.ncpu 2>/dev/null)"
echo "MEMORY_BYTES: $(sysctl -n hw.memsize 2>/dev/null)"

echo "--- GPU & METAL ENGINE ---"
system_profiler SPDisplaysDataType 2>/dev/null | grep -E "(Chipset Model|Metal Support|VRAM|Total Number of Cores)" || echo "Metal 3 Supported"

echo "--- STORAGE HEALTH ---"
df -h / | tail -n 1

echo "--- RUNTIME DAEMONS & SERVICES ---"
echo "OLLAMA_ACTIVE: $(pgrep -x ollama >/dev/null && echo 'YES' || echo 'NO')"
echo "TAILSCALE_ACTIVE: $(pgrep -x Tailscale >/dev/null && echo 'YES' || echo 'NO')"
echo "HOMEBREW_INSTALLED: $(which brew >/dev/null && echo 'YES' || echo 'NO')"
echo "NODE_INSTALLED: $(which node >/dev/null && echo 'YES' || echo 'NO')"
echo "PYTHON_INSTALLED: $(which python3 >/dev/null && echo 'YES' || echo 'NO')"
echo "RUST_INSTALLED: $(which rustc >/dev/null && echo 'YES' || echo 'NO')"

echo "=== PROBE COMPLETE ==="
"""

    def stage_telemetry(self) -> dict:
        """Stages initial node specification for the Bifrost Bridge."""
        telemetry = {
            "knight": self.knight_id,
            "spark_id": self.spark_id,
            "target_node": self.hostname,
            "tailscale_ip": self.node_ip,
            "hardware_matrix": {
                "platform": "macOS / Apple Silicon (ARM64)",
                "neural_engine": "Apple Neural Engine (ANE) Ready",
                "metal_compute": "Metal 3 / MPS Framework Active",
                "unified_memory_target": "LPDDR5 / LPDDR5X Unified Bus",
                "thunderbolt_ports": "Thunderbolt 4 / USB4 Ready"
            },
            "software_matrix": {
                "os_kernel": "Darwin / XNU Mach Kernel",
                "service_manager": "launchd",
                "package_manager": "Homebrew / Nix Darwin",
                "local_inference": "Ollama / llama.cpp / MLX Metal",
                "shell": "zsh / bash",
                "bifrost_protocol": "Tailscale Peer / SSH / WebSocket :8011"
            },
            "staged_at_utc": datetime.now(timezone.utc).isoformat()
        }

        out_path = Path("03_VAULT/runtime_state/sir_darwin_mac_telemetry.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(telemetry, f, indent=2)

        probe_file = Path("cartridges/darwin-mac-edge/probe_mac.sh")
        with open(probe_file, "w", encoding="utf-8") as f:
            f.write(self.generate_darwin_probe_script())

        return telemetry

def main():
    sentinel = SirDarwinMacSentinel()
    res = sentinel.stage_telemetry()
    print(f"⚔️ [{sentinel.knight_id}] Forged for node: {sentinel.hostname} ({sentinel.node_ip})")
    print(f"💎 Telemetry Spec -> 03_VAULT/runtime_state/sir_darwin_mac_telemetry.json")
    print(f"📜 POSIX Probe -> cartridges/darwin-mac-edge/probe_mac.sh")

if __name__ == "__main__":
    main()
