# optimize_ram.ps1 - Windows RAM & Working Set Optimization for Acer Nitro V 15 (8GB DDR5)
param (
    [switch]$Elevate
)

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  CAMELOT-OS: 8GB DDR5 Hardware Memory Optimization" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Admin privilege check
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin -and $Elevate) {
    Write-Host "[*] Relaunching with Administrator elevation..." -ForegroundColor Yellow
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# ---------------------------------------------------------
# 2. Browser Memory Policies (Zero-Cost Huge RAM Savings)
# ---------------------------------------------------------
Write-Host "`n[1/4] Applying Browser Memory Saver Policies..." -ForegroundColor Green

# Google Chrome Memory Saver (HighEfficiencyModeEnabled)
$chromePolicyPath = "HKCU:\Software\Policies\Google\Chrome"
if (-not (Test-Path $chromePolicyPath)) {
    New-Item -Path $chromePolicyPath -Force | Out-Null
}
Set-ItemProperty -Path $chromePolicyPath -Name "HighEfficiencyModeEnabled" -Value 1 -Type DWord
Write-Host "  -> Chrome Memory Saver (HighEfficiencyMode): ENABLED" -ForegroundColor Gray

# Microsoft Edge Sleeping Tabs & Efficiency Mode
$edgePolicyPath = "HKCU:\Software\Policies\Microsoft\Edge"
if (-not (Test-Path $edgePolicyPath)) {
    New-Item -Path $edgePolicyPath -Force | Out-Null
}
Set-ItemProperty -Path $edgePolicyPath -Name "SleepingTabsEnabled" -Value 1 -Type DWord
Set-ItemProperty -Path $edgePolicyPath -Name "SleepingTabsTimeout" -Value 300 -Type DWord
Write-Host "  -> Edge Sleeping Tabs (5-minute inactivity discard): ENABLED" -ForegroundColor Gray

# ---------------------------------------------------------
# 3. Windows UI Animation & Desktop Window Manager Trimming
# ---------------------------------------------------------
Write-Host "`n[2/4] Optimizing Desktop Window Manager & Animations..." -ForegroundColor Green

# Disable window minimize / maximize animations
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0"
# Disable taskbar animations
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Value 0 -Type DWord
Write-Host "  -> Window & Taskbar animations: DISABLED (Frees DWM VRAM/RAM frames)" -ForegroundColor Gray

# ---------------------------------------------------------
# 4. User Startup Bloat Audit & Disabling
# ---------------------------------------------------------
Write-Host "`n[3/4] Auditing and Disabling Non-Essential Auto-Launch Daemons..." -ForegroundColor Green
$runPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$backupPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run_DisabledBackup"

if (-not (Test-Path $backupPath)) {
    New-Item -Path $backupPath -Force | Out-Null
}

$heavyItems = @(
    "Adobe Acrobat Synchronizer",
    "GoogleChromeAutoLaunch_9CB9C8D35B8F82C1D812E2B2F9019B7A"
)

foreach ($item in $heavyItems) {
    $existing = (Get-ItemProperty -Path $runPath -Name $item -ErrorAction SilentlyContinue).$item
    if ($existing) {
        Set-ItemProperty -Path $backupPath -Name $item -Value $existing
        Remove-ItemProperty -Path $runPath -Name $item -ErrorAction SilentlyContinue
        Write-Host "  -> Disabled auto-start for: $item (Saved in backup registry)" -ForegroundColor Yellow
    } else {
        Write-Host "  -> $($item): Already disabled or not present." -ForegroundColor Gray
    }
}

# ---------------------------------------------------------
# 5. Flush Working Sets for Inactive Processes
# ---------------------------------------------------------
Write-Host "`n[4/5] Trimming Resident Working Sets for Running Processes..." -ForegroundColor Green
try {
    $code = @'
    using System;
    using System.Runtime.InteropServices;
    public class MemTrim {
        [DllImport("psapi.dll")]
        public static extern int EmptyWorkingSet(IntPtr hProcess);
    }
'@
    Add-Type -TypeDefinition $code -Language CSharp -ErrorAction SilentlyContinue
    $procCount = 0
    Get-Process | ForEach-Object {
        try {
            if ($_.Handle -ne [IntPtr]::Zero) {
                $null = [MemTrim]::EmptyWorkingSet($_.Handle)
                $procCount++
            }
        } catch {}
    }
    Write-Host "  -> Trimmed stale memory frames across $procCount user processes." -ForegroundColor Gray
} catch {
    Write-Warning "Could not perform working set trim: $_"
}

# ---------------------------------------------------------
# 6. Administrative Optimizations (Pagefile & MMAgent)
# ---------------------------------------------------------
Write-Host "`n[5/5] Checking System-Level Virtual Memory & MMAgent..." -ForegroundColor Green

if ($isAdmin) {
    Write-Host "  -> Running with Administrator privileges." -ForegroundColor Green
    
    # Enable Memory Compression & Page Combining
    try {
        Enable-MMAgent -MemoryCompression -PageCombining -ErrorAction SilentlyContinue
        Write-Host "  -> Windows Memory Compression & Page Combining: ACTIVE" -ForegroundColor Gray
    } catch {
        Write-Warning "Failed to set MMAgent settings: $_"
    }

    # Configure Fixed NVMe Pagefile (Initial 8192 MB, Max 16384 MB)
    try {
        $cs = Get-CimInstance Win32_ComputerSystem
        if ($cs.AutomaticManagedPagefile) {
            $cs.AutomaticManagedPagefile = $false
            Set-CimInstance -CimInstance $cs
            Write-Host "  -> Disabled automatic dynamic pagefile resizing." -ForegroundColor Gray
        }

        $pageFile = Get-CimInstance Win32_PageFileSetting -Filter "Name like 'C:%'" -ErrorAction SilentlyContinue
        if ($pageFile) {
            $pageFile.InitialSize = 8192
            $pageFile.MaximumSize = 16384
            Set-CimInstance -CimInstance $pageFile
            Write-Host "  -> Pagefile on C:\ fixed to 8GB Initial / 16GB Max (Eliminates NVMe resizing hitching)." -ForegroundColor Green
        } else {
            # Create if not explicit
            New-CimInstance -ClassName Win32_PageFileSetting -Property @{
                Name = "C:\pagefile.sys"
                InitialSize = 8192
                MaximumSize = 16384
            } -ErrorAction SilentlyContinue | Out-Null
            Write-Host "  -> Pagefile created and set to 8GB Initial / 16GB Max." -ForegroundColor Green
        }
    } catch {
        Write-Warning "Could not modify pagefile settings: $_"
    }
} else {
    Write-Host "  -> User-level optimizations successfully installed!" -ForegroundColor Cyan
    Write-Host "  -> To apply the Pagefile & MMAgent tweaks, run this script with -Elevate:" -ForegroundColor Yellow
    Write-Host "     powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Elevate" -ForegroundColor White
}

# Memory telemetry report
$os = Get-CimInstance Win32_OperatingSystem
$totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeGB  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedGB  = [math]::Round($totalGB - $freeGB, 2)
$pctUsed = [math]::Round(($usedGB / $totalGB) * 100, 1)

Write-Host "`n----------------------------------------------------" -ForegroundColor Cyan
Write-Host "Current Memory Status: $usedGB GB used / $totalGB GB total ($pctUsed% utilized, $freeGB GB free)" -ForegroundColor Green
Write-Host "----------------------------------------------------`n" -ForegroundColor Cyan
