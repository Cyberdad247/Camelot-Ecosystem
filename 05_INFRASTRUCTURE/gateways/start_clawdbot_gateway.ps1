# Camelot OS — Start Clawdbot Gateway
# Called by: camelot scripts start-gateway
# Gateway runs on loopback :18789

$GatewayPort = 18789
$GatewayCmd  = "$env:USERPROFILE\.clawdbot\gateway.cmd"
$PidFile     = "$env:USERPROFILE\CAMELOT_OS\logs\clawdbot_gateway.pid"
$LogFile     = "$env:USERPROFILE\CAMELOT_OS\logs\clawdbot_gateway.log"

# Ensure logs dir exists
New-Item -ItemType Directory -Force -Path (Split-Path $PidFile) | Out-Null

# Check if already running on port. Get-NetTCPConnection depends on the CIM
# service, which can be broken shell-wide ("Cannot connect to CIM server");
# a plain TCP connect is the authoritative check, CIM is only used to report PID.
$portOpen = $false
$tcp = New-Object System.Net.Sockets.TcpClient
try {
    $connect = $tcp.BeginConnect("127.0.0.1", $GatewayPort, $null, $null)
    if ($connect.AsyncWaitHandle.WaitOne(1500) -and $tcp.Connected) {
        $tcp.EndConnect($connect)
        $portOpen = $true
    }
} catch {} finally { $tcp.Close() }

if ($portOpen) {
    $pid_running = "unknown"
    try {
        $existing = Get-NetTCPConnection -LocalPort $GatewayPort -ErrorAction Stop | Select-Object -First 1
        if ($existing) { $pid_running = $existing.OwningProcess }
    } catch {}
    Write-Host "[CLAWDBOT] Gateway already running on :$GatewayPort (PID $pid_running)"
    exit 0
}

if (-not (Test-Path $GatewayCmd)) {
    Write-Host "[CLAWDBOT] ERROR: gateway.cmd not found at $GatewayCmd"
    exit 1
}

# Launch gateway detached. Use native Start-Process redirection (array-form
# ArgumentList) instead of an embedded `>>` shell redirect — the embedded-redirect
# form caused cmd.exe to exit immediately without ever starting node (empty log,
# dead PID). Separate stdout/stderr files are required by Start-Process.
$ErrFile = "$env:USERPROFILE\CAMELOT_OS\logs\clawdbot_gateway.err"
$proc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c", $GatewayCmd `
    -WindowStyle Hidden `
    -RedirectStandardOutput $LogFile `
    -RedirectStandardError $ErrFile `
    -PassThru



$proc.Id | Out-File -FilePath $PidFile -Encoding ascii
Write-Host "[CLAWDBOT] Gateway started PID=$($proc.Id) on :$GatewayPort"
