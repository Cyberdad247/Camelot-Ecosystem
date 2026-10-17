#!/bin/bash
# CAMELOT-OS: The Glass Panel Ignition
set -e

echo "=========================================================="
echo " 👁️ IGNITE PHASE 4: MOUNTING THE BIFROST BOARD"
echo "=========================================================="

# Ensure Node & npm paths across environments
export PATH="/c/Program Files/nodejs:/mnt/c/Program Files/nodejs:$PATH"

cd apps/bifrost-board

echo "[⚡] Installing React, Zustand, and Tailwind dependencies..."
if command -v npm.cmd >/dev/null 2>&1; then
    npm.cmd install
elif command -v npm >/dev/null 2>&1; then
    npm install
elif [ -f "/mnt/c/Program Files/nodejs/npm" ]; then
    "/mnt/c/Program Files/nodejs/npm" install
elif [ -f "/c/Program Files/nodejs/npm" ]; then
    "/c/Program Files/nodejs/npm" install
else
    echo "❌ Error: npm not found in PATH."
    exit 1
fi

echo "[🛡️] Booting the Luxury Minimalist Brutalism UI..."
echo "     Access the HUD at: http://localhost:5173"
echo "=========================================================="
echo "⚜️_SOVEREIGN_TRUTH"

if command -v npm.cmd >/dev/null 2>&1; then
    npm.cmd run dev
else
    npm run dev
fi
