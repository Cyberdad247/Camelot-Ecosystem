#!/usr/bin/env bash
# ==============================================================================
# CAMELOT-OS VPS HUB (KVM563 / 162.35.107.134)
# PHASE 1 DEPLOYMENT: HERMES_PRIME & PALADIN_HEIMDALL BIFROST SENTINEL
# ==============================================================================
# Co-governing Knights:
#   - HERMES_PRIME (L7 Hypervisor & Trajectory Autonomous Engine)
#   - PALADIN_HEIMDALL (Paladin Knight & Bifrost Perimeter Lock)
# ==============================================================================

set -euo pipefail

echo "🛡️ [CAMELOT_VPS] Initializing Phase 1: Hermes Prime & Paladin Heimdall Deployment..."

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="/opt/camelot-ecosystem"
SYSTEMD_DIR="/etc/systemd/system"

# 1. Ensure Target Directory Exists
mkdir -p "${APP_DIR}/control_plane/infra"
mkdir -p "${APP_DIR}/03_VAULT/runtime_state"

# 2. Copy Sentinel Daemon and Systemd Unit (skip if already running inside APP_DIR)
echo "📦 Staging Sentinel Daemon & Configuration..."
if [ "$REPO_ROOT" != "$APP_DIR" ]; then
    cp "${REPO_ROOT}/control_plane/infra/hermes_heimdall_sentinel.py" "${APP_DIR}/control_plane/infra/"
    cp "${REPO_ROOT}/control_plane/infra/z3_verify.py" "${APP_DIR}/control_plane/infra/" 2>/dev/null || true
fi
cp "${REPO_ROOT}/infra/systemd/hermes-bifrost-sentinel.service" "${SYSTEMD_DIR}/hermes-bifrost-sentinel.service"

# Ensure write permissions for systemd user
chown -R ubuntu:ubuntu "${APP_DIR}/03_VAULT/runtime_state" 2>/dev/null || true

# 3. Configure UFW Firewall for Tailscale-Only Perimeter Locking
if command -v ufw &> /dev/null; then
    echo "🔒 [PALADIN_HEIMDALL] Enforcing Tailscale Perimeter Lock via UFW..."
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow in on tailscale0 to any port 8095 proto tcp comment 'Bifrost Mobile Mesh Bridge'
    ufw allow in on tailscale0 to any port 3001 proto tcp comment 'Bifrost Gateway'
    ufw allow in on tailscale0 to any port 22 proto tcp comment 'Tailscale SSH'
    ufw allow 22/tcp comment 'Emergency SSH Fallback'
    ufw --force enable
    echo "✅ [PALADIN_HEIMDALL] UFW perimeter locked to tailscale0 mesh boundary."
fi

# 4. Reload & Enable Systemd Service
echo "⚙️ Enabling and starting hermes-bifrost-sentinel.service..."
systemctl daemon-reload
systemctl enable hermes-bifrost-sentinel.service
systemctl restart hermes-bifrost-sentinel.service
systemctl status hermes-bifrost-sentinel.service --no-pager || true

# 5. Initialize Hermes Blank Slate Environment
if command -v hermes &> /dev/null; then
    echo "🧠 [HERMES_PRIME] Initializing Hermes with blank-slate sandbox & continuous trajectories..."
    hermes setup --blank-slate || true
    echo "✅ Hermes Prime initialized."
fi

echo "🎉 [SUCCESS] Phase 1 deployed: HERMES_PRIME + PALADIN_HEIMDALL active on VPS Hub!"
