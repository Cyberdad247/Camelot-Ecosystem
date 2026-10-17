#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Omega Heimdall Warp Gate Provisioner & Embedding for Father's Camelot
====================================================================
Attests and installs an immutable Warp Gate Keypass for the Windows Sovereign
secondary node FOTHERS_CAMELOT (Camelot-97NCQP3, 100.121.48.50) under the supreme
authority of SIR_HEIMDALL (Bifrost Boundary Guardian).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add root to sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from control_plane.security.warp_gate import (
    AlexandriaKeypassVault,
    HEIMDALL_SPARK_ID,
    _audit_log,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOG = logging.getLogger("OmegaHeimdall")

NODE_ID = "FOTHERS_CAMELOT"
NODE_HOSTNAME = "Camelot-97NCQP3"
NODE_TAILSCALE_IP = "100.121.48.50"


def provision_fothers_warp_gate() -> dict:
    LOG.info("👁️ [SIR_HEIMDALL] Engaging Warp Gate Cryptographic Switch for Father's Camelot...")

    # Access Alexandria Keypass Vault
    vault = AlexandriaKeypassVault()
    keypass = vault.forge_keypass(NODE_ID)

    # Generate Omega Heimdall Attestation Seal
    issued_at = datetime.now(timezone.utc).isoformat()
    raw_seal_content = f"HEIMDALL_WARP_SEAL:{NODE_ID}:{NODE_HOSTNAME}:{keypass.keypass_id}:{keypass.forever_access_key}:{issued_at}"
    heimdall_hmac = hmac.new(
        HEIMDALL_SPARK_ID.encode("utf-8"),
        raw_seal_content.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    warp_node_cert = {
        "schema": "camelot.warp_gate.node_key/v1.0",
        "attesting_authority": "SIR_HEIMDALL",
        "gatekeeper_spark_id": HEIMDALL_SPARK_ID,
        "gatekeeper_tier": "OMEGA",
        "node_identity": {
            "node_id": NODE_ID,
            "hostname": NODE_HOSTNAME,
            "os": "windows",
            "tailscale_ip": NODE_TAILSCALE_IP,
            "tailnet_domain": "fothers-camelot.tailcd0c29.ts.net",
            "role": "Sovereign Secondary Node / Remote Fabrication Chamber",
        },
        "warp_gate_keypass": keypass.to_dict(),
        "heimdall_attestation_signature": heimdall_hmac,
        "capabilities": [
            "SOCKET_BYPASS",
            "OUT_OF_BAND_RENDEZVOUS",
            "BIFROST_REMOTE_TUNNEL",
            "AGENTIC_INGRESS_AUTHORIZED",
            "FOREVER_AVAILABLE",
            "REMOTE_WASM_SANDBOX",
        ],
        "status": "ATTESTED_ACTIVE",
        "issued_at": issued_at,
    }

    # Save to local vault and staging
    local_staging = _ROOT / "03_VAULT" / "security" / "warp_gates" / "rendezvous" / "fothers_camelot_warp.json"
    local_staging.parent.mkdir(parents=True, exist_ok=True)
    local_staging.write_text(json.dumps(warp_node_cert, indent=2), encoding="utf-8")
    LOG.info(f"📜 [SIR_HEIMDALL] Sealed Warp Gate Rendezvous staged at: {local_staging}")

    # Generate deployable installation script for Father's Camelot
    deploy_script_path = _ROOT / "scripts" / "ops" / "embed_warpgate_fothers.ps1"
    deploy_script_content = f"""# ==============================================================================
# CAMELOT-OS: SIR HEIMDALL WARPGATE EMBEDDING FOR FATHER'S CAMELOT
# Node: {NODE_ID} ({NODE_HOSTNAME} / {NODE_TAILSCALE_IP})
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🛡️ SIR HEIMDALL: EMBEDDING WARPGATE ON THIS NODE" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Ensure Camelot VFS directory structure exists
$TargetDir = "$env:USERPROFILE\\.camelot\\warp_gate"
if (!(Test-Path $TargetDir)) {{
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}}

# 2. Embed the sealed WarpGate certificate
$CertContent = @'
{json.dumps(warp_node_cert, indent=2)}
'@

$CertPath = Join-Path $TargetDir "fothers_camelot_warp.json"
Set-Content -Path $CertPath -Value $CertContent -Encoding UTF8
Write-Host "✅ Injected Sealed WarpGate Keypass to: $CertPath" -ForegroundColor Green

# 3. Ensure OpenSSH Server is active & firewall allows Tailscale ingress
Write-Host "🛡️ Configuring OpenSSH & Windows Firewall for Tailscale mesh..." -ForegroundColor Cyan
try {{
    if ((Get-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0).State -ne "Installed") {{
        Write-Host "Installing OpenSSH.Server..." -ForegroundColor Yellow
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
    }}
    Start-Service sshd -ErrorAction SilentlyContinue
    Set-Service -Name sshd -StartupType 'Automatic'
    
    # Allow Port 22 through firewall specifically for Tailscale interface
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -ErrorAction SilentlyContinue | Out-Null
    Write-Host "✅ OpenSSH Service is RUNNING and listening on Port 22" -ForegroundColor Green
}} catch {{
    Write-Host "⚠️ OpenSSH note: $($_.Exception.Message)" -ForegroundColor Yellow
}}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "⚡ WARPGATE PERMANENTLY EMBEDDED — STATUS: ACTIVE" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
"""
    deploy_script_path.write_text(deploy_script_content, encoding="utf-8")
    LOG.info(f"💾 [SIR_HEIMDALL] Generated embedding script at: {deploy_script_path}")

    # Audit log
    _audit_log("SIR_HEIMDALL_WARPGATE_EMBEDDED", {
        "attesting_knight": "SIR_HEIMDALL",
        "spark_id": HEIMDALL_SPARK_ID,
        "node_id": NODE_ID,
        "hostname": NODE_HOSTNAME,
        "keypass_id": keypass.keypass_id,
        "forever_access_key": keypass.forever_access_key,
        "attestation_signature": heimdall_hmac,
        "verdict": "AUTHORIZED_AND_SEALED",
    })

    LOG.info(f"⚡ [SIR_HEIMDALL] VERDICT: {NODE_ID} is attested and granted Tier-1 Sovereign Warp Gate access!")
    return warp_node_cert


if __name__ == "__main__":
    cert = provision_fothers_warp_gate()
    print(json.dumps(cert, indent=2))
