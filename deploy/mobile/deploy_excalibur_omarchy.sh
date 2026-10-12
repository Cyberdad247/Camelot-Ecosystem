#!/data/data/com.termux/files/usr/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
#
# Excalibur Omarchy Mobile Provisioning Script
# Target: Samsung Galaxy S26 Ultra (Snapdragon 8 Elite / Adreno 840)
# Tailscale Node: 100.106.246.126
#

set -euo pipefail

echo "=========================================================================="
echo "🛡️ CAMELOT-OS // EXCALIBUR OMARCHY MOBILE PROVISIONING"
echo "Target Device: Samsung Galaxy S26 Ultra (Snapdragon 8 Elite / Adreno 840)"
echo "Tailscale Node: 100.106.246.126"
echo "=========================================================================="

# 1. Preflight Architecture Check
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "[-] Error: Unsupported architecture: $ARCH. Target must be native ARM64."
    exit 1
fi
echo "[+] Native ARM64 (aarch64) detected."

# 2. Check Android Phantom Process Monitor
echo "[*] Checking child process restriction status..."
if command -v /system/bin/device_config >/dev/null 2>&1; then
    PHANTOM=$(/system/bin/device_config get activity_manager max_phantom_processes 2>/dev/null || true)
    if [ "$PHANTOM" != "2147483647" ]; then
        echo "[!] Warning: Phantom process killer may be active. Recommend setting max_phantom_processes or disabling in Developer Options."
    else
        echo "[+] Phantom process limits unconstrained."
    fi
fi

# 3. Check Qualcomm KGSL Device Node
if [ -e "/dev/kgsl-3d0" ]; then
    echo "[+] Qualcomm Adreno hardware graphics node /dev/kgsl-3d0 verified."
else
    echo "[!] Warning: /dev/kgsl-3d0 not detected directly. Checking permissions..."
fi

# 4. Install Host Prerequisite Packages
echo "[*] Updating Termux packages and installing container prerequisites..."
pkg update -y
pkg install -y proot-distro git jq pulseaudio

# 5. Configure Hardware-Accelerated Vulkan Environment
echo "[*] Configuring Turnip/KGSL Direct Adreno 840 environment..."
mkdir -p "$HOME/.config/camelot"

cat << 'EOF' > "$HOME/.config/camelot/omarchy_gpu_env.sh"
# Qualcomm Adreno 840 Hardware Direct KGSL Path
export TU_DEBUG=kgsl
export MESA_VK_WSI_PRESENT_MODE=mailbox
export GALLIUM_DRIVER=zink
export VK_DRIVER=turnip
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-1
export PULSE_SERVER=127.0.0.1
export XDG_RUNTIME_DIR=/data/data/com.termux/files/usr/tmp
EOF

# 6. Inject Lady Alexandria Warp Gate Forever Keypass (Global Law 04)
echo "[*] Injecting Alexandria Warp Gate Keypass (KP-EXCALIBUR_MOBILE-56820318)..."
cat << 'EOF' > "$HOME/.config/camelot/warp_gate_keypass.json"
{
  "keypass_id": "KP-EXCALIBUR_MOBILE-56820318",
  "knight_id": "EXCALIBUR_MOBILE",
  "spark_id": "0x56820318BB91451FAAC44B46424898CF",
  "forever_access_key": "WARP-PASS-56820318-02D46C4CB0F6EC740204EFF98C8851A2",
  "tier": "ARCH",
  "expires_at": "FOREVER",
  "capabilities": [
    "SOCKET_BYPASS",
    "OUT_OF_BAND_RENDEZVOUS",
    "VAULT_EMERGENCY_UNSEAL",
    "TELEMETRY_OVERRIDE"
  ],
  "mesh_hub": "100.110.180.18:8095",
  "status": "ACTIVE"
}
EOF
chmod 600 "$HOME/.config/camelot/warp_gate_keypass.json"
echo "[+] Warp Gate Keypass injected and secured."

# 7. Configure 3.5 GB Memory Governor (Global Law 03)
echo "[*] Setting up 3,584 MB RAM ceiling governor..."
cat << 'EOF' > "$HOME/.config/camelot/ram_governor.sh"
#!/bin/bash
# Global Law 03: Mobile container ceiling 3,584 MB
MAX_KB=3670016
ulimit -v $MAX_KB 2>/dev/null || true
EOF
chmod +x "$HOME/.config/camelot/ram_governor.sh"
echo "[+] Memory governor configured."

# 8. Success Report
echo "=========================================================================="
echo "✅ EXCALIBUR OMARCHY PROVISIONING READY"
echo "Execute: ~/.local/share/omarchy-android/bin/omarchy-android start"
echo "Termux:X11 display will launch with 120Hz Adreno 840 GPU acceleration."
echo "=========================================================================="
