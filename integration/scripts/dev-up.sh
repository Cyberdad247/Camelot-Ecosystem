#!/usr/bin/env bash
# Start the slice as native processes, IN ORDER, each health-verified before
# the dependent service starts: gateway -> node-agent -> console (PWA).
# PID/log/metadata files live in integration/.run/.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$INTEGRATION_DIR"

for s in "${SERVICES[@]}"; do
  if service_alive "$s"; then
    echo "$s already running (pid $(service_pid "$s")) — run scripts/dev-down.sh first" >&2
    exit 1
  fi
  # A responding endpoint without our metadata means a FOREIGN process holds
  # the port; starting on top of it would fool the health gate.
  if curl -sf -o /dev/null --max-time 1 "$(health_url "$s")"; then
    echo "$s port already served by a process dev-up did not start — free it first ($(health_url "$s"))" >&2
    exit 1
  fi
done

"$(dirname "${BASH_SOURCE[0]}")/build.sh"
mkdir -p "$RUN_DIR"

teardown() {
  "$INTEGRATION_DIR/scripts/dev-down.sh" >/dev/null 2>&1 || true
  echo "startup aborted (health gate)" >&2
  exit 1
}

start_gated() { # name token seconds -- command...
  local name=$1 token=$2 timeout=$3 t0
  shift 3
  t0=$(now_ms)
  "$@" >"$(log_file "$name")" 2>&1 &
  record_service "$name" $! "$token"
  if wait_healthy "$name" "$timeout"; then
    echo "✔ $name healthy in $(( $(now_ms) - t0 ))ms ($(health_url "$name"))"
  else
    echo "✘ $name failed health gate — last log lines:" >&2
    tail -5 "$(log_file "$name")" >&2 || true
    teardown
  fi
}

env_gateway=(env GATEWAY_ADDR=":$GATEWAY_PORT" GATEWAY_DB="$GATEWAY_DB")
start_gated gateway "$BIN_DIR/gateway" 20 "${env_gateway[@]}" "$BIN_DIR/gateway"

env_agent=(env CAMELOT_NODE_LEASE_KEY="$LEASE_KEY" NODE_AGENT_ADDR="0.0.0.0:$NODE_AGENT_PORT")
start_gated node-agent "$BIN_DIR/camelot-node-agent" 20 "${env_agent[@]}" "$BIN_DIR/camelot-node-agent"

start_gated console "http.server $CONSOLE_PORT" 20 python3 -m http.server "$CONSOLE_PORT" --directory .

echo
echo "Anya Console: http://localhost:$CONSOLE_PORT/kickbox/"
echo "Gateway:      http://localhost:$GATEWAY_PORT/healthz  (audit db: $GATEWAY_DB)"
echo "Node agent:   http://localhost:$NODE_AGENT_PORT/healthz"
echo "Stop:         scripts/dev-down.sh · Status: scripts/status.sh · Logs: scripts/logs.sh"
