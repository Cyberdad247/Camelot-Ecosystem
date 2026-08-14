# SPDX-License-Identifier: MIT

$ErrorActionPreference = "Stop"
$LEDGER_PATH = "C:\Users\vizio\CAMELOT_OS\PROVENANCE_LEDGER.md"

Write-Host "[☁️🧠] OUROBOROS BRIDGE: Initiating Secure NotebookLM Sync..." -ForegroundColor Magenta

$NOTEBOOK_ID = "a9cf586e-1971-4959-bb97-cdcd37257ebb"
$NOTEBOOK_NAME = "living Camelot-OS: The v300.1 Universal Singularity Recompilation"

function Log-Ledger {
    param([string]$Action, [string]$Status)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $entry = "| $timestamp | OUROBOROS_BRIDGE | $Action | $Status |"
    Add-Content -Path $LEDGER_PATH -Value $entry -ErrorAction SilentlyContinue
}

try {
    # Attempt to fetch the notebook to verify the session
    Write-Host "Verifying session and linking to: $NOTEBOOK_NAME" -ForegroundColor DarkGray
    $result = nlm notebook get $NOTEBOOK_ID 2>&1
    
    if ($LASTEXITCODE -ne 0 -or $result -match "Authentication Error") {
        Write-Host "[🛡️🛑] SECURITY GATE: Session expired or invalid." -ForegroundColor Yellow
        Write-Host "Auto-login (interactive Chrome) is disabled during unattended boot for security." -ForegroundColor Yellow
        Write-Host "Please run 'nlm login' manually to re-authenticate." -ForegroundColor Yellow
        Log-Ledger -Action "Verify Link: $NOTEBOOK_NAME" -Status "AUTH_REQUIRED"
    } else {
        Write-Host "[✅] Ouroboros Link Established: $NOTEBOOK_NAME" -ForegroundColor Green
        Log-Ledger -Action "Sync Notebook: $NOTEBOOK_NAME" -Status "SUCCESS"
    }
} catch {
    Write-Host "[🛡️🛑] Failed to establish Ouroboros Bridge: $_" -ForegroundColor Red
    Log-Ledger -Action "Sync Notebook: $NOTEBOOK_NAME" -Status "FAILURE"
}
