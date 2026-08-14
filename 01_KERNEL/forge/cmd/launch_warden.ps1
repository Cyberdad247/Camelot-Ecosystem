# SPDX-License-Identifier: MIT

# 🚀 Omega_CHROME_WARDEN_LAUNCHER (v1.0)
# Guardian: Sir Chrome Warden

Write-Host "🌐 [WARDEN]: Booting Chrome DevTools MCP Bridge..." -ForegroundColor Cyan

$REPO_PATH = "C:\Users\vizio\CAMELOT_OS\02_FORGE\assimilated\chrome-devtools-mcp"
$BUILD_INDEX = "$REPO_PATH\build\src\index.js"

if (-Not (Test-Path $BUILD_INDEX)) {
    Write-Host "❌ [WARDEN]: Build index not found. Ensure 'npm run build' was successful." -ForegroundColor Red
    exit 1
}

# Ensure Chrome is running with remote debugging if required by the user context
# For now, we launch the MCP server which will attempt to connect to localhost:9222
node $BUILD_INDEX
