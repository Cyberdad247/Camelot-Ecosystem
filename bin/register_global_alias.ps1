# Camelot-OS Global Alias Registration Script (Windows PowerShell)

function Register-CamelotAlias {
    $aliasPath = "C:\Users\vizio\CAMELOT_OS\bin\Camelot-OS.ps1"
    $content = @"
# Camelot-OS Global CLI Proxy
& 'C:\Users\vizio\CAMELOT_OS\02_FORGE\cartridge\rustclaw\target\release\rustclaw.exe' `$args
"@
    Set-Content -Path $aliasPath -Value $content
    
    # Add bin to User PATH if not present
    $binDir = "C:\Users\vizio\CAMELOT_OS\bin"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binDir", "User")
        Write-Host "Camelot-OS added to User PATH. Restart your terminal."
    }
}

Register-CamelotAlias
