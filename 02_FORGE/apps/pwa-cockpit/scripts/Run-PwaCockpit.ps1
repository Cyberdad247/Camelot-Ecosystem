[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 3006
)

$ErrorActionPreference = "Stop"
$appRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$envPath = Join-Path $appRoot ".env.local"
$buildId = Join-Path $appRoot ".next\BUILD_ID"
$nextCommand = Join-Path $appRoot "node_modules\.bin\next.cmd"
$logDirectory = Join-Path $appRoot "artifacts\runtime"
$logPath = Join-Path $logDirectory "pwa-cockpit-runtime.log"

if (-not (Test-Path -LiteralPath $envPath)) {
    throw "Missing $envPath. Configure the operator token before starting the Cockpit."
}

$tokenLine = Get-Content -LiteralPath $envPath | Where-Object { $_ -match '^CAMELOT_COCKPIT_TOKEN=' } | Select-Object -First 1
$token = if ($tokenLine) { ($tokenLine -split '=', 2)[1].Trim() } else { "" }
if ($token.Length -lt 16 -or $token -like "replace-*") {
    throw "CAMELOT_COCKPIT_TOKEN must contain at least 16 non-placeholder characters."
}

if (-not (Test-Path -LiteralPath $buildId)) {
    throw "Production build is missing. Run npm run verify before installing the host."
}

if (-not (Test-Path -LiteralPath $nextCommand)) {
    throw "Next.js is not installed. Run npm install before starting the Cockpit."
}

New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
Set-Location -LiteralPath $appRoot
$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
"[$(Get-Date -Format o)] Starting Camelot PWA Cockpit on 127.0.0.1:$Port" | Out-File -LiteralPath $logPath -Append -Encoding utf8
& $nextCommand start --hostname 127.0.0.1 --port $Port 2>&1 | ForEach-Object {
    "[$(Get-Date -Format o)] $_" | Out-File -LiteralPath $logPath -Append -Encoding utf8
}
$exitCode = $LASTEXITCODE
"[$(Get-Date -Format o)] Next.js exited with code $exitCode" | Out-File -LiteralPath $logPath -Append -Encoding utf8
exit $exitCode
