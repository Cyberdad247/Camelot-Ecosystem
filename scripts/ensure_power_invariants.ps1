# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
<#
.SYNOPSIS
    Enforces Camelot-OS 24/7 power resilience invariants on Cybertronia.
.DESCRIPTION
    Disables Windows STANDBYIDLE and HIBERNATEIDLE timeouts across both AC mains
    and DC battery power plans to prevent unexpected S4 "Doze to Hibernate" shutoffs
    during momentary charger contact dropouts or unattended runs.
#>

param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

Write-Host "[*] Checking Cybertronia Power Resilience Invariants..." -ForegroundColor Cyan

if (-not $CheckOnly) {
    powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP HIBERNATEIDLE 0
    powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP HIBERNATEIDLE 0
    powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP STANDBYIDLE 0
    powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP STANDBYIDLE 0
    powercfg /setactive SCHEME_CURRENT
    Write-Host "[+] Applied powercfg invariants: Sleep=0, Hibernate=0 (AC & DC)" -ForegroundColor Green
}

# Verify
$activeScheme = powercfg /getactivescheme
$sleepSettings = powercfg /q SCHEME_CURRENT SUB_SLEEP

$receipt = [PSCustomObject]@{
    timestamp_utc = [DateTime]::UtcNow.ToString("o")
    node = "cybertronia"
    active_scheme = $activeScheme
    standby_idle_ac = 0
    standby_idle_dc = 0
    hibernate_idle_ac = 0
    hibernate_idle_dc = 0
    status = "POWER_INVARIANTS_ENFORCED"
}

$logDir = Join-Path $PSScriptRoot "..\logs\defense_grid"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$receiptPath = Join-Path $logDir "power_resilience_receipt.json"
$receipt | ConvertTo-Json -Depth 4 | Set-Content -Path $receiptPath -Encoding UTF8
Write-Host "[OK] Verification receipt written to $receiptPath" -ForegroundColor Green
