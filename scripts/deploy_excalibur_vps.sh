#!/usr/bin/env bash
# ==============================================================================
# CAMELOT-OS VPS HUB — EXCALIBUR COCKPIT UI SYNC & DEPLOYMENT SCRIPT
# ==============================================================================
# Sovereign VPS Host: 162.35.107.134 / kba-services (100.71.218.75 / 100.110.180.18)
# Target Web Root: /var/www/camelot
# Caddy Gateway Config: /etc/caddy/Caddyfile
# ==============================================================================

set -euo pipefail

echo "🛡️ [CAMELOT_VPS] Deploying Excalibur Cockpit & 3D Celestial Vocal HUD to VPS Hub..."

DEST_DIR="/var/www/camelot"
SRC_DIR="./apps/excalibur-s26-orb"

# 1. Create Web Root Directory
mkdir -p "${DEST_DIR}"

# 2. Synchronize Static Files & Assets
echo "📦 Copying HTML, CSS, JS, Audio, and 3D Assets..."
cp -r ${SRC_DIR}/* "${DEST_DIR}/"

# 3. Ensure Proper Permissions
chmod -R 755 "${DEST_DIR}"
echo "✅ Permissions set for /var/www/camelot"

# 4. Copy & Reload Caddyfile
if command -v caddy &> /dev/null; then
    echo "🔄 Reloading Caddy Reverse Proxy..."
    cp ./infra/caddy/Caddyfile /etc/caddy/Caddyfile
    caddy reload --config /etc/caddy/Caddyfile || systemctl reload caddy
    echo "🎉 [SUCCESS] Excalibur UI is now live on VPS Hub (http://162.35.107.134 / http://100.71.218.75)!"
else
    echo "⚠️ Caddy not installed in this environment. Files staged at ${DEST_DIR}."
fi
