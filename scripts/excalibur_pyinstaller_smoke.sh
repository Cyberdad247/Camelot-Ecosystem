#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# scripts/excalibur_pyinstaller_smoke.sh — CI entry for the EXCALIBUR PyInstaller
# distribution.
#
# Rebuilds `dist/excalibur/excalibur{,.exe}` via PyInstaller, then runs the
# pytest smoke test in tests/test_excalibur_pyinstaller_smoke.py which boots
# the binary as a subprocess on port 8829 and asserts:
#
#   * /health → 200
#   * / (dashboard) → 200 with inline rel="icon" favicon
#   * POST /api/go → 200 with valid X-Camelot-Auth header, 401 without
#   * POST /api/rezero → 200 (iron gate → PAUSED)
#   * excalibur_state.json lands in the operator-supplied EXCALIBUR_DATA_DIR
#     (defaults to %APPDATA%\EXCALIBUR on Windows, $XDG_DATA_HOME/excalibur on
#     POSIX — driven by the controller's _data_root() helper)
#   * logs/excalibur_events.jsonl gets one row per //go and //rezero call
#
# Usage:
#   bash scripts/excalibur_pyinstaller_smoke.sh               # from repo root
#   PYTHON=.venv/Scripts/python.exe bash scripts/excalibur_pyinstaller_smoke.sh
#   SKIP_REBUILD=1 bash scripts/excalibur_pyinstaller_smoke.sh  # use existing dist/
#
# Exits 0 on full pass, non-zero on any failure.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"

PYTHON="${PYTHON:-python}"
LOG_DIR="${LOG_DIR:-data/ci_logs}"
mkdir -p "$LOG_DIR"

echo
echo "=============================="
echo "EXCALIBUR PyInstaller smoke"
echo "REPO: $REPO_ROOT"
echo "PYTHON: $PYTHON"
echo "Log: $LOG_DIR/excalibur_pyinstaller_smoke.log"
echo "=============================="

# Cheap pre-flight: PyInstaller must be importable, otherwise the test is
# skipped (the pytest gates on EXCALIBUR_BUILD_ON_TEST, which we set here).
if ! "$PYTHON" -c "import PyInstaller; print('PyInstaller', PyInstaller.__version__)" 2>/dev/null; then
    echo
    echo "[SMOKE FAIL] PyInstaller not installed in \$PYTHON. Install it first:"
    echo "    $PYTHON -m pip install pyinstaller"
    exit 2
fi

# Pre-flight: spec + binaries on disk.
test -f "$REPO_ROOT/excalibur.spec" || { echo "[SMOKE FAIL] excalibur.spec missing"; exit 2; }
test -f "$REPO_ROOT/excalibur.py"   || { echo "[SMOKE FAIL] excalibur.py missing";   exit 2; }
test -f "$REPO_ROOT/excalibur_controller.py" || { echo "[SMOKE FAIL] excalibur_controller.py missing"; exit 2; }

# Skip-rebuild shorthand. Both env-var names are honoured because:
#   * `EXCALIBUR_SKIP_PYINSTALLER_REBUILD` is the canonical (verbose) name
#     the pytest test reads.
#   * `SKIP_REBUILD` is the friendly shorthand documented at the top of
#     this file. Setting EITHER one tells the test to reuse the cached
#     `dist/excalibur/excalibur{,.exe}` instead of triggering a fresh
#     PyInstaller build (saves ~60-90 s on Windows).
# Truthiness semantics: presence = opt-in to skip. Any non-empty string
# triggers skip (including `0` — `[[ -n "0" ]]` is true). To OPT OUT set
# the variable to the empty string (`SKIP_REBUILD= bash ...`) or `unset`
# it. The Python test reads the same rule.
if [[ -n "${SKIP_REBUILD:-}" || -n "${EXCALIBUR_SKIP_PYINSTALLER_REBUILD:-}" ]]; then
    export EXCALIBUR_SKIP_PYINSTALLER_REBUILD="${EXCALIBUR_SKIP_PYINSTALLER_REBUILD:-${SKIP_REBUILD:-1}}"
    echo "[smoke] SKIP_REBUILD detected; will reuse cached dist/excalibur/ binary."
fi

# Tee everything to a CI log so a failure leaves a useful artefact.
export EXCALIBUR_BUILD_ON_TEST=1
"$PYTHON" -m pytest tests/test_excalibur_pyinstaller_smoke.py \
    -v -s --tb=short --log-cli-level=INFO \
    2>&1 | tee "$LOG_DIR/excalibur_pyinstaller_smoke.log"

echo
echo "=============================="
echo "[SMOKE PASS] EXCALIBUR PyInstaller binary booted and answered every gate."
echo "Log: $LOG_DIR/excalibur_pyinstaller_smoke.log"
echo "=============================="
