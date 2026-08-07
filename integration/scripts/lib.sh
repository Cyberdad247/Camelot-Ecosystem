#!/usr/bin/env bash
# Shared knobs for the native-runtime lifecycle scripts.
# All paths are relative to integration/ (scripts cd there on entry).

INTEGRATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$INTEGRATION_DIR/.runtime"
BIN_DIR="$RUNTIME_DIR/bin"

GATEWAY_PORT=${GATEWAY_PORT:-8788}
NODE_AGENT_PORT=${NODE_AGENT_PORT:-8789}
CONSOLE_PORT=${CONSOLE_PORT:-8080}
LEASE_KEY=${LEASE_KEY:-camelot-demo-key}
GATEWAY_DB=${GATEWAY_DB:-$RUNTIME_DIR/camelot-voice.db}

SERVICES=(gateway node-agent console)

pid_file() { echo "$RUNTIME_DIR/$1.pid"; }
log_file() { echo "$RUNTIME_DIR/$1.log"; }

service_pid() {
  local f
  f=$(pid_file "$1")
  [[ -f $f ]] && cat "$f" || true
}

service_alive() {
  local pid
  pid=$(service_pid "$1")
  [[ -n $pid ]] && kill -0 "$pid" 2>/dev/null
}

health_url() {
  case "$1" in
    gateway) echo "http://localhost:$GATEWAY_PORT/healthz" ;;
    node-agent) echo "http://localhost:$NODE_AGENT_PORT/healthz" ;;
    console) echo "http://localhost:$CONSOLE_PORT/kickbox/index.html" ;;
  esac
}

wait_healthy() { # name, seconds
  local url deadline
  url=$(health_url "$1")
  deadline=$(( $(date +%s) + ${2:-20} ))
  while (( $(date +%s) < deadline )); do
    curl -sf -o /dev/null "$url" && return 0
    sleep 0.5
  done
  return 1
}
