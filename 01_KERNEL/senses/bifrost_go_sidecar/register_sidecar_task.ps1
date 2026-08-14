# SPDX-License-Identifier: MIT

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "start_sidecar.ps1"
if (-not (Test-Path $scriptPath)) {
    throw "Launcher script not found: $scriptPath"
}

$taskName = "Camelot Bifrost Go Sidecar"
$taskRun = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""

$arguments = @(
    "/Create",
    "/F",
    "/SC", "ONLOGON",
    "/TN", $taskName,
    "/RL", "LIMITED",
    "/TR", $taskRun
)

$process = Start-Process -FilePath "schtasks.exe" -ArgumentList $arguments -Wait -PassThru -NoNewWindow
if ($process.ExitCode -eq 0) {
    Write-Host "Registered scheduled task: $taskName"
    exit 0
}

$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
if (-not (Test-Path $startupDir)) {
    New-Item -ItemType Directory -Path $startupDir | Out-Null
}
$startupCmdPath = Join-Path $startupDir "camelot-bifrost-go-sidecar.cmd"
$startupCmd = "@echo off`r`n" +
    "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`"`r`n"
Set-Content -Path $startupCmdPath -Value $startupCmd -Encoding ASCII
Write-Warning "Scheduled task registration failed (exit code $($process.ExitCode)). Installed startup fallback: $startupCmdPath"
