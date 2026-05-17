# Camelot OS — Stop Clawdbot Gateway
# Called by: camelot scripts stop-gateway

$GatewayPort = 18789
$PidFile     = "$env:USERPROFILE\CAMELOT_OS\logs\clawdbot_gateway.pid"

function Stop-ByPidFile {
    if (Test-Path $PidFile) {
        $storedPid = Get-Content $PidFile -Raw | ForEach-Object { $_.Trim() }
        if ($storedPid -match '^\d+$') {
            try {
                Stop-Process -Id ([int]$storedPid) -Force -ErrorAction Stop
                Write-Host "[CLAWDBOT] Stopped gateway PID=$storedPid"
                Remove-Item $PidFile -Force
                return $true
            } catch {
                Write-Host "[CLAWDBOT] PID $storedPid not found, trying port scan..."
            }
        }
    }
    return $false
}

function Stop-ByPort {
    $conn = Get-NetTCPConnection -LocalPort $GatewayPort -ErrorAction SilentlyContinue
    if ($conn) {
        $ownerPid = ($conn | Select-Object -First 1).OwningProcess
        Stop-Process -Id $ownerPid -Force -ErrorAction SilentlyContinue
        Write-Host "[CLAWDBOT] Stopped process on :$GatewayPort (PID $ownerPid)"
        if (Test-Path $PidFile) { Remove-Item $PidFile -Force }
        return $true
    }
    return $false
}

$stopped = Stop-ByPidFile
if (-not $stopped) {
    $stopped = Stop-ByPort
}
if (-not $stopped) {
    Write-Host "[CLAWDBOT] Gateway not running on :$GatewayPort"
}
