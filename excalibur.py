"""excalibur.py — entry-point shim used by excalibur.spec.

When the PyInstaller bundle is run as `excalibur.exe`, this script is the
executable's first Python frame. Its `main()` is what uvicorn's bootloader
imports. When run as plain `python excalibur.py`, it behaves identically.

Defaults: launch the EXCALIBUR dashboard on the configured port (default
8811). All other CLI args follow uvicorn's standard syntax; pass `--help`
after the binary to see them. Camelot-OS `camelot.exe --excalibur` wires
into this entry too via the `bin/camelot.py` dispatcher.
"""
from __future__ import annotations

import os
import sys

# IMPORTANT: this top-level import is what tells PyInstaller's Analysis stage
# to follow excalibur_controller's dependency tree (fastapi, starlette,
# pydantic, pyttsx3 drivers, etc.). If it lives only inside `main()`, the
# dependency walker never sees it and the frozen bundle silently crashes with
# ModuleNotFoundError before uvicorn can even bind a port. Keep this as the
# FIRST executable statement after the `from __future__` import.
import excalibur_controller  # noqa: E402  — intentional top-level side effect

_APP = excalibur_controller.app


def _bootstrap_sys_path() -> None:
    """When frozen by PyInstaller, sys._MEIPASS holds the extracted runtime
    dir containing the bundled assets (excalibur_dashboard.html, bundled
    pyttsx3 drivers, etc.). We add it to sys.path so any *optional* dynamic
    imports inside downstream code (e.g., lazy pyttsx3 driver loaders) can
    locate their data files. PyInstaller already injects MEIPASS on its own,
    but we belt-and-brace it for the COLLECT-folder layout (where the unzipped
    PYZ lives at dist/excalibur/_internal/).
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass and meipass not in sys.path:
            sys.path.insert(0, meipass)


def _parse_int_env(name: str, default: int) -> int:
    """Parse an int env var with a friendly error message on bad input."""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        sys.stderr.write(
            f"excalibur: {name}={raw!r} is not a valid integer. "
            f"Expected something like '8811'.\n"
        )
        sys.exit(2)


def main() -> None:
    _bootstrap_sys_path()
    port = _parse_int_env("EXCALIBUR_PORT", 8811)
    host = os.environ.get("EXCALIBUR_HOST", "127.0.0.1")

    # Hand off to uvicorn programmatically. Pass the live `app` object
    # directly rather than the "module:attr" string so we never rely on
    # uvicorn's dynamic import-string resolver (which is fragile inside a
    # frozen PyInstaller bundle when the module is byte-compiled into PYZ).
    try:
        import uvicorn  # type: ignore
        uvicorn.run(
            _APP,
            host=host,
            port=port,
            log_level=os.environ.get("EXCALIBUR_LOG_LEVEL", "info"),
            reload=False,
        )
    except ImportError:  # pragma: no cover — uvicorn is listed in the spec
        sys.stderr.write("uvicorn not available; this bundle must be rebuilt.\n")
        sys.exit(1)


# Alias for the PyInstaller spec's Analysis target.
excalibur_main = main
