# excalibur.spec — PyInstaller spec for the EXCALIBUR Sovereign Command Deck.
#
# Build with:
#     pyinstaller --clean excalibur.spec
#
# Output: dist/excalibur.exe (Windows) or dist/excalibur (POSIX). The
# executable targets --excalibur as its default subcommand, which boots the
# dashboard on a configurable port. See excalibur.py for the entry point
# shim, and DEPLOYMENT_EXCALIBUR.md for the full distribution story.
#
# Bundles:
#   - excalibur.py              (entry shim — explicitly imports the controller
#                                so PyInstaller follows fastapi/starlette/pydantic)
#   - excalibur_controller.py   (FastAPI control plane; byte-compiled into PYZ)
#   - excalibur_dashboard.html  (single-file UI, copied as data)
#   - pyttsx3                   (optional real TTS — degrades gracefully if
#                                the platform speech engine isn't available)
#   - fastapi + uvicorn + starlette  (HTTP runtime)
#   - everything in stdlib needed for the procedural sine fallback
#
# IMPORTANT: do NOT list excalibur_controller.py under `datas` — that would
# drop the file into MEIPASS as raw bytes without following its imports, and
# uvicorn's dynamic "controller:app" import would then fail with a silent
# ModuleNotFoundError because fastapi/starlette/pydantic were never bundled.
# The controller must be reached through the static import graph (i.e., by
# `import excalibur_controller` inside excalibur.py) so PyInstaller hooks it.

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Transitive hidden imports for fastapi + starlette + pydantic + uvicorn + pyttsx3.
# Only modules that PyInstaller's static Analysis legitimately misses are
# listed here. Modules reached through normal `import x` / `from x import y`
# chains in `excalibur.py` and `excalibur_controller.py` are already pulled
# in by Analysis automatically — listing them again is dead weight.
#
#   * `uvicorn.server` — the worker runtime class is loaded lazily by uvicorn's
#     CLI parser (not via static import) so Analysis misses it on cold builds.
#   * `pyttsx3.drivers.*` — the platform drivers are loaded lazily via
#     `pyttsx3.init()` introspection, so we list all four common drivers to
#     keep Windows / macOS / Linux / Termux first-boot deterministic.
#
# Trimmed leaves: `starlette.{responses,middleware.cors,routing}` and the
# `uvicorn.{logging,loops,protocols,lifespan}` tree are all pulled in
# transitively via the static import graph now that
# `import excalibur_controller` lives at the top of `excalibur.py` and the
# controller's `from fastapi.responses import ...` / `from fastapi.middleware.cors
# import CORSMiddleware` imports get walked.
hidden = [
    "uvicorn.server",
    # Defensive: `starlette.responses` is reached transitively through
    # `from fastapi.responses import FileResponse, JSONResponse, ...` in
    # excalibur_controller.py on PyInstaller >= 5.13, but earlier versions
    # leaked this namespace. Keeping the explicit reference costs ~50 KB
    # but guarantees the boot path is stable across PyInstaller upgrades.
    # Remove this line once the CI matrix is locked to PyInstaller >= 6.x.
    "starlette.responses",
    "pyttsx3.drivers",
    "pyttsx3.drivers.sapi5",
    "pyttsx3.drivers.nsss",
    "pyttsx3.drivers.espeak",
]

a = Analysis(
    ["excalibur.py"],
    pathex=["."],
    binaries=[],
    datas=[
        # Only the dashboard is a real data file. excalibur_controller.py is
        # NOT listed here — see the IMPORTANT block at the top of this spec.
        ("excalibur_dashboard.html", "."),
        *collect_data_files("pyttsx3"),
    ],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim things the bundle doesn't need for the local-edge runtime.
        "matplotlib",
        "numpy.tests",
        "pandas",
        "ipython",
        "jupyter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="excalibur",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="excalibur",
)
