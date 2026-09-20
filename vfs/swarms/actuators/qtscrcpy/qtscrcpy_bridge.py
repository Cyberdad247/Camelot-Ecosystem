# SPDX-License-Identifier: MIT
"""QtScrcpy Bridge Sentinel for Excalibur Command Center (S26 Ultra).

Wraps ADB and scrcpy command synthesis for low-latency visual ingress and touch control.
"""

from __future__ import annotations

import subprocess
from typing import Dict, Any


def get_excalibur_mirror_spec(
    device_ip: str = "100.106.246.126:5555",
    bitrate_mbps: int = 8,
    fps: int = 60,
) -> Dict[str, Any]:
    return {
        "device_ip": device_ip,
        "bitrate_mbps": bitrate_mbps,
        "fps": fps,
        "scrcpy_command": f"scrcpy -s {device_ip} --video-bit-rate {bitrate_mbps}M --max-fps {fps} --audio-codec=opus",
        "adb_connect_command": f"adb connect {device_ip}",
    }


def tap_excalibur(x: int, y: int, device_ip: str = "100.106.246.126:5555") -> str:
    cmd = ["adb", "-s", device_ip, "shell", "input", "tap", str(x), str(y)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return f"Tap ({x}, {y}) sent to {device_ip}. Exit: {res.returncode}"
    except Exception as e:
        return f"ADB dispatch error: {e}"


if __name__ == "__main__":
    print(get_excalibur_mirror_spec())
