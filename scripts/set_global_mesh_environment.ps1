# SPDX-License-Identifier: MIT
# Authority: King Arthur (Vizion) / SIR_HELIOS = Omega_Anti_Gravity_2.0
# Sets Global Windows User Environment Variables and PowerShell Profile integrations

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  OMEGA ANTIGRAVITY 2.0: GLOBAL MESH ENVIRONMENT REGISTRAR" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$envVars = @{
    "OPENAI_API_BASE"        = "https://api.chatanywhere.org/v1"
    "OPENAI_BASE_URL"        = "https://api.chatanywhere.org/v1"
    "OPENAI_API_KEY"         = "sk-a76oLgZdMNOVTRfPWJzim1j4HO6XNJHFyHMUr7lDqWx7gbq2"
    "CHATANYWHERE_API_BASE"  = "https://api.chatanywhere.org/v1"
    "CHATANYWHERE_API_KEY"   = "sk-a76oLgZdMNOVTRfPWJzim1j4HO6XNJHFyHMUr7lDqWx7gbq2"
    "OPENCODEX_URL"          = "http://127.0.0.1:10100"
    "NINE_ROUTER_URL"        = "http://127.0.0.1:8079"
    "BITROUTER_URL"          = "http://127.0.0.1:8077"
    "OMNIROUTE_URL"          = "http://127.0.0.1:20128/v1"
    "CLAUDE_CODE_ROUTER_URL" = "http://127.0.0.1:8079"
}

foreach ($key in $envVars.Keys) {
    $val = $envVars[$key]
    [System.Environment]::SetEnvironmentVariable($key, $val, [System.EnvironmentVariableTarget]::User)
    [System.Environment]::SetEnvironmentVariable($key, $val, [System.EnvironmentVariableTarget]::Process)
    Write-Host "[GLOBAL SET] User env: $key = $val" -ForegroundColor Green
}

# Copy .env.local to User Home directory (C:\Users\vizio\.env.local)
$repoEnv = "C:\Users\vizio\CAMELOT_OS\.env.local"
$userEnv = "C:\Users\vizio\.env.local"
if (Test-Path $repoEnv) {
    Copy-Item -Path $repoEnv -Destination $userEnv -Force
    Write-Host "[GLOBAL SET] Mirrored .env.local to $userEnv" -ForegroundColor Green
}

# Configure PowerShell Profile
$profileTargets = @(
    "C:\Users\vizio\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1",
    "C:\Users\vizio\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1",
    "C:\Users\vizio\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
)

$meshHeader = "# >>> OMEGA ANTIGRAVITY 2.0 SOVEREIGN MESH >>>"
$meshFooter = "# <<< OMEGA ANTIGRAVITY 2.0 SOVEREIGN MESH <<<"

$profileSnippet = @"

$meshHeader
# Auto-injected by SIR_HELIOS = Omega_Anti_Gravity_2.0
`$env:OPENAI_API_BASE       = "https://api.chatanywhere.org/v1"
`$env:OPENAI_BASE_URL       = "https://api.chatanywhere.org/v1"
`$env:OPENAI_API_KEY        = "sk-a76oLgZdMNOVTRfPWJzim1j4HO6XNJHFyHMUr7lDqWx7gbq2"
`$env:CHATANYWHERE_API_BASE = "https://api.chatanywhere.org/v1"
`$env:CHATANYWHERE_API_KEY  = "sk-a76oLgZdMNOVTRfPWJzim1j4HO6XNJHFyHMUr7lDqWx7gbq2"
`$env:OPENCODEX_URL         = "http://127.0.0.1:10100"
`$env:NINE_ROUTER_URL       = "http://127.0.0.1:8079"
`$env:BITROUTER_URL         = "http://127.0.0.1:8077"
`$env:OMNIROUTE_URL         = "http://127.0.0.1:20128/v1"

function claude-mesh {
    param([string]`$target = "chatanywhere")
    & 'C:\Users\vizio\CAMELOT_OS\scripts\launch_claude_code_mesh.ps1' -TargetRouter `$target @args
}

function omniroute-audit {
    python 'C:\Users\vizio\CAMELOT_OS\control_plane\runners\omniroute_swarm_daemon.py' --check-once
}

function omniroute-daemon {
    python 'C:\Users\vizio\CAMELOT_OS\control_plane\runners\omniroute_swarm_daemon.py' --daemon @args
}
$meshFooter
"@

foreach ($prof in $profileTargets) {
    try {
        $parentDir = Split-Path $prof -Parent
        if (-not (Test-Path $parentDir)) {
            New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
        }
        
        $currentContent = ""
        if (Test-Path $prof) {
            $currentContent = Get-Content -Path $prof -Raw
        }
        
        if ($currentContent -match [regex]::Escape($meshHeader)) {
            # Replace existing block
            $pattern = "(?s)" + [regex]::Escape($meshHeader) + ".*?" + [regex]::Escape($meshFooter)
            $newContent = [regex]::Replace($currentContent, $pattern, $profileSnippet.Trim())
            Set-Content -Path $prof -Value $newContent -Force
            Write-Host "[GLOBAL SET] Updated profile block in $prof" -ForegroundColor Cyan
        } else {
            # Append block
            Add-Content -Path $prof -Value $profileSnippet -Force
            Write-Host "[GLOBAL SET] Injected profile block into $prof" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "[WARN] Skipped profile target ${prof}: $_" -ForegroundColor DarkGray
    }
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  GLOBAL INTEGRATION COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
