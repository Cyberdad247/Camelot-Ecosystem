#!/usr/bin/env bash
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
