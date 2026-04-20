# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Native Observability Launcher (NO DOCKER)
#
# Titanium Law I: Go binaries only. Docker is outlawed on this host.
# Prometheus and Grafana both ship standalone Windows exes — we use those.
#
# Expected binary layout:
#   02_FORGE/kinetic/bin/prometheus/prometheus.exe
#   02_FORGE/kinetic/bin/grafana/bin/grafana-server.exe
#
# Run: pwsh monitoring/start_observability.ps1
# Stop: Ctrl+C or kill prometheus.exe / grafana-server.exe

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Bin  = Join-Path $Root '02_FORGE\kinetic\bin'
$PromExe  = Join-Path $Bin  'prometheus\prometheus.exe'
$PromCfg  = Join-Path $PSScriptRoot 'prometheus.yml'
$PromData = Join-Path $PSScriptRoot 'prometheus_data'
$GrafExe  = Join-Path $Bin  'grafana\bin\grafana-server.exe'
$GrafHome = Join-Path $Bin  'grafana'

# --- RAM pre-flight (Law VII: 8 GB physical ceiling) -----------------------
$os = Get-CimInstance Win32_OperatingSystem
$availGB = [math]::Round($os.FreePhysicalMemory/1MB, 2)
if ($availGB -lt 1.5) {
    Write-Error "RAM headroom only $availGB GB — need >= 1.5 GB free to launch observability. Reclaim first."
    exit 1
}

# --- Binary presence check --------------------------------------------------
$missing = @()
if (-not (Test-Path $PromExe))  { $missing += "prometheus.exe at $PromExe" }
if (-not (Test-Path $GrafExe))  { $missing += "grafana-server.exe at $GrafExe" }
if ($missing.Count -gt 0) {
    Write-Host "MISSING BINARIES:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
    Write-Host "See monitoring/BINARIES_REQUIRED.md for download URLs."
    exit 2
}

# --- Launch -----------------------------------------------------------------
New-Item -ItemType Directory -Force -Path $PromData | Out-Null

Write-Host "[IGNITE] Prometheus -> http://localhost:9090" -ForegroundColor Green
$prom = Start-Process -FilePath $PromExe `
    -ArgumentList @(
        "--config.file=$PromCfg",
        "--storage.tsdb.path=$PromData",
        "--web.listen-address=127.0.0.1:9090"
    ) -PassThru -NoNewWindow

Write-Host "[IGNITE] Grafana    -> http://localhost:3000" -ForegroundColor Green
$graf = Start-Process -FilePath $GrafExe `
    -ArgumentList @("--homepath", $GrafHome) `
    -PassThru -NoNewWindow

Write-Host ""
Write-Host "Prometheus PID: $($prom.Id)    Grafana PID: $($graf.Id)"
Write-Host "Stop: Stop-Process -Id $($prom.Id),$($graf.Id)"
