#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
# ========================================================================================
# [SYSTEM ACTIVATION]: CAMELOT-OS INTERPRETABLE CONTEXT METHODOLOGY (ICM) VFS SCAFFOLD
# [GOVERNANCE]: ANYA_FIRST_LAW // ANYA_LAST_LAW // THE_ELEVENTH_LAW // POST-CONDITIONS
# [SAFETY]: Zero-hotpath, deterministic directory slabs, and preflight probe verification
# ========================================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "================================================================================"
echo "🛡️  CAMELOT-OS VFS & ICM SCAFFOLDING BOOTSTRAP"
echo "================================================================================"
echo "• Root Directory  : ${REPO_ROOT}"
echo "• Invocation Mode : Deterministic Plane Initialization"
echo "--------------------------------------------------------------------------------"

# 1. Canonical System Planes
SYSTEM_PLANES=(
  "01_KERNEL"
  "02_FORGE"
  "03_VAULT"
  "04_KINETIC"
  "apps"
  "control_plane"
  "vfs"
  "scripts"
  "tests"
)

echo "⏳ [1/4] Scaffolding Core Architectural Planes..."
for plane in "${SYSTEM_PLANES[@]}"; do
  if [[ ! -d "${plane}" ]]; then
    mkdir -p "${plane}"
    echo "   [+] Created plane: ${plane}/"
  else
    echo "   [✓] Present plane: ${plane}/"
  fi
done

# 2. Canonical VFS Sub-Directory Slabs
VFS_SUBDIRS=(
  "vfs/backplane"
  "vfs/business"
  "vfs/cartridges"
  "vfs/checks"
  "vfs/edu"
  "vfs/fitness"
  "vfs/general"
  "vfs/genes"
  "vfs/knowledge"
  "vfs/logs"
  "vfs/nodes"
  "vfs/notebooks"
  "vfs/open_notebook"
  "vfs/skills"
  "vfs/source"
  "vfs/swarms"
  "vfs/telemetry"
  "vfs/worktree"
)

echo "⏳ [2/4] Verifying VFS Context Directory Slabs..."
for slab in "${VFS_SUBDIRS[@]}"; do
  if [[ ! -d "${slab}" ]]; then
    mkdir -p "${slab}"
    echo "   [+] Created slab: ${slab}/"
  fi
done
echo "   [✓] All 18 VFS Context Slabs Verified."

# 3. Mandatory VFS Specification Verification
echo "⏳ [3/4] Running 070 VFS Scaffold Integrity Preflight Probe..."
PYTHON_BIN=""
if command -v python3 &>/dev/null; then
  PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
  PYTHON_BIN="python"
fi

if [[ -n "${PYTHON_BIN}" ]]; then
  "${PYTHON_BIN}" -m control_plane.preflight.probes.vfs_present_run \
    --required vfs/preflight.md vfs/systeminstructions.md vfs/skills.md vfs/rosters.md vfs/protocols.md
  echo "   [✓] Preflight probe 070 passed."
else
  echo "   [!] Warning: Python binary not located in PATH; verifying files via shell..."
  MANDATORY_FILES=(
    "vfs/preflight.md"
    "vfs/systeminstructions.md"
    "vfs/skills.md"
    "vfs/rosters.md"
    "vfs/protocols.md"
  )
  for f in "${MANDATORY_FILES[@]}"; do
    if [[ ! -f "${f}" ]]; then
      echo "   [✗] Missing required VFS document: ${f}" >&2
      exit 1
    fi
  done
  echo "   [✓] Mandatory VFS files verified via direct shell probe."
fi

# 4. Measured VFS Resource Sweep Audit
echo "⏳ [4/4] Executing Non-Destructive VFS Resource Audit..."
if [[ -n "${PYTHON_BIN}" && -f "scripts/vfs_janitorial_sweep.py" ]]; then
  "${PYTHON_BIN}" scripts/vfs_janitorial_sweep.py "$@"
else
  echo "   [i] Janitorial sweep skipped (python or sweep script absent)."
fi

echo "================================================================================"
echo "✨ [VFS_STATUS]: POST-CONDITIONS SATISFIED — VFS SCAFFOLD FULLY LOCKED"
echo "================================================================================"
exit 0
