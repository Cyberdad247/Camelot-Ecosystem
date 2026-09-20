# SPDX-License-Identifier: MIT

# Camelot-OS Global Alias Registration Script (Windows PowerShell)

function Register-CamelotAlias {
    $repoRoot = "C:\Users\vizio\CAMELOT_OS"
    $binDir = "$repoRoot\bin"
    $venvScripts = "$repoRoot\.venv\Scripts"
    $aliasPath = "$binDir\Camelot-OS.ps1"
    $content = @"
# Camelot-OS Global CLI Proxy
& 'C:\Users\vizio\CAMELOT_OS\02_FORGE\cartridge\rustclaw\target\release\rustclaw.exe' `$args
"@
    Set-Content -Path $aliasPath -Value $content

    # Shim: camelot.ps1 -> unified WARP_GATE CLI via venv python (pip install -e . also exposes camelot.exe)
    $camelotShim = "$binDir\camelot.ps1"
    $camelotShimContent = @"
# camelot global shim — prefers installed entry point, falls back to repo source
`$exe = Join-Path "$venvScripts" "camelot.exe"
if (Test-Path `$exe) { & `$exe @args; exit `$LASTEXITCODE }
& "$venvScripts\python.exe" "$repoRoot\bin\camelot.py" @args
"@
    Set-Content -Path $camelotShim -Value $camelotShimContent

    # Shim: awaken.ps1 -> boot sequencer (supports --status --json --snapshot)
    $awakenShim = "$binDir\awaken.ps1"
    $awakenShimContent = @"
& "$venvScripts\python.exe" "$repoRoot\bin\awaken.py" @args
"@
    Set-Content -Path $awakenShim -Value $awakenShimContent

    # Add bin + .venv\Scripts to User PATH if not present
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $updated = $currentPath
    if ($currentPath -notlike "*$binDir*") { $updated = "$updated;$binDir" }
    if ($currentPath -notlike "*$venvScripts*") { $updated = "$updated;$venvScripts" }
    if ($updated -ne $currentPath) {
        [Environment]::SetEnvironmentVariable("Path", $updated, "User")
        Write-Host "Camelot-OS added to User PATH (bin + .venv\\Scripts). Restart your terminal."
    }
}

Register-CamelotAlias
