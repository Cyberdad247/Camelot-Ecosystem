$ErrorActionPreference = "Continue"
$log = "C:\Users\vizio\CAMELOT_OS\_tmp\admin_final.log"
"=== Final cleanup $(Get-Date) ===" | Out-File $log

# 1) Re-disable CoworkVMService (VMware uninstaller re-enabled it)
try {
  Set-Service CoworkVMService -StartupType Disabled -ErrorAction Stop
  Stop-Service CoworkVMService -Force -ErrorAction SilentlyContinue
  "CoworkVMService disabled" | Out-File $log -Append
} catch { "Cowork FAIL: $($_.Exception.Message)" | Out-File $log -Append }

# 2) Planet9 Stub via MSI GUID (watchdog 180s)
try {
  $proc = Start-Process msiexec.exe -ArgumentList "/x {18eae271-44ac-5152-b237-7dac60ccd85a} /qn /norestart" -PassThru
  if ($proc.WaitForExit(180000)) { "Planet9 MSI exit=$($proc.ExitCode)" | Out-File $log -Append }
  else { "Planet9 MSI still running after 180s (left running, retry in Settings if needed)" | Out-File $log -Append }
} catch { "Planet9 FAIL: $($_.Exception.Message)" | Out-File $log -Append }

# 3) TikTok LIVE Studio (watchdog 90s)
try {
  $proc = Start-Process "C:\Program Files\TikTok LIVE Studio\TikTok LIVE Studio Uninstaller.exe" -ArgumentList "/S" -PassThru
  if ($proc.WaitForExit(90000)) { "TikTok exit=$($proc.ExitCode)" | Out-File $log -Append }
  else { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue; "TikTok uninstaller timed out after 90s, killed" | Out-File $log -Append }
} catch { "TikTok FAIL: $($_.Exception.Message)" | Out-File $log -Append }

"=== Done $(Get-Date) ===" | Out-File $log -Append
