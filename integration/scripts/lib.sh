#!/usr/bin/env bash
# Shared knobs for the native-runtime lifecycle scripts.
# All runtime state (PIDs, logs, sockets, db, temp) lives in integration/.run/.

INTEGRATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$INTEGRATION_DIR/.run"
BIN_DIR="$RUN_DIR/bin"

GATEWAY_PORT=${GATEWAY_PORT:-8788}
NODE_AGENT_PORT=${NODE_AGENT_PORT:-8789}
CONSOLE_PORT=${CONSOLE_PORT:-8080}
LEASE_KEY=${LEASE_KEY:-camelot-demo-key}
GATEWAY_DB=${GATEWAY_DB:-$RUN_DIR/camelot-voice.db}

# Startup order matters (dev-up): gateway first, then the node-agent, then
# the PWA — each health-verified before its dependent starts.
SERVICES=(gateway node-agent console)

pid_file() { echo "$RUN_DIR/$1.pid"; }
log_file() { echo "$RUN_DIR/$1.log"; }
meta_file() { echo "$RUN_DIR/$1.meta"; }

service_pid() {
  local f
  f=$(pid_file "$1")
  [[ -f $f ]] && cat "$f" || true
}

# A service counts as "ours" only if the PID from .run/ is alive AND its
# /proc cmdline still contains the token we recorded at spawn time. This is
# what makes dev-down safe: it can never kill a recycled PID.
service_alive() {
  local pid token
  pid=$(service_pid "$1")
  [[ -n $pid ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  token=$(cat "$(meta_file "$1")" 2>/dev/null) || return 1
  tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -qF "$token"
}

record_service() { # name pid cmdline-token
  echo "$2" >"$(pid_file "$1")"
  echo "$3" >"$(meta_file "$1")"
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
    sleep 0.3
  done
  return 1
}

now_ms() { date +%s%3N; }
