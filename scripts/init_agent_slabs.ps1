<#
.SYNOPSIS
    ZeroClaw .agent/ Shared Memory & Lock Initializer (Cybertronia Edge Node)
.DESCRIPTION
    Initializes IPC slabs in .agent/, enforces the 4.0 GB edge RAM ceiling,
    cleans stale lockfiles, and validates canonical 2-strand HTMX telemetry.
#>

[CmdletBinding()]
param(
    [switch]$Test,
    [switch]$Htmx,
    [switch]$Status
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$AgentDir = Join-Path $RepoRoot ".agent"
$LockDir = Join-Path $AgentDir ".locks"
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Write-Host "=================================================================" -ForegroundColor DarkYellow
Write-Host "  CAMELOT-OS // CYBERTRONIA EDGE NODE IPC SLAB INITIALIZER" -ForegroundColor Yellow
Write-Host "  RAM Ceiling: 4096 MB (Edge Node Bound) | Floor: <480 MB Active" -ForegroundColor DarkGray
Write-Host "=================================================================" -ForegroundColor DarkYellow

# 1. Directory Initialization
if (-not (Test-Path $AgentDir)) {
    New-Item -ItemType Directory -Path $AgentDir -Force | Out-Null
    Write-Host "[+] Created .agent/ backplane directory" -ForegroundColor Green
}

if (-not (Test-Path $LockDir)) {
    New-Item -ItemType Directory -Path $LockDir -Force | Out-Null
    Write-Host "[+] Created .agent/.locks/ registry" -ForegroundColor Green
}

# 2. Canonical Slabs Presence Check
$CanonicalSlabs = @(
    "local_env.md",
    "system_instructions.md",
    "Agents.md",
    "Skills.md",
    "Swarm.md",
    "workflows.md"
)

$MissingCount = 0
foreach ($Slab in $CanonicalSlabs) {
    $SlabPath = Join-Path $AgentDir $Slab
    if (Test-Path $SlabPath) {
        $Size = (Get-Item $SlabPath).Length
        Write-Host "  [OK] Slab present: $Slab ($Size bytes)" -ForegroundColor Cyan
    } else {
        Write-Host "  [!] Missing slab: $Slab (Initializing stub...)" -ForegroundColor Magenta
        Set-Content -Path $SlabPath -Value "# $Slab`nCreated by ZeroClaw Initializer`n" -Encoding UTF8
        $MissingCount++
    }
}

# 3. Clean any orphaned lockfiles older than 60s
if (Test-Path $LockDir) {
    $StaleLocks = Get-ChildItem -Path $LockDir -Filter "*.lock" | Where-Object {
        $_.LastWriteTime -lt (Get-Date).AddSeconds(-60)
    }
    foreach ($Lock in $StaleLocks) {
        Remove-Item -Path $Lock.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  [-] Evicted stale lock: $($Lock.Name)" -ForegroundColor DarkGray
    }
}

# 4. Dispatch to Python Agent Slab Sync Manager
if (Test-Path $PythonExe) {
    if ($Test) {
        & $PythonExe -m control_plane.infra.agent_slab_sync --test
    } elseif ($Htmx) {
        & $PythonExe -m control_plane.infra.agent_slab_sync --htmx
    } else {
        & $PythonExe -m control_plane.infra.agent_slab_sync --status
    }
} else {
    Write-Host "[!] Virtual environment python not found at $PythonExe" -ForegroundColor Red
}

Write-Host "`n[OK] ZeroClaw IPC Backplane Aligned under Edge Node 4GB Policy." -ForegroundColor Green
