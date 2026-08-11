"""Pytest fixtures for in-package loading of Camelot kernel modules.

The mempalace tests under ``tests/`` originally loaded
``01_KERNEL/memory/mempalace_l2.py`` as a top-level module via raw
``importlib.util.spec_from_file_location("mempalace_l2", ...)``. That does
NOT establish a parent package, but ``mempalace_l2.py`` performs a
**relative** import at module load time::

    from .cloudbrain_connector import CloudBrainConnector

→ ``ImportError: attempted relative import with no known parent package``.

This conftest registers ``01_KERNEL.memory`` (which already provides a
real ``__init__.py``) as a synthetic Python package alias in
``sys.modules``, then loads ``mempalace_l2.py`` as a child submodule of
that alias so relative imports resolve correctly. The fixture is
session-scoped: the bootstrap runs once per pytest session and is fully
idempotent.

Tests consume the ``meml2`` fixture instead of doing their own
``importlib.util`` dance, e.g.::

    def test_x(meml2):
        l2 = mempalace_module.MemPalaceL2(storage_path=tmp)
        ...

Why a synthetic package alias instead of mutating ``sys.path``?
    * It avoids polluting ``sys.path`` for every other test in the suite.
    * It keeps the loaded module's qualified name pointing to a stable
      sentinel (``_mempalace_test_pkg.mempalace_l2``) so debugging and
      tracebacks remain unambiguous.
    * It does NOT write any new file under ``01_KERNEL/memory/``; the
      existing ``__init__.py`` is loaded as-is.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# MemPalaceL2 refuses to start without MEMPALACE_SECRET rather than silently
# falling back to the public default key that used to ship in the repo. The
# suite opts into the insecure development key explicitly — a test index needs a
# stable key, and making the opt-in visible here keeps it out of library code.
os.environ.setdefault("MEMPALACE_ALLOW_INSECURE_SECRET", "1")
KG_MEM_DIR = REPO_ROOT / "01_KERNEL" / "memory"
KG_MEM_INIT = KG_MEM_DIR / "__init__.py"

# Stable sentinel: the synthetic package that hosts the in-test submodule.
PKG_NAME = "_mempalace_test_pkg"


def _register_parent_package() -> ModuleType:
    """Register ``01_KERNEL.memory`` as ``PKG_NAME`` in ``sys.modules``.

    Loads the existing on-disk ``__init__.py`` so the package is a real
    Python package (not a namespace stub). Re-uses a cached entry if the
    bootstrap already ran in this process.
    """
    cached = sys.modules.get(PKG_NAME)
    if cached is not None and hasattr(cached, "__path__"):
        return cached

    if not KG_MEM_INIT.exists():
        raise RuntimeError(
            f"Expected {KG_MEM_INIT} to exist; the relative imports inside "
            "01_KERNEL/memory/*.py require a real package marker, but the "
            "marker is missing. Refusing to fabricate one from conftest."
        )

    spec = importlib.util.spec_from_file_location(PKG_NAME, KG_MEM_INIT)
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"importlib could not build a spec for {KG_MEM_INIT}; "
            "refusing to fabricate a synthetic package."
        )
    parent = importlib.util.module_from_spec(spec)
    sys.modules[PKG_NAME] = parent
    spec.loader.exec_module(parent)
    # Reinforce __path__ in case __init__.py didn't set it (some markers don't).
    if not getattr(parent, "__path__", None):
        parent.__path__ = [str(KG_MEM_DIR)]
    return parent


def _bootstrap_meml2() -> ModuleType:
    """Idempotently load ``01_KERNEL.memory.mempalace_l2`` as a real submodule.

    Returns the loaded module object so callers (fixtures/tests) can do
    ``cls = bootstrap().MemPalaceL2``.
    """
    full_name = f"{PKG_NAME}.mempalace_l2"
    sub_path = KG_MEM_DIR / "mempalace_l2.py"

    cached = sys.modules.get(full_name)
    if cached is not None and hasattr(cached, "MemPalaceL2"):
        return cached

    _register_parent_package()

    sub_spec = importlib.util.spec_from_file_location(full_name, sub_path)
    if sub_spec is None or sub_spec.loader is None:
        raise RuntimeError(
            f"importlib could not build a spec for {sub_path}; refusing to "
            "fabricate a synthetic submodule."
        )
    sub_module = importlib.util.module_from_spec(sub_spec)
    # Bind submodule to its parent BEFORE exec_module so relative imports
    # (`from .cloudbrain_connector import CloudBrainConnector`) resolve
    # through the parent's __path__.
    parent = sys.modules[PKG_NAME]
    parent.mempalace_l2 = sub_module
    sys.modules[full_name] = sub_module
    sub_spec.loader.exec_module(sub_module)
    return sub_module


@pytest.fixture(scope="session")
def meml2() -> ModuleType:
    """Session-scoped fixture: returns the loaded ``mempalace_l2`` module.

    Use directly::

        def test_x(meml2):
            l2 = meml2.MemPalaceL2(storage_path=tmp_path)
            ...
    """
    return _bootstrap_meml2()


@pytest.fixture(scope="session")
def mempalace_module() -> ModuleType:
    """Alias of :func:`meml2` for call-site readability."""
    return _bootstrap_meml2()
