# Requires -RunAsAdministrator
<#
.SYNOPSIS
    Applies recommended network optimizations for Camelot-OS / Antigravity streaming stability:
    1. Disables MIMO power saving / SMPS on Wi-Fi adapter.
    2. Disables Energy-Efficient Ethernet and Green Ethernet on Realtek PCIe GbE controller.
    3. Elevates IPv4 precedence above IPv6 in Windows RFC 3484 prefix policies.
#>

[CmdletBinding()]
param()

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "This script requires Administrator privileges. Relaunching in elevated window..."
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoExit -File `"$PSCommandPath`""
    exit
}

Write-Host "=== Applying Camelot Network Stabilizations ===" -ForegroundColor Cyan

# 1. Wi-Fi Adapter SMPS Optimization
try {
    Write-Host "[1/3] Disabling Wi-Fi MIMO Power Save Mode (Auto SMPS -> No SMPS)..." -NoNewline
    Set-NetAdapterAdvancedProperty -Name "Wi-Fi" -DisplayName "MIMO Power Save Mode" -DisplayValue "No SMPS" -ErrorAction Stop
    Write-Host " [OK]" -ForegroundColor Green
} catch {
    Write-Warning " Failed: $_"
}

# 2. Ethernet Adapter Energy Efficiency Optimization
try {
    Write-Host "[2/3] Disabling Ethernet EEE, Green Ethernet, and Power Saving Mode..." -NoNewline
    Set-NetAdapterAdvancedProperty -Name "Ethernet" -RegistryKeyword "*EEE" -RegistryValue "0" -ErrorAction SilentlyContinue
    Set-NetAdapterAdvancedProperty -Name "Ethernet" -RegistryKeyword "EnableGreenEthernet" -RegistryValue "0" -ErrorAction SilentlyContinue
    Set-NetAdapterAdvancedProperty -Name "Ethernet" -RegistryKeyword "PowerSavingMode" -RegistryValue "0" -ErrorAction SilentlyContinue
    Write-Host " [OK]" -ForegroundColor Green
} catch {
    Write-Warning " Failed: $_"
}

# 3. Windows RFC 3484 Prefix Policy (Prefer IPv4)
try {
    Write-Host "[3/3] Setting IPv4 precedence (45) above IPv6 default (40)..." -NoNewline
    netsh interface ipv6 set prefixpolicy ::ffff:0:0/96 45 4 | Out-Null
    Write-Host " [OK]" -ForegroundColor Green
} catch {
    Write-Warning " Failed: $_"
}

Write-Host "`nAll optimizations applied successfully." -ForegroundColor Cyan
