# SPDX-License-Identifier: MIT

param(
    [string]$TargetDir = "$HOME\workspace",
    [switch]$Force
)

Write-Host "🧹 Sir Scavenger's Cleaning Service initiated on: $TargetDir" -ForegroundColor Cyan

$patterns = @("node_modules", "__pycache__", ".pytest_cache")
$folders = Get-ChildItem -Path $TargetDir -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object { $patterns -contains $_.Name }

if ($folders.Count -eq 0) {
    Write-Host "✨ No clutter found. The forge is clean." -ForegroundColor Green
    exit
}

$totalSize = 0
foreach ($folder in $folders) {
    try {
        $size = (Get-ChildItem $folder.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $totalSize += $size
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "Found: $($folder.FullName) ($sizeMB MB)" -ForegroundColor Yellow
    } catch {
        Write-Host "Access Denied: $($folder.FullName)" -ForegroundColor Red
    }
}

$totalMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "`nTotal Potentially Reclaimable Space: $totalMB MB" -ForegroundColor White

if ($Force -or (Read-Host "Do you want to delete these items? (y/n)") -eq 'y') {
    foreach ($folder in $folders) {
        Write-Host "Removing $($folder.FullName)..." -NoNewline
        try {
            Remove-Item -Path $folder.FullName -Recurse -Force -ErrorAction Stop
            Write-Host " Done." -ForegroundColor Green
        } catch {
            Write-Host " Failed. ($($_))" -ForegroundColor Red
        }
    }
    Write-Host "`n✨ Cleanup Complete." -ForegroundColor Cyan
} else {
    Write-Host "Operation Cancelled." -ForegroundColor Gray
}
