#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Omega Heimdall Warp Key Provisioner for Mobile Hardware
======================================================
Attests and installs an immutable Warp Gate Keypass directly onto the target
Samsung Galaxy S26 Ultra (SM-S948U) under the supreme authority of OMEGA_HEIMDALL.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
import time
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

TARGET_ADB_SERIALS = ["192.168.88.2:5555", "R3GL2009ZCH"]


def get_active_adb_target() -> str:
    """Finds the active, authorized ADB target."""
    for target in TARGET_ADB_SERIALS:
        res = subprocess.run(
            ["adb", "-s", target, "get-state"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and "device" in res.stdout:
            return target
    raise RuntimeError("No active authorized ADB device found on targets: " + str(TARGET_ADB_SERIALS))


def query_device_prop(serial: str, prop: str) -> str:
    res = subprocess.run(
        ["adb", "-s", serial, "shell", "getprop", prop],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return res.stdout.strip()


def install_warp_key_to_device() -> dict:
    LOG.info("👁️ [OMEGA_HEIMDALL] Activating Gatekeeper of the Bifrost & Thresholds...")
    target_serial = get_active_adb_target()
    LOG.info(f"⚡ [OMEGA_HEIMDALL] Locked target device link via ADB: {target_serial}")

    # Query device hardware knots
    model = query_device_prop(target_serial, "ro.product.model") or "SM-S948U"
    soc = query_device_prop(target_serial, "ro.soc.model") or "SM8850"
    cpu_abi = query_device_prop(target_serial, "ro.product.cpu.abi") or "arm64-v8a"
    serial_no = query_device_prop(target_serial, "ro.serialno") or "R3GL2009ZCH"

    LOG.info(f"📱 [OMEGA_HEIMDALL] Hardware Node: {model} (SoC: {soc}, ABI: {cpu_abi}, S/N: {serial_no})")

    # Access Alexandria Keypass Vault
    vault = AlexandriaKeypassVault()
    keypass = vault.forge_keypass("EXCALIBUR_MOBILE")

    # Generate Omega Heimdall Attestation Seal
    issued_at = datetime.now(timezone.utc).isoformat()
    raw_seal_content = f"HEIMDALL_WARP_SEAL:{model}:{serial_no}:{keypass.keypass_id}:{keypass.forever_access_key}:{issued_at}"
    heimdall_hmac = hmac.new(
        HEIMDALL_SPARK_ID.encode("utf-8"),
        raw_seal_content.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    warp_device_cert = {
        "schema": "camelot.warp_gate.device_key/v1.0",
        "attesting_authority": "OMEGA_HEIMDALL",
        "gatekeeper_spark_id": HEIMDALL_SPARK_ID,
        "gatekeeper_tier": "OMEGA",
        "device_identity": {
            "model": model,
            "soc": soc,
            "cpu_abi": cpu_abi,
            "serial_no": serial_no,
            "tailscale_ip": "100.106.246.126",
            "wifi_ip": "192.168.88.2",
            "adb_endpoint": "5555",
        },
        "warp_gate_keypass": keypass.to_dict(),
        "heimdall_attestation_signature": heimdall_hmac,
        "capabilities": [
            "SOCKET_BYPASS",
            "OUT_OF_BAND_RENDEZVOUS",
            "DIRECT_KGSL_VULKAN_120HZ",
            "AGENTIC_INGRESS_AUTHORIZED",
            "FOREVER_AVAILABLE",
        ],
        "status": "ATTESTED_ACTIVE",
        "issued_at": issued_at,
    }

    # Save to local staging
    local_staging = _ROOT / "03_VAULT" / "runtime_state" / "excalibur_device_warp_key.json"
    local_staging.parent.mkdir(parents=True, exist_ok=True)
    local_staging.write_text(json.dumps(warp_device_cert, indent=2), encoding="utf-8")
    LOG.info(f"📜 [OMEGA_HEIMDALL] Sealed Device Warp Key staged at: {local_staging}")

    # Push to device: /data/local/tmp and /sdcard/Download
    device_tmp_path = "/data/local/tmp/warp_gate_keypass.json"
    device_sdcard_path = "/sdcard/Download/warp_gate_keypass.json"

    subprocess.run(
        ["adb", "-s", target_serial, "push", str(local_staging), device_tmp_path],
        check=True,
        capture_output=True,
    )
    LOG.info(f"🔑 [OMEGA_HEIMDALL] Injected Warp Key to device: {device_tmp_path}")

    subprocess.run(
        ["adb", "-s", target_serial, "push", str(local_staging), device_sdcard_path],
        check=True,
        capture_output=True,
    )
    LOG.info(f"📂 [OMEGA_HEIMDALL] Mirrored Warp Key to shared storage: {device_sdcard_path}")

    # Read back and verify hash integrity
    read_back = subprocess.run(
        ["adb", "-s", target_serial, "shell", "cat", device_tmp_path],
        capture_output=True,
        text=True,
        check=True,
    )
    verified_data = json.loads(read_back.stdout)
    assert verified_data["heimdall_attestation_signature"] == heimdall_hmac, "Attestation signature mismatch on device!"

    # Log to permanent audit ledger
    _audit_log("OMEGA_HEIMDALL_DEVICE_WARP_KEY_INSTALLED", {
        "attesting_knight": "OMEGA_HEIMDALL",
        "spark_id": HEIMDALL_SPARK_ID,
        "device_model": model,
        "device_serial": serial_no,
        "keypass_id": keypass.keypass_id,
        "forever_access_key": keypass.forever_access_key,
        "attestation_signature": heimdall_hmac,
        "device_tmp_path": device_tmp_path,
        "verdict": "AUTHORIZED_AND_SEALED",
    })

    LOG.info("🛡️ [OMEGA_HEIMDALL] VERDICT: Device SM-S948U is permanently keyed and attested into Camelot-OS!")
    return warp_device_cert


if __name__ == "__main__":
    cert = install_warp_key_to_device()
    print(json.dumps(cert, indent=2))
