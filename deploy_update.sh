#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/multivoice-router"
SERVICE_NAME="multivoice-router"
GIT_BRANCH="main"
HEALTH_CHECK_URL="http://127.0.0.1:8000/health"

log() { echo -e "\e[32m[DEPLOY $(date +'%Y-%m-%d %H:%M:%S')]\e[0m $1"; }

cd "${APP_DIR}" || exit 1

log "Pulling latest git changes..."
git fetch origin "${GIT_BRANCH}"
git reset --hard "origin/${GIT_BRANCH}"

log "Purging orphaned POSIX shared memory segments..."
rm -f /dev/shm/merlin_* || true

log "Updating virtualenv dependencies..."
./venv/bin/pip install --quiet --upgrade pip
if [[ -f "requirements.txt" ]]; then
  ./venv/bin/pip install --quiet -r requirements.txt
fi

log "Reloading systemd service..."
sudo systemctl reload "${SERVICE_NAME}" || sudo systemctl restart "${SERVICE_NAME}"

log "Verifying health check..."
sleep 2
curl -s "${HEALTH_CHECK_URL}" | grep -q "online" && log "Deployment Succeeded!" || log "Deployment Health Warning!"
