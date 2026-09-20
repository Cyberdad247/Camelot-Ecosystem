# SPDX-License-Identifier: MIT
# Register Camelot CLIProxyAPI as Windows Scheduled Task - logon autostart + persistence

$ErrorActionPreference = "Stop"

$taskName = "Camelot CLIProxyAPI"
$exe = "C:\Users\vizio\CLIProxyAPI\cli-proxy-api.exe"
$dir = "C:\Users\vizio\CLIProxyAPI"
$wrapper = "C:\Users\vizio\CAMELOT_OS\bin\cliproxy_keepalive.ps1"

if (-not (Test-Path $exe)) { throw "CLIProxyAPI binary not found at $exe" }

# Keepalive wrapper - polls :8080 every 30s, respawns if dead
$wrapperLines = @(
  "# Camelot CLIProxyAPI keepalive",
  "`$exe = `"C:\Users\vizio\CLIProxyAPI\cli-proxy-api.exe`"",
  "`$dir = `"C:\Users\vizio\CLIProxyAPI`"",
  "while (`$true) {",
  "  try {",
  "    `$r = Invoke-WebRequest -Uri `"http://127.0.0.1:8080/v1/models`" -Headers @{Authorization=`"Bearer proxy-admin-key`"} -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop",
  "    if (`$r.StatusCode -eq 200) { Start-Sleep -Seconds 30; continue }",
  "  } catch {}",
  "  `$running = Get-Process | Where-Object { `$_.Path -eq `$exe } -ErrorAction SilentlyContinue",
  "  if (-not `$running) { try { Start-Process -FilePath `$exe -WorkingDirectory `$dir -WindowStyle Hidden } catch {} }",
  "  Start-Sleep -Seconds 10",
  "}"
)
Set-Content -Path $wrapper -Value ($wrapperLines -join "`r`n") -Encoding UTF8

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$wrapper`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit 0
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

try { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Camelot-OS CLIProxyAPI :8080 - Zero-Burn local proxy" | Out-Null

try { Start-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue; Write-Host "Task $taskName registered and started." } catch { Write-Host "Task $taskName registered (start pending logon)." }

schtasks /Query /TN $taskName /V /FO LIST 2>&1 | Select-String -Pattern "TaskName|Status"
