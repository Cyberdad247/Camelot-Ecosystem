# CAMELOT-OS Release Builder (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "[⚡] Initiating Cargo Release Build for Camelot-Ecosystem..." -ForegroundColor Cyan
cargo build --release -p camelot-kernel ; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
cargo build --release -p camelot-spawner ; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
cargo build --release -p camelot-transport ; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
cargo build --release -p camelot-runtime ; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[🏆] Build successful. Binaries staged in target/release/." -ForegroundColor Green
