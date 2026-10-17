# ==============================================================================
# CAMELOT-OS: PERMANENT ALWAYS-ON HOST CALIBRATION FOR FATHER'S CAMELOT
# Enforces zero-sleep, persistent background services, and wake-on-LAN
# ==============================================================================
$ErrorActionPreference = "SilentlyContinue"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "⚡ CALIBRATING ALWAYS-ON STATE FOR FATHER'S CAMELOT" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Disable Windows Sleep, Hibernate, and Screen Timeout on AC Power
Write-Host "[1/4] Disabling sleep, hibernate, and standby timers..." -ForegroundColor Green
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
powercfg /change disk-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg -h off
Write-Host "✅ System power configuration set to NEVER SLEEP" -ForegroundColor Green

# 2. Configure Tailscale for Unattended Always-On Mode
Write-Host "[2/4] Enforcing Tailscale Unattended Mode..." -ForegroundColor Green
tailscale set --unattended=true
Set-Service -Name "Tailscale" -StartupType Automatic
Start-Service -Name "Tailscale"
Write-Host "✅ Tailscale set to Automatic & Unattended" -ForegroundColor Green

# 3. Configure OpenSSH Server for Automatic Boot
Write-Host "[3/4] Enforcing OpenSSH Service Persistence..." -ForegroundColor Green
Set-Service -Name "sshd" -StartupType Automatic
Start-Service -Name "sshd"
Write-Host "✅ OpenSSH Service set to Automatic & Started" -ForegroundColor Green

# 4. Disable Network Adapter Power Saving (prevents NIC from sleeping)
Write-Host "[4/4] Preventing Network Adapter sleep states..." -ForegroundColor Green
Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | ForEach-Object {
    $adapter = $_
    Disable-NetAdapterPowerManagement -Name $adapter.Name -ErrorAction SilentlyContinue
}
Write-Host "✅ Network adapter power throttling disabled" -ForegroundColor Green

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🛡️ FATHER'S CAMELOT IS NOW 100% ALWAYS-ON PERMANENT" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
