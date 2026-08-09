#!/usr/bin/env bash
# Resource + latency benchmark for the native slice (Phase 1.5 item 10).
# Measures: per-process RSS, CPU %, cold-start times (gateway, node-agent,
# PWA ready), turn request latency, audio-feature job latency.
# Starts its own stack (refuses if one is already up), writes the report to
# .run/benchmark.txt, and tears the stack down at the end.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$INTEGRATION_DIR"

for s in "${SERVICES[@]}"; do
  if service_alive "$s"; then
    echo "stack already running — scripts/dev-down.sh first" >&2
    exit 1
  fi
done

REPORT="$RUN_DIR/benchmark.txt"
TURNS=${TURNS:-20}
JOBS=${JOBS:-20}

# dev-up already prints per-service cold-start times; capture them.
up_out=$("$SCRIPT_DIR/dev-up.sh")
cold_gateway=$(grep -oP 'gateway healthy in \K[0-9]+' <<<"$up_out" | head -1)
cold_agent=$(grep -oP 'node-agent healthy in \K[0-9]+' <<<"$up_out" | head -1)
cold_console=$(grep -oP 'console healthy in \K[0-9]+' <<<"$up_out" | head -1)

# Warm both request paths once before timing.
turn_payload() {
  printf '{"sessionId":"bench","turnId":"bench-%s","modality":"text","transcript":"read staging status","startedAtMs":1}' "$1"
}
job_payload() {
  local exp="2030-01-01T00:00:00Z"
  local node="" tenant=""
  # An enrolled agent only accepts leases bound to itself (Phase 4A).
  if [[ $ENABLE_TAILSCALE_MESH == true ]]; then
    node=$CAMELOT_NODE_ID
    tenant=$CAMELOT_TENANT_ID
  fi
  local token
  token=$(python3 - "$LEASE_KEY" "$exp" "$node" "$tenant" <<'EOF'
import hashlib, hmac, sys
key, exp, node, tenant = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
msg = f"bench-lease|compute:audio.features|{exp}|{node}|{tenant}".encode()
print(hmac.new(key.encode(), msg, hashlib.sha256).hexdigest())
EOF
)
  printf '{"jobId":"bench-%s","kind":"audio.features","lease":{"leaseId":"bench-lease","capability":"compute:audio.features","status":"approved","expiresAt":"%s","token":"%s","nodeId":"%s","tenantId":"%s"},"frames":[{"frameId":"f0","samples":[%s]}],"frameSize":256}' \
    "$1" "$exp" "$token" "$node" "$tenant" "$(python3 -c 'print(",".join("0.1" for _ in range(1024)))')"
}

gw_curl -sf -o /dev/null -X POST "http://localhost:$GATEWAY_PORT/v1/voice/turns" -H 'content-type: application/json' -d "$(turn_payload warm)"
curl -sf -o /dev/null -X POST "http://localhost:$NODE_AGENT_PORT/v1/compute" -H 'content-type: application/json' -d "$(job_payload warm)"

time_requests() { # url count payload_fn
  local url=$1 count=$2 payload_fn=$3 times=""
  for i in $(seq 1 "$count"); do
    t=$(gw_curl -sf -o /dev/null -w '%{time_total}' -X POST "$url" \
      -H 'content-type: application/json' -d "$("$payload_fn" "$i")")
    times+="$t "
  done
  python3 -c "
import sys
ts = sorted(float(x)*1000 for x in '''$times'''.split())
n = len(ts)
print(f'min={ts[0]:.1f}ms avg={sum(ts)/n:.1f}ms p95={ts[int(n*0.95)-1]:.1f}ms max={ts[-1]:.1f}ms (n={n})')"
}

turn_latency=$(time_requests "http://localhost:$GATEWAY_PORT/v1/voice/turns" "$TURNS" turn_payload)
job_latency=$(time_requests "http://localhost:$NODE_AGENT_PORT/v1/compute" "$JOBS" job_payload)

