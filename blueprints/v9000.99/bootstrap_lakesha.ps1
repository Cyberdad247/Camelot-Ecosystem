<#
  CAMELOT-OS Lakesha Local Bootstrap

  Run this locally on the Lakesha Windows host after receiving it via Taildrop.
  This script intentionally does not contain secrets. Set WEBHOOK_SECRET and
  CAMELOT_CARTRIDGE_HMAC_KEY in the local Lakesha session before execution.
#>

[CmdletBinding()]
param(
    [string]$RepoUrl = "https://github.com/Cyberdad247/Camelot-Ecosystem.git",
    [string]$InstallRoot = "$env:USERPROFILE\Camelot-Ecosystem",
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
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Fail "Required command not found on Lakesha: $Name"
    }
}

Write-Host "[SIR_CODEX] Starting Lakesha local bootstrap." -ForegroundColor Cyan

Require-Command git

if (-not $env:WEBHOOK_SECRET) {
    Fail "WEBHOOK_SECRET is not set in this local Lakesha session."
}

if (-not $env:CAMELOT_CARTRIDGE_HMAC_KEY) {
    Fail "CAMELOT_CARTRIDGE_HMAC_KEY is not set in this local Lakesha session."
}

if (-not (Test-Path -LiteralPath $InstallRoot)) {
    git clone $RepoUrl $InstallRoot
} else {
    Write-Host "[INFO] Repository already exists: $InstallRoot" -ForegroundColor Yellow
}

Set-Location $InstallRoot

New-Item -ItemType Directory -Path $PackagesDir -Force | Out-Null
$env:CAMELOT_CARTRIDGE_PACKAGES = $PackagesDir

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    Fail "No Python runtime found. Install Python or add it to PATH on Lakesha."
}

Write-Host "[INFO] Installing required Python packages locally." -ForegroundColor Yellow
& $python.Source -m pip install cryptography pydantic
if ($LASTEXITCODE -ne 0) {
    Fail "Python dependency install failed."
}

Write-Host "[INFO] Booting drone node on ${HostAddress}:$Port." -ForegroundColor Green
& $python.Source -m control_plane.drone_node --node-id $NodeId --host $HostAddress --port $Port --packages-dir $PackagesDir
