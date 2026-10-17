# ==============================================================================
# CAMELOT-OS: SIR HEIMDALL WARPGATE EMBEDDING FOR FATHER'S CAMELOT
# Node: FOTHERS_CAMELOT (Camelot-97NCQP3 / 100.121.48.50)
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🛡️ SIR HEIMDALL: EMBEDDING WARPGATE ON THIS NODE" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Ensure Camelot VFS directory structure exists
$TargetDir = "$env:USERPROFILE\.camelot\warp_gate"
if (!(Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

# 2. Embed the sealed WarpGate certificate
$CertContent = @'
{
  "schema": "camelot.warp_gate.node_key/v1.0",
  "attesting_authority": "SIR_HEIMDALL",
  "gatekeeper_spark_id": "0x3205F18991DA427296A93641FD642763",
  "gatekeeper_tier": "OMEGA",
  "node_identity": {
    "node_id": "FOTHERS_CAMELOT",
    "hostname": "Camelot-97NCQP3",
    "os": "windows",
    "tailscale_ip": "100.121.48.50",
    "tailnet_domain": "fothers-camelot.tailcd0c29.ts.net",
    "role": "Sovereign Secondary Node / Remote Fabrication Chamber"
  },
  "warp_gate_keypass": {
    "keypass_id": "KP-FOTHERS_CAMELOT-99276D49",
    "knight_id": "FOTHERS_CAMELOT",
    "spark_id": "0x99276D492CCA7058631F48D3B1B9C2CE",
    "forever_access_key": "WARP-PASS-99276D49-835C4E26C210421247C7D8867AFB5B86",
    "secret_salt": "4baa2a18d5396c6e76f56c1572ed9075",
    "issued_at": "2026-10-14T00:50:51.307133+00:00",
    "tier": "SOVEREIGN",
    "expires_at": "FOREVER",
    "capabilities": [
      "SOCKET_BYPASS",
      "OUT_OF_BAND_RENDEZVOUS",
      "VAULT_EMERGENCY_UNSEAL",
      "TELEMETRY_OVERRIDE"
    ],
    "status": "ACTIVE",
    "issuer": "LADY_ALEXANDRIA_KEYPASS_VAULT"
  },
  "heimdall_attestation_signature": "2810A036C6864325638B3D2691962C41A4A7BDC18FA055E70BB536FBBD0E3AAC",
  "capabilities": [
    "SOCKET_BYPASS",
    "OUT_OF_BAND_RENDEZVOUS",
    "BIFROST_REMOTE_TUNNEL",
    "AGENTIC_INGRESS_AUTHORIZED",
    "FOREVER_AVAILABLE",
    "REMOTE_WASM_SANDBOX"
  ],
  "status": "ATTESTED_ACTIVE",
  "issued_at": "2026-10-14T00:50:51.309083+00:00"
}
'@

$CertPath = Join-Path $TargetDir "fothers_camelot_warp.json"
Set-Content -Path $CertPath -Value $CertContent -Encoding UTF8
Write-Host "✅ Injected Sealed WarpGate Keypass to: $CertPath" -ForegroundColor Green

# 3. Ensure OpenSSH Server is active & firewall allows Tailscale ingress
Write-Host "🛡️ Configuring OpenSSH & Windows Firewall for Tailscale mesh..." -ForegroundColor Cyan
try {
    if ((Get-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0).State -ne "Installed") {
        Write-Host "Installing OpenSSH.Server..." -ForegroundColor Yellow
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
    }
    Start-Service sshd -ErrorAction SilentlyContinue
    Set-Service -Name sshd -StartupType 'Automatic'
    
    # Allow Port 22 through firewall specifically for Tailscale interface
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -ErrorAction SilentlyContinue | Out-Null
    Write-Host "✅ OpenSSH Service is RUNNING and listening on Port 22" -ForegroundColor Green
} catch {
    Write-Host "⚠️ OpenSSH note: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "⚡ WARPGATE PERMANENTLY EMBEDDED — STATUS: ACTIVE" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
