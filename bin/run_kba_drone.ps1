# Camelot-OS KBA Drone launcher — loads secrets from ~/.camelot/kba_drone.env and
# starts the governed drone (Heimdall + CloudBrain). Used by the CamelotKBADrone
# scheduled task so the drone survives logout/reboot, independent of any session.
$ErrorActionPreference = "Stop"

$envFile = Join-Path $HOME ".camelot\kba_drone.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

Set-Location (Join-Path $HOME "CAMELOT_OS")
python -m control_plane.drone_node --node-id kba-drone-cybertronia --host 100.118.224.52 --port 9000
