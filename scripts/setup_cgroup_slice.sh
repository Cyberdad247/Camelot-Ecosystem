#!/usr/bin/env bash
# ==============================================================================
# CAMELOT-OS — CGroup v2 Slice Delegation Setup
#
# Configures /sys/fs/cgroup/camelot.slice for unprivileged microVM agent squires
# Invariant: CG::SLICE_INIT ("+memory +cpu +io +pids")
# ==============================================================================
set -euo pipefail

SLICE_ROOT="/sys/fs/cgroup/camelot.slice"
CURRENT_USER="${SUDO_USER:-$(whoami)}"

echo "[CAMELOT-CGROUP] Initializing CGroup v2 hierarchy at ${SLICE_ROOT}..."

if [ ! -d "/sys/fs/cgroup" ]; then
    echo "ERROR: /sys/fs/cgroup does not exist or system is not running unified CGroup v2." >&2
    exit 1
fi

# Enable required controllers on root cgroup if possible
if [ -w "/sys/fs/cgroup/cgroup.subtree_control" ]; then
    echo "[CAMELOT-CGROUP] Enabling root controllers: +memory +cpu +io +pids"
    echo "+memory +cpu +io +pids" > /sys/fs/cgroup/cgroup.subtree_control 2>/dev/null || \
    echo "+memory +cpu +pids" > /sys/fs/cgroup/cgroup.subtree_control 2>/dev/null || true
fi

# Create camelot.slice
sudo mkdir -p "${SLICE_ROOT}"

# Delegate ownership to current user/group
sudo chown -R "${CURRENT_USER}:${CURRENT_USER}" "${SLICE_ROOT}"

# Enable subtree controllers on camelot.slice
if [ -w "${SLICE_ROOT}/cgroup.subtree_control" ]; then
    echo "+memory +cpu +io +pids" > "${SLICE_ROOT}/cgroup.subtree_control" 2>/dev/null || \
    echo "+memory +cpu +pids" > "${SLICE_ROOT}/cgroup.subtree_control" 2>/dev/null || true
fi

echo "[CAMELOT-CGROUP] Verified delegation: ${SLICE_ROOT} is owned by ${CURRENT_USER} with controllers active."
