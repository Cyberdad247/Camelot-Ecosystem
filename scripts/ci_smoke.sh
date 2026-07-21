#!/usr/bin/env bash
# scripts/ci_smoke.sh — single CI entry for the portable-CLI tests.
#
# Orchestrates the three checks that together prove the cartridge
# subcommand surface is shippable:
#
#   1. Dev-mode unit tests      — pytest on the cartridge trio +
#                                 portable-subcommands modules
#   2. Forensic bundle check    — scripts/verify_frozen_bundle.py
#                                 (dist/camelot.exe contents)
#   3. Frozen-binary smoke      — scripts/cartridge_smoke.sh
#                                 (end-to-end frozen-mode behaviour)
#
# Designed to be invoked from CI after a fresh
# ``pyinstaller --clean camelot.spec`` build. Each step is idempotent
# and self-contained: a failure in step 1 short-circuits steps 2 + 3
# (no point piling bundle errors on top of unit-test failures); a
# failure in step 2 or 3 still returns the failing step's exit code so
# CI can pin-point which gate tripped.
#
# Usage:
#   bash scripts/ci_smoke.sh                      # full orchestration
#   SKIP_SMOKE=1 bash scripts/ci_smoke.sh         # skip frozen-smoke
#   PYTHON=.venv/Scripts/python.exe bash scripts/ci_smoke.sh
set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"

PYTHON="${PYTHON:-python}"
LOG_DIR="$REPO_ROOT/data/ci_logs"
mkdir -p "$LOG_DIR"

step() {
    local name="$1"
    local log="$LOG_DIR/${name}.log"
    echo
    echo "=============================="
    echo "CI STEP: $name"
    echo "Log: $log"
    echo "=============================="
}

run_step_unit_tests() {
    step unit_tests
    "$PYTHON" -m pytest tests/test_camelot_portable_subcommands.py \
        tests/test_cartridges_v4000_trio.py \
        -v 2>&1 | tee "$LOG_DIR/unit_tests.log"
}

run_step_bundle_check() {
    step bundle_check
    "$PYTHON" scripts/verify_frozen_bundle.py 2>&1 | tee "$LOG_DIR/bundle_check.log"
}

run_step_frozen_smoke() {
    step frozen_smoke
    bash scripts/cartridge_smoke.sh 2>&1 | tee "$LOG_DIR/frozen_smoke.log"
}

FAILED=0
for step_fn in run_step_unit_tests run_step_bundle_check; do
    if ! "$step_fn"; then
        echo
        echo "[CI FAIL] $step_fn tripped"
        FAILED=1
        # Bundle check needs unit tests to pass; skip if they failed.
        if [[ "$step_fn" == "run_step_unit_tests" ]]; then
            echo "[CI SKIP] bundle_check + frozen_smoke (unit tests failed)"
            break
        fi
    fi
done

if [[ "$FAILED" -eq 0 ]] && [[ -z "${SKIP_SMOKE:-}" ]]; then
    if ! run_step_frozen_smoke; then
        echo "[CI FAIL] run_step_frozen_smoke tripped"
        FAILED=1
    fi
elif [[ -z "${SKIP_SMOKE:-}" ]]; then
    echo "[CI SKIP] frozen_smoke (earlier step failed)"
fi

echo
echo "=============================="
if [[ "$FAILED" -eq 0 ]]; then
    echo "[CI PASS] All steps succeeded"
    echo "Logs: $LOG_DIR"
    exit 0
else
    echo "[CI FAIL] One or more steps tripped — see $LOG_DIR"
    exit 1
fi
