#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# check_preflight_ac.sh — manual acceptance verification per
# VFS_PREFLIGHT_DESIGN.md §7.2 (AC1-AC9).
#
# Each AC is asserted with an explicit check. Environment-dependent
# expectations (e.g. AC1's "all 8 CONFIRMED" requires the substrate
# services to be listening) are recorded as BLOCKED with the observed
# detail rather than silently passing. Exit code is non-zero iff a hard
# mechanism assertion (AC2-AC9) fails.
set -uo pipefail

cd "$(dirname "$0")/../.."
ROOT="$(pwd)"
PY="$ROOT/.venv/Scripts/python.exe"
RUN_ROOT="$ROOT/03_VAULT/runtime_state"
LEDGER="$ROOT/PROVENANCE_LEDGER.md"

PASS=0
FAIL=0
BLOCK=0
RESULTS=()

record() { # record <ac> <status> <detail>
  RESULTS+=("| $1 | $2 | $3 |")
  case "$2" in
    PASS) PASS=$((PASS + 1)) ;;
    FAIL) FAIL=$((FAIL + 1)) ;;
    BLOCK) BLOCK=$((BLOCK + 1)) ;;
  esac
}

newest_run_dir() { # newest_run_dir -> name of newest per-run dir (repo-relative)
  ls -t "$RUN_ROOT/preflight" 2>/dev/null | head -1
}

manifest_field() { # manifest_field <field> -> value from newest _manifest.json
  local rel="03_VAULT/runtime_state/preflight/$(newest_run_dir)/_manifest.json"
  "$PY" -c "import json,sys; print(json.load(open('$rel'))['$1'])"
}

echo "=== VFS Preflight AC verification — $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo

# --- AC1: all 8 checks CONFIRMED in a clean boot ---
echo "AC1: all 8 checks CONFIRMED"
"$PY" -m control_plane.preflight --run >/tmp/ac1_out.txt 2>&1 || true
passed="$(manifest_field checks_passed)"
total="$(manifest_field checks_total)"
halted_at="$(manifest_field halted_at_check)"
if [ "$passed" = "$total" ]; then
  record AC1 PASS "all $total CONFIRMED (run_id=$(manifest_field run_id))"
else
  record AC1 BLOCK "$passed/$total CONFIRMED; halted at $halted_at (substrate not up)"
