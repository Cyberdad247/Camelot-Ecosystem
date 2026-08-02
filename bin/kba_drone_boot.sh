#!/usr/bin/env bash
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
#
# KBA Drone Boot — stand up a Camelot-OS empire-drone for KickBox Audio on the
# tailnet. Run this ON the kba-services box. It joins the tailnet (tag:empire-drone),
# auto-detects its own tailnet IP, and launches the governed drone node.
#
#   TS_AUTHKEY=tskey-...            (optional) reusable/ephemeral tailnet auth key
#   WEBHOOK_SECRET=...             REQUIRED  shared HMAC secret for bridge auth
#   CAMELOT_CARTRIDGE_HMAC_KEY=... REQUIRED* cartridge signing key (*or Ed25519 keygen)
#   OMNI_ROUTER_URL=http://<omni>  (optional) register this drone with the router
#
# Usage:
#   WEBHOOK_SECRET=... CAMELOT_CARTRIDGE_HMAC_KEY=... bash bin/kba_drone_boot.sh
#   # bind a specific tailnet IP instead of auto-detect:
#   KBA_DRONE_HOST=100.125.205.66 ... bash bin/kba_drone_boot.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_ID="${KBA_NODE_ID:-kba-drone-1}"
PORT="${KBA_DRONE_PORT:-9000}"   # empire-drone worker range 9000-9100
HOSTNAME_TS="${KBA_TS_HOSTNAME:-kba-services}"

echo "== Camelot-OS KBA Drone Boot =="
echo "   repo: $REPO_ROOT"

# 1. Preconditions -----------------------------------------------------------
if [ -z "${WEBHOOK_SECRET:-}" ]; then
  echo "FATAL: WEBHOOK_SECRET is required (bridge HMAC auth)." >&2; exit 2
fi
if [ -z "${CAMELOT_CARTRIDGE_HMAC_KEY:-}" ] && [ -z "${CAMELOT_CARTRIDGE_PRIVATE_KEY:-}" ]; then
  if [ ! -f "$HOME/.camelot/cartridge_ed25519" ]; then
    echo "FATAL: no cartridge signing key. Set CAMELOT_CARTRIDGE_HMAC_KEY, or run:" >&2
    echo "       python -m cartridge.cartridge_crypto keygen" >&2
    exit 2
  fi
fi

# 2. Join the tailnet as an empire-drone -------------------------------------
if command -v tailscale >/dev/null 2>&1; then
  if [ -n "${TS_AUTHKEY:-}" ]; then
    echo "-- tailscale up (tag:empire-drone, hostname=$HOSTNAME_TS)"
    sudo tailscale up --authkey "$TS_AUTHKEY" \
      --advertise-tags=tag:empire-drone --hostname "$HOSTNAME_TS" --ssh || true
  fi
  TAILNET_IP="$(tailscale ip -4 2>/dev/null | head -1 || true)"
else
  echo "WARN: tailscale not found on PATH — the drone will bind a local IP only." >&2
  TAILNET_IP=""
fi

HOST="${KBA_DRONE_HOST:-${TAILNET_IP:-127.0.0.1}}"
if [ "$HOST" = "127.0.0.1" ]; then
  echo "WARN: binding loopback (no tailnet IP detected). The drone won't be reachable over the tailnet." >&2
fi
echo "-- binding $HOST:$PORT  (tailnet_ip=${TAILNET_IP:-none})"

# 3. Launch the governed drone ----------------------------------------------
cd "$REPO_ROOT"
EXTRA=()
[ -n "${OMNI_ROUTER_URL:-}" ] && EXTRA+=(--register-url "$OMNI_ROUTER_URL")
# Enable enterprise trust + RBAC if a trust store / rbac overlay is present.
[ -f "$HOME/.camelot/trust_store.json" ] && EXTRA+=(--enterprise-trust)
[ -f "$HOME/.camelot/cartridge_rbac.json" ] && EXTRA+=(--rbac)

exec python -m control_plane.drone_node \
  --node-id "$NODE_ID" --host "$HOST" --port "$PORT" "${EXTRA[@]}"
