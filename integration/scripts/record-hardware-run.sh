#!/usr/bin/env bash
# Release-gate recorder (Phases 2-4A). Runs the full native validation on
# THIS machine and writes the results into docs/benchmarks/ — the artifact
# the merge/tag gate requires. Six of the nine checklist items are automated
# here; the remaining three need a second machine, your tailnet, and your
# ears, and are left as checkboxes.
#
# Usage:  ENABLE_TAILSCALE_MESH=true ./scripts/record-hardware-run.sh
set -euo pipefail
export ENABLE_HERMES_VOICE=${ENABLE_HERMES_VOICE:-true}
export ENABLE_TAILSCALE_MESH=${ENABLE_TAILSCALE_MESH:-false}
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
OUT_DIR="$INTEGRATION_DIR/../docs/benchmarks"
OUT="$OUT_DIR/$STAMP-$HOST.md"
mkdir -p "$OUT_DIR"

mem_total=$(awk '/MemTotal/ {printf "%.1f GB", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo "unknown")
cpu_model=$(awk -F': ' '/model name/ {print $2; exit}' /proc/cpuinfo 2>/dev/null || echo "unknown")
gpu_model=$( (lspci 2>/dev/null | grep -iE 'vga|3d|display' | head -1 | cut -d: -f3) || true )
gpu_model=${gpu_model:-none detected}

mem_field() { awk -v k="$1:" '$1 == k {printf "%.0f", $2/1024}' /proc/meminfo 2>/dev/null || echo 0; }
swap_total=$(mem_field SwapTotal)
swap_free_before=$(mem_field SwapFree)
avail_before=$(mem_field MemAvailable)

# Checklist item 1: local-only startup must be unaffected by everything the
# later phases added. Prove it with a full smoke pass, mesh flag absent.
echo "== pass A: local-only (mesh off)"
local_rc=0
(
  export ENABLE_TAILSCALE_MESH=false
  "$(dirname "${BASH_SOURCE[0]}")/dev-up.sh" >/dev/null
) || local_rc=1
if [[ $local_rc -eq 0 ]]; then
  local_only_out=$(ENABLE_TAILSCALE_MESH=false "$(dirname "${BASH_SOURCE[0]}")/smoke.sh") || local_rc=$?
fi
local_only_out=${local_only_out:-"(local-only pass did not run)"}
"$(dirname "${BASH_SOURCE[0]}")/dev-down.sh" >/dev/null

echo "== pass B: full stack (voice=$ENABLE_HERMES_VOICE mesh=$ENABLE_TAILSCALE_MESH)"
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

# Checklist items 3-7, automated (see scripts/mesh-gate-probes.sh).
probes_rc=0
if [[ $ENABLE_TAILSCALE_MESH == true ]]; then
  echo "== mesh gate probes"
  probes_out=$("$(dirname "${BASH_SOURCE[0]}")/mesh-gate-probes.sh") || probes_rc=$?
else
  probes_out="(skipped -- ENABLE_TAILSCALE_MESH was not true)"
fi

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

# Memory pressure across the whole run. A few MB of swap movement on a busy
# desktop is normal; hundreds of MB against an 8 GB box is the thrashing the
# PASS threshold rules out.
swap_free_after=$(mem_field SwapFree)
avail_after=$(mem_field MemAvailable)
if [[ ${swap_total:-0} -gt 0 ]]; then
  swap_line="swap ${swap_total}MB total; used +$(( swap_free_before - swap_free_after ))MB during the run"
else
  swap_line="no swap configured"
fi
mem_line="MemAvailable ${avail_before}MB -> ${avail_after}MB (delta $(( avail_before - avail_after ))MB); $swap_line"

{
  echo "# Hardware run — $STAMP on $HOST"
  echo
  echo "Phases 2-4A release-gate record — merge/tag gate for PR #200 (camelot-kickbox-voice-v0.2.0) and prerequisite for Phase 4B."
  echo
  echo "| Field | Value |"
  echo "|---|---|"
  echo "| Host | $HOST ($(uname -srm)) |"
  echo "| CPU | $cpu_model × $(nproc) |"
  echo "| RAM | $mem_total |"
  echo "| GPU | $gpu_model |"
  echo "| Voice | ENABLE_HERMES_VOICE=$ENABLE_HERMES_VOICE |"
  echo "| Mesh | ENABLE_TAILSCALE_MESH=$ENABLE_TAILSCALE_MESH |"
  echo "| Local-only pass (item 1) | $([ "$local_rc" -eq 0 ] && echo PASSED || echo "FAILED (rc=$local_rc)") |"
  echo "| Mesh gate probes (items 3-7) | $([ "$probes_rc" -eq 0 ] && echo PASSED || echo "FAILED (rc=$probes_rc)") |"
  echo "| Idle RSS | $idle_rss |"
  echo "| Fallback latency | $fallback_ms |"
  echo "| Memory pressure | $mem_line |"
  echo "| Smoke | $([ "$smoke_rc" -eq 0 ] && echo PASSED || echo "FAILED (rc=$smoke_rc)") |"
  echo
  echo '## Item 1 -- local-only smoke (mesh flag absent)'
  echo '```'
  echo "$local_only_out"
  echo '```'
  echo
  echo '## Full-stack smoke'
  echo '```'
  echo "$smoke_out"
  echo '```'
  echo
  echo '## Items 3-7 -- mesh gate probes'
  echo '```'
  echo "$probes_out"
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
  echo '## Manual checklist — the three items no script can do'
  echo
  echo '### Item 2 — a real remote node (needs a second machine on your tailnet)'
  echo '- [ ] Second machine agent enrolled; appears in Node Status as *pending*'
  echo '- [ ] After POST /v1/nodes/<id>/trust it shows *trusted · ready*'
  echo '- [ ] A read-only job routed to it returns a result (the route line names it)'
  echo
  echo '### Item 8 — transport loss'
  echo '- [ ] `tailscale down` on the remote → node degrades/offline within ~45s'
  echo '- [ ] Work continues locally throughout; no errors surface to the user'
  echo '- [ ] `tailscale up` → node returns (re-promote from limited if needed)'
  echo
  echo '### Item 9 — voice + model in the browser'
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
  echo '### Local-only invariant (must hold regardless of CAMELOT_NODE_ID)'
  echo '```'
  echo 'unset ENABLE_TAILSCALE_MESH'
  echo 'CAMELOT_NODE_ID=anything ENABLE_HERMES_VOICE=true make dev-up && make smoke && make dev-down'
  echo '```'
  echo '- [ ] Passes with no node-bound lease required (agent healthz shows nodeId empty)'
  echo
  echo "_Verdict (fill in): PASS / FAIL — notes:_"
} > "$OUT"

echo
echo "recorded → $OUT"
echo "Fill in the manual checklist + verdict, then commit the file."
[[ $smoke_rc -eq 0 ]] || exit "$smoke_rc"
