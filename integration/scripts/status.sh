#!/usr/bin/env bash
# Show process + health state for every slice service.
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

rc=0
for s in "${ALL_SERVICES[@]}"; do
  pid=$(service_pid "$s")
  if service_alive "$s"; then
    if curl -sf -o /dev/null "$(health_url "$s")"; then
      echo "✔ $s  pid=$pid  healthy  $(health_url "$s")"
    else
      echo "⚠ $s  pid=$pid  running but unhealthy"; rc=1
    fi
  elif [[ $s == hermes && $ENABLE_HERMES_VOICE != true ]]; then
    echo "· hermes  disabled (set ENABLE_HERMES_VOICE=true to start the voice adapter)"
  else
    echo "✘ $s  not running"; rc=1
  fi
done
[[ -f $GATEWAY_DB ]] && echo "audit db: $GATEWAY_DB ($(du -h "$GATEWAY_DB" | cut -f1))"

# Mesh view: trust bands and health as the gateway sees them.
if [[ $ENABLE_TAILSCALE_MESH == true ]]; then
  nodes=$(curl -sf "http://localhost:$GATEWAY_PORT/v1/nodes" 2>/dev/null || true)
  if [[ -n $nodes ]]; then
    echo "$nodes" | python3 -c "
import json, sys
for n in json.load(sys.stdin)['nodes']:
    scope = 'local' if n['local'] else 'remote'
    print(f\"mesh node: {n['nodeId']} ({scope}) trust={n['trust']} health={n['health']} caps={len(n['capabilities'])} addr={n['addressHash']}\")" || true
  else
    echo "mesh: gateway unreachable"
  fi
fi
exit $rc
