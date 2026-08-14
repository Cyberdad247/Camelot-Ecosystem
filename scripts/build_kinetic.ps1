# SPDX-License-Identifier: MIT

# build_kinetic.ps1 — CAMELOT Kinetic Binary Build Harness (Windows PowerShell)
# =================================================================================
# Run from CAMELOT_OS root: powershell -ExecutionPolicy Bypass -File scripts\build_kinetic.ps1
#
# Targets:
#   1. kinetic_edge\swarm_spawner  -> bin\swarm-spawner.exe
#   2. kinetic_edge\pqcrypto       -> bin\camelot-pqcrypto.exe
#   3. 02_FORGE\vizion-telemetry   -> bin\vizion-telemetry.exe (Go)
#
# Requirements: cargo (rustup), go 1.21+
# Usage:
#   .\scripts\build_kinetic.ps1          # build all
#   .\scripts\build_kinetic.ps1 swarm    # build swarm-spawner only
#   .\scripts\build_kinetic.ps1 pqcrypto # build pqcrypto only
#   .\scripts\build_kinetic.ps1 vizion   # build vizion-telemetry only
#   .\scripts\build_kinetic.ps1 selftest # run pqcrypto self-test after build

param([string]$Target = "all")

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Bin  = Join-Path $Root "bin"
if (-not (Test-Path $Bin)) { New-Item -ItemType Directory -Path $Bin | Out-Null }

function ok   { param($msg) Write-Host "  OK  $msg" -ForegroundColor Green }
function warn { param($msg) Write-Host "  WARN $msg" -ForegroundColor Yellow }
function fail { param($msg) Write-Host "  FAIL $msg" -ForegroundColor Red }
function info { param($msg) Write-Host "       $msg" -ForegroundColor Cyan }

$Pass = 0; $Fail = 0

function Build-SwarmSpawner {
    Write-Host "`n[1/3] swarm-spawner (Rust Tokio SRDL)" -ForegroundColor Cyan
    $src = Join-Path $Root "kinetic_edge\swarm_spawner"
    if (-not (Test-Path "$src\Cargo.toml")) { fail "Cargo.toml not found at $src"; return $false }
    info "cargo build --release ..."
    $out = & cargo build --release --manifest-path "$src\Cargo.toml" 2>&1
    $out | Select-Object -Last 5 | ForEach-Object { info $_ }
    $exe = Join-Path $src "target\release\swarm-spawner.exe"
    if (Test-Path $exe) {
        Copy-Item $exe "$Bin\swarm-spawner.exe" -Force
        $sz = [math]::Round((Get-Item "$Bin\swarm-spawner.exe").Length / 1MB, 2)
        ok "swarm-spawner.exe -> bin\ ($($sz)MB)"
        return $true
    }
    fail "swarm-spawner.exe not found after build"; return $false
}

function Build-PQCrypto {
    Write-Host "`n[2/3] camelot-pqcrypto (Rust ML-KEM-768 + ML-DSA-65)" -ForegroundColor Cyan
    $src = Join-Path $Root "kinetic_edge\pqcrypto"
    if (-not (Test-Path "$src\Cargo.toml")) { fail "Cargo.toml not found at $src"; return $false }
    info "cargo build --release ..."
    $out = & cargo build --release --manifest-path "$src\Cargo.toml" 2>&1
    $out | Select-Object -Last 5 | ForEach-Object { info $_ }
    $exe = Join-Path $src "target\release\camelot-pqcrypto.exe"
    if (Test-Path $exe) {
        Copy-Item $exe "$Bin\camelot-pqcrypto.exe" -Force
        $sz = [math]::Round((Get-Item "$Bin\camelot-pqcrypto.exe").Length / 1MB, 2)
        ok "camelot-pqcrypto.exe -> bin\ ($($sz)MB)"
        return $true
    }
    fail "camelot-pqcrypto.exe not found after build"; return $false
}

function Build-Vizion {
    Write-Host "`n[3/3] vizion-telemetry (Go BubbleTea + GPU panel)" -ForegroundColor Cyan
    $src = Join-Path $Root "02_FORGE\vizion-telemetry"
    if (-not (Test-Path "$src\go.mod")) { fail "go.mod not found at $src"; return $false }
    info "go build -ldflags='-s -w' ..."
    Push-Location $src
    try {
        $out = & go build -ldflags="-s -w" -o "$Bin\vizion-telemetry.exe" . 2>&1
        $out | ForEach-Object { info $_ }
    } finally { Pop-Location }
    if (Test-Path "$Bin\vizion-telemetry.exe") {
        $sz = [math]::Round((Get-Item "$Bin\vizion-telemetry.exe").Length / 1MB, 2)
        ok "vizion-telemetry.exe -> bin\ ($($sz)MB)"
        return $true
    }
    fail "vizion-telemetry.exe not found after build"; return $false
}

function Run-SelfTest {
    Write-Host "`n[SELF-TEST] camelot-pqcrypto round-trip" -ForegroundColor Cyan
    $exe = "$Bin\camelot-pqcrypto.exe"
    if (-not (Test-Path $exe)) { warn "pqcrypto binary not found — build first"; return $false }
    $result = & $exe self-test 2>&1 | Out-String
    Write-Host $result
    if ($result -match '"status":\s*"PASS"') {
        ok "ML-KEM-768 + ML-DSA-65 self-test PASS"
        return $true
    }
    fail "self-test FAIL"; return $false
}

# ── Entry ─────────────────────────────────────────────────────────────────────

Write-Host "`nCAMELOT Kinetic Build Harness v400.1.0" -ForegroundColor Magenta
Write-Host "ROOT: $Root" -ForegroundColor Cyan
Write-Host "BIN:  $Bin"  -ForegroundColor Cyan

switch ($Target.ToLower()) {
    "swarm"    { if (Build-SwarmSpawner) { $Pass++ } else { $Fail++ } }
    "pqcrypto" { if (Build-PQCrypto)    { $Pass++ } else { $Fail++ } }
    "vizion"   { if (Build-Vizion)       { $Pass++ } else { $Fail++ } }
    "selftest"  { if (Run-SelfTest)      { $Pass++ } else { $Fail++ } }
    "all" {
        if (Build-SwarmSpawner) { $Pass++ } else { $Fail++ }
        if (Build-PQCrypto)     { $Pass++ } else { $Fail++ }
        if (Build-Vizion)        { $Pass++ } else { $Fail++ }
        if (Run-SelfTest)       { $Pass++ } else { $Fail++ }
    }
    default {
        Write-Host "Usage: build_kinetic.ps1 [all|swarm|pqcrypto|vizion|selftest]"
        exit 1
    }
}

Write-Host ""
if ($Fail -eq 0) {
    ok "Build complete: $Pass targets built"
    Write-Host "  Run: python bin\awaken.py --status" -ForegroundColor Cyan
} else {
    warn "Build partial: $Pass OK, $Fail FAILED"
    exit 1
}
