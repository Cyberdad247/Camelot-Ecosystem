#!/usr/bin/env python3
"""
CAMELOT-OS Portable Installer — Zero Dependencies
WARP_GATE v1.0.0

Installs Camelot-OS using only Python standard library (no pip, no curl).
Works on Windows, Linux, macOS. Designed for thumbdrive deployment.

Usage:
    python install_portable.py                  # auto-detect everything
    python install_portable.py --portable       # no PATH writes, local config only
    python install_portable.py --no-configure   # skip auto-configure step
    python install_portable.py --home /path/to/CAMELOT_OS
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

CAMELOT_VERSION = "400.1.0"
WARP_VERSION    = "1.0.0"
MIN_PYTHON      = (3, 11)

# ── Output helpers ─────────────────────────────────────────────────────────────

IS_WIN  = platform.system() == "Windows"
BOLD    = "" if IS_WIN else "\033[1m"
GREEN   = "" if IS_WIN else "\033[0;32m"
YELLOW  = "" if IS_WIN else "\033[1;33m"
CYAN    = "" if IS_WIN else "\033[0;36m"
RED     = "" if IS_WIN else "\033[0;31m"
RESET   = "" if IS_WIN else "\033[0m"


def banner():
    print(f"\n{YELLOW}{BOLD}  ============================================{RESET}")
    print(f"{YELLOW}{BOLD}   CAMELOT-OS v{CAMELOT_VERSION}  //  WARP_GATE v{WARP_VERSION}{RESET}")
    print(f"{YELLOW}{BOLD}   Portable Python Installer{RESET}")
    print(f"{YELLOW}{BOLD}  ============================================{RESET}\n")

def step(msg: str):  print(f"\n{CYAN}{BOLD}  >>  {RESET}{msg}")
def ok(msg: str):    print(f"  {GREEN}[OK]{RESET} {msg}")
def warn(msg: str):  print(f"  {YELLOW}[!!]{RESET} {msg}")
def fail(msg: str):
    print(f"  {RED}[XX]{RESET} {msg}")
    sys.exit(1)


# ── Python version check ───────────────────────────────────────────────────────

def check_python():
    v = sys.version_info[:2]
    if v < MIN_PYTHON:
        fail(
            f"Python {'.'.join(map(str, MIN_PYTHON))}+ required. "
            f"Found: {'.'.join(map(str, v))}\n"
            "    Download: https://python.org/downloads"
        )
    ok(f"Python {sys.version.split()[0]}")
    return sys.executable


# ── Locate CAMELOT_OS root ─────────────────────────────────────────────────────

def find_repo(override: str | None = None) -> Path:
    candidates = []

    if override:
        candidates.append(Path(override))

    env_home = os.environ.get("CAMELOT_OS_HOME")
    if env_home:
        candidates.append(Path(env_home))

    # Relative to this script: script is in scripts/, repo is parent
    script_parent = Path(__file__).resolve().parent.parent
    candidates.append(script_parent)

    # Common locations
    home = Path.home()
    candidates += [
        home / "CAMELOT_OS",
        home / "projects" / "CAMELOT_OS",
        Path("C:/Users") / os.environ.get("USERNAME", "user") / "CAMELOT_OS",
    ]

    for p in candidates:
        if p.exists() and (p / "pyproject.toml").exists():
            return p

    fail(
        "CAMELOT_OS repository not found.\n"
        "    Clone it first: git clone https://github.com/your-org/CAMELOT_OS.git\n"
        "    Then run: python install_portable.py --home /path/to/CAMELOT_OS"
    )


# ── Virtual environment ────────────────────────────────────────────────────────

def ensure_venv(repo: Path, python_exe: str) -> tuple[Path, str]:
    venv_dir = repo / ".venv"

    if IS_WIN:
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_bin    = venv_dir / "Scripts"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_bin    = venv_dir / "bin"

    if venv_python.exists():
        ok(f"Existing .venv: {venv_dir}")
        return venv_bin, str(venv_python)

    step(f"Creating .venv at {venv_dir} ...")
    subprocess.run([python_exe, "-m", "venv", str(venv_dir)], check=True)

    if not venv_python.exists():
        fail(f"Failed to create .venv — check permissions on {repo}")

    ok(".venv created")
    return venv_bin, str(venv_python)


# ── Package installation ───────────────────────────────────────────────────────

MIN_PACKAGES = ["httpx", "rich", "psutil", "pyyaml"]

def install_packages(venv_python: str):
    step("Installing required packages...")

    missing = []
    for pkg in MIN_PACKAGES:
        mod = pkg.replace("-", "_")
        result = subprocess.run(
            [venv_python, "-c", f"import {mod}"],
            capture_output=True
        )
        if result.returncode != 0:
            missing.append(pkg)

    if not missing:
        ok("All required packages already present")
        return

    print(f"  Installing: {', '.join(missing)}")

    # Try uv first (faster), fall back to pip
    uv = shutil.which("uv")
    if uv:
        subprocess.run([uv, "pip", "install", "--python", venv_python] + missing, check=True)
    else:
        subprocess.run(
            [venv_python, "-m", "pip", "install", "--quiet"] + missing,
            check=True
        )
    ok("Packages installed")


# ── Command wrappers ───────────────────────────────────────────────────────────

def create_wrappers(repo: Path, venv_bin: Path, venv_python: str, force: bool = False):
    step("Creating command wrappers...")

    wrappers = {
        "camelot":        "bin/camelot.py",
        "ai":             "bin/camelot.py",
        "ks":             "bin/knight_session.py",
        "knight-session": "bin/knight_session.py",
    }

    for name, script_rel in wrappers.items():
        script_path = repo / script_rel

        if IS_WIN:
            dest = venv_bin / f"{name}.cmd"
            if dest.exists() and not force:
                ok(f"{name}.cmd already exists")
                continue
            content = f'@echo off\n"{venv_python}" -X utf8 "{script_path}" %*\n'
            dest.write_text(content, encoding="ascii")
        else:
            dest = venv_bin / name
            if dest.exists() and not force:
                ok(f"{name} already exists")
                continue
            content = f'#!/usr/bin/env bash\nexec "{venv_python}" -X utf8 "{script_path}" "$@"\n'
            dest.write_text(content, encoding="utf-8")
            dest.chmod(0o755)

        ok(f"Created: {dest.name}")


# ── PATH registration ──────────────────────────────────────────────────────────

def register_path(venv_bin: Path, repo: Path, portable: bool):
    if portable:
        warn("Portable mode — skipping PATH registration")
        return

    step("Registering PATH...")

    venv_bin_str = str(venv_bin)

    if IS_WIN:
        # Windows: set User-scope PATH via reg
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0, winreg.KEY_READ | winreg.KEY_WRITE
            )
            current, _ = winreg.QueryValueEx(key, "PATH")
            if venv_bin_str not in current:
                new_path = f"{current};{venv_bin_str}"
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                ok(f"Added to User PATH: {venv_bin_str}")
                warn("Open a new terminal for PATH changes to take effect")
            else:
                ok("Already in User PATH")

            # Also set CAMELOT_OS_HOME
            winreg.SetValueEx(key, "CAMELOT_OS_HOME", 0, winreg.REG_SZ, str(repo))
            winreg.CloseKey(key)
            ok(f"Set CAMELOT_OS_HOME = {repo}")
        except Exception as e:
            warn(f"Could not write registry PATH: {e}")
            warn(f"Manually add to PATH: {venv_bin_str}")
    else:
        # Unix: write to shell configs
        profile_block = (
            f"\n# ── CAMELOT-OS Integration (WARP_GATE v{WARP_VERSION}) ──────────────────────────\n"
            f'export CAMELOT_OS_HOME="{repo}"\n'
            f'export PATH="{venv_bin_str}:$PATH"\n'
            f"alias ai='camelot'\n"
            f"# Type 'camelot' to warp into Camelot-OS\n"
            f"# ─────────────────────────────────────────────────────────────────────────────\n"
        )
        home = Path.home()
        configs = [f for f in [
            home / ".bashrc",
            home / ".zshrc",
            home / ".profile",
        ] if f.exists()]

        if not configs:
            configs = [home / ".profile"]
            configs[0].touch()

        for cfg in configs:
            text = cfg.read_text(encoding="utf-8", errors="replace")
            if "CAMELOT-OS Integration" not in text:
                cfg.write_text(text + profile_block, encoding="utf-8")
                ok(f"Profile updated: {cfg}")
            else:
                ok(f"Profile already configured: {cfg}")


# ── Write portable config ──────────────────────────────────────────────────────

def write_portable_config(repo: Path, venv_bin: Path):
    """Write a minimal config.json next to install script for portable mode."""
    import json
    config = {
        "version": "1.0.0",
        "portable": True,
        "camelot_home": str(repo),
        "venv_bin": str(venv_bin),
        "note": "Portable install — run camelot configure to detect services",
    }
    config_path = Path(".") / "camelot_config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    ok(f"Portable config: {config_path.resolve()}")


# ── Run camelot configure ──────────────────────────────────────────────────────

def run_configure(venv_python: str, repo: Path):
    step("Running auto-configuration...")
    print()
    try:
        subprocess.run(
            [venv_python, "-X", "utf8", str(repo / "bin" / "camelot.py"), "configure"],
            check=False
        )
    except Exception as e:
        warn(f"Configure step failed (non-fatal): {e}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CAMELOT-OS Portable Installer — zero pip/curl dependencies"
    )
    parser.add_argument("--home", metavar="PATH",
                        help="Path to CAMELOT_OS repository root")
    parser.add_argument("--portable", action="store_true",
                        help="Portable mode — no PATH writes, config next to script")
    parser.add_argument("--no-configure", action="store_true",
                        help="Skip camelot configure after install")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing wrappers")
    args = parser.parse_args()

    banner()

    # 1. Python check
    step("Checking Python version...")
    python_exe = check_python()

    # 2. Locate repo
    step("Locating CAMELOT_OS root...")
    repo = find_repo(args.home)
    ok(f"Repository: {repo}")

    # 3. Virtual environment
    step("Setting up virtual environment...")
    venv_bin, venv_python = ensure_venv(repo, python_exe)

    # 4. Packages
    install_packages(venv_python)

    # 5. Wrappers
    create_wrappers(repo, venv_bin, venv_python, force=args.force)

    # 6. PATH / profile
    if args.portable:
        write_portable_config(repo, venv_bin)
    register_path(venv_bin, repo, portable=args.portable)

    # 7. Configure
    if not args.no_configure:
        run_configure(venv_python, repo)

    # Done
    print(f"\n{GREEN}{BOLD}  ============================================{RESET}")
    print(f"{GREEN}{BOLD}   CAMELOT-OS installation complete!{RESET}")
    print(f"{GREEN}{BOLD}  ============================================{RESET}")
    print(f"\n  Commands: {CYAN}camelot{RESET}  {CYAN}ai{RESET}  {CYAN}ks{RESET}  {CYAN}knight-session{RESET}")
    if args.portable:
        print(f"\n  {YELLOW}Portable mode — add {venv_bin} to PATH manually if needed{RESET}")
    else:
        print(f"\n  {YELLOW}Open a new terminal, then type: camelot{RESET}")
    print()


if __name__ == "__main__":
    main()
