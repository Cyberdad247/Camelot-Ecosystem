#!/usr/bin/env bash
# ==============================================================================
# Merlin Multivoice Router: Automated Release Setup & Service Deployer
# ==============================================================================

set -e

# Cleanup trap for shared memory
trap 'echo "🧹 [DEPLOY] Cleaning up /dev/shm..."; rm -f /dev/shm/merlin_pcm_shm*' EXIT

echo "🚀 [DEPLOY] Initiating Release Setup for /opt/multivoice-router..."

# Ensure we are in the correct directory
cd /opt/multivoice-router

# 1. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 [DEPLOY] Creating Python Virtual Environment..."
    python3 -m venv venv
fi

# 2. Install dependencies
echo "📦 [DEPLOY] Installing packages from requirements.txt..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. Apply Systemd configuration if available and running with systemd
if [ -d "/etc/systemd/system" ]; then
    echo "⚙️ [DEPLOY] Configuring Systemd Service..."
    sudo cp -f << 'EOF' /etc/systemd/system/multivoice-router.service
[Unit]
Description=Merlin Multivoice Router Service
After=network.target

[Service]
User=vizio
WorkingDirectory=/opt/multivoice-router
ExecStart=/opt/multivoice-router/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    echo "⚙️ [DEPLOY] Reloading systemd daemon & restarting service..."
    sudo systemctl daemon-reload
    sudo systemctl enable multivoice-router.service
    sudo systemctl restart multivoice-router.service
    echo "✅ [DEPLOY] Systemd service is up and running."
else
    echo "⚠️ [DEPLOY] systemd not detected. You can run manually via: ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000"
fi

echo "🎉 [DEPLOY] Release Setup completed successfully!"
