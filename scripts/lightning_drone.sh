#!/bin/bash
# SPDX-License-Identifier: MIT

set -e
# 1. Enforce Scarcity Protocol (1GB ZRAM LZ4)
if ! lsmod | grep -q zram; then modprobe zram num_devices=1; fi
echo lz4 > /sys/block/zram0/comp_algorithm && echo 1024M > /sys/block/zram0/disksize
mkswap /dev/zram0 && swapon -p 32767 /dev/zram0
# 2. Install Rust 'uv' Accelerator & Tailscale
apt-get update -qq && apt-get install -y -qq curl git
curl -fsSL https://tailscale.com/install.sh | sh
curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/usr/local/bin" sh
# 3. Forge Directory Lattice
mkdir -p /opt/camelot/{bin,cartridges,zeroclaw,bifrost_client} /var/camelot/world_tree
useradd -r -s /bin/false camelot || true
chown -R camelot:camelot /opt/camelot /var/camelot && chmod 750 /opt/camelot
# 4. Authenticate to Mesh (Requires $TS_AUTH_KEY injected by SIR_OCTAVIAN)
tailscale up --authkey=$TS_AUTH_KEY --hostname=empire-drone-$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
