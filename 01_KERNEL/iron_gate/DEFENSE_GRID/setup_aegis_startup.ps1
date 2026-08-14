# SPDX-License-Identifier: MIT

# AEGIS: User-Level Startup Registration
# Purpose: Ensures DEFENSE_GRID starts on logon without requiring Admin.

$STARTUP_FOLDER = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$BAT_PATH = "$STARTUP_FOLDER\AegisPulse.bat"
$TRIGGER_SCRIPT = "c:\Users\vizio\CAMELOT_OS\01_KERNEL\DEFENSE_GRID\activate_aegis.ps1"

Write-Host "Registering Aegis Defense Grid in User Startup..." -ForegroundColor Yellow

$batContent = "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$TRIGGER_SCRIPT`""
Set-Content -Path $BAT_PATH -Value $batContent

Write-Host "[AEGIS]: User-Level Startup Established at $BAT_PATH." -ForegroundColor Green
Write-Host "The Watchtower will now engage automatically at logon." -ForegroundColor Cyan

# Immediate Strike: Run the script now to verify
Write-Host "Pulse Ignition..." -ForegroundColor Yellow
& $TRIGGER_SCRIPT
