#!/usr/bin/env bash
# N082: Installation and deployment script
set -e

echo "[+] Extracting bundle to /opt/htmx-docs..."
sudo mkdir -p /opt/htmx-docs
sudo tar -xzvf htmx-docs-release.tar.gz -C /opt/htmx-docs

echo "[+] Securing permissions..."
sudo chown -R sys-docs:sys-docs /opt/htmx-docs

echo "[+] Installing systemd service (N040)..."
sudo cp deploy/htmx-docs.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now htmx-docs

echo "[+] Appending Caddy configuration (N041)..."
# Assuming standard Caddy imports from /etc/caddy/conf.d/
sudo cp deploy/Caddyfile /etc/caddy/conf.d/htmx-docs.caddy
sudo systemctl reload caddy

echo "[+] N082 Deployment complete. Service is live behind Caddy."
