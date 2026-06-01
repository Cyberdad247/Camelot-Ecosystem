#!/usr/bin/env python3
"""Build the CAMELOT-OS portable single-file binary via PyInstaller.

Usage:
    python scripts/build_portable.py [--clean] [--test]

Outputs:
    dist/camelot.exe   (Windows)
    dist/camelot       (Linux/macOS)
"""
import os
import sys
import shutil
import subprocess
import platform
import tempfile
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"
BUILD = REPO / "build"
SPEC = REPO / "camelot.spec"
VENV_PYTHON = REPO / ".venv" / "Scripts" / "python.exe" if platform.system() == "Windows" \
    else REPO / ".venv" / "bin" / "python"


def run(cmd: list, **kwargs):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"  [FAIL] exit code {result.returncode}")
        sys.exit(result.returncode)
    return result


def check_pyinstaller():
    try:
        import PyInstaller
        print(f"  [OK] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  [!!] PyInstaller not found — installing...")
        run([str(VENV_PYTHON), "-m", "pip", "install", "pyinstaller>=6.0"])


def check_upx():
    if shutil.which("upx"):
        print("  [OK] UPX found (binary compression enabled)")
        return True
    else:
        print("  [..] UPX not found (binary will be larger; install upx for compression)")
        return False


def clean():
    for d in (DIST, BUILD):
        if d.exists():
            shutil.rmtree(d)
            print(f"  [OK] Removed {d}")
    pycache = REPO / "bin" / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache)


def build():
    python = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    run([
        python, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC),
    ], cwd=str(REPO))


def get_binary_path() -> Path:
    exe_name = "camelot.exe" if platform.system() == "Windows" else "camelot"
    return DIST / exe_name


def test_binary(binary: Path):
    print("\n  --- Running smoke tests ---")
    tests_passed = 0
    tests_failed = 0

    def check(label: str, cmd: list, expected_in_output: str = None, expected_exit: int = 0):
        nonlocal tests_passed, tests_failed
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        stdout = result.stdout + result.stderr
        ok = result.returncode == expected_exit
        if expected_in_output:
            ok = ok and expected_in_output.lower() in stdout.lower()
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {label}")
        if not ok:
            print(f"       exit={result.returncode} stdout={stdout[:200]}")
            tests_failed += 1
        else:
            tests_passed += 1

    check("--version flag", [str(binary), "--version"], "camelot")
    check("--list flag", [str(binary), "--list"], "knight")
    check("help text (no args)", [str(binary), "--help"], "camelot", expected_exit=0)

    # Test from isolated temp dir (simulates running from non-repo location)
    with tempfile.TemporaryDirectory() as tmp:
        env = os.environ.copy()
        env.pop("CAMELOT_OS_HOME", None)  # ensure no repo env var
        result = subprocess.run(
            [str(binary), "--version"],
            cwd=tmp, capture_output=True, text=True, env=env, timeout=15
        )
        ok = result.returncode == 0 and "camelot" in (result.stdout + result.stderr).lower()
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} --version from isolated temp dir")
        if ok:
            tests_passed += 1
        else:
            tests_failed += 1

    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0


def report_size(binary: Path):
    size_mb = binary.stat().st_size / 1_048_576
    status = "[OK]" if size_mb <= 80 else "[!!]"
    print(f"  {status} Binary size: {size_mb:.1f} MB  (target: <=80 MB)")


def main():
    parser = argparse.ArgumentParser(description="Build CAMELOT-OS portable binary")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts first")
    parser.add_argument("--test", action="store_true", help="Run smoke tests after build")
    parser.add_argument("--no-upx", action="store_true", help="Disable UPX compression check")
    args = parser.parse_args()

    print("\n  ============================================")
    print("   CAMELOT-OS Portable Binary Builder")
    print("   WARP_GATE v1.0.0")
    print("  ============================================\n")

    print("  >> Checking prerequisites...")
    check_pyinstaller()
    if not args.no_upx:
        check_upx()

    if args.clean:
        print("\n  >> Cleaning previous build artifacts...")
        clean()

    print("\n  >> Building portable binary...")
    build()

    binary = get_binary_path()
    if not binary.exists():
        print(f"\n  [FAIL] Binary not found at expected path: {binary}")
        sys.exit(1)

    print(f"\n  [OK] Binary built: {binary}")
    report_size(binary)

    if args.test:
        print("\n  >> Running smoke tests...")
        success = test_binary(binary)
        if not success:
            sys.exit(1)

    print("\n  ============================================")
    print("   Build complete!")
    print(f"   Binary: {binary}")
    print("  ============================================\n")
    print("  Next steps:")
    print("    1. Copy dist/camelot.exe to any machine or thumbdrive")
    print("    2. Run: camelot configure  (first-time setup)")
    print("    3. Run: camelot            (warp into Camelot-OS)")
    print()


if __name__ == "__main__":
    main()
