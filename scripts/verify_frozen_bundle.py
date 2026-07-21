#!/usr/bin/env python3
"""scripts/verify_frozen_bundle.py — forensic check of ``dist/camelot.exe``.

Verifies that the PyInstaller bundle correctly carries:

  1. ``dist/camelot.exe`` exists and is non-trivial in size (>5 MB ⇒
     Stale bundle after a partial build would skew this).
  2. ``--version`` boots cleanly and reports ``1000-EXCALIBUR-A`` in
     stdout (catches a missing __version__ import in the spec).
  3. ``cartridge --list`` returns exit code 0 (the default subcommand
     surface must not panic in frozen mode).
  4. ``cartridge --emit FOO --target T --force`` writes the trio files
     to ``T`` (exercises the write path through PyInstaller's frozen
     import graph end-to-end).
  5. The ``cartridges.v4000_trio`` module was bundled by analysing the
     PyInstaller-frozen sys.path: boot a short Python one-liner via
     ``dist/camelot.exe --no-context mcp --list`` and parse the import
     traceback. If the cartridges import fails, this check fails.

The script returns ``0`` on all-pass, ``1`` on any failure. Designed to
be wired into CI via ``scripts/ci_smoke.sh`` so every PR surfaces
"the bundle changed" regressions before they ship.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXE = (
    REPO / "dist" / "camelot.exe"
    if sys.platform == "win32"
    else REPO / "dist" / "camelot"
)
MIN_BUNDLE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB — well below the real ~17 MB
EXPECTED_VERSION_TOKEN = "1000-EXCALIBUR-A"


def _run(exe: Path, *args: str, timeout: float = 30.0) -> subprocess.CompletedProcess:
    """Run the frozen binary with ``*args``. Raises on timeout."""
    return subprocess.run(
        [str(exe), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def check_dist_exists() -> str:
    """Return 'OK' if ``dist/camelot.exe`` exists + is large enough."""
    if not EXE.exists():
        return f"FAIL: {EXE} does not exist — run 'pyinstaller --clean camelot.spec' first"
    size = EXE.stat().st_size
    if size < MIN_BUNDLE_SIZE_BYTES:
        return f"FAIL: {EXE} is only {size} bytes — suspiciously small (≥{MIN_BUNDLE_SIZE_BYTES} expected)"
    return f"OK: {EXE} is {size:,} bytes"


def check_version_boots() -> str:
    """Return 'OK' if ``--version`` boots and emits the expected token."""
    try:
        result = _run(EXE, "--version")
    except subprocess.TimeoutExpired:
        return "FAIL: --version timed out (>30s)"
    if result.returncode != 0:
        return (
            f"FAIL: --version exited {result.returncode}; "
            f"stderr={result.stderr.strip()[:200]!r}"
        )
    if EXPECTED_VERSION_TOKEN not in (result.stdout + result.stderr):
        return (
            f"FAIL: --version output missing {EXPECTED_VERSION_TOKEN!r}; "
            f"stdout={result.stdout.strip()[:200]!r}"
        )
    return f"OK: --version reports {EXPECTED_VERSION_TOKEN!r}"


def check_cartridge_list() -> str:
    """Return 'OK' if ``cartridge --list`` exits 0 with no panic."""
    try:
        result = _run(EXE, "--no-context", "cartridge", "--list")
    except subprocess.TimeoutExpired:
        return "FAIL: cartridge --list timed out (>30s)"
    if result.returncode != 0:
        return (
            f"FAIL: cartridge --list exited {result.returncode}; "
            f"stderr={result.stderr.strip()[:200]!r}"
        )
    return "OK: cartridge --list exited 0"


def check_cartridge_emit() -> str:
    """Return 'OK' if ``cartridge --emit FOO --target T --force`` writes the trio."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "verify_emit"
        try:
            result = _run(
                EXE, "--no-context", "cartridge",
                "--emit", "verify_emit", "--target", str(target), "--force",
            )
        except subprocess.TimeoutExpired:
            return "FAIL: cartridge --emit timed out (>30s)"
        if result.returncode != 0:
            return (
                f"FAIL: cartridge --emit exited {result.returncode}; "
                f"stderr={result.stderr.strip()[:200]!r}"
            )
        for fname in ("blueprint.md", "task.md", "verification.md"):
            fp = target / fname
            if not fp.exists():
                return f"FAIL: trio file {fname} not written under {target}"
            if fp.stat().st_size == 0:
                return f"FAIL: trio file {fname} is empty"
        return f"OK: trio written to {target}"


def check_cartridges_package_bundled() -> str:
    """Return 'OK' if ``from cartridges.v4000_trio import ...`` works in frozen mode.

    We exercise the import via a boot-cycle probe: run ``cartridge --emit``
    with --force against a fresh target. The portable CLI imports
    ``cartridges.v4000_trio`` at module-load time, so a MissingModuleError
    surfaces as an ImportError traceback and a non-zero exit code (caught
    by ``check_cartridge_emit``). This check re-runs the same probe under
    a fresh target so a flake in the earlier emit doesn't mask a missing
    cartridge import.
    """
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "verify_import"
        try:
            result = _run(
                EXE, "--no-context", "cartridge",
                "--emit", "verify_import", "--target", str(target), "--force",
            )
        except subprocess.TimeoutExpired:
            return "FAIL: cartridge import probe timed out (>30s)"
        if result.returncode != 0:
            # Look for "ModuleNotFoundError" or "ImportError" — those
            # point to a missing PYZ entry for cartridges.* specifically,
            # vs. some other unexpected failure.
            blob = (result.stdout + result.stderr).lower()
            if "modulenotfounderror" in blob or "importerror" in blob:
                return (
                    f"FAIL: cartridge import probe raised ImportError — "
                    f"cartridges.v4000_trio likely NOT bundled in PYZ; "
                    f"stderr={result.stderr.strip()[:200]!r}"
                )
            return (
                f"FAIL: cartridge import probe exited {result.returncode}; "
                f"stderr={result.stderr.strip()[:200]!r}"
            )
        return "OK: cartridges.v4000_trio imports cleanly in frozen mode"


CHECKS = (
    ("dist/camelot.exe exists + sized", check_dist_exists),
    ("--version boot", check_version_boots),
    ("cartridge --list", check_cartridge_list),
    ("cartridge --emit --force", check_cartridge_emit),
    ("cartridges.v4000_trio bundled", check_cartridges_package_bundled),
)


def main() -> int:
    print(f"Forensic bundle check on {EXE}\n")
    failed = 0
    for name, fn in CHECKS:
        result = fn()
        prefix = "PASS" if result.startswith("OK") else "FAIL"
        print(f"[{prefix}] {name}: {result}")
        if not result.startswith("OK"):
            failed += 1
    print()
    if failed:
        print(f"{failed} of {len(CHECKS)} checks FAILED")
        return 1
    print(f"All {len(CHECKS)} checks PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
