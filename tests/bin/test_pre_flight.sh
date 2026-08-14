#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# tests/bin/test_pre_flight.sh — PR #5 (gate-of-gates) test suite.
#
# Verifies the pre-flight script's exit-code classifier against 7 scenarios:
#   1. OK   good tree        → exit 0
#   2. CRIT missing required → exit 2
#   3. GEN  extra non-templated .env → exit 1
#   4. BOOT example present, live .env.appwrite missing → exit 3
#   5. SCHEMA json-load smoke → exit 0 (cascade interpreter; sys.argv path)
#   6. MISSING-SCHEMA refusal → exit 2 (pre-flight refuses to run blind)
#   7. FORBIDDEN paths alone (no other drifts) → exit 1 (locks classifier)
#
# Path A (thinker round 8): sterile test fixtures — each positive test builds
# only the 16 schema-required canonical files (no realistic-noise `cp -r`).
# This isolates the gate's classifier logic from incidental fixture drift.
set -uo pipefail

# ── Resolve paths ────────────────────────────────────────────────────────────
TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$TESTS_DIR/../.." && pwd)"
PRE_FLIGHT="$REPO_ROOT/bin/pre_flight.sh"
SCHEMA="$REPO_ROOT/docs/schemas/notebooklm_master_schema.json"
TMPROOT="$(mktemp -d -p /tmp pre_flight_test_XXXXXX)"
trap 'rm -rf "$TMPROOT"' EXIT

