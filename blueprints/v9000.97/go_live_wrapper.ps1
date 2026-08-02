<#
  CAMELOT-OS Enterprise V1.0 Go-Live Wrapper

  Operator-executed script. It validates Vercel identity/linking, KBA SSH,
  remote Wasmtime version, local/remote WASM hashes, then stages the WASM pill
  before promoting it and restarting camelotd.
#>

[CmdletBinding()]
param(
    [string]$KbaIp = "100.115.92.4",
    [string]$ExpectedHash = "9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095",
    [string]$MinimumWasmtimeVersion = "46.0.1",
    [string]$VercelScope = "",
    [string]$VercelProject = "",
    [switch]$AssumeYes
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    Write-Host "[FATAL] $Message" -ForegroundColor Red
    exit 1
}

function Require-ExitCode([string]$Action) {
    if ($LASTEXITCODE -ne 0) {
        Fail "$Action failed with exit code $LASTEXITCODE."
    }
}

function Confirm-OrAbort([string]$Prompt) {
    if ($AssumeYes) {
        Write-Host "[CONFIRMED] $Prompt" -ForegroundColor DarkGreen
        return
    }

    $answer = Read-Host "$Prompt Type YES to continue"
    if ($answer -cne "YES") {
        Fail "Aborted by operator."
    }
}

function Parse-WasmtimeVersion([string]$VersionOutput) {
    if ($VersionOutput -notmatch "wasmtime\s+(\d+\.\d+\.\d+)") {
        Fail "Could not parse Wasmtime version from: $VersionOutput"
    }

    return [version]$Matches[1]
}

$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..")
$frontendDir = Join-Path $repoRoot "02_FORGE\generated\ukg_omega_glyph_v1000\Node_A_Frontend"
$wasmPath = Join-Path $repoRoot "target\wasm32-wasip1\release\aaliyah_comms.wasm"
$remoteStagingDir = "/tmp/camelot_staging"
$remoteStagingPath = "$remoteStagingDir/aaliyah_comms.wasm"
$remotePillDir = "/opt/camelot/cartridges/pills"
$remotePillPath = "$remotePillDir/aaliyah_comms.wasm"

Write-Host "[SIR_WATCHDOG] Starting go-live validation wrapper." -ForegroundColor Cyan
Write-Host "Repo root: $repoRoot"
Write-Host "KBA target: $KbaIp"

if (-not (Test-Path -LiteralPath $frontendDir)) {
    Fail "Frontend directory missing: $frontendDir"
}

if (-not (Test-Path -LiteralPath $wasmPath)) {
    Fail "WASM artifact missing: $wasmPath"
}

$localHash = (Get-FileHash -LiteralPath $wasmPath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($localHash -ne $ExpectedHash) {
    Fail "Local WASM hash mismatch. Expected $ExpectedHash, got $localHash."
}
Write-Host "[OK] Local WASM hash verified: $localHash" -ForegroundColor Green

Write-Host "`n[1/5] Verifying Vercel account and project link." -ForegroundColor Yellow
Push-Location $frontendDir
try {
    & npx vercel whoami
    Require-ExitCode "Vercel whoami"

    if ($VercelScope -and $VercelProject) {
        & npx vercel link --yes --scope $VercelScope --project $VercelProject
    } else {
        & npx vercel link
    }
    Require-ExitCode "Vercel link"

    Confirm-OrAbort "Confirm the Vercel account and linked project/team are correct."
}
finally {
    Pop-Location
}

Write-Host "`n[2/5] Verifying SSH connectivity and remote identity." -ForegroundColor Yellow
$remoteHost = & ssh "root@$KbaIp" "hostname"
Require-ExitCode "KBA hostname check"
Write-Host "Remote hostname: $remoteHost" -ForegroundColor Green
Confirm-OrAbort "Confirm this is the intended KBA host."

Write-Host "`n[3/5] Verifying remote Wasmtime version." -ForegroundColor Yellow
$wasmtimeOutput = & ssh "root@$KbaIp" "wasmtime --version"
Require-ExitCode "KBA Wasmtime version check"
$remoteWasmtimeVersion = Parse-WasmtimeVersion ($wasmtimeOutput -join "`n")
$minimumVersion = [version]$MinimumWasmtimeVersion
if ($remoteWasmtimeVersion -lt $minimumVersion) {
    Fail "Remote Wasmtime $remoteWasmtimeVersion is older than required $minimumVersion."
}
Write-Host "[OK] Remote Wasmtime version: $remoteWasmtimeVersion" -ForegroundColor Green

Write-Host "`n[4/5] Staging WASM pill and verifying remote hash." -ForegroundColor Yellow
& ssh "root@$KbaIp" "mkdir -p $remoteStagingDir"
Require-ExitCode "Create remote staging directory"

& scp $wasmPath "root@${KbaIp}:$remoteStagingPath"
Require-ExitCode "SCP staged WASM"

$remoteHashRaw = & ssh "root@$KbaIp" "sha256sum $remoteStagingPath"
Require-ExitCode "Remote staged hash"
$remoteHash = (($remoteHashRaw -join " ") -split "\s+")[0].ToUpperInvariant()

if ($remoteHash -ne $ExpectedHash) {
    Write-Host "[FATAL] Remote hash mismatch. Expected $ExpectedHash, got $remoteHash." -ForegroundColor Red
    & ssh "root@$KbaIp" "rm -f $remoteStagingPath"
    exit 1
}
Write-Host "[OK] Remote staged hash verified: $remoteHash" -ForegroundColor Green

Write-Host "`n[5/5] All gates passed." -ForegroundColor Cyan
Confirm-OrAbort "Execute production mutation: promote WASM, restart camelotd, deploy Vercel production."

Write-Host "`n[MUTATION] Promoting WASM pill and restarting camelotd." -ForegroundColor Yellow
& ssh "root@$KbaIp" "mkdir -p $remotePillDir && mv $remoteStagingPath $remotePillPath && sha256sum $remotePillPath && systemctl restart camelotd && systemctl status camelotd --no-pager"
Require-ExitCode "KBA mutation block"

Write-Host "`n[MUTATION] Deploying frontend to Vercel production." -ForegroundColor Yellow
Push-Location $frontendDir
try {
    if ($AssumeYes) {
        & npx vercel deploy --prod --yes
    } else {
        & npx vercel deploy --prod
    }
    Require-ExitCode "Vercel production deploy"
}
finally {
    Pop-Location
}

Write-Host "`n[SYSTEM] Enterprise V1.0 mutation block completed." -ForegroundColor Green
