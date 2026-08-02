<#
  CAMELOT-OS Lakesha Drone Restarter

  Run locally on Lakesha. Stops whatever is currently bound to the drone's
  port, then re-launches it exactly like start_lakesha_drone.ps1 — prompting
  fresh for WEBHOOK_SECRET / CAMELOT_CARTRIDGE_HMAC_KEY. This script does not
  store secrets.

  Use this when the drone's current secrets no longer match what the control
  node (Excalibur/cybertronia) has on file, and you want to realign them by
  re-entering the same values used elsewhere rather than hunting down the
  original PowerShell window.
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

Write-Host "[SIR_CODEX] Restarting Lakesha drone on port $Port" -ForegroundColor Cyan

# ── Stop whatever currently owns the drone's port ───────────────────────────
$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    foreach ($conn in $existing) {
        $procId = $conn.OwningProcess
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "[INFO] Stopping existing process on port ${Port}: PID $procId ($($proc.ProcessName))" -ForegroundColor Yellow
            Stop-Process -Id $procId -Force
            Start-Sleep -Seconds 2
        }
    }
} else {
    Write-Host "[INFO] Nothing currently bound to port $Port" -ForegroundColor Yellow
}

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    Fail "Repo root not found: $RepoRoot"
}

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot "control_plane\drone_node.py"))) {
    Fail "control_plane\drone_node.py not found under $RepoRoot"
}

# Force fresh prompts even if this session has stale values set.
$env:WEBHOOK_SECRET = Read-Host "WEBHOOK_SECRET (match the control node's value)"
$env:CAMELOT_CARTRIDGE_HMAC_KEY = Read-Host "CAMELOT_CARTRIDGE_HMAC_KEY (match the control node's value)"

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
