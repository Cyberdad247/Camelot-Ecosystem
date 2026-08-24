# Camelot-OS KBA Drone — lakesha launcher (run from the extracted bundle folder)
# Governed drone: signed cartridges -> trust -> RBAC -> real KBA executor -> audit,
# with Sir Heimdall on watch. Reachable over the tailnet at 100.100.155.55:9000.
#
# SECURITY: this script must never contain secret values. Secrets are resolved
# in order of precedence:
#   1. Current PowerShell session ($env:WEBHOOK_SECRET / $env:CAMELOT_CARTRIDGE_HMAC_KEY)
#   2. Local gitignored file .drone_secrets.ps1 (same directory; see run_drone.keygen.ps1)
#   3. Interactive Read-Host prompt (never persisted to disk)
# The script fails fast if any secret is still missing.

[CmdletBinding()]
param(
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

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$localSecrets = Join-Path $scriptDir ".drone_secrets.ps1"

function Get-SessionEnv([string]$Name) {
    return [Environment]::GetEnvironmentVariable($Name, 'Process')
}

function Set-SessionEnv([string]$Name, [string]$Value) {
    [Environment]::SetEnvironmentVariable($Name, $Value, 'Process')
}

function Resolve-Secret {
    param([string]$Name, [string]$Prompt)

    # 1. Session env
    $value = Get-SessionEnv $Name
    if ($value) { return $value }

    # 2. Local gitignored file (rotated keys live here, never in git)
    if (Test-Path -LiteralPath $localSecrets) {
        . $localSecrets
        $value = Get-SessionEnv $Name
        if ($value) { return $value }
    }

    # 3. Interactive prompt (never persisted to disk)
    $value = Read-Host $Prompt
    if ($value) { Set-SessionEnv $Name $value }

    return Get-SessionEnv $Name
}

if (-not (Test-Path -LiteralPath (Join-Path $scriptDir "control_plane\drone_node.py"))) {
    Fail "control_plane\drone_node.py not found next to run_drone.ps1"
}

$env:WEBHOOK_SECRET = Resolve-Secret "WEBHOOK_SECRET" "WEBHOOK_SECRET (match the control plane's value)"
$env:CAMELOT_CARTRIDGE_HMAC_KEY = Resolve-Secret "CAMELOT_CARTRIDGE_HMAC_KEY" "CAMELOT_CARTRIDGE_HMAC_KEY (match the control plane's value)"

if (-not $env:WEBHOOK_SECRET) {
    Fail "WEBHOOK_SECRET is still empty."
}

if (-not $env:CAMELOT_CARTRIDGE_HMAC_KEY) {
    Fail "CAMELOT_CARTRIDGE_HMAC_KEY is still empty."
}

Write-Host "[OK] WEBHOOK_SECRET set: $([bool]$env:WEBHOOK_SECRET)" -ForegroundColor Green
Write-Host "[OK] HMAC key set: $([bool]$env:CAMELOT_CARTRIDGE_HMAC_KEY)" -ForegroundColor Green

Set-Location $scriptDir
python -m control_plane.drone_node --node-id $NodeId --host $HostAddress --port $Port
