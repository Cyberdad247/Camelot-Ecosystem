# CAMELOT-OS: The Cognitive VFS Ignition (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 🧠 IGNITE PHASE 5: MOUNTING THE COGNITIVE VFS" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "[⚡] Scaffolding the Open Knowledge Format (OKF) tree..." -ForegroundColor Green
New-Item -ItemType Directory -Path ".agent/Personas/Merlin_Omega" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent/Personas/Sir_Boris" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent/Personas/Sir_Codex" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent/skills" -Force | Out-Null

Write-Host "[🛡️] VFS Topology Generated." -ForegroundColor Green
Write-Host "     Root Anchor: .agent/Claude.md" -ForegroundColor Gray
Write-Host "     Omni-Router: .agent/Router.md" -ForegroundColor Gray
Write-Host "     Knight Nodes: .agent/Personas/" -ForegroundColor Gray
Write-Host ""
Write-Host "[🏆] The AI's physical memory structure is locked." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "⚜️_SOVEREIGN_TRUTH" -ForegroundColor Magenta
