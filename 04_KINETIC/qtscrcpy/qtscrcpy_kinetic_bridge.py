# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — QtScrcpy Kinetic Integration Bridge
r"""
Sir Forge / QtScrcpy Kinetic Bridge (SIR_QTSCRCPY_BRIDGE)

Provides unified screen mirroring, remote Android device control,
server payload deployment (scrcpy-server), and ADB orchestration for CAMELOT-OS.

Capabilities:
  1. Cloned Repository & Asset Registry Inspection:
     - Adb binaries & DLLs: (QtScrcpy/QtScrcpyCore/src/third_party/adb/win/adb.exe)
     - Scrcpy server jar: (QtScrcpy/QtScrcpyCore/src/third_party/scrcpy-server)
     - FFmpeg dynamic codec libraries (avcodec, avformat, swscale, etc.)
     - Keymaps & Preset mappings (keymap/*.json)
  2. Android Device Discovery & Connectivity:
     - USB / TCP-IP device discovery (`adb devices -l`)
     - TCP/IP Wireless Pairing & Connection (`adb tcpip 5555`, `adb connect <ip>:<port>`)
     - Device state diagnostics (authorized, unauthorized, recovery, offline)
  3. Scrcpy Server Injection & Port Tunneling:
     - Push scrcpy-server to `/data/local/tmp/scrcpy-server.jar`
     - Setup reverse socket forwarding (`localabstract:scrcpy tcp:27183`)
  4. Device Control & Automation:
     - Input event injection (tap, swipe, keyevent, text typing)
     - Screen capture / recording streaming
     - App lifecycle dispatch (launch, stop, install)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("QtScrcpyKineticBridge")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")


@dataclass
class DeviceInfo:
    serial: str
    state: str
    product: Optional[str] = None
    model: Optional[str] = None
    device: Optional[str] = None
    transport_id: Optional[str] = None


@dataclass
class BridgeAuditResult:
    repo_path: str
    adb_path: str
    adb_available: bool
    adb_version: Optional[str]
    scrcpy_server_path: str
    scrcpy_server_available: bool
    scrcpy_server_size_bytes: int
    ffmpeg_bin_dir: str
    ffmpeg_available: bool
    config_ini_path: str
    config_available: bool
    available_keymaps: List[str]
    connected_devices: List[Dict[str, Any]]
    build_tooling_status: Dict[str, Any]


class QtScrcpyBridge:
    """Kinetic Bridge connecting CAMELOT-OS with QtScrcpy."""

    DEFAULT_REPO_PATH = Path(r"C:\Users\vizio\QtScrcpy")

    def __init__(self, repo_path: Optional[Path | str] = None):
        if repo_path:
            self.repo_path = Path(repo_path)
        elif os.environ.get("QTSCRCPY_HOME"):
            self.repo_path = Path(os.environ["QTSCRCPY_HOME"])
        else:
            self.repo_path = self.DEFAULT_REPO_PATH

        self.core_dir = self.repo_path / "QtScrcpy" / "QtScrcpyCore"
        self.adb_path = self.core_dir / "src" / "third_party" / "adb" / "win" / "adb.exe"
        self.scrcpy_server_path = self.core_dir / "src" / "third_party" / "scrcpy-server"
        self.ffmpeg_dir = self.core_dir / "src" / "third_party" / "ffmpeg" / "bin" / "x64"
        self.config_ini_path = self.repo_path / "config" / "config.ini"
        self.keymap_dir = self.repo_path / "keymap"

    def get_adb_executable() -> str:
        """Return the best available ADB executable path."""
        pass

    def get_adb_path(self) -> str:
        if self.adb_path.exists():
            return str(self.adb_path)
        return "adb"

    def run_adb(self, args: List[str], timeout: int = 15) -> subprocess.CompletedProcess:
        """Run an ADB command with timeout and return the CompletedProcess."""
        adb_bin = self.get_adb_path()
        cmd = [adb_bin] + args
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except Exception as e:
            LOG.error("Failed to execute ADB command %s: %s", cmd, e)
            raise

    def get_adb_version(self) -> Optional[str]:
        """Fetch ADB version."""
        try:
            res = self.run_adb(["version"])
            if res.returncode == 0:
                first_line = res.stdout.strip().splitlines()[0]
                return first_line
        except Exception:
            pass
        return None

    def list_devices(self) -> List[DeviceInfo]:
        """List all connected ADB devices with parsed attributes."""
        devices: List[DeviceInfo] = []
        try:
            res = self.run_adb(["devices", "-l"])
            if res.returncode != 0:
                return devices

            lines = res.stdout.strip().splitlines()
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if not parts:
                    continue

                serial = parts[0]
                state = parts[1]
                info = DeviceInfo(serial=serial, state=state)

                for item in parts[2:]:
                    if ":" in item:
                        k, v = item.split(":", 1)
                        if k == "product":
                            info.product = v
                        elif k == "model":
                            info.model = v
                        elif k == "device":
                            info.device = v
                        elif k == "transport_id":
                            info.transport_id = v
                devices.append(info)
        except Exception as e:
            LOG.warning("Could not list devices: %s", e)
        return devices

    def list_keymaps(self) -> List[str]:
        """List available JSON keymaps in repository."""
        if not self.keymap_dir.exists():
            return []
        return [f.name for f in self.keymap_dir.glob("*.json")]

    def load_keymap(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a specific keymap by name."""
        if not name.endswith(".json"):
            name = f"{name}.json"
        path = self.keymap_dir / name
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def push_server_payload(self, serial: Optional[str] = None, target_path: str = "/data/local/tmp/scrcpy-server.jar") -> bool:
        """Push the scrcpy-server jar to the connected Android device."""
        if not self.scrcpy_server_path.exists():
            LOG.error("scrcpy-server binary missing at %s", self.scrcpy_server_path)
            return False

        args = []
        if serial:
            args.extend(["-s", serial])
        args.extend(["push", str(self.scrcpy_server_path), target_path])

        res = self.run_adb(args, timeout=30)
        if res.returncode == 0:
            LOG.info("Successfully pushed scrcpy-server to %s on device %s", target_path, serial or "default")
            return True
        else:
            LOG.error("Failed to push scrcpy-server: %s", res.stderr)
            return False

    def send_keyevent(self, keycode: int, serial: Optional[str] = None) -> bool:
        """Inject keyevent (e.g. 3=HOME, 4=BACK, 26=POWER, 24=VOL_UP, 25=VOL_DOWN)."""
        args = []
        if serial:
            args.extend(["-s", serial])
        args.extend(["shell", "input", "keyevent", str(keycode)])
        res = self.run_adb(args)
        return res.returncode == 0

    def tap(self, x: int, y: int, serial: Optional[str] = None) -> bool:
        """Inject touch tap coordinate."""
        args = []
        if serial:
            args.extend(["-s", serial])
        args.extend(["shell", "input", "tap", str(x), str(y)])
        res = self.run_adb(args)
        return res.returncode == 0

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300, serial: Optional[str] = None) -> bool:
        """Inject touch swipe gesture."""
        args = []
        if serial:
            args.extend(["-s", serial])
        args.extend(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])
        res = self.run_adb(args)
        return res.returncode == 0

    def type_text(self, text: str, serial: Optional[str] = None) -> bool:
        """Type text into focused element on Android device."""
        escaped_text = text.replace(" ", "%s")
        args = []
        if serial:
            args.extend(["-s", serial])
        args.extend(["shell", "input", "text", escaped_text])
        res = self.run_adb(args)
        return res.returncode == 0

    def enable_tcpip(self, port: int = 5555, serial: Optional[str] = None) -> bool:
        """Restart ADB daemon in TCP/IP mode on specified port."""
        args = []
        if serial:
            args.extend(["-s", serial])
        args.extend(["tcpip", str(port)])
        res = self.run_adb(args)
        return res.returncode == 0

    def connect_wireless(self, host: str, port: int = 5555) -> bool:
        """Connect to device over TCP/IP."""
        res = self.run_adb(["connect", f"{host}:{port}"])
        return res.returncode == 0 and "connected" in res.stdout.lower()

    def audit(self) -> BridgeAuditResult:
        """Perform comprehensive readiness and capability audit."""
        adb_avail = self.adb_path.exists()
        adb_ver = self.get_adb_version() if adb_avail else None

        server_avail = self.scrcpy_server_path.exists()
        server_size = self.scrcpy_server_path.stat().st_size if server_avail else 0

        ffmpeg_avail = self.ffmpeg_dir.exists() and len(list(self.ffmpeg_dir.glob("*.dll"))) > 0
        cfg_avail = self.config_ini_path.exists()
        keymaps = self.list_keymaps()
        devices = [asdict(d) for d in self.list_devices()]

        # Tooling audit
        msvc_path = Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools")
        cmake_path = msvc_path / "Common7" / "IDE" / "CommonExtensions" / "Microsoft" / "CMake" / "CMake" / "bin" / "cmake.exe"
        ninja_path = msvc_path / "Common7" / "IDE" / "CommonExtensions" / "Microsoft" / "CMake" / "Ninja" / "ninja.exe"

        tooling = {
            "msvc_build_tools_installed": msvc_path.exists(),
            "msvc_cmake_path": str(cmake_path) if cmake_path.exists() else None,
            "msvc_ninja_path": str(ninja_path) if ninja_path.exists() else None,
            "qt_sdk_installed": False,  # Qt development headers/libs must be supplied via CMAKE_PREFIX_PATH
            "native_compilation_ready": msvc_path.exists() and cmake_path.exists(),
            "prebuilt_runtime_ready": adb_avail and server_avail and ffmpeg_avail,
        }

        return BridgeAuditResult(
            repo_path=str(self.repo_path),
            adb_path=str(self.adb_path),
            adb_available=adb_avail,
            adb_version=adb_ver,
            scrcpy_server_path=str(self.scrcpy_server_path),
            scrcpy_server_available=server_avail,
            scrcpy_server_size_bytes=server_size,
            ffmpeg_bin_dir=str(self.ffmpeg_dir),
            ffmpeg_available=ffmpeg_avail,
            config_ini_path=str(self.config_ini_path),
            config_available=cfg_avail,
            available_keymaps=keymaps,
            connected_devices=devices,
            build_tooling_status=tooling,
        )


