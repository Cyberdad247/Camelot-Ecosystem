# CAMELOT-OS Starship prompt integration
# Source this from PowerShell after installing Starship.
# Official init form: Invoke-Expression (&starship init powershell)
$env:STARSHIP_CONFIG = 'C:\Users\vizio\CAMELOT_OS\03_VAULT\runtime_state\starship\camelot-starship.toml'
if (Get-Command starship -ErrorAction SilentlyContinue) {
    Invoke-Expression (&starship init powershell)
} else {
    Write-Warning 'Starship executable not found. Install Starship, then re-source this file.'
}
