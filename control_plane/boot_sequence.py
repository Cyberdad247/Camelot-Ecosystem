"""Re-usable boot sequence logic for Camelot-OS."""

from __future__ import annotations

import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ANSI escape
_C = {"g": "\033[92m", "y": "\033[93m", "r": "\033[91m", "c": "\033[96m",
      "m": "\033[95m", "b": "\033[94m", "w": "\033[97m", "d": "\033[2m",
      "x": "\033[0m", "B": "\033[1m"}

_STRIP_RICH = re.compile(r"\[/?[a-zA-Z_ ]*\]")

def _strip(msg: str) -> str:
    return _STRIP_RICH.sub("", msg).strip()

def _detect_home() -> Path:
    env = os.environ.get("CAMELOT_OS_HOME")
    if env and Path(env).is_dir():
        return Path(env)
    candidates = [
        Path.home() / "CAMELOT_OS",
        Path("C:/Users/vizio/CAMELOT_OS"),
        Path(__file__).resolve().parent.parent,
    ]
    for c in candidates:
        if (c / "03_VAULT" / "training" / "configs" / "hud.py").exists():
            return c
    return Path(__file__).resolve().parent.parent

def _detect_venv_python(home: Path) -> Path:
    env = os.environ.get("CAMELOT_VENV")
    if env and Path(env).exists():
        return Path(env)
    system = platform.system()
    if system == "Windows":
        venv_py = home / ".venv_camelot" / "Scripts" / "python.exe"
    else:
        venv_py = home / ".venv_camelot" / "bin" / "python"
    if venv_py.exists():
        return venv_py
    return Path(sys.executable)

def boot_harness(home: Path):
    harness_py = home / "control_plane" / "harness.py"
    pid_file   = home / "logs" / "harness.pid"
    if not harness_py.exists():
        return False, "harness.py not found — skipped"

    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Improved check for Windows/Unix
            if platform.system() == "Windows":
                import ctypes
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
                if h:
                    ctypes.windll.kernel32.CloseHandle(h)
                    return True, f"Sovereign Harness already running PID={pid}"
                else:
                    raise OSError("Process not found")
            else:
                os.kill(pid, 0)
            return True, f"Sovereign Harness already running PID={pid}"
        except (OSError, ValueError, SystemError):
            pid_file.unlink(missing_ok=True)

    venv_py = _detect_venv_python(home)
    py = str(venv_py) if venv_py.exists() else sys.executable
    kwargs: dict = {"cwd": str(home)}
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    else:
        kwargs["start_new_session"] = True

    try:
        proc = subprocess.Popen([py, str(harness_py)], **kwargs)
        time.sleep(1.2)
        if proc.poll() is not None:
            return False, f"Harness exited immediately (code {proc.returncode})"
        return True, f"Sovereign Harness spawned PID={proc.pid}"
    except Exception as e:
        return False, f"Harness spawn failed: {type(e).__name__}: {e}"

def boot_telemetry(home: Path):
    binary = home / "bin" / "vizion-telemetry.exe"
    if not binary.exists():
        binary = home / "01_KERNEL" / "senses" / "vizion-telemetry" / "vizion-telemetry.exe"
    if not binary.exists():
        return False, "vizion-telemetry.exe not found"

    kwargs: dict = dict(cwd=str(home))
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    else:
        kwargs["start_new_session"] = True

    try:
        proc = subprocess.Popen([str(binary)], **kwargs)
        time.sleep(0.5)
        if proc.poll() is not None:
            return False, f"exited immediately (code {proc.returncode})"
        return True, f"PID {proc.pid} — terminal TUI active"
    except Exception as e:
        return False, f"launch failed: {e}"

def run_boot(home: Path, quick: bool = False) -> dict:
    hud_path = home / "03_VAULT" / "training" / "configs" / "hud.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("hud", hud_path)
    hud = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hud)
    
    phases = [
        ("CLIProxyAPI   :8080", hud._boot_cliproxy),
        ("Defense Grid       ", hud._boot_defense_grid),
        ("Kinetic Edge  :3001", hud._boot_kinetic_edge),
        ("Cloud Brain   (RPC)", hud._boot_cloud_brain),
        ("Vizion Telemetry   ", lambda: boot_telemetry(home)),
        ("Sovereign Harness  ", lambda: boot_harness(home)),
    ]
    results = {}
    t_total = time.perf_counter()
    for label, fn in phases:
        t0 = time.perf_counter()
        try:
            _, msg = fn()
            ok = not any(k in msg for k in ("[red]", "failed", "unreachable", "[yellow]"))
            clean = _strip(msg)
        except Exception as e:
            ok, clean = False, f"exception: {type(e).__name__}: {e}"
        dt = (time.perf_counter() - t0) * 1000
        results[label.strip()] = {"ok": ok, "msg": clean, "ms": round(dt)}
        if not quick:
            glyph = f"{_C['g']}✅{_C['x']}" if ok else f"{_C['y']}⚠ {_C['x']}"
            print(f"  {glyph} {_C['B']}{label}{_C['x']}  {clean}  {_C['d']}({dt:.0f}ms){_C['x']}")
    results["_total_ms"] = round((time.perf_counter() - t_total) * 1000)
    return results
