#!/bin/bash
set -e

echo "=================================================="
echo "⚡ IGNITING CONTROL PLANE PHASE 3: MCP BRIDGE"
echo "=================================================="

# Ensure Go is in PATH across Git Bash, WSL, and standard environments
export PATH="/c/Program Files/Go/bin:/c/Go/bin:/mnt/c/Program Files/Go/bin:$PATH"

# 1. Compile the Multivoice-Router with embedded MCP server
cd control_plane
if command -v go.exe >/dev/null 2>&1; then
    go.exe build -o multivoice_router.exe multivoice_router.go mcp_server.go
elif command -v go >/dev/null 2>&1; then
    go build -o multivoice_router.exe multivoice_router.go mcp_server.go
elif [ -f "/mnt/c/Program Files/Go/bin/go.exe" ]; then
    "/mnt/c/Program Files/Go/bin/go.exe" build -o multivoice_router.exe multivoice_router.go mcp_server.go
elif [ -f "/c/Program Files/Go/bin/go.exe" ]; then
    "/c/Program Files/Go/bin/go.exe" build -o multivoice_router.exe multivoice_router.go mcp_server.go
else
    echo "❌ Error: Go binary not found in PATH or standard install directories."
    exit 1
fi

echo "✅ Built control_plane/multivoice_router.exe binary"
cd ..

# 2. Check universal MCP config presence
if [ -f ".camelot/config/mcp_config.json" ]; then
    echo "✅ Universal MCP mount config verified (.camelot/config/mcp_config.json)"
fi

echo "=================================================="
echo "🛡️ CONTROL PLANE PHASE 3 MCP BRIDGE ARMED"
echo "=================================================="
