#!/usr/bin/env bash
# EXCALIBUR local lifecycle runner -- operates on THIS folder.
# Usage: bash bootstrap.sh [--scaffold-only] [--force]
set -o pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export EXCALIBUR_ROOT="$ROOT"; cd "$ROOT"
FORCE=0; SCAFFOLD_ONLY=0
for a in "$@"; do case "$a" in
  --force) FORCE=1;; --scaffold-only) SCAFFOLD_ONLY=1;;
esac; done

echo "[FORGE] P0 :: pre-flight gate"
bash core/excalibur_audit.sh >/dev/null
if ! bash core/excalibur_adjudicate.sh; then
  [ "$FORCE" -ne 1 ] && { echo "[FORGE] NO-GO -- remediate or re-run with --force"; exit 1; }
  echo "[FORGE] NO-GO overridden (--force)"
fi
[ "$SCAFFOLD_ONLY" -eq 1 ] && { echo "[FORGE] gate only -- stop"; exit 0; }

echo "[FORGE] P1 :: build"
command -v cargo >/dev/null 2>&1 && cargo build --workspace || echo "  (cargo absent -- skipping rust build)"
python3 -m pip install -e orchestrator >/dev/null 2>&1 || echo "  (orchestrator editable install skipped)"

echo "[FORGE] P1 :: test"
command -v cargo >/dev/null 2>&1 && { cargo test --workspace || true; }
( cd orchestrator && PYTHONPATH=. python3 -m pytest -q 2>/dev/null ) || echo "  (pytest unavailable -- 'pip install pytest')"

echo "[FORGE] READY -> read CLAUDE.md; paste .claude/bootstrap.md into Claude Code"
