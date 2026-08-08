#!/usr/bin/env bash
# Local-only invariant check, self-contained and footgun-proof.
#
#   Mesh disabled must mean local-only authorization semantics, even when a
#   node id is present in the environment. A transport-related variable must
#   never silently switch on node-bound lease enforcement.
#
# This script FORCES the mesh off itself (rather than trusting the caller's
# shell) and deliberately sets a non-default CAMELOT_NODE_ID, so an exported
# ENABLE_TAILSCALE_MESH cannot produce a false PASS.
set -uo pipefail

# Force the conditions under test — do not inherit them.
unset ENABLE_TAILSCALE_MESH
export ENABLE_TAILSCALE_MESH=false
export ENABLE_HERMES_VOICE=${ENABLE_HERMES_VOICE:-true}
export CAMELOT_NODE_ID=${CAMELOT_NODE_ID:-nondefault-local-id}

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$INTEGRATION_DIR"

echo "── local-only invariant (mesh forced off, CAMELOT_NODE_ID=$CAMELOT_NODE_ID)"

for s in "${ALL_SERVICES[@]}"; do
  if service_alive "$s"; then
    echo "   ✘ a stack is already running — scripts/dev-down.sh first" >&2
    exit 1
  fi
done

rc=0
"$SCRIPT_DIR/dev-up.sh" >/dev/null || rc=1
if [[ $rc -ne 0 ]]; then
  echo "   ✘ stack failed to start"
  "$SCRIPT_DIR/dev-down.sh" >/dev/null 2>&1
  exit 1
fi

# The agent must NOT be enrolled: an empty nodeId is what proves node-bound
# lease enforcement is off despite CAMELOT_NODE_ID being set.
health=$(curl -sf "http://localhost:$NODE_AGENT_PORT/healthz" || echo '{}')
agent_node=$(echo "$health" | python3 -c "import json,sys; print(json.load(sys.stdin).get('nodeId',''))" 2>/dev/null)
if [[ -z $agent_node ]]; then
  echo "   ✔ agent reports an empty nodeId (binding not required)"
else
  echo "   ✘ agent enrolled as '$agent_node' with the mesh off — binding would be required"
  rc=1
fi

# Mesh endpoints must report nothing enrolled.
node_count=$(curl -sf "http://localhost:$GATEWAY_PORT/v1/nodes" \
  | python3 -c "import json,sys; print(len(json.load(sys.stdin)['nodes']))" 2>/dev/null || echo "?")
if [[ $node_count == 0 ]]; then
  echo "   ✔ gateway registry is empty (no enrolment happened)"
else
  echo "   ✘ gateway has $node_count node(s) registered with the mesh off"
  rc=1
fi

# The full smoke must pass using unbound leases only.
if smoke_out=$("$SCRIPT_DIR/smoke.sh"); then
  echo "   ✔ $(echo "$smoke_out" | tail -1 | sed 's/^✅ //')"
else
  echo "   ✘ local-only smoke FAILED:"
  echo "$smoke_out" | tail -5
  rc=1
fi

"$SCRIPT_DIR/dev-down.sh" >/dev/null

if [[ $rc -eq 0 ]]; then
  echo "── local-only invariant: PASS"
else
  echo "── local-only invariant: FAIL"
fi
exit $rc
