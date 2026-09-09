#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# Sovereign S26 Ultra — Termux Daemon Supervisor & Sentinel Bridge
# ==============================================================================
set -euo pipefail

echo "=================================================================="
echo "📱 CAMELOT S26 ULTRA — SOVEREIGN SENTINEL ORB INITIALIZER"
echo "=================================================================="

# Check Termux background wake-lock
if command -v termux-wake-lock &>/dev/null; then
    termux-wake-lock
    echo "  [OK] Termux wake-lock active (24/7 background audio loop)"
fi

# Ensure directories exist
mkdir -p "$HOME/.camelot/excalibur/queue"
mkdir -p "$HOME/.camelot/logs"

# Verify Tailscale on Android
if command -v tailscale &>/dev/null; then
    echo "  [OK] Tailscale detected on S26"
    tailscale ping -c 1 100.110.180.18 || echo "  [WARN] VPS Hub unreachable"
fi

# Launch Background Audio DSP & Streamer (if native binaries exist)
if [ -f "$PREFIX/bin/camelot-audio-dsp" ]; then
    echo "  [START] Starting camelot-audio-dsp..."
    "$PREFIX/bin/camelot-audio-dsp" >> "$HOME/.camelot/logs/audio-dsp.log" 2>&1 &
fi

if [ -f "$PREFIX/bin/camelot-streamer" ]; then
    echo "  [START] Starting camelot-streamer..."
    "$PREFIX/bin/camelot-streamer" >> "$HOME/.camelot/logs/streamer.log" 2>&1 &
fi

echo "=================================================================="
echo "⚔️ S26 ULTRA SENTINEL ORB READY"
echo "   PWA Live at: https://excalibur-s26-orb.vercel.app"
echo "=================================================================="
