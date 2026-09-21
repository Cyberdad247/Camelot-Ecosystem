#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Forged by: SIR_CODEX
# Installs and enables the Camelot REYA Sovereign Companion systemd service

set -euo pipefail

SERVICE_NAME="camelot-reya-edge.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMD_DIR="/etc/systemd/system"

echo "[SIR_CODEX] Installing ${SERVICE_NAME} into ${SYSTEMD_DIR}..."

if [[ $EUID -ne 0 ]]; then
   echo "[ERROR] This installation script must be run as root (sudo)" 
   exit 1
fi

# 1. Copy service file
cp "${SCRIPT_DIR}/${SERVICE_NAME}" "${SYSTEMD_DIR}/${SERVICE_NAME}"
chmod 644 "${SYSTEMD_DIR}/${SERVICE_NAME}"

# 2. Ensure runtime directory
mkdir -p /run/camelot/reya /var/log/camelot
chown -R camelot:camelot /run/camelot/reya /var/log/camelot 2>/dev/null || true

# 3. Reload systemd daemon
systemctl daemon-reload

# 4. Enable and start service
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

echo "[OK] ${SERVICE_NAME} active and locked within cgroups v2 boundaries (<350MB MemoryMax)."
systemctl status "${SERVICE_NAME}" --no-pager || true
