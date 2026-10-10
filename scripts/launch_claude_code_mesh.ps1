<#
.SYNOPSIS
Launch Local Claude-Code within the Omega AntiGravity 2.0 Sovereign Mesh
Authority: SIR_HELIOS = Omega_Anti_Gravity_2.0
Knights: SIR_HELIOS & SIR_CODEX

.DESCRIPTION
Exports the environment variables to route Claude Code through 9Router (:8079),
ChatAnywhere (https://api.chatanywhere.org/v1), and the OmniRoute gateway.
#>

param(
    [string]$TargetRouter = "chatanywhere", # options: chatanywhere, 9router, omniroute
    [switch]$CheckHealth
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  OMEGA ANTIGRAVITY 2.0: LOCAL CLAUDE-CODE MESH LAUNCHER" -ForegroundColor Yellow
Write-Host "  Authority: SIR_HELIOS | Mode: $TargetRouter" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Load .env.local if present
$envFile = Join-Path $PSScriptRoot "..\.env.local"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $val = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $val, [System.EnvironmentVariableTarget]::Process)
        }
    }
    Write-Host "[OK] Loaded secrets and endpoints from .env.local" -ForegroundColor Green
}

switch ($TargetRouter) {
    "chatanywhere" {
        $env:OPENAI_BASE_URL = "https://api.chatanywhere.org/v1"
        $env:OPENAI_API_KEY = "sk-a76oLgZdMNOVTRfPWJzim1j4HO6XNJHFyHMUr7lDqWx7gbq2"
        $env:ANTHROPIC_BASE_URL = "http://127.0.0.1:8080/v1"
        Write-Host "--> Wired to ChatAnywhere Global Proxy ($env:OPENAI_BASE_URL)" -ForegroundColor Magenta
    }
    "9router" {
        $env:ANTHROPIC_BASE_URL = "http://127.0.0.1:8079/v1"
        $env:OPENAI_BASE_URL = "http://127.0.0.1:8079/v1"
        Write-Host "--> Wired to 9Router 24k ops/s Packet Scheduler (:8079)" -ForegroundColor Magenta
    }
    "omniroute" {
        $env:ANTHROPIC_BASE_URL = "http://127.0.0.1:20128/v1"
        $env:OPENAI_BASE_URL = "http://127.0.0.1:20128/v1"
        Write-Host "--> Wired to OmniRoute Sovereign Gateway (:20128)" -ForegroundColor Magenta
    }
}

if ($CheckHealth) {
    Write-Host "[INFO] Performing health check on active routes..." -ForegroundColor Yellow
    python "$PSScriptRoot\..\control_plane\runners\omniroute_swarm_daemon.py" --check-once
    exit 0
}

Write-Host "[READY] Environment sealed. Starting claude CLI..." -ForegroundColor Green
if (Get-Command claude -ErrorAction SilentlyContinue) {
    & claude @args
} else {
    Write-Host "[WARN] 'claude' CLI not found on PATH. Environment is prepared for invocation." -ForegroundColor Yellow
}
