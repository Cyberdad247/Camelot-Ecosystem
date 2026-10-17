#!/usr/bin/env bash
# ==============================================================================
# CAMELOT-OS — Host Memory & KSM Density Tuning (ARM64 / WSL2 / Pi5)
#
# Implements Invariant: HOST::MULTIPLIERS
# KSM (run=1, scan=1000, sleep=20ms) + vm.overcommit_memory=1 + fs.file-max=1048576
# Enables 35-50 concurrent microVMs within a 2.5 GiB memory pool.
# ==============================================================================
set -euo pipefail

echo "[CAMELOT-TUNE] Applying Host Density & Kernel Multipliers..."

# 1. Kernel Samepage Merging (KSM)
if [ -d "/sys/kernel/mm/ksm" ]; then
    echo "[CAMELOT-TUNE] Enabling Kernel Samepage Merging (KSM)..."
    echo 1 | sudo tee /sys/kernel/mm/ksm/run > /dev/null
    echo 1000 | sudo tee /sys/kernel/mm/ksm/pages_to_scan > /dev/null
    echo 20 | sudo tee /sys/kernel/mm/ksm/sleep_millisecs > /dev/null
    echo "[CAMELOT-TUNE] KSM active: run=1, pages_to_scan=1000, sleep_millisecs=20ms"
else
    echo "[CAMELOT-TUNE] NOTICE: /sys/kernel/mm/ksm not found in this kernel; skipping KSM."
fi

# 2. Virtual Memory Overcommit (vm.overcommit_memory=1)
echo "[CAMELOT-TUNE] Configuring memory overcommit (vm.overcommit_memory=1)..."
sudo sysctl -w vm.overcommit_memory=1 > /dev/null

# 3. File Descriptor Ceiling (fs.file-max=1048576)
echo "[CAMELOT-TUNE] Raising file descriptor ceiling (fs.file-max=1048576)..."
sudo sysctl -w fs.file-max=1048576 > /dev/null

echo "[CAMELOT-TUNE] Density tuning complete. Ready for 50-VM progressive burst."
