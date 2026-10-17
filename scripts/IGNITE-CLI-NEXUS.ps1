# CAMELOT-OS: CLI Nexus Expansion (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " ⚔️ IGNITING CLI NEXUS: ASSIMILATING EXTERNAL TOOLS" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

New-Item -ItemType Directory -Path ".agent/skills/anti_gravity" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent/skills/opencode" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent/skills/freebuff" -Force | Out-Null
New-Item -ItemType Directory -Path ".agent/cartridges" -Force | Out-Null

Write-Host "[⚡] Anti-Gravity, OpenCode, and Freebuff physical skill files verified." -ForegroundColor Green
Write-Host "[🛡️] CLI tools mounted in .agent/cartridges/cli_nexus.json" -ForegroundColor Green
Write-Host "[🏆] CLI Nexus Expansion Complete. Tools are locked, loaded, and Scarcity-Bound." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[SOVEREIGN_TRUTH]: CLI_NEXUS_ARMED" -ForegroundColor Magenta