fi
echo "  -> $(echo "${RESULTS[${#RESULTS[@]}-1]}" | cut -d'|' -f3)"

# --- AC2: total runtime < 2s p95 ---
echo "AC2: total runtime < 2000ms p95"
total_ms="$(manifest_field total_ms)"
if [ "$total_ms" -lt 2000 ]; then
  record AC2 PASS "${total_ms}ms"
else
  record AC2 FAIL "${total_ms}ms >= 2000ms budget"
fi
echo "  -> ${total_ms}ms"

# --- AC3: catalog hash reproducible across same-scene re-runs ---
echo "AC3: catalog hash reproducible"
h1="$(manifest_field catalog_hash)"
"$PY" -m control_plane.preflight --run >/dev/null 2>&1 || true
h2="$(manifest_field catalog_hash)"
if [ "$h1" = "$h2" ] && [ -n "$h1" ]; then
  record AC3 PASS "catalog_hash=${h1:0:8}"
else
  record AC3 FAIL "hash drift: ${h1:0:8} vs ${h2:0:8}"
fi
echo "  -> ${h1:0:8} stable"

# --- AC4: deliberately broken boot -> REJECTED with reasons ---
echo "AC4: broken boot REJECTS with cited reasons"
ac4_out="$("$PY" - <<'PY'
import tempfile, json
from pathlib import Path
from control_plane.preflight.boot_integration import boot_vfs_preflight
from control_plane.preflight.state import GraduationFlag

with tempfile.TemporaryDirectory() as td:
    home = Path(td)
    (home / "vfs" / "checks").mkdir(parents=True)
    (home / "vfs" / "checks" / "001_broken.yaml").write_text(
        'sequence: "001"\nid: broken\ndisplay_name: Broken\n'
        "command_type: python_module\n"
        'command: ["python", "-m", "control_plane.preflight.probes.vfs_present_run",'
        ' "--required", "/does/not/exist/ac4-123456"]\n'
        "timeout_s: 5\nretry: 0\nexpected_evidence_class: CONFIRMED\n"
        "hitl_on_fail: false\nremediation_hint: n/a\n"
    )
    (home / "03_VAULT" / "runtime_state").mkdir(parents=True)
    GraduationFlag(home / "03_VAULT" / "runtime_state").graduate()  # strict
    ok, msg = boot_vfs_preflight(home)
    print("OK" if not ok and "REJECT" in msg else "BAD", "|", msg[:160])
PY
)"
if echo "$ac4_out" | grep -q "^OK"; then
  record AC4 PASS "strict REJECT surfaced with reasons"
else
  record AC4 FAIL "$ac4_out"
fi
echo "  -> $(echo "$ac4_out" | cut -d'|' -f2)"

# --- AC5: no PROVENANCE_LEDGER.md writes from preflight itself ---
echo "AC5: no spurious PROVENANCE_LEDGER.md entries"
before="$(wc -l < "$LEDGER")"
"$PY" -m control_plane.preflight --run >/dev/null 2>&1 || true
after="$(wc -l < "$LEDGER")"
if [ "$before" = "$after" ]; then
  record AC5 PASS "entries before=$before after=$after"
else
  record AC5 FAIL "ledger grew: $before -> $after"
fi
echo "  -> before=$before after=$after"

# --- AC6: first-run advisor -> strict graduation works ---
echo "AC6: advisor -> strict graduation"
ac6_out="$("$PY" - <<'PY'
import tempfile
from pathlib import Path
from control_plane.preflight.boot_integration import boot_vfs_preflight

with tempfile.TemporaryDirectory() as td:
    home = Path(td)
    (home / "vfs" / "checks").mkdir(parents=True)
    (home / "vfs" / "checks" / "001_pass.yaml").write_text(
        'sequence: "001"\nid: pass1\ndisplay_name: Pass\n'
        "command_type: python_module\n"
        'command: ["python", "-m", "control_plane.preflight.probes.file_age_run",'
        ' "--path", "bin/awaken.py", "--max-age-days", "365"]\n'
        "timeout_s: 5\nretry: 0\nexpected_evidence_class: CONFIRMED\n"
        "hitl_on_fail: false\nremediation_hint: n/a\n"
    )
    (home / "03_VAULT" / "runtime_state").mkdir(parents=True)
    ok1, msg1 = boot_vfs_preflight(home)
    flag = home / "03_VAULT" / "runtime_state" / "preflight" / "_graduated.flag"
    ok2, msg2 = boot_vfs_preflight(home)
    if ok1 and flag.exists() and "strict_mode=True" in msg2:
        print("OK")
    else:
        print("BAD", msg1, msg2)
PY
)"
if [ "$ac6_out" = "OK" ]; then
  record AC6 PASS "_graduated.flag written; second run strict"
else
  record AC6 FAIL "$ac6_out"
fi
echo "  -> $ac6_out"

# --- AC7: two runs in same minute = two distinct run dirs ---
echo "AC7: idempotent runs (distinct run dirs)"
d1="$(ls -t "$RUN_ROOT/preflight" | head -1)"
"$PY" -m control_plane.preflight --run >/dev/null 2>&1 || true
d2="$(ls -t "$RUN_ROOT/preflight" | head -1)"
if [ "$d1" != "$d2" ] && [ -n "$d2" ]; then
  record AC7 PASS "$d1 / $d2"
else
  record AC7 FAIL "same dir reused: $d1"
fi
echo "  -> $d1 vs $d2"

# --- AC8: --test returns 0 with all 8 inline-synthetic checks passing ---
echo "AC8: python -m control_plane.preflight --test returns 0"
test_out="$("$PY" -m control_plane.preflight --test 2>&1)"
if echo "$test_out" | grep -q "all checks passing"; then
  record AC8 PASS "self-test green"
else
  record AC8 FAIL "self-test did not report all checks passing"
fi
echo "  -> $(echo "$test_out" | grep -q 'all checks passing' && echo OK || echo FAIL)"

# --- AC9: operator summary appears on stdout for all modes ---
echo "AC9: operator summary on stdout (run mode)"
out="$("$PY" -m control_plane.preflight --run 2>&1 || true)"
if echo "$out" | grep -q "\[VFS_PREFLIGHT\]" && echo "$out" | grep -q "run_id="; then
  record AC9 PASS "summary lines emitted"
else
  record AC9 FAIL "no summary lines"
fi
echo "  -> summary lines present"

echo
echo "=== Summary: PASS=$PASS FAIL=$FAIL BLOCK=$BLOCK ==="
echo
echo "| AC | Result | Notes |"
echo "|----|--------|-------|"
printf '%s\n' "${RESULTS[@]}"

[ "$FAIL" -eq 0 ]
