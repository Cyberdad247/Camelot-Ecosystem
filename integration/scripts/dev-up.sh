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

"$SCRIPT_DIR/build.sh"
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

# Mint (or reuse) the API token before anything starts, so every caller in
# this stack shares one credential.
mkdir -p "$RUN_DIR"
if [[ -n ${CAMELOT_API_TOKEN:-} ]]; then
  API_TOKEN="$CAMELOT_API_TOKEN"
else
  API_TOKEN=$(head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')
fi
printf '%s\n' "$API_TOKEN" >"$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"
# The console is a static page served from a different origin, so it needs the
# token from its OWN origin. Same-origin policy is what keeps a hostile page
# from reading it; the gateway origin allow-list is what keeps one from using it.
printf '%s\n' "$API_TOKEN" >"$CONSOLE_TOKEN_FILE"

env_gateway=(env GATEWAY_ADDR="$GATEWAY_BIND:$GATEWAY_PORT"
  CAMELOT_API_TOKEN="$API_TOKEN"
  CAMELOT_ALLOWED_ORIGINS="http://localhost:$CONSOLE_PORT,http://127.0.0.1:$CONSOLE_PORT" GATEWAY_DB="$GATEWAY_DB"
  ENABLE_MODEL_PROVIDER="${ENABLE_MODEL_PROVIDER:-false}"
  MODEL_PROVIDER_ALLOW="${MODEL_PROVIDER_ALLOW:-deterministic}"
  MODEL_PROVIDER_NAME="${MODEL_PROVIDER_NAME:-configured}"
  MODEL_PROVIDER_URL="${MODEL_PROVIDER_URL:-}"
  MODEL_PROVIDER_MODEL="${MODEL_PROVIDER_MODEL:-default}"
  MODEL_PROVIDER_API_KEY="${MODEL_PROVIDER_API_KEY:-}"
  MODEL_TIMEOUT="${MODEL_TIMEOUT:-10s}"
  CAMELOT_LOCAL_NODE_ID="$CAMELOT_LOCAL_NODE_ID"
  CAMELOT_NODE_LEASE_KEY="$LEASE_KEY")
start_gated gateway "$BIN_DIR/gateway" 20 "${env_gateway[@]}" "$BIN_DIR/gateway"

env_agent=(env CAMELOT_NODE_LEASE_KEY="$LEASE_KEY" CAMELOT_API_TOKEN="$API_TOKEN" NODE_AGENT_ADDR="0.0.0.0:$NODE_AGENT_PORT"
  ENABLE_TAILSCALE_MESH="$ENABLE_TAILSCALE_MESH"
  CAMELOT_GATEWAY_URL="http://127.0.0.1:$GATEWAY_PORT"
  CAMELOT_NODE_ID="$CAMELOT_NODE_ID" CAMELOT_TENANT_ID="$CAMELOT_TENANT_ID"
  CAMELOT_NODE_NAME="$CAMELOT_NODE_NAME"
  CAMELOT_NODE_ENROL_SECRET="$CAMELOT_NODE_ENROL_SECRET"
  CAMELOT_NODE_DISPATCH_URL="${CAMELOT_NODE_DISPATCH_URL:-http://127.0.0.1:$NODE_AGENT_PORT}")
start_gated node-agent "$BIN_DIR/camelot-node-agent" 20 "${env_agent[@]}" "$BIN_DIR/camelot-node-agent"

if [[ $ENABLE_HERMES_VOICE == true ]]; then
  env_hermes=(env HERMES_PORT="$HERMES_PORT"
    HERMES_STT_ENGINE="${HERMES_STT_ENGINE:-fixture}" HERMES_TTS_ENGINE="${HERMES_TTS_ENGINE:-fixture}"
    HERMES_STT_CMD="${HERMES_STT_CMD:-}" HERMES_TTS_CMD="${HERMES_TTS_CMD:-}"
    HERMES_STT_SCRIPT="${HERMES_STT_SCRIPT:-}")
  start_gated hermes "hermes/src/server.mjs" 20 "${env_hermes[@]}" node hermes/src/server.mjs
fi

start_gated console "http.server $CONSOLE_PORT" 20 python3 -m http.server "$CONSOLE_PORT" --directory .

echo
echo "Anya Console: http://localhost:$CONSOLE_PORT/kickbox/"
echo "Gateway:      http://localhost:$GATEWAY_PORT/healthz  (audit db: $GATEWAY_DB)"
echo "Node agent:   http://localhost:$NODE_AGENT_PORT/healthz"
if [[ $ENABLE_TAILSCALE_MESH == true ]]; then
  echo "Mesh:         enabled as node '$CAMELOT_NODE_ID' (tenant $CAMELOT_TENANT_ID) — GET /v1/nodes"
fi
echo "Stop:         scripts/dev-down.sh · Status: scripts/status.sh · Logs: scripts/logs.sh"
