#!/usr/bin/env bash
# forge_deploy.sh :: LUKAS_FORGE orchestrator :: PROFILE nitro-v15-cpu
# Sequence: SWARM SQUIRES -> SIR CODEX -> SIR HELIO -> SIR BORIS
set -o pipefail
ROOT="${EXCALIBUR_ROOT:-$HOME/excalibur}"
export EXCALIBUR_ROOT="$ROOT"

# --- SWARM SQUIRES :: concurrent scaffold ---
mkdir -p "$ROOT/core/audit_logs" &
mkdir -p "$ROOT/core/topology_maps" &
wait

# --- SIR CODEX :: probe -> JSON telemetry ---
bash "$ROOT/core/excalibur_audit.sh" >/dev/null

# --- SIR HELIO :: static topology at core/excalibur_topology.md ---

# --- SIR BORIS :: adjudication ---
bash "$ROOT/core/excalibur_adjudicate.sh"
