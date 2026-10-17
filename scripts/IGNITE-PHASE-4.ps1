# CAMELOT-OS: The Glass Panel Ignition (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 👁️ IGNITE PHASE 4: MOUNTING THE BIFROST BOARD" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

Push-Location apps/bifrost-board
try {
    Write-Host "[⚡] Installing React, Zustand, and Tailwind dependencies..." -ForegroundColor Green
    npm install

    Write-Host "[🛡️] Booting the Luxury Minimalist Brutalism UI..." -ForegroundColor Green
    Write-Host "     Access the HUD at: http://localhost:5173" -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "⚜️_SOVEREIGN_TRUTH" -ForegroundColor Magenta

    npm run dev
} finally {
    Pop-Location
}
