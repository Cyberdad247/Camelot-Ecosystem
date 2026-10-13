#!/bin/bash
# CAMELOT-OS Release Builder
set -e

echo "[⚡] Initiating Cargo Release Build for Camelot-Ecosystem..."
cargo build --release -p camelot-kernel
cargo build --release -p camelot-spawner
cargo build --release -p camelot-transport
cargo build --release -p camelot-runtime

echo "[🏆] Build successful. Binaries staged in target/release/."
