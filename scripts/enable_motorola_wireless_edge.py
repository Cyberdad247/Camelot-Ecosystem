#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Motorola Moto G Power 5G (2024) Wireless Debugging & Edge Bridge Activator
==========================================================================
Enables cable-free wireless operation for the Camelot-OS Edge Node over
local Wi-Fi (192.168.1.68:5555) or Tailscale Mesh (100.89.129.105:5555).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from control_plane.infra.mesh_topology import ip_of

DEFAULT_ADB_PATHS = [
    Path(r"C:\Users\vizio\AppData\Local\CamelotTools\QtScrcpy-v4.1.1\QtScrcpy-win-x64-v4.1.1\adb.exe"),
    Path(r"C:\Users\vizio\AppData\Local\CamelotTools\platform-tools\adb.exe"),
    Path(r"C:\Users\vizio\QtScrcpy\QtScrcpy\QtScrcpyCore\src\third_party\adb\win\adb.exe"),
]

MOTO_SERIAL = "ZY22L3K36P"
MOTO_WIFI_IP = "192.168.1.68"
MOTO_TAILSCALE_IP = ip_of("motorola_moto_g_power")
WIRELESS_PORT = 5555


def get_adb_path() -> Path:
    for p in DEFAULT_ADB_PATHS:
        if p.exists():
            return p
    return Path("adb")


def get_env() -> dict[str, str]:
    env = dict(os.environ)
    adbkey_path = Path.home() / ".android" / "adbkey"
    if adbkey_path.exists():
        env["ADB_VENDOR_KEYS"] = str(adbkey_path)
    return env


def run_adb(args: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    adb_bin = str(get_adb_path())
    return subprocess.run(
        [adb_bin] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=get_env(),
    )


def enable_wireless_debugging() -> bool:
    print("=" * 70)
    print("📱 MOTOROLA MOTO G POWER 5G — WIRELESS DEBUGGING SETUP")
    print("=" * 70)

    # 1. Check attached devices
    res = run_adb(["devices", "-l"])
    print(f"[ADB Devices Output]\n{res.stdout.strip()}\n")

    is_usb_attached = MOTO_SERIAL in res.stdout
    is_already_wireless = f"{MOTO_WIFI_IP}:{WIRELESS_PORT}" in res.stdout or f"{MOTO_TAILSCALE_IP}:{WIRELESS_PORT}" in res.stdout

    if is_already_wireless:
        print("✅ Device is ALREADY connected wirelessly!")
        print("🎉 Cable is not required. Edge node is operating untethered.")
        return True

    if is_usb_attached:
        print(f"🔌 Device {MOTO_SERIAL} detected via USB.")
        print(f"⚡ Setting TCP/IP port {WIRELESS_PORT}...")
        res_tcp = run_adb(["-s", MOTO_SERIAL, "tcpip", str(WIRELESS_PORT)])
        print(res_tcp.stdout.strip())
        time.sleep(2)

    # 2. Attempt wireless connection via Wi-Fi IP
    print(f"📡 Attempting wireless connection to Wi-Fi IP {MOTO_WIFI_IP}:{WIRELESS_PORT}...")
    res_conn_wifi = run_adb(["connect", f"{MOTO_WIFI_IP}:{WIRELESS_PORT}"])
    print(res_conn_wifi.stdout.strip())

    if "connected to" in res_conn_wifi.stdout.lower():
        print(f"\n🎉 SUCCESS: Connected wirelessly to {MOTO_WIFI_IP}:{WIRELESS_PORT}!")
        print("⚡ You may now UNPLUG the USB cable. The node will remain connected.")
        return True

    # 3. Attempt wireless connection via Tailscale IP
    print(f"🌐 Attempting wireless connection to Tailscale IP {MOTO_TAILSCALE_IP}:{WIRELESS_PORT}...")
    try:
        res_conn_ts = run_adb(["connect", f"{MOTO_TAILSCALE_IP}:{WIRELESS_PORT}"], timeout=5)
        print(res_conn_ts.stdout.strip())
        if "connected to" in res_conn_ts.stdout.lower():
            print(f"\n🎉 SUCCESS: Connected wirelessly via Tailscale {MOTO_TAILSCALE_IP}:{WIRELESS_PORT}!")
            print("⚡ You may now UNPLUG the USB cable. The node will remain connected.")
            return True
    except subprocess.TimeoutExpired:
        print(f"⏱️ Tailscale IP connection timed out (Tailscale VPN may be idle on phone).")

    print("\n📱 NOTE FOR OPERATOR:")
    print("👉 Look at the Motorola Moto G Power 5G screen:")
    print("   Unlock the phone and check the prompt: 'Allow USB debugging?'")
    print("   Check 'Always allow from this computer' and tap 'Allow'.")
    print("   Then re-run this script or connect via QtScrcpy!")
    return False


if __name__ == "__main__":
    enable_wireless_debugging()
