$WshShell = New-Object -ComObject WScript.Shell

$destinations = @(
    [Environment]::GetFolderPath('Desktop'),
    [Environment]::GetFolderPath('CommonDesktop'),
    'C:\Users\vizio\OneDrive\Desktop',
    'C:\Users\Public\Desktop'
) | Select-Object -Unique

foreach ($dest in $destinations) {
    if (Test-Path $dest) {
        Write-Output "Populating shortcuts in: $dest"

        # 1. QtScrcpy GUI Shortcut (.lnk)
        $s1 = $WshShell.CreateShortcut((Join-Path $dest "QtScrcpy.lnk"))
        $s1.TargetPath = "C:\Users\vizio\AppData\Local\CamelotTools\QtScrcpy-v4.1.1\QtScrcpy-win-x64-v4.1.1\QtScrcpy.exe"
        $s1.WorkingDirectory = "C:\Users\vizio\AppData\Local\CamelotTools\QtScrcpy-v4.1.1\QtScrcpy-win-x64-v4.1.1"
        $s1.IconLocation = "C:\Users\vizio\AppData\Local\CamelotTools\QtScrcpy-v4.1.1\QtScrcpy-win-x64-v4.1.1\QtScrcpy.exe,0"
        $s1.Description = "Camelot-OS QtScrcpy GUI Orchestrator"
        $s1.Save()

        # 2. Direct Motorola Mirror Shortcut (.lnk)
        $s2 = $WshShell.CreateShortcut((Join-Path $dest "Motorola Screen Mirror.lnk"))
        $s2.TargetPath = "C:\Users\vizio\CAMELOT_OS\bin\moto.cmd"
        $s2.WorkingDirectory = "C:\Users\vizio\CAMELOT_OS"
        $s2.Description = "Direct Motorola Moto G Power 5G Mirror"
        $s2.Save()

        # 3. VPS Tmux Multiplexer Bus Shortcut (.lnk)
        $s3 = $WshShell.CreateShortcut((Join-Path $dest "Camelot VPS Tmux.lnk"))
        $s3.TargetPath = "C:\Users\vizio\CAMELOT_OS\bin\vps-tmux.cmd"
        $s3.WorkingDirectory = "C:\Users\vizio\CAMELOT_OS"
        $s3.Description = "Camelot-OS VPS Tmux Cockpit"
        $s3.Save()
    }
}
Write-Output "All Desktop shortcuts created and verified."
