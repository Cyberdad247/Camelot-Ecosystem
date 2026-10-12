# -*- coding: utf-8 -*-
"""Canonical repository-root resolution for control_plane modules.

Why this module exists
----------------------
``control_plane`` modules live at two different nesting depths — the package
root itself and the ``core/``, ``dispatch/``, ``runes/``, ``infra/`` and
``cluster/`` subdirectories — and the compatibility finder in
``control_plane.__init__`` makes each subdirectory module importable under two
names (``control_plane.rbac_matrix`` *and* ``control_plane.core.rbac_matrix``).

A hand-counted ``Path(__file__).parent.parent`` chain therefore encodes the
file's current depth as a constant. When modules were reorganised into
subdirectories the imports kept working (the finder handles those) but every
such chain silently began resolving one level short, producing phantom paths
like ``control_plane/03_VAULT/...`` instead of the real vault at the repo root.
Nothing raised: ``mkdir(parents=True)`` happily created the phantom tree and
``if not path.exists(): return {}`` treated the miss as "no data".

Resolving the root by *searching for repository markers* removes the depth
constant entirely, so these paths survive any future move.

Usage
-----
    from control_plane._paths import REPO_ROOT

Use an absolute import rather than a relative one: a relative ``..`` would
resolve differently depending on which of the two module names the finder
loaded the caller under.
"""
from __future__ import annotations

import os
from pathlib import Path

__all__ = ["REPO_ROOT", "VAULT", "KERNEL", "repo_root"]

# Directories/files that together identify the CAMELOT-OS repository root.
# Two independent hits are required so that a subdirectory which happens to
# contain one of these names cannot masquerade as the root.
_MARKERS: tuple[str, ...] = (
    "03_VAULT",
    "01_KERNEL",
    "02_FORGE",
    "Cargo.toml",
    "pyproject.toml",
)

# Operators may pin the root explicitly; several modules already honoured
# CAMELOT_HOME / CAMELOT_OS_HOME, so both are respected here in one place.
_ENV_OVERRIDES: tuple[str, ...] = ("CAMELOT_HOME", "CAMELOT_OS_HOME")


def _from_env() -> Path | None:
    for var in _ENV_OVERRIDES:
        raw = os.environ.get(var)
        if raw:
            candidate = Path(raw).expanduser()
            if candidate.is_dir():
                return candidate.resolve()
    return None


def repo_root() -> Path:
    """Return the repository root, searching upward for marker files.

    Falls back to the package parent (``control_plane/_paths.py`` ->
    ``control_plane`` -> root) if no marker pair is found, which keeps the
    module usable when the tree is vendored somewhere unusual.
    """
    pinned = _from_env()
    if pinned is not None:
        return pinned

    here = Path(__file__).resolve()
    for candidate in here.parents:
        hits = sum(1 for marker in _MARKERS if (candidate / marker).exists())
        if hits >= 2:
            return candidate
    return here.parent.parent


REPO_ROOT: Path = repo_root()
VAULT: Path = REPO_ROOT / "03_VAULT"
KERNEL: Path = REPO_ROOT / "01_KERNEL"
