# ============================================================
# CAMELOT-OS Installer - Windows PowerShell
# WARP_GATE v1.0.0
# Usage: .\scripts\install.ps1
#        iex (iwr https://raw.githubusercontent.com/.../install.ps1).Content
# ============================================================

param(
    [switch]$NoProfile,
    [switch]$NoConfigure,
    [switch]$Portable,
    [switch]$Force,
    [string]$CamelotHome
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$CAMELOT_VERSION = "400.1.0"
$WARP_VERSION    = "1.0.0"
$MIN_PYTHON      = [version]"3.11"

# ---- Helpers -----------------------------------------------------------------

function Write-Step { param([string]$Msg)
    Write-Host "`n  " -NoNewline
    Write-Host ">>  " -ForegroundColor Cyan -NoNewline
    Write-Host $Msg
}
function Write-Ok   { param([string]$M)
    Write-Host "  " -NoNewline
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host $M
}
function Write-Warn { param([string]$M)
    Write-Host "  " -NoNewline
    Write-Host "[!!] " -ForegroundColor Yellow -NoNewline
    Write-Host $M
}

function Test-CmdExists { param([string]$Cmd)
    return [bool](Get-Command $Cmd -ErrorAction SilentlyContinue)
}

function Add-ToUserPath { param([string]$Dir)
    $current = [System.Environment]::GetEnvironmentVariable("PATH","User")
    if ($current -notlike "*$Dir*") {
        $new = if ($current) { "$current;$Dir" } else { $Dir }
        [System.Environment]::SetEnvironmentVariable("PATH", $new, "User")
        $env:PATH = "$env:PATH;$Dir"
        return $true
    }
    return $false
}

# ---- Banner ------------------------------------------------------------------

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Yellow
Write-Host "   CAMELOT-OS v$CAMELOT_VERSION  //  WARP_GATE v$WARP_VERSION" -ForegroundColor Yellow
Write-Host "   Windows PowerShell Installer" -ForegroundColor Yellow
Write-Host "  ============================================" -ForegroundColor Yellow
Write-Host ""

# ---- Locate CAMELOT_OS root --------------------------------------------------

Write-Step "Locating CAMELOT_OS root..."

if ($CamelotHome) {
    $REPO = $CamelotHome
} elseif ($env:CAMELOT_OS_HOME) {
    $REPO = $env:CAMELOT_OS_HOME
} else {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if ($scriptDir) {
        $REPO = Split-Path -Parent $scriptDir
    } else {
        $REPO = "C:\Users\$env:USERNAME\CAMELOT_OS"
    }
}

if (-not (Test-Path "$REPO\pyproject.toml")) {
    Write-Host "  [XX] Cannot find CAMELOT_OS at: $REPO" -ForegroundColor Red
    Write-Warn "Clone the repo first: git clone https://github.com/your-org/CAMELOT_OS.git"
    exit 1
}

Write-Ok "CAMELOT_OS root: $REPO"
$VENV_DIR     = "$REPO\.venv"
$VENV_PYTHON  = "$VENV_DIR\Scripts\python.exe"
$VENV_SCRIPTS = "$VENV_DIR\Scripts"

# ---- Check Python ------------------------------------------------------------

Write-Step "Checking Python version..."

$pythonCmd = $null

foreach ($cmd in @("python", "python3", "py")) {
    if (-not (Test-CmdExists $cmd)) { continue }

    $verOutput = ""
    try {
        $verOutput = (& $cmd --version 2>&1)
    } catch {
        continue
    }

    $verStr = "$verOutput"
    if ($verStr -match "Python (\d+\.\d+)") {
        $v = [version]$Matches[1]
        if ($v -ge $MIN_PYTHON) {
            $pythonCmd = $cmd
            Write-Ok "Found: $verStr"
            break
        } else {
            Write-Warn "Found $verStr - need >= $MIN_PYTHON"
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "  [XX] Python $MIN_PYTHON+ not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Install via winget:" -ForegroundColor White
    Write-Host "    winget install Python.Python.3.11" -ForegroundColor Cyan
    Write-Host "  Or: https://python.org/downloads" -ForegroundColor White
    exit 1
}

# ---- Create / verify virtual environment -------------------------------------

Write-Step "Checking virtual environment..."

if (Test-Path $VENV_PYTHON) {
    Write-Ok "Existing .venv found: $VENV_DIR"
} else {
    Write-Host "  Creating .venv at $VENV_DIR ..."
    if (Test-CmdExists "uv") {
        & uv venv "$VENV_DIR" --python $pythonCmd
    } else {
        & $pythonCmd -m venv "$VENV_DIR"
    }
    if (-not (Test-Path $VENV_PYTHON)) {
        Write-Host "  [XX] Failed to create .venv" -ForegroundColor Red
        exit 1
    }
    Write-Ok ".venv created"
}

# ---- Install minimum packages ------------------------------------------------

Write-Step "Installing required packages into .venv..."

$MIN_PACKAGES = @("httpx", "rich", "psutil", "pyyaml")
$missing = @()

$_savedEA = $ErrorActionPreference
$ErrorActionPreference = "Continue"
foreach ($pkg in $MIN_PACKAGES) {
    $mod = $pkg.Replace("-","_")
    & $VENV_PYTHON -c "import $mod" 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { $missing += $pkg }
}
$ErrorActionPreference = $_savedEA

if ($missing.Count -gt 0) {
    Write-Host "  Installing: $($missing -join ', ')" -ForegroundColor Cyan
    if (Test-CmdExists "uv") {
        & uv pip install --python $VENV_PYTHON @missing
    } else {
        & $VENV_PYTHON -m pip install --quiet @missing
    }
    Write-Ok "Packages installed"
} else {
    Write-Ok "All required packages already present"
}

# ---- Create .cmd wrappers ----------------------------------------------------

Write-Step "Creating command wrappers in .venv\Scripts..."

$WRAPPERS = @{
    "camelot.cmd"        = "bin\camelot.py"
    "ai.cmd"             = "bin\camelot.py"
    "ks.cmd"             = "bin\knight_session.py"
    "knight-session.cmd" = "bin\knight_session.py"
}

foreach ($kv in $WRAPPERS.GetEnumerator()) {
    $wrapperPath = "$VENV_SCRIPTS\$($kv.Key)"
    $scriptPath  = "$REPO\$($kv.Value)"

    if ((Test-Path $wrapperPath) -and (-not $Force)) {
        Write-Ok "$($kv.Key) already exists"
        continue
    }

    $content = "@echo off`r`n`"$VENV_PYTHON`" -X utf8 `"$scriptPath`" %*`r`n"
    [System.IO.File]::WriteAllText($wrapperPath, $content, [System.Text.Encoding]::ASCII)
    Write-Ok "Created: $($kv.Key)"
}

# ---- Register PATH -----------------------------------------------------------

if (-not $Portable) {
    Write-Step "Registering PATH..."

    $added = Add-ToUserPath $VENV_SCRIPTS
    if ($added) {
        Write-Ok "Added to User PATH: $VENV_SCRIPTS"
        Write-Warn "Open a new terminal for PATH changes to take effect"
    } else {
        Write-Ok "Already in PATH: $VENV_SCRIPTS"
    }

    $existing = [System.Environment]::GetEnvironmentVariable("CAMELOT_OS_HOME","User")
    if ($existing -ne $REPO) {
        [System.Environment]::SetEnvironmentVariable("CAMELOT_OS_HOME", $REPO, "User")
        $env:CAMELOT_OS_HOME = $REPO
        Write-Ok "Set CAMELOT_OS_HOME = $REPO"
    }
}

# ---- PowerShell profile ------------------------------------------------------

if ((-not $NoProfile) -and (-not $Portable)) {
    Write-Step "Configuring PowerShell profile..."

    $profilePath = $PROFILE.CurrentUserAllHosts
    if (-not $profilePath) { $profilePath = "$HOME\Documents\PowerShell\profile.ps1" }

    $profileDir = Split-Path -Parent $profilePath
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }

    $PROFILE_BLOCK = @"

# ---- CAMELOT-OS Integration (WARP_GATE v$WARP_VERSION) -----------------------
`$env:CAMELOT_OS_HOME = "$REPO"
if (`$env:PATH -notlike "*$VENV_SCRIPTS*") {
    `$env:PATH = "$VENV_SCRIPTS;" + `$env:PATH
}
Set-Alias -Name ai -Value camelot -ErrorAction SilentlyContinue
# Type 'camelot' to warp into Camelot-OS
# -------------------------------------------------------------------------------
"@

    $currentProfile = ""
    if (Test-Path $profilePath) {
        $currentProfile = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
    }

    if ($currentProfile -notlike "*CAMELOT-OS Integration*") {
        Add-Content -Path $profilePath -Value $PROFILE_BLOCK -Encoding UTF8
        Write-Ok "Profile updated: $profilePath"
    } else {
        Write-Ok "Profile already contains Camelot-OS block"
    }
}

# ---- Run camelot configure ---------------------------------------------------

if (-not $NoConfigure) {
    Write-Step "Running auto-configuration..."
    Write-Host ""
    try {
        & $VENV_PYTHON -X utf8 "$REPO\bin\camelot.py" configure
    } catch {
        Write-Warn "Configure step had errors (non-fatal): $_"
    }
}

# ---- Done --------------------------------------------------------------------

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Green
Write-Host "   CAMELOT-OS installation complete!" -ForegroundColor Green
Write-Host "  ============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Commands available:" -ForegroundColor White
Write-Host "    camelot          warp into Camelot-OS REPL" -ForegroundColor Cyan
Write-Host "    camelot status   probe all services" -ForegroundColor Cyan
Write-Host "    ai               alias for camelot" -ForegroundColor Cyan
Write-Host "    ks               direct knight-session REPL" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Open a new terminal, then type: camelot" -ForegroundColor Yellow
Write-Host ""
