$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$exePath = Join-Path $repoRoot "bin\bifrost_go_sidecar.exe"
$sidecarDir = Join-Path $repoRoot "01_KERNEL\senses\bifrost_go_sidecar"
$logsDir = Join-Path $repoRoot "logs"
$tokenPath = Join-Path $env:USERPROFILE ".camelot\bifrost.token"

if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

if (-not (Test-Path $tokenPath)) {
    throw "Bifrost token file missing: $tokenPath"
}

$token = (Get-Content -Path $tokenPath -Encoding Ascii -ErrorAction Stop | Select-Object -First 1).Trim()
if ([string]::IsNullOrWhiteSpace($token)) {
    throw "Bifrost token is empty at $tokenPath"
}

# Avoid duplicate sidecar launches if port is already active.
try {
    $existing = Get-NetTCPConnection -State Listen -LocalPort 8011 -ErrorAction Stop
    if ($existing) {
        Write-Host "Bifrost Go Sidecar already listening on :8011"
        exit 0
    }
} catch {
    # Continue to spawn if probe cannot determine state.
}

$env:CAMELOT_GATEWAY_TOKEN = $token
$env:BIFROST_SIDECAR_BIND_ADDR = "127.0.0.1:8011"
$env:BIFROST_SIDECAR_UPSTREAM_URL = "http://127.0.0.1:8001"
$env:BIFROST_SIDECAR_ALLOW_ENV_TOKEN_FALLBACK = "0"

$stdout = Join-Path $logsDir "bifrost_go_sidecar.task.out.log"
$stderr = Join-Path $logsDir "bifrost_go_sidecar.task.err.log"

if (Test-Path $exePath) {
    Start-Process -FilePath $exePath -WorkingDirectory (Split-Path -Parent $exePath) -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
    Write-Host "Started sidecar binary: $exePath"
    exit 0
}

$goExe = Get-Command go -ErrorAction SilentlyContinue
if (-not $goExe) {
    throw "Neither sidecar exe nor Go toolchain found. Expected $exePath or `go` in PATH."
}

Start-Process -FilePath $goExe.Source -ArgumentList "run", "." -WorkingDirectory $sidecarDir -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
Write-Host "Started sidecar via go run in $sidecarDir"
