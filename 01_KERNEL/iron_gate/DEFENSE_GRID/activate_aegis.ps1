# AEGIS: Background Activation Script
# Starts the Eternal Heartbeat daemon in a hidden window.

$EXE_PATH = "c:\Users\vizio\CAMELOT_OS\01_KERNEL\cmd\pulse\heartbeat.exe"
$LOG_PATH = "c:\Users\vizio\CAMELOT_OS\logs\aegis_pulse.log"
$ERR_PATH = "c:\Users\vizio\CAMELOT_OS\logs\aegis_err.log"

if (-not (Test-Path "c:\Users\vizio\CAMELOT_OS\logs")) {
    New-Item -ItemType Directory -Path "c:\Users\vizio\CAMELOT_OS\logs" -Force
}

Write-Host "[AEGIS]: Initiating Background Watchtower..." -ForegroundColor Yellow

# Check if already running
$existing = Get-Process -Name "heartbeat" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[AEGIS]: Pulse already active (PID: $($existing.Id)). Restarting..." -ForegroundColor Yellow
    Stop-Process -Name "heartbeat" -Force
    Start-Sleep -Seconds 2
}

# Start in background with split logging redirection
Start-Process -FilePath $EXE_PATH -WindowStyle Hidden -RedirectStandardOutput $LOG_PATH -RedirectStandardError $ERR_PATH

Write-Host "[AEGIS]: Watchtower Pulse backgrounded." -ForegroundColor Green
Write-Host "Logs: $LOG_PATH" -ForegroundColor Cyan
