# SPDX-License-Identifier: MIT

# Camelot Apex OS — Control Plane Package
#
# Modules are organized into subdirectories:
#   core/     — gate, governance, HITL (anya_gate, factory_lane, soul_oversight, ...)
#   dispatch/ — routing, dispatch, agent management (bifrost, switchboard, ...)
#   runes/    — runic commands, CLI, TOON (runic_router, camelot_cli, ...)
#   infra/    — infrastructure, memory, sync, observability, bridges, phase_h, ...
#   cluster/  — swarm daemons (agents_daemon, consensus_daemon, ...)
#
# A meta-path finder intercepts ``control_plane.<module>`` imports and
# redirects them to the correct subdirectory, so legacy code like
# ``from control_plane.anya_gate import AnyaGate`` continues to work.

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

_PACKAGE_DIR = Path(__file__).resolve().parent
_SUBDIRS = ("core", "dispatch", "runes", "infra", "cluster")


class _ControlPlaneModuleFinder:
    """Meta-path finder that redirects ``control_plane.<name>`` imports
    to ``control_plane.<subdir>.<name>`` when the bare module has been
    moved into a subdirectory."""

    def find_spec(self, fullname: str, path: Any, target: Any = None) -> Any:
        if not fullname.startswith("control_plane."):
            return None
        # Skip the package itself and dunder modules
        if fullname == "control_plane":
            return None
        if fullname.split(".")[-1].startswith("_"):
            return None

        # Extract the leaf module name (last component after control_plane.)
        parts = fullname.split(".")
        leaf = parts[-1]

        for subdir in _SUBDIRS:
            candidate = _PACKAGE_DIR / subdir / f"{leaf}.py"
            if candidate.is_file():
                # Use fullname (the name being imported) so the module is
                # cached under the correct key in sys.modules and its
                # __package__ is derived from the top-level package, not
                # from the subdirectory it physically lives in.
                spec = importlib.util.spec_from_file_location(fullname, str(candidate))
                if spec is not None:
                    spec.submodule_search_locations = None
                    return spec

        return None


def _install() -> None:
    """Insert the redirecting finder into sys.meta_path once."""
    for entry in sys.meta_path:
        if isinstance(entry, _ControlPlaneModuleFinder):
            return
    sys.meta_path.insert(0, _ControlPlaneModuleFinder())


_install()
