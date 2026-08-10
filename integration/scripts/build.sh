#!/usr/bin/env bash
# Build every slice component natively (no Docker).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
cd "$INTEGRATION_DIR"

mkdir -p "$BIN_DIR"

echo "── contracts + console (tsc)"
npm install --no-audit --no-fund >/dev/null
npm run build >/dev/null

echo "── gateway (go)"
(cd gateway && go build -o "$BIN_DIR/gateway" .)

echo "── node-agent (cargo)"
(cd .. && cargo build -q -p camelot-node-agent)
cp ../target/debug/camelot-node-agent "$BIN_DIR/"

echo "build OK → $BIN_DIR"
