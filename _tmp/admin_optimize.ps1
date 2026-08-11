$ErrorActionPreference = "Continue"
$log = "C:\Users\vizio\CAMELOT_OS\_tmp\admin_optimize.log"
"=== Admin optimize $(Get-Date) ===" | Out-File $log

# ---- 0) Backup current pagefile config for reversibility ----
try {
  $pp = (Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" -ErrorAction Stop).PagingFiles
  "ORIGINAL PagingFiles: $pp" | Out-File $log -Append
} catch { "PagingFiles backup FAIL: $($_.Exception.Message)" | Out-File $log -Append }

# ---- 1) Disable bloat / background services ----
$svcs = @(
  "AcerARTAIMMXDriverService","AcerARTAIMMXService","AcerCCAgentSvis","AcerDIAgentSvis",
  "AcerDeviceEnablingServiceV2","AcerEZSvc","AcerGAICameraService","AcerLightingService",
  "AcerPixyService","AcerQAAgentSvis","AcerServiceSvc","ACCSvc","AASSvc",
  "AdobeARMservice","DiagTrack","chromoting","CoworkVMService"
)
foreach($s in $svcs){
  try {
    $svc = Get-Service -Name $s -ErrorAction Stop
    Set-Service -Name $s -StartupType Disabled
    Stop-Service -Name $s -Force -ErrorAction SilentlyContinue
    "DISABLED service: $s" | Out-File $log -Append
  } catch { "SERVICE FAIL $s : $($_.Exception.Message)" | Out-File $log -Append }
}

# ---- 2) Shrink pagefile to fixed 8 GB (effective after reboot) ----
try {
  Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" `
    -Name PagingFiles -Value "C:\pagefile.sys 8192 8192" -Type MultiString
  "PAGEFILE set to 8192 MB (effective after reboot)" | Out-File $log -Append
} catch { "PAGEFILE FAIL: $($_.Exception.Message)" | Out-File $log -Append }

# ---- 3) Uninstall approved bloatware (silent) ----
$msiGUIDs = @(
  "{EA5A8470-5696-42BB-A922-B85E4231D15D}",  # 3CX Phone System
  "{6EC7759F-B700-4743-BB65-BD3ED905D545}",  # VMware Workstation
  "{323EA05D-046D-449D-9D7C-89243C957CCE}",  # Acer User Experience Improvement Program
  "{AFB52E98-7597-4484-9202-58F0FD3512ED}",  # Acer Care Center Service
  "{0C5ED25A-B8D1-4E71-BFCB-6B370A4EA19C}",  # Acer Jumpstart
  "{22165EE8-F79D-4400-A6FB-8E35391B8BEF}"   # Acer Configuration Manager
)
foreach($g in $msiGUIDs){
  try {
    $p = Start-Process msiexec.exe -ArgumentList "/x `"$g`" /qn /norestart" -Wait -PassThru
    "MSI uninstall $g exit=$($p.ExitCode)" | Out-File $log -Append
  } catch { "MSI FAIL $g : $($_.Exception.Message)" | Out-File $log -Append }
}

# Planet9 Stub
try {
  $p = Start-Process "C:\Program Files\Planet9 Stub\Uninstall Planet9 Stub.exe" -ArgumentList "/allusers" -Wait -PassThru
  "Planet9 uninstall exit=$($p.ExitCode)" | Out-File $log -Append
} catch { "PLANET9 FAIL: $($_.Exception.Message)" | Out-File $log -Append }

# TikTok LIVE Studio (NSIS-style uninstaller, /S silent)
try {
  $p = Start-Process "C:\Program Files\TikTok LIVE Studio\TikTok LIVE Studio Uninstaller.exe" -ArgumentList "/S" -Wait -PassThru
  "TikTok uninstall exit=$($p.ExitCode)" | Out-File $log -Append
} catch { "TIKTOK FAIL: $($_.Exception.Message)" | Out-File $log -Append }

"=== Done $(Get-Date) ===" | Out-File $log -Append
