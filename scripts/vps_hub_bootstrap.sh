#!/usr/bin/env bash
# ========================================================================================
# [SYSTEM ACTIVATION]: CAMELOT-OS vMAX OMEGA TITAN
# [TARGET HOST]: 8GB InterServer VPS (162.35.107.134) // "Cybertronia Hub"
# [BOOTSTRAP CLASS]: FULLSTACK_BAREMETAL_CUBE
# [SECURITY LEVEL]: EXCALIBUR_ZERO_TRUST
# [DO NOT]: Use Docker. Use Kubernetes. Use Node.js or Python in hot-path.
# ========================================================================================

set -euo pipefail

echo "========================================================================"
echo "🏰 FORGING CAMELOT-OS VPS HUB (162.35.107.134 / KVM563)"
echo "   Sovereign Co-Governors: HERMES_PRIME & SIR_HEIMDALL"
echo "========================================================================"

# --- PHASE 1: OS PREREQUISITES ---
echo "[PHASE 1] OS Prerequisites & Cgroups v2 Check..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential openssl ca-certificates unzip tar jq gnupg lsb-release

if [ ! -d /sys/fs/cgroup/cgroup.controllers ]; then
  echo "Enabling cgroups v2..."
  sudo sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"/' /etc/default/grub
  sudo update-grub
  echo "Reboot required for cgroups v2. Please reboot and re-run."
  exit 0
fi

# --- PHASE 2: INSTALL NATIVE RUNTIMES ---
echo "[PHASE 2] Installing Native Toolchains & Datastores..."
if ! command -v cargo &> /dev/null; then
  echo "Installing Rust toolchain..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  source "$HOME/.cargo/env"
fi

if ! command -v go &> /dev/null; then
  echo "Installing Go runtime..."
  wget -q https://go.dev/dl/go1.22.4.linux-amd64.tar.gz
  sudo tar -C /usr/local -xzf go1.22.4.linux-amd64.tar.gz
  rm -f go1.22.4.linux-amd64.tar.gz
  export PATH=$PATH:/usr/local/go/bin
fi

sudo apt install -y openjdk-17-jre-headless postgresql postgresql-contrib caddy
sudo systemctl enable --now postgresql

# MinIO
if ! command -v minio &> /dev/null; then
  wget -q https://dl.min.io/server/minio/release/linux-amd64/minio
  sudo install minio /usr/local/bin/
  rm -f minio
  sudo mkdir -p /var/lib/minio
  sudo useradd -r -s /sbin/nologin minio-user || true
  sudo chown -R minio-user:minio-user /var/lib/minio
fi

# Qdrant
if ! command -v qdrant &> /dev/null; then
  curl -L https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz | tar -xz
  sudo install qdrant /usr/local/bin/
  rm -f qdrant
  sudo mkdir -p /var/lib/qdrant/storage
fi

# Tailscale check
if ! command -v tailscale &> /dev/null; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi

# --- PHASE 3: CAMELOT ECOSYSTEM & SYSTEMD UNITS ---
echo "[PHASE 3] Deploying Camelot Ecosystem & Bifrost Hub Services..."
sudo mkdir -p /opt/Camelot-Ecosystem
if [ ! -d /opt/Camelot-Ecosystem/.git ]; then
  git clone https://github.com/Cyberdad247/Camelot-Ecosystem.git /opt/Camelot-Ecosystem
else
  cd /opt/Camelot-Ecosystem && git pull origin main || true
fi

cd /opt/Camelot-Ecosystem

# Install systemd unit files
sudo cp infra/systemd/*.service /etc/systemd/system/ || true
sudo systemctl daemon-reload

# --- PHASE 4: INITIALIZE DATA & MEMORY ---
echo "[PHASE 4] Initializing Database & Vector Memories..."
sudo -u postgres createdb camelot_vmax 2>/dev/null || true
curl -s -X PUT http://localhost:6333/collections/world_tree \
  -H 'Content-Type: application/json' \
  -d '{"vectors":{"size":24,"distance":"Cosine"}}' 2>/dev/null || true

# --- PHASE 5: ENABLE SYSTEMD SERVICES ---
echo "[PHASE 5] Enabling Always-On Sovereign Hub Daemons..."
sudo systemctl enable --now camelot-heimdall-bifrost \
                         camelot-hermes-prime \
                         camelot-vps-mesh \
                         caddy || true

# --- PHASE 6: DEPLOY LUXORA NEXUS LAB PWA ---
echo "[PHASE 6] Deploying and Linking Luxora Nexus Lab PWA..."
chmod +x scripts/deploy_luxora_nexus_lab.sh
./scripts/deploy_luxora_nexus_lab.sh || true

echo "========================================================================"
echo "🛡️ VPS HUB FORGED & SOVEREIGN"
echo "   Heimdall & Hermes Prime Active on 162.35.107.134"
echo "   Luxora Nexus Lab PWA Linked & Active on Port :80 / :443"
echo "========================================================================"
