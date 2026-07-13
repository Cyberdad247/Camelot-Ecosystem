[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 3006,
    [string]$TaskName = "Camelot-PWA-Cockpit"
)

$ErrorActionPreference = "Stop"
$appRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
foreach ($listener in @($listeners)) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    if ($process.CommandLine -like "*$appRoot*") {
        Stop-Process -Id $listener.OwningProcess -Force
    }
}

$tailscale = Get-Command tailscale.exe -ErrorAction SilentlyContinue
if ($tailscale) {
    & $tailscale.Source serve reset
}

[pscustomobject]@{ Task = $TaskName; Removed = $true; TailnetServeReset = [bool]$tailscale } | ConvertTo-Json
