<#
  CAMELOT-OS Lakesha Drone Starter

  Run locally on Lakesha from any PowerShell directory. This script does not
  store secrets; it prompts for the two required values if they are not already
  set in the current session.
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = "C:\Users\Camelot-os",
    [string]$PackagesDir = "$env:LOCALAPPDATA\Camelot\cartridge\packages",
    [string]$NodeId = "kba-drone-lakesha",
    [string]$HostAddress = "100.100.155.55",
    [int]$Port = 9000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    Write-Host "[FATAL] $Message" -ForegroundColor Red
    exit 1
}

function Require-Command([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        Fail "Required command not found: $Name"
    }

    return $command
}

Write-Host "[SIR_CODEX] Starting Lakesha drone from $RepoRoot" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    Fail "Repo root not found: $RepoRoot"
}

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot "control_plane\drone_node.py"))) {
    Fail "control_plane\drone_node.py not found under $RepoRoot"
}

if (-not $env:WEBHOOK_SECRET) {
    $env:WEBHOOK_SECRET = Read-Host "WEBHOOK_SECRET"
}

if (-not $env:CAMELOT_CARTRIDGE_HMAC_KEY) {
    $env:CAMELOT_CARTRIDGE_HMAC_KEY = Read-Host "CAMELOT_CARTRIDGE_HMAC_KEY"
}

if (-not $env:WEBHOOK_SECRET) {
    Fail "WEBHOOK_SECRET is still empty."
}

if (-not $env:CAMELOT_CARTRIDGE_HMAC_KEY) {
    Fail "CAMELOT_CARTRIDGE_HMAC_KEY is still empty."
}

New-Item -ItemType Directory -Path $PackagesDir -Force | Out-Null
$env:CAMELOT_CARTRIDGE_PACKAGES = $PackagesDir

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Require-Command py
}

Set-Location $RepoRoot

Write-Host "[OK] WEBHOOK_SECRET set: $([bool]$env:WEBHOOK_SECRET)" -ForegroundColor Green
Write-Host "[OK] HMAC key set: $([bool]$env:CAMELOT_CARTRIDGE_HMAC_KEY)" -ForegroundColor Green
Write-Host "[OK] Packages dir: $PackagesDir" -ForegroundColor Green
Write-Host "[INFO] Binding drone to ${HostAddress}:$Port" -ForegroundColor Yellow

& $python.Source -m control_plane.drone_node `
    --node-id $NodeId `
    --host $HostAddress `
    --port $Port `
    --packages-dir $PackagesDir
