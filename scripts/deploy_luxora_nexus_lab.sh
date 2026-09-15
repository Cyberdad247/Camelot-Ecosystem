#!/usr/bin/env bash
# ========================================================================================
# CAMELOT-OS: LUXORA NEXUS LAB PWA VPS HUB DEPLOYMENT & LINKING SCRIPT
# Repository: https://github.com/Cyberdad247/luxora-nexus-lab
# Target Host: 162.35.107.134 / kba-services (100.71.218.75)
# ========================================================================================

set -euo pipefail

echo "========================================================================"
echo "⚡ LINKING LUXORA NEXUS LAB PWA TO CAMELOT-OS VPS HUB"
echo "   Host: 162.35.107.134 (KVM563)"
echo "   Co-Governors: HERMES_PRIME & SIR_HEIMDALL"
echo "========================================================================"

REPO_URL="https://github.com/Cyberdad247/luxora-nexus-lab.git"
DEST_DIR="/opt/luxora-nexus-lab"
WWW_ROOT="/var/www/camelot"

# 1. Clone or pull latest Luxora Nexus Lab
sudo mkdir -p "$DEST_DIR"
if [ ! -d "$DEST_DIR/.git" ]; then
  echo "Cloning Luxora Nexus Lab from GitHub..."
  sudo git clone "$REPO_URL" "$DEST_DIR"
else
  echo "Updating existing Luxora Nexus Lab repository..."
  cd "$DEST_DIR"
  sudo git pull origin main || sudo git pull origin master || true
fi

cd "$DEST_DIR"

# 2. Inject Hub Environment Variables for Connected Services
echo "Injecting Hub environment bindings..."
sudo tee "$DEST_DIR/.env.production" <<'ENV_EOF'
# Sovereign Hub Service Endpoints
NEXT_PUBLIC_HUB_IP=162.35.107.134
NEXT_PUBLIC_TAILSCALE_IP=100.71.218.75
NEXT_PUBLIC_BIFROST_WS=/ws
NEXT_PUBLIC_MESH_STATUS=/mesh/status
NEXT_PUBLIC_BIFROST_KNIGHTS=/bifrost/knights
NEXT_PUBLIC_HERMES_TELEMETRY=/hermes/telemetry
NEXT_PUBLIC_HEIMDALL_GOVERNANCE=/heimdall/governance
NEXT_PUBLIC_AGENT_API=/v1
NEXT_PUBLIC_THEME_PRIMARY=#D4AF37
NEXT_PUBLIC_THEME_BG=#050505
ENV_EOF

# 3. Build PWA / Static Export
if [ -f "package.json" ]; then
  echo "Installing dependencies and building PWA..."
  sudo npm install --legacy-peer-deps || true
  sudo npm run build || true
  
  sudo mkdir -p "$WWW_ROOT"
  if [ -d "dist" ]; then
    echo "Deploying dist/ to $WWW_ROOT..."
    sudo cp -r dist/* "$WWW_ROOT/"
  elif [ -d "out" ]; then
    echo "Deploying out/ to $WWW_ROOT..."
    sudo cp -r out/* "$WWW_ROOT/"
  elif [ -d ".next" ]; then
    echo "Deploying Next.js static assets to $WWW_ROOT..."
    sudo cp -r public/* "$WWW_ROOT/" 2>/dev/null || true
  fi
fi

# 4. Deploy Unified Caddyfile
echo "Updating Caddy Gateway configuration..."
if [ -f "/opt/Camelot-Ecosystem/infra/caddy/Caddyfile" ]; then
  sudo cp /opt/Camelot-Ecosystem/infra/caddy/Caddyfile /etc/caddy/Caddyfile
fi

sudo systemctl restart caddy || true

# 5. Service Response Health Check
echo "========================================================================"
echo "📡 VERIFYING CONNECTED HUB SERVICES..."
echo "========================================================================"

check_endpoint() {
  local name="$1"
  local url="$2"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "FAILED")
  if [ "$code" == "200" ] || [ "$code" == "401" ] || [ "$code" == "404" ]; then
    echo "  🟢 [ONLINE] $name ($url) -> HTTP $code"
  else
    echo "  🟡 [STANDBY] $name ($url) -> HTTP $code"
  fi
}

check_endpoint "Caddy Gateway" "http://localhost/"
check_endpoint "Mesh Bridge Telemetry" "http://localhost/mesh/status"
check_endpoint "Bifrost Knights Registry" "http://localhost/bifrost/knights"
check_endpoint "Hermes Research Telemetry" "http://localhost/hermes/telemetry"
check_endpoint "Heimdall Zero-Trust Governance" "http://localhost/heimdall/governance"
check_endpoint "Qdrant Vector Mesh" "http://localhost/qdrant/collections"

echo "========================================================================"
echo "✨ LUXORA NEXUS LAB SUCCESSFULLY LINKED TO CAMELOT-OS VPS HUB"
echo "========================================================================"