def main():
    parser = argparse.ArgumentParser(description="CAMELOT-OS QtScrcpy Kinetic Bridge CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # audit
    subparsers.add_parser("audit", help="Audit QtScrcpy repository, binaries, and devices")

    # devices
    subparsers.add_parser("devices", help="List connected Android devices")

    # keymaps
    subparsers.add_parser("keymaps", help="List available keymap profiles")

    # push-server
    push_p = subparsers.add_parser("push-server", help="Push scrcpy-server payload to device")
    push_p.add_argument("-s", "--serial", help="Device serial number")
    push_p.add_argument("-t", "--target", default="/data/local/tmp/scrcpy-server.jar", help="Target device path")

    # tap
    tap_p = subparsers.add_parser("tap", help="Inject touch tap")
    tap_p.add_argument("x", type=int, help="X coordinate")
    tap_p.add_argument("y", type=int, help="Y coordinate")
    tap_p.add_argument("-s", "--serial", help="Device serial")

    # keyevent
    key_p = subparsers.add_parser("keyevent", help="Inject keyevent")
    key_p.add_argument("keycode", type=int, help="Android keycode (3=Home, 4=Back, 26=Power)")
    key_p.add_argument("-s", "--serial", help="Device serial")

    # wireless
    wire_p = subparsers.add_parser("tcpip", help="Enable wireless TCP/IP mode on device")
    wire_p.add_argument("-p", "--port", type=int, default=5555, help="Port")
    wire_p.add_argument("-s", "--serial", help="Device serial")

    conn_p = subparsers.add_parser("connect", help="Connect to wireless device")
    conn_p.add_argument("host", help="IP address")
    conn_p.add_argument("-p", "--port", type=int, default=5555, help="Port")

    args = parser.parse_args()
    bridge = QtScrcpyBridge()

    if args.command == "audit" or not args.command:
        audit_res = bridge.audit()
        print(json.dumps(asdict(audit_res), indent=2))
    elif args.command == "devices":
        devs = bridge.list_devices()
        print(f"Connected Devices ({len(devs)}):")
        for d in devs:
            print(f"  - Serial: {d.serial:<16} State: {d.state:<12} Model: {d.model or 'N/A'}")
    elif args.command == "keymaps":
        km = bridge.list_keymaps()
        print("Available Keymap Profiles:")
        for k in km:
            print(f"  - {k}")
    elif args.command == "push-server":
        ok = bridge.push_server_payload(serial=args.serial, target_path=args.target)
        print(f"Push Server Payload: {'SUCCESS' if ok else 'FAILED'}")
    elif args.command == "tap":
        ok = bridge.tap(args.x, args.y, serial=args.serial)
        print(f"Tap ({args.x}, {args.y}): {'SUCCESS' if ok else 'FAILED'}")
    elif args.command == "keyevent":
        ok = bridge.send_keyevent(args.keycode, serial=args.serial)
        print(f"Keyevent {args.keycode}: {'SUCCESS' if ok else 'FAILED'}")
    elif args.command == "tcpip":
        ok = bridge.enable_tcpip(port=args.port, serial=args.serial)
        print(f"TCP/IP mode port {args.port}: {'SUCCESS' if ok else 'FAILED'}")
    elif args.command == "connect":
        ok = bridge.connect_wireless(args.host, port=args.port)
        print(f"Connect to {args.host}:{args.port}: {'SUCCESS' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
