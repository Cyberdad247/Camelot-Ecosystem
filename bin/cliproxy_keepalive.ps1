# Camelot CLIProxyAPI keepalive
$exe = "C:\Users\vizio\CLIProxyAPI\cli-proxy-api.exe"
$dir = "C:\Users\vizio\CLIProxyAPI"
while ($true) {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8080/v1/models" -Headers @{Authorization="Bearer proxy-admin-key"} -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    if ($r.StatusCode -eq 200) { Start-Sleep -Seconds 30; continue }
  } catch {}
  $running = Get-Process | Where-Object { $_.Path -eq $exe } -ErrorAction SilentlyContinue
  if (-not $running) { try { Start-Process -FilePath $exe -WorkingDirectory $dir -WindowStyle Hidden } catch {} }
  Start-Sleep -Seconds 10
}
