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

echo "── smoke (ENABLE_HERMES_VOICE=$ENABLE_HERMES_VOICE)"
"$(dirname "${BASH_SOURCE[0]}")/dev-up.sh" >/dev/null
smoke_out=$("$(dirname "${BASH_SOURCE[0]}")/smoke.sh") && smoke_rc=0 || smoke_rc=$?
status_out=$("$(dirname "${BASH_SOURCE[0]}")/status.sh" || true)
"$(dirname "${BASH_SOURCE[0]}")/dev-down.sh" >/dev/null

echo "── benchmark"
bench_out=$("$(dirname "${BASH_SOURCE[0]}")/benchmark.sh")

{
  echo "# Hardware run — $STAMP on $HOST"
  echo
  echo "Phase 2 release-gate record (docs/architecture/bootstrap-plan.md; Phase 3 prerequisite)."
  echo
  echo "| Field | Value |"
  echo "|---|---|"
  echo "| Host | $HOST ($(uname -srm)) |"
  echo "| CPU | $cpu_model × $(nproc) |"
  echo "| RAM | $mem_total |"
  echo "| Voice | ENABLE_HERMES_VOICE=$ENABLE_HERMES_VOICE |"
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
  echo
  echo "_Verdict (fill in): PASS / FAIL — notes:_"
} > "$OUT"

echo
echo "recorded → $OUT"
echo "Fill in the manual checklist + verdict, then commit the file."
[[ $smoke_rc -eq 0 ]] || exit "$smoke_rc"
