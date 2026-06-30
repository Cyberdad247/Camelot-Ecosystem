# Cybertronia server supervisor.
# Keeps the Go daemons alive (restart-on-crash) so cybertronia is an always-on
# server. Launched at logon by the "CybertroniaServer" scheduled task.
#   - go_router        :8077  (SSE command router; public via Tailscale Funnel)
#   - bifrost_sidecar  :8011  (Bifrost bridge -> upstream :8001)
# This script never exits; it polls every 5s and relaunches any daemon that died.

$ErrorActionPreference = "Continue"
$root = "C:\Users\vizio\CAMELOT_OS"
$logDir = Join-Path $root "logs\cybertronia"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# go_router reports this as its node name in SSE events.
$env:CAMELOT_NODE = "cybertronia"
# Path to the compiled Rust RTK engine (Go -> Rust rune dispatch).
$env:CAMELOT_RTK_BIN = "$root\target\release\rtk_cli.exe"
# Cognitive service (Graphify/MemCastle/sync over HTTP) port + scheduled //sync.
# :8090 is taken by saltare_gateway, so use :8092.
$env:COGNITIVE_PORT = "8092"
$env:CAMELOT_COGNITIVE_URL = "http://127.0.0.1:8092"  # go_router /cognitive proxy target
$env:COGNITIVE_SYNC_INTERVAL = "1800"  # auto //sync every 30 min (edge-first; skips if cloud down)

$daemons = @(
  @{ Name = "go_router";       Exe = "$root\control_plane\go_router\go_router.exe";              Args = @("serve", ":8077") },
  @{ Name = "bifrost_sidecar"; Exe = "$root\01_KERNEL\senses\bifrost_go_sidecar\bifrost_sidecar.exe"; Args = @() },
  @{ Name = "cognitive_service"; Exe = "python"; Args = @("$root\control_plane\cognitive_service.py") }
)

$procs = @{}
"[{0}] Cybertronia supervisor online" -f (Get-Date -Format s) | Add-Content (Join-Path $logDir "supervisor.log")

while ($true) {
  foreach ($d in $daemons) {
    $p = $procs[$d.Name]
    if (-not $p -or $p.HasExited) {
      $log = Join-Path $logDir ($d.Name + ".log")
      $err = Join-Path $logDir ($d.Name + ".err.log")
      "[{0}] (re)starting {1}" -f (Get-Date -Format s), $d.Name | Add-Content (Join-Path $logDir "supervisor.log")
      try {
        if ($d.Args.Count -gt 0) {
          $procs[$d.Name] = Start-Process -FilePath $d.Exe -ArgumentList $d.Args `
            -RedirectStandardOutput $log -RedirectStandardError $err -WindowStyle Hidden -PassThru
        } else {
          $procs[$d.Name] = Start-Process -FilePath $d.Exe `
            -RedirectStandardOutput $log -RedirectStandardError $err -WindowStyle Hidden -PassThru
        }
      } catch {
        "[{0}] FAILED to start {1}: {2}" -f (Get-Date -Format s), $d.Name, $_ | Add-Content (Join-Path $logDir "supervisor.log")
      }
    }
  }
  Start-Sleep -Seconds 5
}
