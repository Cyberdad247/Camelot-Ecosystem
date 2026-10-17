# PowerShell Ignition Script for Phase 3 MCP Bridge
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "⚡ IGNITING CONTROL PLANE PHASE 3: MCP BRIDGE" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Compile the Multivoice-Router with embedded MCP server
Push-Location control_plane
try {
    go build -o multivoice_router.exe multivoice_router.go mcp_server.go
    Write-Host "✅ Built control_plane/multivoice_router.exe binary" -ForegroundColor Green
} finally {
    Pop-Location
}

# 2. Check universal MCP config presence
if (Test-Path ".camelot\config\mcp_config.json") {
    Write-Host "✅ Universal MCP mount config verified (.camelot/config/mcp_config.json)" -ForegroundColor Green
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🛡️ CONTROL PLANE PHASE 3 MCP BRIDGE ARMED" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