# Let CPU counters settle post-load, then sample RSS + CPU%.
sleep 2
proc_stats() { # name
  local pid
  pid=$(service_pid "$1")
  ps -o rss=,%cpu= -p "$pid" | awk '{printf "rss=%.1fMB cpu=%s%%", $1/1024, $2}'
}

db_size="n/a"
[[ -f $GATEWAY_DB ]] && db_size=$(du -h "$GATEWAY_DB" | cut -f1)
log_size=$(du -ch "$RUN_DIR"/*.log 2>/dev/null | tail -1 | cut -f1)

hermes_lines=()
if [[ $ENABLE_HERMES_VOICE == true ]]; then
  cold_hermes=$(grep -oP 'hermes healthy in \K[0-9]+' <<<"$up_out" | head -1)
  stt_payload=$(python3 -c "
import base64, json, math, struct
sr = 16000
pcm = b''.join(struct.pack('<h', int(math.sin(2*math.pi*440*i/sr)*0.5*32767)) for i in range(int(sr*0.7)))
print(json.dumps({'sampleRate': sr, 'pcm16': base64.b64encode(pcm).decode()}))")
  stt_t=$(curl -sf -o /dev/null -w '%{time_total}' -X POST "http://localhost:$HERMES_PORT/v1/stt" \
    -H 'content-type: application/json' -d "$stt_payload")
  tts_t=$(curl -sf -o /dev/null -w '%{time_total}' -X POST "http://localhost:$HERMES_PORT/v1/tts" \
    -H 'content-type: application/json' -d '{"text":"Staging is green and holding."}')
  stt_ms=$(python3 -c "print(f'{$stt_t*1000:.1f}')")
  tts_ms=$(python3 -c "print(f'{$tts_t*1000:.1f}')")
  hermes_lines+=("hermes:      $(proc_stats hermes)  cold-start=${cold_hermes}ms")
  hermes_lines+=("hermes latency: stt(700ms audio)=${stt_ms}ms tts=${tts_ms}ms")
fi

{
  echo "── Camelot x Kickbox slice benchmark ($(date -u +%FT%TZ), host: $(uname -m), $(nproc) cpus)"
  echo "cold start:  gateway=${cold_gateway}ms  node-agent=${cold_agent}ms  console-ready=${cold_console}ms"
  echo "gateway:     $(proc_stats gateway)"
  echo "node-agent:  $(proc_stats node-agent)"
  echo "console:     $(proc_stats console)  (python http.server dev stand-in)"
  for line in "${hermes_lines[@]+"${hermes_lines[@]}"}"; do echo "$line"; done
  echo "audit db:    $db_size · logs: $log_size"
  echo "turn latency (POST /v1/voice/turns, tier-1):    $turn_latency"
  echo "compute latency (POST /v1/compute, 1024-sample batch): $job_latency"
  if [[ ${ENABLE_TAILSCALE_MESH:-false} == true ]]; then
    node_t0=$(now_ms)
    gw_curl -sf -o /dev/null -X POST "http://localhost:$GATEWAY_PORT/v1/nodes/jobs" \
      -H 'content-type: application/json' \
      -d "{\"tenantId\":\"${CAMELOT_TENANT_ID}\",\"capability\":\"compute:audio.features\",\"payload\":{\"frames\":[{\"frameId\":\"f0\",\"samples\":[0.1,0.2,0.3,0.4]}],\"frameSize\":2}}" || true
    echo "mesh: node-job round trip (enrol->lease->dispatch->result) = $(( $(now_ms) - node_t0 ))ms; nodes=$(gw_curl -sf "http://localhost:$GATEWAY_PORT/v1/nodes" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["nodes"]))')"
  fi
  gw_curl -sf "http://localhost:$GATEWAY_PORT/v1/models/stats" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"model routing: provider={d['provider']} requests={d['requests']} fallbacks={d['fallbacks']} \"
      f\"first-token={d['avgFirstTokenMs']:.0f}ms completion={d['avgCompletionMs']:.0f}ms\")"
} | tee "$REPORT"

"$SCRIPT_DIR/dev-down.sh" >/dev/null
echo "── stack stopped; report saved to $REPORT"
