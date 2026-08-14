# SPDX-License-Identifier: MIT

$ErrorActionPreference = "Stop"

Write-Host "EXCALIBUR OS: SYSTEM BOOT SEQUENCE" -ForegroundColor Yellow

# 0. Sync Ouroboros (NotebookLM) Bridge
Write-Host "Initializing NotebookLM Integration..." -ForegroundColor Cyan
& "c:\Users\vizio\CAMELOT_OS\01_KERNEL\senses\integrations\ouroboros_sync.ps1"

# 0.1 Start Saltare MCP Gateway
Write-Host "Igniting Saltare Gateway (Port 8080)..." -ForegroundColor Cyan
$SALT_BIN = "c:\Users\vizio\CAMELOT_OS\02_FORGE\KINETIC_ARMORY\saltare\saltare_gateway.exe"
$SALT_CONF = "c:\Users\vizio\CAMELOT_OS\01_KERNEL\EXCALIBUR\config\saltare.toml"
Start-Process -FilePath $SALT_BIN -ArgumentList "mcp", "http", "--port", "8080", "--config", $SALT_CONF

# 1. Start Backend
Write-Host "Igniting Merlin Kernel (Port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "`$env:GEMINI_API_KEY='${GEMINI_API_KEY}'; python c:\Users\vizio\CAMELOT_OS\01_KERNEL\core\excalibur.py"

# 2. Start Frontend
Write-Host "Igniting Celestial Lab (Port 3005)..." -ForegroundColor Cyan
Set-Location "c:\Users\vizio\CAMELOT_OS\02_FORGE\web"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "npx next dev -p 3005 -H 127.0.0.1"

# 3. Start Gradio Interface
Write-Host "Igniting Sovereign Spire (Gradio, Port 7860)..." -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "python c:\Users\vizio\CAMELOT_OS\01_KERNEL\EXCALIBUR\system\gradio_app.py"

Write-Host "SYSTEM ACTIVE. ALL INTERFACES SEALED." -ForegroundColor Green
Write-Host "--- SOVEREIGN URLS ---" -ForegroundColor Yellow
Write-Host "🎬 Media Hub: http://100.118.224.52 (or cybertronia.tailcd0c29.ts.net)"
Write-Host "🧠 Sovereign Spire: http://100.118.224.52:8081 (or cybertronia.tailcd0c29.ts.net:8081)"
Write-Host "🌌 Celestial Lab: http://100.118.224.52:8082 (or cybertronia.tailcd0c29.ts.net:8082)"
Write-Host "----------------------"
