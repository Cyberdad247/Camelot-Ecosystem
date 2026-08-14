#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# Camelot-OS // Kinetic Local Engine Control Script (scripts/ctl.sh)
# Target Node: Bare-metal Laptop Server (Tailscale IP: 100.71.218.75)

set -e

TAILSCALE_IP="100.71.218.75"
HTTP_PORT="4433"
GRPC_PORT="4434"

function usage() {
  echo "Usage: $0 {start|stop|restart|status|health}"
  echo "  start    - Build & run local Bifrost mesh native binary"
  echo "  stop     - Terminate local Bifrost mesh process"
  echo "  restart  - Restart local Bifrost engine"
  echo "  status   - Show process status and listening ports"
  echo "  health   - Probe http://$TAILSCALE_IP:$HTTP_PORT/health"
  exit 1
}

function start_bifrost() {
  echo "⚡ [BIFROST_START] Building & launching Bifrost mesh binary on $TAILSCALE_IP..."
  cd "$(dirname "$0")/.."
  
  if [ -f "apps/bifrost/main.go" ]; then
    (cd apps/bifrost && go build -o ../../bin/bifrost_engine main.go)
    nohup ./bin/bifrost_engine > .runtime_logs/bifrost.log 2>&1 &
    echo "✓ Bifrost engine launched in background (PID: $!). Logs: .runtime_logs/bifrost.log"
  else
    echo "❌ Error: apps/bifrost/main.go not found."
    exit 1
  fi
}

function stop_bifrost() {
  echo "🛑 [BIFROST_STOP] Stopping local Bifrost processes..."
  pkill -f "bifrost_engine" || true
  echo "✓ Stopped."
}

function status_bifrost() {
  echo "🔍 [BIFROST_STATUS] Checking process state..."
  ps aux | grep "[b]ifrost_engine" || echo "Bifrost engine is not running."
  echo ""
  echo "Netstat / Port listeners on $TAILSCALE_IP:"
  netstat -ano | grep "$TAILSCALE_IP" || echo "No active bindings on $TAILSCALE_IP"
}

function health_bifrost() {
  echo "🩺 [BIFROST_HEALTH] Probing http://$TAILSCALE_IP:$HTTP_PORT/health..."
  curl -s "http://$TAILSCALE_IP:$HTTP_PORT/health" || echo "❌ Probe failed: Node offline or un-reachable."
  echo ""
}

case "$1" in
  start)
    start_bifrost
    ;;
  stop)
    stop_bifrost
    ;;
  restart)
    stop_bifrost
    sleep 1
    start_bifrost
    ;;
  status)
    status_bifrost
    ;;
  health)
    health_bifrost
    ;;
  *)
    usage
    ;;
esac
