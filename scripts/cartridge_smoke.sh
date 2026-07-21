#!/usr/bin/env bash
# scripts/cartridge_smoke.sh — verify the PyInstaller bundle end-to-end.
#
# Runs the six frozen-binary smokes for the cartridge subcommand:
#   1. --version boot            (must exit 0)
#   2. cartridge --list           (must exit 0; default behaviour)
#   3. cartridge --emit FRESH     (must exit 0; trio files written)
#   4. cartridge --emit MODIFIED  (must exit 1 — refusal without --force)
#   5. cartridge --emit --force   (must exit 0; overwrites modified trio)
#   6. cartridge --emit from non-repo cwd (must exit 0; PyInstaller
#      bundle resolves ``cartridges.v4000_trio`` regardless of CWD)
#
# Every smoke's full stdout + stderr is captured to ``data/smoke_logs/``
# so a post-run diff in CI can surface regressions. Designed to be run
# after a fresh ``pyinstaller --clean camelot.spec`` build — invoke
# ``scripts/ci_smoke.sh`` for the orchestrator version that wraps both
# this script AND ``verify_frozen_bundle.py``.
#
# Usage:
#   bash scripts/cartridge_smoke.sh                    # use ./dist/camelot.exe
#   EXE=path/to/custom.exe bash scripts/cartridge_smoke.sh
set -euo pipefail

cd "$(dirname "$0")/.."

REPO_ROOT="$(pwd)"
EXE="${EXE:-$REPO_ROOT/dist/camelot.exe}"

LOG_DIR="$REPO_ROOT/data/smoke_logs"
mkdir -p "$LOG_DIR"

if [[ ! -f "$EXE" ]]; then
    echo "[FAIL] $EXE not found. Run 'pyinstaller --clean camelot.spec' first."
    exit 2
fi

# Stable logger: tee to a per-smoke log + echo a single OK/FAIL line.
# Returns the wrapped command's exit code on FAIL so set -e trips.
run_smoke() {
    local name="$1"
    shift
    local log="$LOG_DIR/${name}.log"
    echo "====== $name ======"
    if "$@" 2>&1 | tee "$log"; then
        echo "[OK] $name"
        echo
    else
        local rc="${PIPESTATUS[0]}"
        echo "[FAIL] $name (rc=$rc — see $log)"
        exit "$rc"
    fi
}

# Pick a tmp dir that lives across smoke 3..5 so the trio persists
# between them. /tmp on bash-on-Windows maps to a real Windows path.
T="$(mktemp -d)"
T2="$(mktemp -d)"
trap 'rm -rf "$T" "$T2"' EXIT

# Smoke 1: --version boot
run_smoke boot_version \
    "$EXE" --version

# Smoke 2: cartridge --list (default behaviour)
run_smoke cartridge_list_default \
    "$EXE" --no-context cartridge --list

# Smoke 3: cartridge --emit FRESH target (must proceed + write trio)
run_smoke cartridge_emit_fresh \
    "$EXE" --no-context cartridge --emit smoke_fresh --target "$T/p1"

# Smoke 4: cartridge --emit MODIFIED trio without --force (must refuse rc=1)
# Seed the trio with user content, then re-emit without --force.
mkdir -p "$T/p2"
printf '# Blueprint — p2\n\n## USER-OWNED RATIONALE — DO NOT CLOBBER\n' \
    > "$T/p2/blueprint.md"
run_smoke cartridge_emit_modified_refuses \
    "$EXE" --no-context cartridge --emit smoke_modified --target "$T/p2" \
    || {
        # Smoke 4 expects rc=1, NOT rc=0. The harness expects success on
        # every smoke; this one ENFORCES rc=1 by hand.
        log="$LOG_DIR/cartridge_emit_modified_refuses.log"
        # Re-run, capture rc, assert 1.
        set +e
        "$EXE" --no-context cartridge --emit smoke_modified \
            --target "$T/p2" > "$log" 2>&1
        rc=$?
        set -e
        if [[ "$rc" -eq 1 ]]; then
            echo "[OK] cartridge_emit_modified_refuses (rc=1)"
            echo
        else
            echo "[FAIL] cartridge_emit_modified_refuses (expected rc=1, got $rc — see $log)"
            exit 1
        fi
    }

# Smoke 5: cartridge --emit --force (must proceed + rewrite the modified trio)
run_smoke cartridge_emit_force_overrides \
    "$EXE" --no-context cartridge --emit smoke_modified --target "$T/p2" --force

# Smoke 6: cartridge --emit from a non-repo cwd (the binary must still
# resolve cartridges.v4000_trio via PyInstaller's bundled import path).
run_smoke cartridge_emit_non_repo_cwd \
    bash -c "cd '$T2' && '$EXE' --no-context cartridge --emit smoke_cwdtest --target '$T2/p3'"
run_smoke cartridge_emit_non_repo_cwd_actual \
    bash -c "cd '$T2' && '$EXE' --no-context cartridge --emit smoke_cwdtest_real --target '$T2/p4'"

echo "====== Smoke harness complete ======"
echo "Logs: $LOG_DIR"
echo "Smokes: $(ls -1 "$LOG_DIR" | wc -l) files"
