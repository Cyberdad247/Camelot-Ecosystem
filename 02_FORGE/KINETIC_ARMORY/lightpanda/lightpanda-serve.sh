#!/usr/bin/env bash
# ============================================================
# Lightpanda CDP Server Launcher
# Camelot Apex OS — Kinetic Armory
# Exposes headless browser at ws://127.0.0.1:9222
# 16x lighter than Chromium — preserves 8GB RAM ceiling
# ============================================================

set -euo pipefail

LIGHTPANDA_BIN="${LIGHTPANDA_BIN:-./lightpanda}"
LIGHTPANDA_HOST="${LIGHTPANDA_HOST:-127.0.0.1}"
LIGHTPANDA_PORT="${LIGHTPANDA_PORT:-9222}"
LIGHTPANDA_URL="https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-x86_64-linux"

echo "[KINETIC] Lightpanda CDP Server"
echo "  Host: ${LIGHTPANDA_HOST}:${LIGHTPANDA_PORT}"

# --- Auto-install if binary not found ---
if [ ! -f "${LIGHTPANDA_BIN}" ]; then
    echo "[KINETIC] Binary not found. Downloading..."
    curl -L -o "${LIGHTPANDA_BIN}" "${LIGHTPANDA_URL}"
    chmod a+x "${LIGHTPANDA_BIN}"
    echo "[KINETIC] Downloaded and made executable."
fi

# --- Verify binary ---
if [ ! -x "${LIGHTPANDA_BIN}" ]; then
    echo "[ERROR] ${LIGHTPANDA_BIN} is not executable."
    exit 1
fi

# --- Kill stale instance if running ---
if lsof -ti:"${LIGHTPANDA_PORT}" >/dev/null 2>&1; then
    echo "[KINETIC] Port ${LIGHTPANDA_PORT} in use. Killing stale process..."
    kill "$(lsof -ti:"${LIGHTPANDA_PORT}")" 2>/dev/null || true
    sleep 1
fi

# --- Launch ---
echo "[KINETIC] Starting Lightpanda CDP server..."
exec "${LIGHTPANDA_BIN}" serve \
    --host "${LIGHTPANDA_HOST}" \
    --port "${LIGHTPANDA_PORT}" \
    --obey-robots \
    --log-format pretty \
    --log-level info
