#!/usr/bin/env bash
# =============================================================================
# Camelot-OS — harness CI gate (thin wrapper)
#
# Single CI entry point for the contract-harness battery. Every build / PR /
# release must pass this gate before promotion. The actual checks, order, and
# per-check reporting live in harness/run_all.py (see
# docs/architecture/harness-gate.md for the documented checklist); this script
# exists so CI can invoke the gate without knowing the interpreter details.
#
# Any check failure makes run_all.py exit non-zero, which (via `set -e`) makes
# this script fail the build too.
#
# Usage:  bash harness/gate.sh
# Env:    PYTHON overrides the interpreter (default: python)
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${PYTHON:-python}" "$HERE/run_all.py" "$@"
