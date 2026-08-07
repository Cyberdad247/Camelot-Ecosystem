#!/usr/bin/env bash
# Phase 2 release-gate recorder. Runs the full native voice validation on
# THIS machine and writes the results into docs/integration/hardware-runs/
# — the artifact the Phase 3 prerequisite requires. Review, fill in the
# manual checklist, then commit the file.
#
# Usage:  ./scripts/record-hardware-run.sh          (voice on by default)
set -euo pipefail
export ENABLE_HERMES_VOICE=${ENABLE_HERMES_VOICE:-true}
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$INTEGRATION_DIR"

for s in "${ALL_SERVICES[@]}"; do
  if service_alive "$s"; then
    echo "stack already running — scripts/dev-down.sh first" >&2
    exit 1
  fi
done

STAMP=$(date -u +%F)
HOST=$(hostname -s 2>/dev/null || echo host)
OUT_DIR="$INTEGRATION_DIR/../docs/integration/hardware-runs"
OUT="$OUT_DIR/$STAMP-$HOST.md"
mkdir -p "$OUT_DIR"

mem_total=$(awk '/MemTotal/ {printf "%.1f GB", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo "unknown")
cpu_model=$(awk -F': ' '/model name/ {print $2; exit}' /proc/cpuinfo 2>/dev/null || echo "unknown")
gpu_model=$( (lspci 2>/dev/null | grep -iE 'vga|3d|display' | head -1 | cut -d: -f3) || true )
gpu_model=${gpu_model:-none detected}

echo "── smoke (ENABLE_HERMES_VOICE=$ENABLE_HERMES_VOICE)"
"$(dirname "${BASH_SOURCE[0]}")/dev-up.sh" >/dev/null

# Idle RSS: sampled after health gates, before any load.
sleep 2
idle_rss=""
for s in "${SERVICES[@]}"; do
  pid=$(service_pid "$s")
  rss=$(ps -o rss= -p "$pid" 2>/dev/null | awk '{printf "%.1fMB", $1/1024}')
  idle_rss+="$s=$rss "
done

smoke_out=$("$(dirname "${BASH_SOURCE[0]}")/smoke.sh") && smoke_rc=0 || smoke_rc=$?
status_out=$("$(dirname "${BASH_SOURCE[0]}")/status.sh" || true)
"$(dirname "${BASH_SOURCE[0]}")/dev-down.sh" >/dev/null

echo "── benchmark (active RSS + latencies)"
bench_out=$("$(dirname "${BASH_SOURCE[0]}")/benchmark.sh")

# Provider failure-to-fallback latency: a throwaway gateway on :8791 pointed
# at a dead provider URL with a 1s timeout; measure POST-turn -> fallback
# recorded in /v1/models/stats.
echo "── fallback-latency probe"
FB_PORT=8791
env GATEWAY_ADDR=":$FB_PORT" GATEWAY_DB=":memory:" \
  ENABLE_MODEL_PROVIDER=true MODEL_PROVIDER_ALLOW="deterministic,probe" \
  MODEL_PROVIDER_NAME=probe MODEL_PROVIDER_URL="http://127.0.0.1:9/dead" \
  MODEL_TIMEOUT=1s \
  "$BIN_DIR/gateway" >"$RUN_DIR/fallback-probe.log" 2>&1 &
fb_pid=$!
for _ in $(seq 1 20); do
  curl -sf -o /dev/null "http://localhost:$FB_PORT/healthz" && break
  sleep 0.3
done
fb_t0=$(now_ms)
curl -sf -o /dev/null -X POST "http://localhost:$FB_PORT/v1/voice/turns" \
  -H 'content-type: application/json' \
  -d '{"sessionId":"probe","turnId":"probe-1","modality":"text","transcript":"read staging status","startedAtMs":1}'
fallback_ms="not reached"
for _ in $(seq 1 60); do
  fb=$(curl -sf "http://localhost:$FB_PORT/v1/models/stats" | python3 -c "import json,sys; print(json.load(sys.stdin)['fallbacks'])" 2>/dev/null || echo 0)
  if [[ $fb -ge 1 ]]; then
    fallback_ms="$(( $(now_ms) - fb_t0 ))ms (dead provider, 1s timeout, until fallback recorded)"
    break
  fi
  sleep 0.2
done
kill "$fb_pid" 2>/dev/null || true

{
  echo "# Hardware run — $STAMP on $HOST"
  echo
  echo "Phase 2+3 release-gate record (docs/architecture/bootstrap-plan.md; merge/tag gate for PR #200 and prerequisite for Phase 4A)."
  echo
  echo "| Field | Value |"
  echo "|---|---|"
  echo "| Host | $HOST ($(uname -srm)) |"
  echo "| CPU | $cpu_model × $(nproc) |"
  echo "| RAM | $mem_total |"
  echo "| GPU | $gpu_model |"
  echo "| Voice | ENABLE_HERMES_VOICE=$ENABLE_HERMES_VOICE |"
  echo "| Idle RSS | $idle_rss |"
  echo "| Fallback latency | $fallback_ms |"
  echo "| Smoke | $([ "$smoke_rc" -eq 0 ] && echo PASSED || echo "FAILED (rc=$smoke_rc)") |"
  echo
  echo '## Smoke output'
  echo '```'
  echo "$smoke_out"
  echo '```'
  echo
  echo '## Status snapshot'
  echo '```'
  echo "$status_out"
  echo '```'
  echo
  echo '## Benchmark'
  echo '```'
  echo "$bench_out"
  echo '```'
  echo
  echo '## Manual checklist (fill in by hand in the browser)'
  echo
  echo '- [ ] Microphone permission DENIED → text mode remains usable, visible notice'
  echo '- [ ] Silence while holding PTT → "no speech" notice, nothing submitted'
  echo '- [ ] Quiet speech → low-confidence review prompt, must press Send'
  echo '- [ ] Normal speech → voice turn submitted, decision card + audit entry'
  echo '- [ ] Barge-in while TTS is speaking → playback stops instantly, stream cancelled'
  echo '- [ ] Tier-2 spoken request → draft artifact + consumed lease in audit'
  echo '- [ ] Tier-3 spoken request → blocked until visible Approve; Deny revokes'
  echo '- [ ] TTS start latency after reply completes: ______ (perceived, browser)'
  echo '- [ ] Barge-in stop latency while speaking: ______ (perceived — must feel immediate)'
  echo '- [ ] Browser used: ______'
  echo
  echo "_Verdict (fill in): PASS / FAIL — notes:_"
} > "$OUT"

echo
echo "recorded → $OUT"
echo "Fill in the manual checklist + verdict, then commit the file."
[[ $smoke_rc -eq 0 ]] || exit "$smoke_rc"
