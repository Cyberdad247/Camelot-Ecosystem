#!/usr/bin/env bash
set -euo pipefail

echo "Installing Camelot Reya Edge daemon..."
sudo cp infra/systemd/camelot-reya-edge.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable camelot-reya-edge.service
sudo systemctl restart camelot-reya-edge.service
echo "Camelot Reya Edge daemon active and bounded under cgroups v2."
