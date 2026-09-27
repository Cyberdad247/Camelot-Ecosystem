# CAMELOT-OS Host Hardware & Memory Optimizer
# Target: cybertronia (Acer Nitro V 15 ANV15-51)
# Substrate: PowerShell 5.1 / 7+

[CmdletBinding()]
param (
    [switch]$CloseNitroGUI = $true,
    [switch]$CheckTelemetry = $true,
    [switch]$ServiceTuning = $false
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  CAMELOT-OS // HOST TELEMETRY & HARDWARE OPTIMIZER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. NitroSense GUI Memory Guard
$nitroProcs = Get-Process -Name "*nitro*" -ErrorAction SilentlyContinue
if ($nitroProcs) {
    $totalMem = ($nitroProcs | Measure-Object -Property WorkingSet64 -Sum).Sum / 1MB
    Write-Host "[!] Found $($nitroProcs.Count) NitroSense GUI process(es) consuming $([math]::Round($totalMem, 1)) MB RAM." -ForegroundColor Yellow
    
    if ($CloseNitroGUI) {
        Write-Host "[*] Terminating front-end GUI to recover memory headroom..." -ForegroundColor Gray
        Stop-Process -Name "NitroSense" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
        Write-Host "[+] NitroSense GUI closed. Hardware fans remain governed by ASMSvc." -ForegroundColor Green
    }
} else {
    Write-Host "[+] NitroSense GUI is not running (Optimal low-overhead state)." -ForegroundColor Green
}

# 2. Verify Kernel EC / Hardware Governor
$asm = Get-Service -Name "ASMSvc" -ErrorAction SilentlyContinue
if ($asm -and $asm.Status -eq "Running") {
    Write-Host "[+] Acer System Monitor Service (ASMSvc): RUNNING (EC fan curves active)." -ForegroundColor Green
} else {
    Write-Host "[WARN] ASMSvc is not detected or stopped. Hardware fan control may default to passive." -ForegroundColor Yellow
}

# 3. Service Tuning (Elevated Only)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($ServiceTuning -or $isAdmin) {
    Write-Host "[*] Checking optional background services..." -ForegroundColor Gray
    $servicesToDemote = @("AcerARTAIMMXService", "AcerARTAIMMXDriverService")
    foreach ($svcName in $servicesToDemote) {
        $svc = Get-Service -Name $svcName -ErrorAction SilentlyContinue
        if ($svc) {
            if ($isAdmin) {
                if ($svc.Status -eq "Running") {
                    Stop-Service -Name $svcName -Force -ErrorAction SilentlyContinue
                    Write-Host "[+] Stopped service: $svcName" -ForegroundColor Green
                }
                if ($svc.StartType -ne "Manual") {
                    Set-Service -Name $svcName -StartupType Manual -ErrorAction SilentlyContinue
                    Write-Host "[+] Set service to Manual: $svcName" -ForegroundColor Green
                }
            } else {
                Write-Host "[INFO] Run this script in an Elevated Administrator PowerShell to disable $svcName." -ForegroundColor DarkYellow
            }
        }
    }
}

# 4. Live Memory & Hardware Snapshot
if ($CheckTelemetry) {
    Write-Host "`n--- LIVE HOST TELEMETRY ---" -ForegroundColor Cyan
    $os = Get-CimInstance Win32_OperatingSystem
    $totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $freeRAM = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $usedRAM = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 2)
    $pctUsed = [math]::Round(($usedRAM / $totalRAM) * 100, 1)

    $ramColor = if ($pctUsed -gt 85) { "Red" } else { "Green" }
    Write-Host "RAM Status:  $usedRAM GB Used / $totalRAM GB Total ($pctUsed% load) | $freeRAM GB Free" -ForegroundColor $ramColor

    $gpu = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($gpu) {
        $smi = & nvidia-smi --query-gpu=temperature.gpu,power.draw,utilization.gpu --format=csv,noheader,nounits 2>$null
        if ($smi) {
            $parts = $smi -split ",\s*"
            Write-Host "RTX 2050:    Temp: $($parts[0])C | Power: $($parts[1])W | Load: $($parts[2])%" -ForegroundColor Green
        }
    }
}

Write-Host "`n[+] Hardware optimization sweep complete.`n" -ForegroundColor Cyan
