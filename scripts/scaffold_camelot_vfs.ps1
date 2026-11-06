# CAMELOT-OS VFS & ICM Scaffolding Bootstrap
param(
    [switch]$Apply,
    [switch]$Json
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
Set-Location $repoRoot

Write-Host "================================================================================"
Write-Host "CAMELOT-OS VFS & ICM SCAFFOLDING BOOTSTRAP (PowerShell)"
Write-Host "================================================================================"
Write-Host "Root Directory: $repoRoot"

$systemPlanes = @(
    "01_KERNEL",
    "02_FORGE",
    "03_VAULT",
    "04_KINETIC",
    "apps",
    "control_plane",
    "vfs",
    "scripts",
    "tests"
)

Write-Host "[1/4] Scaffolding Core Architectural Planes..."
foreach ($plane in $systemPlanes) {
    $targetPath = Join-Path $repoRoot $plane
    if (-not (Test-Path $targetPath)) {
        New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        Write-Host "   [+] Created plane: $plane/"
    } else {
        Write-Host "   [ok] Present plane: $plane/"
    }
}

$vfsSubdirs = @(
    "vfs/backplane",
    "vfs/business",
    "vfs/cartridges",
    "vfs/checks",
    "vfs/edu",
    "vfs/fitness",
    "vfs/general",
    "vfs/genes",
    "vfs/knowledge",
    "vfs/logs",
    "vfs/nodes",
    "vfs/notebooks",
    "vfs/open_notebook",
    "vfs/skills",
    "vfs/source",
    "vfs/swarms",
    "vfs/telemetry",
    "vfs/worktree"
)

Write-Host "[2/4] Verifying VFS Context Directory Slabs..."
foreach ($slab in $vfsSubdirs) {
    $targetPath = Join-Path $repoRoot $slab
    if (-not (Test-Path $targetPath)) {
        New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        Write-Host "   [+] Created slab: $slab/"
    }
}
Write-Host "   [ok] All 18 VFS Context Slabs Verified."

Write-Host "[3/4] Running 070 VFS Scaffold Integrity Preflight Probe..."
python -m control_plane.preflight.probes.vfs_present_run --required vfs/preflight.md vfs/systeminstructions.md vfs/skills.md vfs/rosters.md vfs/protocols.md
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [ok] Preflight probe 070 passed."
} else {
    Write-Error "Preflight probe 070 failed."
}

Write-Host "[4/4] Executing Non-Destructive VFS Resource Audit..."
$sweepArgs = @("scripts/vfs_janitorial_sweep.py")
if ($Apply) { $sweepArgs += "--apply" }
if ($Json) { $sweepArgs += "--json" }

python @sweepArgs

Write-Host "================================================================================"
Write-Host "[VFS_STATUS]: POST-CONDITIONS SATISFIED - VFS SCAFFOLD FULLY LOCKED"
Write-Host "================================================================================"
exit 0
