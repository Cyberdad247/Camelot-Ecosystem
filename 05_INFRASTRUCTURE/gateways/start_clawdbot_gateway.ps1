# Camelot OS — Start Clawdbot Gateway
# Called by: camelot scripts start-gateway
# Gateway runs on loopback :18789

$GatewayPort = 18789
$GatewayCmd  = "$env:USERPROFILE\.clawdbot\gateway.cmd"
$PidFile     = "$env:USERPROFILE\CAMELOT_OS\logs\clawdbot_gateway.pid"
$LogFile     = "$env:USERPROFILE\CAMELOT_OS\logs\clawdbot_gateway.log"

# Ensure logs dir exists
New-Item -ItemType Directory -Force -Path (Split-Path $PidFile) | Out-Null

# Check if already running on port
$existing = Get-NetTCPConnection -LocalPort $GatewayPort -ErrorAction SilentlyContinue
if ($existing) {
    $pid_running = ($existing | Select-Object -First 1).OwningProcess
    Write-Host "[CLAWDBOT] Gateway already running on :$GatewayPort (PID $pid_running)"
    exit 0
}

if (-not (Test-Path $GatewayCmd)) {
    Write-Host "[CLAWDBOT] ERROR: gateway.cmd not found at $GatewayCmd"
    exit 1
}

# Launch gateway detached, redirect output to log
$proc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c `"$GatewayCmd`" >> `"$LogFile`" 2>&1" `
    -WindowStyle Hidden `
    -PassThru

$proc.Id | Out-File -FilePath $PidFile -Encoding ascii
Write-Host "[CLAWDBOT] Gateway started PID=$($proc.Id) on :$GatewayPort"
