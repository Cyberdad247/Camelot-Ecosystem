# Camelot-OS KBA Drone — rotate local drone secrets.
#
# Regenerates .drone_secrets.ps1 (gitignored) with two fresh CSPRNG values.
# Run this on the control plane when rotating, then distribute the SAME values
# to every peer:
#   - WEBHOOK_SECRET            -> apps/bifrost env + omni-router dispatch env
#                                 (control_plane/dispatch/bifrost_gateway.py signs
#                                  with it; apps/bifrost/src/server.ts verifies)
#   - CAMELOT_CARTRIDGE_HMAC_KEY -> cartridge signer env (02_FORGE/cartridge/cartridge_crypto.py)
#
# Usage:  powershell -ExecutionPolicy Bypass -File run_drone.keygen.ps1

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$outPath = Join-Path $scriptDir ".drone_secrets.ps1"

# Generate via Python's CSPRNG (secrets.token_hex) — same bit lengths as the
# original committed values (160-bit WEBHOOK_SECRET, 192-bit cartridge key).
$pyScript = @'
import secrets
print(secrets.token_hex(20))   # WEBHOOK_SECRET (40 hex chars)
print(secrets.token_hex(24))   # CAMELOT_CARTRIDGE_HMAC_KEY (48 hex chars)
'@

$generated = python -c $pyScript
if ($LASTEXITCODE -ne 0 -or $generated.Count -lt 2) {
    Write-Host "[FATAL] Could not generate secrets via python." -ForegroundColor Red
    exit 1
}

$webhook = $generated[0].Trim()
$hmac    = $generated[1].Trim()

$content = @"
# Local drone secrets - GENERATED $(Get-Date -Format 'yyyy-MM-dd') by run_drone.keygen.ps1
# DO NOT COMMIT. This file is gitignored.
`$env:WEBHOOK_SECRET            = "$webhook"
`$env:CAMELOT_CARTRIDGE_HMAC_KEY = "$hmac"
"@

Set-Content -LiteralPath $outPath -Value $content -Encoding ASCII
Write-Host "[OK] Rotated secrets written to $outPath" -ForegroundColor Green
Write-Host "[INFO] Distribute the SAME values to every peer (bifrost env, omni-router dispatch, cartridge signer)." -ForegroundColor Yellow
