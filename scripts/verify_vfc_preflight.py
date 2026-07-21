#!/usr/bin/env python3
"""Fail-closed preflight for the Camelot Voice-First Cartridge."""

from __future__ import annotations

import ctypes
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIN_FREE_MB = 800.0
MAX_USED_MB = 7.2 * 1024


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def memory_mb() -> tuple[float, float, float]:
    if os.name != "nt":
        page_size = os.sysconf("SC_PAGE_SIZE")
        total = os.sysconf("SC_PHYS_PAGES") * page_size
        free = os.sysconf("SC_AVPHYS_PAGES") * page_size
    else:
        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise ctypes.WinError()
        total = status.ullTotalPhys
        free = status.ullAvailPhys
    scale = 1024 * 1024
    total_mb = total / scale
    free_mb = free / scale
    return total_mb, free_mb, total_mb - free_mb


REQUIRED_MARKERS = {
    "docs/protocols/pre-flight.md": ["pre-flight"],
    "02_FORGE/packages/voice-first-runtime/src/voice-first-runtime.ts": [
        "AudioWorkletNode",
        "shared-ring",
        "message-port",
    ],
    "02_FORGE/packages/voice-first-runtime/src/shared-pcm-ring.ts": ["SharedArrayBuffer"],
    "02_FORGE/apps/pwa-cockpit/public/voice-capture.worklet.js": ["camelot-voice-capture"],
    "02_FORGE/apps/pwa-cockpit/src/app/api/voice/frames/route.ts": [
        "MAX_FRAME_BYTES = 3_200",
        "voice.use",
        "127.0.0.1",
    ],
    "02_FORGE/apps/pwa-cockpit/src/cartridges/interphase/interphase-cartridge.tsx": [
        "useVoiceFirstRuntime",
        "Start capture",
    ],
    "02_FORGE/KINETIC_ARMORY/omnivoice-router/omnivoice-router.ts": [
        "/ingest_pcm",
        "isLoopback",
        'server.listen(PORT, "127.0.0.1"',
    ],
    "control_plane/forge_law.py": ["Forge"],
    "control_plane/worker.py": [
        "audio_path.relative_to(audio_root)",
        "audio_path.unlink(missing_ok=True)",
    ],
}


def main() -> int:
    checks: list[dict[str, object]] = []
    total_mb, free_mb, used_mb = memory_mb()
    resource_ok = free_mb >= MIN_FREE_MB and used_mb <= MAX_USED_MB
    checks.append(
        {
            "name": "resource_gate",
            "ok": resource_ok,
            "total_mb": round(total_mb, 1),
            "free_mb": round(free_mb, 1),
            "used_mb": round(used_mb, 1),
            "minimum_free_mb": MIN_FREE_MB,
            "maximum_used_mb": MAX_USED_MB,
        }
    )

    for relative, markers in REQUIRED_MARKERS.items():
        path = ROOT / relative
        missing: list[str] = []
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace")
            missing = [marker for marker in markers if marker not in content]
        checks.append(
            {
                "name": relative,
                "ok": path.is_file() and not missing,
                "missing_markers": missing,
            }
        )

    architecture_ok = all(bool(check["ok"]) for check in checks[1:])
    result = {
        "pulse": "VFC_PREFLIGHT",
        "decision": "GO" if resource_ok and architecture_ok else "NO-GO",
        "resource_ok": resource_ok,
        "architecture_ok": architecture_ok,
        "checks": checks,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["decision"] == "GO" else 1


if __name__ == "__main__":
    sys.exit(main())
