<#
.SYNOPSIS
Bootstrap script for the Camelot HTMX Documentation Site (EVD-HTMX-SITE-001).

.DESCRIPTION
Initializes the local development environment, synchronizes dependencies,
verifies go:embed assets, runs the validation test suite, and launches 
the bare-metal server.
#>

$ErrorActionPreference = "Stop"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  CAMELOT WORLD_TREE: HTMX DOCS BOOTSTRAP SEQUENCE     " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Dependencies
Write-Host "[*] Verifying Go toolchain..." -ForegroundColor Magenta
if (!(Get-Command "go" -ErrorAction SilentlyContinue)) {
    Write-Error "FATAL: Go is not installed or not in PATH. Please install Go 1.21+."
    exit 1
}
$goVer = go version
Write-Host "    Found: $goVer"

# 2. Sync Modules
Write-Host "[*] Synchronizing Go modules (go mod tidy)..." -ForegroundColor Magenta
go mod tidy

# 3. Verify Asset Directories (Required for go:embed)
Write-Host "[*] Verifying go:embed virtual filesystem assets..." -ForegroundColor Magenta
$requiredDirs = @("docs", "static", "templates")
foreach ($dir in $requiredDirs) {
    if (!(Test-Path $dir)) {
        Write-Host "    [-] Missing required directory: $dir. Forging..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    } else {
        Write-Host "    [+] Directory attached: $dir/" -ForegroundColor Green
    }
}

# 4. Run Validation Suite (N110)
Write-Host "[*] Executing Gideon Verdict Validation Suite (N110)..." -ForegroundColor Magenta
go test ./...
if ($LASTEXITCODE -ne 0) {
    Write-Error "FATAL: Validation suite failed. Halting bootstrap sequence."
    exit 1
}
Write-Host "    [+] Validation Matrix Passed." -ForegroundColor Green

# 5. Build Bare-Metal Server
Write-Host "[*] Forging bare-metal executable (server.exe)..." -ForegroundColor Magenta
go build -o server.exe ./cmd/server
Write-Host "    [+] Executable compiled successfully." -ForegroundColor Green
Write-Host ""

# 6. Launch
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  BOOTSTRAP COMPLETE. LAUNCHING NEURAL LINK...         " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
.\server.exe
