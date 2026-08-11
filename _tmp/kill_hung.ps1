Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "powershell.exe" -and $_.CommandLine -like "*admin_optimize*" } | ForEach-Object {
  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  Write-Host ("killed hung elevated script PID " + $_.ProcessId)
}
Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like "*Planet9*" -or $_.ExecutablePath -like "*TikTok*" } | ForEach-Object {
  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  Write-Host ("killed uninstaller " + $_.Name)
}
Write-Host "kill pass done"
