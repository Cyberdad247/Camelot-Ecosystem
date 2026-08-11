$ErrorActionPreference = 'Continue'
$log = 'C:\Users\vizio\CAMELOT_OS\_tmp\remove_planet9.log'
$key = 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\18eae271-44ac-5152-b237-7dac60ccd85a'
$backup = 'C:\Users\vizio\camelot_startup_backup_20260810\Planet9_UninstallKey_backup.reg'

"=== remove_planet9 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Tee-Object -FilePath $log

# 1. Backup the uninstall registry key
try {
    reg export "HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\18eae271-44ac-5152-b237-7dac60ccd85a" $backup /y | Out-Null
    "Registry key backed up to: $backup" | Tee-Object -FilePath $log -Append
} catch {
    "Backup failed: $($_.Exception.Message)" | Tee-Object -FilePath $log -Append
}

# 2. Delete the uninstall registry key
try {
    if (Test-Path $key) {
        Remove-Item -Path $key -Recurse -Force
        "Uninstall key deleted." | Tee-Object -FilePath $log -Append
    } else {
        "Uninstall key already gone." | Tee-Object -FilePath $log -Append
    }
} catch {
    "Key delete failed: $($_.Exception.Message)" | Tee-Object -FilePath $log -Append
}

# 3. Clean any related Planet9 registry remnants under HKLM\Software
$remnants = @('HKLM:\Software\Planet9', 'HKLM:\Software\WOW6432Node\Planet9', 'HKLM:\Software\Acer Incorporated\Planet9')
foreach ($r in $remnants) {
    if (Test-Path $r) {
        Remove-Item -Path $r -Recurse -Force
        "Removed registry remnant: $r" | Tee-Object -FilePath $log -Append
    }
}

# 4. Delete the install folder
$folder = 'C:\Program Files\Planet9 Stub'
try {
    if (Test-Path $folder) {
        Remove-Item -Path $folder -Recurse -Force
        "Folder removed: $folder" | Tee-Object -FilePath $log -Append
    } else {
        "Folder already gone." | Tee-Object -FilePath $log -Append
    }
} catch {
    "Folder delete failed: $($_.Exception.Message)" | Tee-Object -FilePath $log -Append
}

"=== DONE ===" | Tee-Object -FilePath $log -Append
