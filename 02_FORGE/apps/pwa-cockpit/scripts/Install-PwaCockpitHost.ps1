[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 3006,
    [string]$TaskName = "Camelot-PWA-Cockpit",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$appRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runner = Join-Path $PSScriptRoot "Run-PwaCockpit.ps1"
$account = "$env:USERDOMAIN\$env:USERNAME"

if (-not $SkipBuild) {
    Push-Location -LiteralPath $appRoot
    try {
        & npm.cmd run verify
        if ($LASTEXITCODE -ne 0) { throw "Cockpit verification failed." }
    } finally {
        Pop-Location
    }
}

$listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
foreach ($listener in @($listeners)) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    if ($process.CommandLine -notlike "*$appRoot*") {
        throw "Port $Port is owned by an unrelated process ($($listener.OwningProcess))."
    }
    Stop-Process -Id $listener.OwningProcess -Force
}

$powershell = (Get-Command powershell.exe).Source
$arguments = "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$runner`" -Port $Port"
$action = New-ScheduledTaskAction -Execute $powershell -Argument $arguments -WorkingDirectory $appRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $account
$principal = New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 3650) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Authenticated Camelot-OS PWA Cockpit host" -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName

$deadline = (Get-Date).AddSeconds(30)
do {
    Start-Sleep -Milliseconds 500
    $ready = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
} until ($ready -or (Get-Date) -gt $deadline)

if (-not $ready) {
    throw "The Cockpit task did not bind 127.0.0.1:$Port. Inspect artifacts\runtime\pwa-cockpit-runtime.log."
}

$tailscale = Get-Command tailscale.exe -ErrorAction SilentlyContinue
$tailnetUrl = $null
if ($tailscale) {
    & $tailscale.Source serve --bg --yes $Port
    if ($LASTEXITCODE -ne 0) { throw "Tailscale Serve configuration failed." }
    $status = & $tailscale.Source status --json | ConvertFrom-Json
    if ($status.Self.DNSName) { $tailnetUrl = "https://$($status.Self.DNSName.TrimEnd('.'))/" }
}

[pscustomobject]@{
    Task = $TaskName
    State = (Get-ScheduledTask -TaskName $TaskName).State.ToString()
    LocalUrl = "http://localhost:$Port"
    TailnetUrl = $tailnetUrl
    ExecutionEnabled = $false
} | ConvertTo-Json
