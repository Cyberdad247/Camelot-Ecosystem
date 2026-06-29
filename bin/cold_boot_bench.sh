#!/usr/bin/env bash
# bin/cold_boot_bench.sh
# ---------------------------------------------------------------------------
# Phase 3 cold-boot benchmark hand-off stub.
# ---------------------------------------------------------------------------
# Reads 03_VAULT/runtime_state/hive_ide_apex_v1000/wsl2_verdict.json, confirms
# final=GO, and reports the operator-actionable bench hand-off commands.
#
# INTENTIONALLY does NOT fire:
#   - cargo test on ouroboros_engine (12 ms cold-boot target — HUMAN_GATE)
#   - any edits to 01_KERNEL/core/microvm_cages/ (UFFD + qemu-img COW — HUMAN_GATE)
#   - any production-surface state changes
#
# Reversibility: `git checkout HEAD -- bin/cold_boot_bench.sh` cleanly removes.
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

VERDICT_FILE="03_VAULT/runtime_state/hive_ide_apex_v1000/wsl2_verdict.json"

if [ ! -f "$VERDICT_FILE" ]; then
    printf '{"bench":"NO-GO","detail":"%s missing; run `bash bin/phase3_one_shot.sh` from inside your WSL2 distro first"}\n' "$VERDICT_FILE"
    exit 1
fi

# Tolerate whitespace in JSON keys (mirrors the regex pattern in
# bin/phase3_one_shot.sh's extract_verdict helper).
RAW=$(tr -d '\n' < "$VERDICT_FILE")
FINAL=$(printf '%s' "$RAW" | grep -oE '"final":[[:space:]]*"[A-Z-]+"' | head -1 | sed 's/^"final":[[:space:]]*"//; s/"$//' || true)
CAPTURED_AT=$(printf '%s' "$RAW" | grep -oE '"captured_at":[[:space:]]*"[^"]+"' | head -1 | sed 's/^"captured_at":[[:space:]]*"//; s/"$//' || true)
POLISH4=$(printf '%s' "$RAW" | grep -oE '"polish_4":[[:space:]]*"[a-z]+"' | head -1 | sed 's/^"polish_4":[[:space:]]*"//; s/"$//' || true)

if [ "$FINAL" != "GO" ]; then
    printf '{"bench":"NO-GO","detail":"verdict final=%s (expected GO); re-run `bash bin/phase3_one_shot.sh` inside WSL2 to refresh","verdict_file":"%s","captured_at":"%s","polish_4":"%s"}\n' \
        "$FINAL" "$VERDICT_FILE" "${CAPTURED_AT:-?}" "${POLISH4:-?}"
    exit 1
fi

printf '{"bench":"READY","detail":"wsl2 verdict final=GO; bench hand-off commands below","verdict_file":"%s","captured_at":"%s","polish_4":"%s"}\n' \
    "$VERDICT_FILE" "${CAPTURED_AT:-?}" "${POLISH4:-?}"

# Freshness gate: warn if the verdict is older than 1 hour. The substrate can
# drift (nested-virt toggled off, kernel updated, libkrun upgraded), so a
# stale verdict should NOT be used to stage the 12 ms bench without a
# wrapper re-run. `date -d` parses the ISO-8601 captured_at; tolerates parse
# failure by silently skipping the freshness check (still emits the bench
# commands; operator decides whether to proceed).
# Skip-path: empty OR unparseable captured_at -> silently skip the age check.
# Do NOT default to `1970-01-01T00:00:00Z` because `NOW_EPOCH - 0` would
# produce a multi-decade AGE_SECS that spuriously fires the >1h WARN.
NOW_EPOCH=$(date +%s 2>/dev/null || echo 0)
CAPTURED_EPOCH=0
if [ -n "$CAPTURED_AT" ]; then
    CAPTURED_EPOCH=$(date -d "$CAPTURED_AT" +%s 2>/dev/null || echo 0)
fi
if [ "$NOW_EPOCH" -gt 0 ] && [ "$CAPTURED_EPOCH" -gt 0 ]; then
    AGE_SECS=$((NOW_EPOCH - CAPTURED_EPOCH))
    if [ "$AGE_SECS" -gt 3600 ]; then
        printf 'WARN: wsl2_verdict.json is %s seconds old (>1h); recommend re-running `bash bin/phase3_one_shot.sh` to refresh before firing the bench.\n' "$AGE_SECS" >&2
    fi
fi

cat <<'BENCH_HANDOFF'

=== Operator-actionable bench hand-off commands ===
HUMAN_GATE required for the destructive UFFD + qemu-img scaffolding edits to
01_KERNEL/core/microvm_cages/. Provide CAMELOT_DASHBOARD_OPERATOR_TOKEN at the
next prompt to authorize control_plane/soul_oversight.pre_execute on this cut.

  # 1. Confirm the substrate was actually approved (one-shot re-verify).
  bash bin/phase3_one_shot.sh 2>&1 | tail -3

  # 2. (When authorized) the orchestrator will scaffold:
  #    - 01_KERNEL/core/microvm_cages/uffd_server.rs   (Rust UFFD polling shell)
  #    - 01_KERNEL/core/microvm_cages/cow_snapshotter.sh  (qemu-img COW wrapper)

  # 3. Fire the live BitNet b1.58 + selective-scan SSM + UFFD-controlled cold
  #    boot via the ouroboros engine test harness:
  cargo test --manifest-path 01_KERNEL/reasoning/ouroboros_engine \
      -- --nocapture 2>&1 | tee 03_VAULT/runtime_state/hive_ide_apex_v1000/cold_boot_bench.log

  # 4. Once the log shows the 12 ms cold-boot number reproducible, this script
  #    plus the bench log feed the canonical cold_boot_bench.json capture:
  #    03_VAULT/runtime_state/hive_ide_apex_v1000/cold_boot_bench.json
  #    evidence_class promotion: planned -> confirmed.
BENCH_HANDOFF
exit 0