PASS=0; FAIL=0
ok()   { echo "  [PASS] $1"; PASS=$((PASS+1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }

# ── Sterile-canonic fixture: only the 16 schema-required files (Path A) ──────
# Replaces the prior `cp -r` bulk-mirror that imported 2199 fixture files and
# accidentally triggered general_drift supernumerary detection on bulk-realism.
build_good_fixture() {
    local dir="$1"
    mkdir -p \
        "$dir/control_plane" \
        "$dir/bin" \
        "$dir/docs/architecture" \
        "$dir/docs/schemas"

    # 6 control_plane canonical modules
    touch "$dir/control_plane/appwrite_client.py"
    touch "$dir/control_plane/bifrost_appwrite_dispatch.py"
    touch "$dir/control_plane/bifrost_gateway.py"
    touch "$dir/control_plane/heimdall_bifrost_governance.py"
    touch "$dir/control_plane/soul_oversight.py"
    touch "$dir/control_plane/notebooklm_graphify_bridge.py"

    # 3 bin canonical scripts
    touch "$dir/bin/appwrite_bootstrap.sh"
    touch "$dir/bin/notebooklm_mcp_server.py"
    touch "$dir/bin/pre_flight.sh"

    # 4 docs/architecture canonical markdocs
    touch "$dir/docs/architecture/TITAN_TIER_EXECUTION_PROMPT_2026-07-14.md"
    touch "$dir/docs/architecture/SYSTEM_PROMPT_v2_2026-07-14.md"
    touch "$dir/docs/architecture/NOTES_MNEMOSYNE_WIRING.md"
    touch "$dir/docs/architecture/LIVE_VERIFY_RUNBOOK_2026-07-14.md"

    # 1 schema self-reference (real bytes so json.load succeeds if pre-flight touches it)
    cp "$SCHEMA" "$dir/docs/schemas/notebooklm_master_schema.json" 2>/dev/null \
        || touch "$dir/docs/schemas/notebooklm_master_schema.json"

    # 2 repo-root configs
    touch "$dir/pyproject.toml"
    touch "$dir/docker-compose.appwrite.yml"

    # Strip dev-env clutter
    rm -f \
        "$dir/.env" "$dir/.env.appwrite" "$dir/.env.appwrite.example" \
        "$dir/.env.example" "$dir/.env.template" \
        2>/dev/null || true
}

# ── Run pre_flight with a schema path, return cleaned stdout-stderr + exit ─────
run_preflight() {
    local fixture_root="$1"
    local out_json="$2"
    local schema_path="$3"
    bash "$PRE_FLIGHT" "$fixture_root" "$out_json" "$schema_path" 2>/dev/null
    echo $?
}

# ──────────────────────────────────────────────────────────────────────────────
echo "=== PR #5 pre_flight.sh test suite (Path A: sterile fixtures) ==="
echo ""

# Test 1: clean sterile fixture → 0
echo "T1: clean sterile fixture -> expect 0"
GOOD="$TMPROOT/good"
build_good_fixture "$GOOD"
EXIT=$(run_preflight "$GOOD" "$TMPROOT/out1.json" "$SCHEMA")
if [ "$EXIT" = "0" ]; then ok "clean fixture exit=0"; else fail "clean fixture exit=$EXIT (want 0)"; fi

# Test 2: missing required control_plane/appwrite_client.py → 2 (critical)
echo "T2: missing control_plane/appwrite_client.py -> expect 2"
CRIT="$TMPROOT/critical"
build_good_fixture "$CRIT"
rm -f "$CRIT/control_plane/appwrite_client.py"
EXIT=$(run_preflight "$CRIT" "$TMPROOT/out2.json" "$SCHEMA")
if [ "$EXIT" = "2" ]; then ok "critical drift exit=2"; else fail "critical drift exit=$EXIT (want 2)"; fi

# Test 3: extra non-templated .env at root → 1 (general)
echo "T3: extra non-templated .env -> expect 1"
GEN="$TMPROOT/general"
build_good_fixture "$GEN"
echo "RAW_SECRET_NOT_GITIGNORED=should_not_be_here" > "$GEN/.env"
EXIT=$(run_preflight "$GEN" "$TMPROOT/out3.json" "$SCHEMA")
if [ "$EXIT" = "1" ]; then ok "general drift exit=1"; else fail "general drift exit=$EXIT (want 1)"; fi
rm -f "$GEN/.env"

# Test 4: .env.appwrite.example present, .env.appwrite missing → 3 (bootstrap)
echo "T4: .env.appwrite.example without .env.appwrite -> expect 3"
BOOT="$TMPROOT/bootstrap"
build_good_fixture "$BOOT"
printf '_APP_ENV=production\n_APP_DB_PASS=changeme\n' > "$BOOT/.env.appwrite.example"
EXIT=$(run_preflight "$BOOT" "$TMPROOT/out4.json" "$SCHEMA")
if [ "$EXIT" = "3" ]; then ok "bootstrap drift exit=3"; else fail "bootstrap drift exit=$EXIT (want 3)"; fi

# Test 5: schema is loadable as JSON (cascade interpreter; sys.argv path-dodge).
echo "T5: schema json-load smoke"
DETECTED_PYTHON=$(command -v python3 || command -v python || command -v py)
if [ -n "$DETECTED_PYTHON" ] && "$DETECTED_PYTHON" -c "import json, sys; d=json.load(open(sys.argv[1])); assert d.get('schema_version','').startswith('camelot.mnemosyne.pre-flight')" "$SCHEMA" 2>/dev/null; then
    ok "schema json-load + schema_version prefix correct"
else
    fail "schema json-load failed (cascade interpreter unavailable or assertion broke)"
fi

# Test 6: pre-flight refuses to run without a valid schema path → 2 (critical)
echo "T6: missing schema file -> expect 2 (refusal-to-run-blind)"
NOSCHEMA="$TMPROOT/noschema"
build_good_fixture "$NOSCHEMA"
EXIT=$(run_preflight "$NOSCHEMA" "$TMPROOT/out6.json" "$TMPROOT/no-such-schema.json")
if [ "$EXIT" = "2" ]; then ok "missing schema exit=2"; else fail "missing schema exit=$EXIT (want 2)"; fi

# Test 7: forbidden paths alone (no threshold breach / no missing required) → 1 (general).
echo "T7: forbidden paths alone -> expect 1 (general drift, not critical-2)"
FORBID="$TMPROOT/forbidden"
build_good_fixture "$FORBID"
touch "$FORBID/stray_untracked_secret.env"
EXIT=$(run_preflight "$FORBID" "$TMPROOT/out7.json" "$SCHEMA")
if [ "$EXIT" = "1" ]; then ok "forbidden-paths-alone exit=1"; else fail "forbidden-paths-alone exit=$EXIT (want 1)"; fi
rm -f "$FORBID/stray_untracked_secret.env"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "==== Summary ===="
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
    echo "ALL PRE_FLIGHT TESTS PASSED"
    exit 0
else
    echo "FAILURES: $FAIL"
    exit 1
fi
