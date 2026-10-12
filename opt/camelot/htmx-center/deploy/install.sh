#!/bin/bash
set -euo pipefail

echo "⚜️ Forging HTMX Command Center..."

# 1. Build Go binary
cd /opt/camelot/htmx-center
go build -o /usr/local/bin/camelot-htmx-center main.go

# 2. Install systemd unit
sudo cp deploy/camelot-htmx.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now camelot-htmx.service

# 3. Verify
curl -s http://localhost:8080/ | grep "Camelot-OS"
echo "✅ HTMX Center is live on port 8080."
