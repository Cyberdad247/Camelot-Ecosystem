# -*- mode: python ; coding: utf-8 -*-
# CAMELOT-OS Portable Binary Spec — WARP_GATE v1.0.0
# Build: pyinstaller camelot.spec
# Output: dist/camelot.exe (Windows) | dist/camelot (Linux/macOS)

import sys
import os
from pathlib import Path

REPO = Path(SPECPATH)
CLAUDE_MD = Path.home() / "CLAUDE.md"

# --- Collect data assets ---
datas = []

# CLAUDE.md constitution (from home dir or repo root)
if CLAUDE_MD.exists():
    datas.append((str(CLAUDE_MD), "."))
elif (REPO / "CLAUDE.md").exists():
    datas.append((str(REPO / "CLAUDE.md"), "."))

# OmniRoute config
omniroute = REPO / "03_VAULT" / "training" / "configs" / "config" / "omniroute.json"
if omniroute.exists():
    datas.append((str(omniroute), "."))

# Cartridges directory
cartridges_dir = REPO / "03_VAULT" / "training" / "configs" / "cartridges"
if cartridges_dir.exists():
    datas.append((str(cartridges_dir), "cartridges"))

# Skills directory (optional)
skills_dir = REPO / ".hive" / "skills"
if skills_dir.exists():
    datas.append((str(skills_dir), "skills"))

# Completion scripts (for shell-setup in portable mode)
completions_dir = REPO / "completions"
if completions_dir.exists():
    datas.append((str(completions_dir), "completions"))

a = Analysis(
    [str(REPO / "bin" / "camelot_portable.py")],
    pathex=[str(REPO), str(REPO / "bin")],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "httpx",
        "rich",
        "rich.console",
        "rich.markdown",
        "rich.panel",
        "rich.live",
        "rich.spinner",
        "rich.table",
        "rich.prompt",
        "yaml",
        "psutil",
        "keyring",
        "keyring.backends",
        "keyring.backends.Windows",
        "camelot_keys",
        "camelot_shell_setup",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Heavy ML libs not needed in portable binary
        "torch", "torchvision", "torchaudio",
        "transformers", "tokenizers", "datasets",
        "sklearn", "scipy", "numpy",
        "cv2", "PIL", "matplotlib",
        "tensorflow", "keras",
        "pandas", "pyarrow",
        "langchain", "pydantic_ai",
        "IPython", "jupyter",
        "boto3", "botocore",
        "cryptography", "OpenSSL",
        "grpc", "google.protobuf",
        "sqlalchemy", "alembic",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="camelot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
