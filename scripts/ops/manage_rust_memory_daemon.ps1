# manage_rust_memory_daemon.ps1 — Autonomous Rust Memory Governor Daemon Manager
param (
    [ValidateSet("start", "stop", "status", "restart", "trim")]
    [string]$Action = "status",
    [int]$Interval = 60,
    [double]$Threshold = 80.0,
    [string]$HeartbeatPath = "03_VAULT\runtime_state\pagekeeper_heartbeat.json",
    [string]$LogPath = "03_VAULT\runtime_state\pagekeeper_daemon.log",
    [string]$PidPath = "03_VAULT\runtime_state\pagekeeper_daemon.pid"
)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$BinaryPath = Join-Path $RepoRoot "target\release\squires_rs.exe"
$HeartbeatFullPath = Join-Path $RepoRoot $HeartbeatPath
$LogFullPath = Join-Path $RepoRoot $LogPath
$PidFullPath = Join-Path $RepoRoot $PidPath

function Get-DaemonProcess {
    if (Test-Path $PidFullPath) {
        $raw = Get-Content $PidFullPath -Raw -ErrorAction SilentlyContinue
        if ($raw) {
            $savedPid = $raw.Trim()
            if ($savedPid -match '^\d+$') {
                $proc = Get-Process -Id ([int]$savedPid) -ErrorAction SilentlyContinue
                if ($proc -and $proc.ProcessName -match "squires_rs") {
                    return $proc
                }
            }
        }
    }
    $procs = Get-Process -Name "squires_rs" -ErrorAction SilentlyContinue
    if ($procs) {
        return $procs[0]
    }
    return $null
}

if ($Action -eq "start") {
    $existing = Get-DaemonProcess
    if ($existing) {
        $existingId = $existing.Id
        Write-Host "[!] PageKeeper Rust Daemon is already running with PID $existingId" -ForegroundColor Yellow
        exit 0
    }

    if (-not (Test-Path $BinaryPath)) {
        Write-Host "[-] Binary not found at $BinaryPath. Compiling release binary..." -ForegroundColor Cyan
        & cargo build --release -p squires_rs --manifest-path (Join-Path $RepoRoot "Cargo.toml")
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[-] Cargo build failed." -ForegroundColor Red
            exit 1
        }
    }

    $runtimeDir = Split-Path $HeartbeatFullPath -Parent
    if (-not (Test-Path $runtimeDir)) {
        New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
    }

    Write-Host "[+] Launching autonomous Rust memory governor daemon..." -ForegroundColor Green
    Write-Host "    Interval:    ${Interval}s" -ForegroundColor Gray
    Write-Host "    Threshold:   ${Threshold}%" -ForegroundColor Gray
    Write-Host "    Heartbeat:   $HeartbeatPath" -ForegroundColor Gray
    Write-Host "    Log file:    $LogPath" -ForegroundColor Gray

    $procArgs = @("daemon", "--interval", "$Interval", "--threshold", "$Threshold", "--heartbeat", "$HeartbeatFullPath")
    $proc = Start-Process -FilePath $BinaryPath -ArgumentList $procArgs -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru
    $procId = $proc.Id
    $procId | Out-File -FilePath $PidFullPath -Encoding ascii -Force
    Write-Host "[OK] PageKeeper Rust Daemon started successfully with PID $procId" -ForegroundColor Green
    exit 0
}

if ($Action -eq "stop") {
    $proc = Get-DaemonProcess
    if ($proc) {
        $procId = $proc.Id
        Write-Host "[*] Stopping PageKeeper Rust Daemon with PID $procId" -ForegroundColor Yellow
        Stop-Process -Id $procId -Force
        if (Test-Path $PidFullPath) {
            Remove-Item $PidFullPath -Force
        }
        Write-Host "[OK] Daemon terminated." -ForegroundColor Green
    } else {
        Write-Host "[!] No active PageKeeper Rust Daemon found." -ForegroundColor Yellow
    }
    exit 0
}

if ($Action -eq "restart") {
    & $PSCommandPath -Action "stop"
    Start-Sleep -Seconds 1
    & $PSCommandPath -Action "start" -Interval $Interval -Threshold $Threshold
    exit 0
}

if ($Action -eq "trim") {
    Write-Host "[*] Executing immediate one-shot working set trim via Rust native FFI..." -ForegroundColor Cyan
    & $BinaryPath pagekeeper --trim
    exit 0
}

if ($Action -eq "status") {
    Write-Host "=== CAMELOT-OS Rust Memory Governor Daemon Status ===" -ForegroundColor Cyan
    $proc = Get-DaemonProcess
    if ($proc) {
        $procId = $proc.Id
        $wsMb = [math]::Round($proc.WorkingSet64 / 1MB, 2)
        Write-Host "Daemon State:    RUNNING" -ForegroundColor Green
        Write-Host "PID:             $procId" -ForegroundColor Gray
        Write-Host "Resident Memory: $wsMb MB (Well below 4GB Global Law 03 ceiling)" -ForegroundColor Gray
    } else {
        Write-Host "Daemon State:    STOPPED" -ForegroundColor Yellow
    }

    if (Test-Path $HeartbeatFullPath) {
        Write-Host "`nLatest Heartbeat Telemetry ($HeartbeatPath):" -ForegroundColor Cyan
        Get-Content $HeartbeatFullPath -Raw | Write-Host -ForegroundColor Gray
    } else {
        Write-Host "`nNo heartbeat report found at $HeartbeatPath." -ForegroundColor Gray
    }
    exit 0
}
