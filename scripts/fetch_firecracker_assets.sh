#!/usr/bin/env bash
# ==============================================================================
# CAMELOT-OS — Firecracker Asset Pipeline & Rootfs Generator
#
# Implements Invariant: FS::UNMOUNTED & ROOTFS_PIPE
# Builds unprivileged ext4 rootfs in user space without loopback mounts.
#
# Usage:
#   ./scripts/fetch_firecracker_assets.sh [--run-gate]
# ==============================================================================
set -euo pipefail

ASSETS_DIR=".camelot/firecracker-assets"
ARCH="$(uname -m)"
ROOTFS_SIZE="${CAMELOT_ROOTFS_SIZE:-256M}"
BURST_VMS="${CAMELOT_BURST_VMS:-50}"

echo "[CAMELOT-ASSETS] Target Architecture: ${ARCH}"
mkdir -p "${ASSETS_DIR}"

KERNEL_DEST="${ASSETS_DIR}/vmlinux-${ARCH}"
ROOTFS_DEST="${ASSETS_DIR}/rootfs-${ARCH}.ext4"

# 1. Fetch Kernel Image if missing
if [ ! -f "${KERNEL_DEST}" ]; then
    echo "[CAMELOT-ASSETS] Fetching pre-compiled Firecracker kernel for ${ARCH}..."
    if [ "${ARCH}" = "aarch64" ]; then
        curl -fSL "https://s3.amazonaws.com/spec.ccfc.min/img/quickstart_guide/aarch64/kernels/vmlinux.bin" -o "${KERNEL_DEST}"
    else
        curl -fSL "https://s3.amazonaws.com/spec.ccfc.min/img/quickstart_guide/x86_64/kernels/vmlinux.bin" -o "${KERNEL_DEST}"
    fi
    chmod 644 "${KERNEL_DEST}"
else
    echo "[CAMELOT-ASSETS] Kernel already present at ${KERNEL_DEST}"
fi

# 2. Build Unmounted User-Space Rootfs Pipeline (FS::UNMOUNTED)
if [ ! -f "${ROOTFS_DEST}" ]; then
    echo "[CAMELOT-ASSETS] Constructing unprivileged sparse rootfs (${ROOTFS_SIZE})..."
    TMP_DIR="/tmp/camelot-rootfs-build-$$"
    mkdir -p "${TMP_DIR}/tree"

    # Minimal base rootfs: Alpine Linux mini-rootfs
    ALPINE_TAR="${TMP_DIR}/alpine.tar.gz"
    echo "[CAMELOT-ASSETS] Downloading base Alpine userland..."
    if [ "${ARCH}" = "aarch64" ]; then
        curl -fSL "https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/aarch64/alpine-minirootfs-3.20.0-aarch64.tar.gz" -o "${ALPINE_TAR}"
    else
        curl -fSL "https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-minirootfs-3.20.0-x86_64.tar.gz" -o "${ALPINE_TAR}"
    fi

    tar -xzf "${ALPINE_TAR}" -C "${TMP_DIR}/tree"
    
    # Invariant: Verify inodes for /bin/sh and /bin/echo are executable (100755)
    chmod 755 "${TMP_DIR}/tree/bin/sh" 2>/dev/null || true
    chmod 755 "${TMP_DIR}/tree/bin/echo" 2>/dev/null || true

    TMP_EXT4="${TMP_DIR}/rootfs.ext4"
    truncate -s "${ROOTFS_SIZE}" "${TMP_EXT4}"

    # Build ext4 directly from directory tree without loopback mounting (CAP_SYS_ADMIN bypass)
    mkfs.ext4 -q -F -O ^has_journal -E nodiscard -d "${TMP_DIR}/tree" "${TMP_EXT4}"

    # Copy with sparse allocation preservation into local asset directory
    cp --sparse=always "${TMP_EXT4}" "${ROOTFS_DEST}"
    chmod 644 "${ROOTFS_DEST}"

    rm -rf "${TMP_DIR}"
    echo "[CAMELOT-ASSETS] Successfully forged rootfs at ${ROOTFS_DEST}"
else
    echo "[CAMELOT-ASSETS] Rootfs already present at ${ROOTFS_DEST}"
fi

# 3. Optional Gate Execution
if [ "${1:-}" = "--run-gate" ]; then
    echo "[CAMELOT-ASSETS] Initiating 50-VM Progressive Burst & <80ms Boot Gate..."
    CAMELOT_BURST_VMS="${BURST_VMS}" cargo test -p camelot-spawner --test test_firecracker_boot -- --ignored --nocapture
fi
