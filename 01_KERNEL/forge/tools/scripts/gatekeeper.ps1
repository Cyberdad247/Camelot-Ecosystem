# SPDX-License-Identifier: MIT

param (
    [Parameter(Mandatory=$false)][string]$Path = $PWD,
    [string]$TrashRoot = "$HOME\.project-clean-trash",
    [string]$SanctuaryPath = "$HOME\workspace"
)

# 1. Setup Trash and Sanctuary
$today = Get-Date -Format "yyyy-MM-dd"
$trashDir = Join-Path $TrashRoot $today
if (!(Test-Path $trashDir)) { New-Item -ItemType Directory -Force -Path $trashDir | Out-Null }
if (!(Test-Path $SanctuaryPath)) { New-Item -ItemType Directory -Force -Path $SanctuaryPath | Out-Null }

# 2. Get Candidates (Top Level Only)
# Exclude system/critical folders if running in root
$excludes = @("workspace", ".project-clean-trash", "AppData", "Windows", "Program Files", "Program Files (x86)", ".git", ".vscode")
$candidates = Get-ChildItem -Path $Path -ErrorAction SilentlyContinue | Where-Object { $excludes -notcontains $_.Name }

if ($candidates.Count -eq 0) {
    Write-Host "🛡️  The Gatekeeper finds no candidates in this realm." -ForegroundColor Cyan
    exit
}

# 3. The Process
foreach ($item in $candidates) {
    Clear-Host
    Write-Host "⚔️  THE GATEKEEPER ⚔️" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------"
    Write-Host "Scanning: $Path"
    Write-Host "------------------------------------------------------------"
    
    # Item Details
    $sizeMB = 0
    if ($item.PSIsContainer) {
        Write-Host "🏰 FORTRESS (Folder): " -NoNewline; Write-Host $item.Name -ForegroundColor Yellow
        # Quick size calc (can be slow for huge folders, maybe skip?)
        # $sizeMB = (Get-ChildItem $item.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    } else {
        Write-Host "📜 SCROLL (File):     " -NoNewline; Write-Host $item.Name -ForegroundColor Yellow
        $sizeMB = $item.Length / 1MB
        Write-Host "   Size:             " -NoNewline; Write-Host ("{0:N2} MB" -f $sizeMB) -ForegroundColor Gray
    }
    
    Write-Host "   Last Modified:    " -NoNewline; Write-Host $item.LastWriteTime -ForegroundColor Gray
    Write-Host "------------------------------------------------------------"
    Write-Host "[I] INTEGRATE  -> Move to $SanctuaryPath"
    Write-Host "[E] EXPUNGE    -> Move to Trash ($today)"
    Write-Host "[S] SKIP       -> Leave here"
    if (!($item.PSIsContainer)) { Write-Host "[V] VIEW       -> Read first 10 lines" }
    Write-Host "[Q] QUIT       -> End session"
    Write-Host "------------------------------------------------------------"
    
    $action = Read-Host "Your Command? (i/e/s/v/q)"
    
    switch ($action.ToLower()) {
        "i" {
            $sub = Read-Host "   > Enter subfolder name in Workspace (Enter for root)"
            $target = $SanctuaryPath
            if ($sub -ne "") {
                $target = Join-Path $SanctuaryPath $sub
                if (!(Test-Path $target)) { New-Item -ItemType Directory -Force -Path $target | Out-Null }
            }
            
            # Check for collision
            $destPath = Join-Path $target $item.Name
            if (Test-Path $destPath) {
                Write-Host "   ⚠️  Collision detected! Appending timestamp." -ForegroundColor Red
                $newName = "$($item.Name)_$(Get-Date -Format 'HHmmss')"
                Rename-Item -Path $item.FullName -NewName $newName
                Move-Item (Join-Path $Path $newName) $target
            } else {
                Move-Item $item.FullName $target
            }
            Write-Host "   ✅ Integrated." -ForegroundColor Green
            Start-Sleep -Milliseconds 500
        }
        "e" {
            Move-Item $item.FullName $trashDir
            Write-Host "   🗑️  Expunged." -ForegroundColor Red
            Start-Sleep -Milliseconds 500
        }
        "v" {
            if (!($item.PSIsContainer)) {
                Write-Host "--- CONTENT PREVIEW ---" -ForegroundColor Cyan
                Get-Content $item.FullName -TotalCount 10
                Write-Host "-----------------------" -ForegroundColor Cyan
                Pause
            }
        }
        "q" {
            Write-Host "Gatekeeper session ended."
            exit
        }
        default {
            Write-Host "   ⏭️  Skipping." -ForegroundColor Gray
        }
    }
}

Write-Host "`n🛡️  Cycle Complete." -ForegroundColor Cyan
