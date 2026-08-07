#!/usr/bin/env bash
# Start the slice as native processes with health-gated startup.
# PID/log files live in integration/.runtime/.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$INTEGRATION_DIR"

for s in "${SERVICES[@]}"; do
  if service_alive "$s"; then
    echo "$s already running (pid $(service_pid "$s")) — run scripts/dev-down.sh first" >&2
    exit 1
  fi
done

"$(dirname "${BASH_SOURCE[0]}")/build.sh"
mkdir -p "$RUNTIME_DIR"

GATEWAY_ADDR=":$GATEWAY_PORT" GATEWAY_DB="$GATEWAY_DB" \
  "$BIN_DIR/gateway" >"$(log_file gateway)" 2>&1 &
echo $! >"$(pid_file gateway)"

CAMELOT_NODE_LEASE_KEY="$LEASE_KEY" NODE_AGENT_ADDR="0.0.0.0:$NODE_AGENT_PORT" \
  "$BIN_DIR/camelot-node-agent" >"$(log_file node-agent)" 2>&1 &
echo $! >"$(pid_file node-agent)"

python3 -m http.server "$CONSOLE_PORT" --directory . >"$(log_file console)" 2>&1 &
echo $! >"$(pid_file console)"

failed=0
for s in "${SERVICES[@]}"; do
  if wait_healthy "$s" 20; then
    echo "✔ $s healthy ($(health_url "$s"))"
  else
    echo "✘ $s failed health gate — last log lines:" >&2
    tail -5 "$(log_file "$s")" >&2 || true
    failed=1
  fi
done

if (( failed )); then
  "$(dirname "${BASH_SOURCE[0]}")/dev-down.sh" >/dev/null || true
  echo "startup aborted (health gate)" >&2
  exit 1
fi

echo
echo "Anya Console: http://localhost:$CONSOLE_PORT/kickbox/"
echo "Gateway:      http://localhost:$GATEWAY_PORT/healthz  (audit db: $GATEWAY_DB)"
echo "Node agent:   http://localhost:$NODE_AGENT_PORT/healthz"
echo "Stop:         scripts/dev-down.sh · Status: scripts/status.sh · Logs: scripts/logs.sh"
