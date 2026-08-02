"""Thin Python shim that exposes Ouroboros as a repo-root Python module.

The canonical Ouroboros implementation lives at
``03_VAULT/training/configs/ouroboros.py`` (a full SQLite-backed persistence
layer with ``log_execution``, ``get_history``, ``get_stats``,
``export_all``). Several runtime call sites (``03_VAULT/training/configs/
hud.py``, ``camelot.py``, ``knights/coder.py``) and the local test
``03_VAULT/training/configs/tests/test_ouroboros.py`` rely on a top-level
``from ouroboros import …``. Historically each of those modules pulsed
``sys.path.insert(0, "03_VAULT/training/configs")`` locally; that is
brittle and produces latent ``ImportError``s when the runtime path differs.

This shim sits at the repo root. When Python resolves ``import ouroboros``
it loads this file, executes the canonical implementation in place, and
**replaces** ``sys.modules[__name__]`` with the loaded implementation
**before** the implementation runs. The result: every consumer that grabs
``ouroboros`` receives the canonical module object directly, so::

    monkeypatch.setattr(ouroboros, "DB_PATH", db_path)
    monkeypatch.setattr(ouroboros, "_initialized", False)

in the local test suite mutates the exact globals dictionary that
``_ensure_init`` and ``log_execution`` read from — preserving test
isolation semantics.

Design notes:
    * Single source of truth — the SQLite layer still lives only at
      ``03_VAULT/training/configs/ouroboros.py``; this file does NOT
      duplicate any logic.
    * Module identity preserved — no proxy / PEP 562 ``__getattr__``
      forwarding that would silently decouple ``monkeypatch`` writes
      from the implementation's read-side globals.
    * Import-time side effects of the canonical module (``_setup_logging``)
      execute exactly once, into the real module namespace.
    * No new ``__init__.py`` is dropped into ``03_VAULT/training/configs/``,
      so existing relative-import contracts are unchanged.
"""

import importlib.util
import os
import sys


def _bootstrap_canonical_ouroboros() -> None:
    """Load the canonical implementation in place and swap sys.modules."""
    repo_root = os.path.dirname(os.path.abspath(__file__))
    impl_path = os.path.join(
        repo_root, "03_VAULT", "training", "configs", "ouroboros.py",
    )

    if not os.path.isfile(impl_path):
        raise ImportError(
            f"Canonical Ouroboros implementation not found at {impl_path}. "
            "The shim requires 03_VAULT/training/configs/ouroboros.py to exist."
        )

    # ``__name__`` here is the shim's qualified name ("ouroboros"), which
    # equals the file stem, so we use it directly instead of aliasing via
    # a string constant. Reuse keeps the shim coupled to its own filename.
    spec = importlib.util.spec_from_file_location(__name__, impl_path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"importlib could not build a module spec for {impl_path}; "
            "refusing to fabricate a synthetic ouroboros module."
        )

    impl = importlib.util.module_from_spec(spec)

    # CRITICAL: register the impl in sys.modules BEFORE exec_module runs.
    # Two reasons:
    #   1. Any further `from ouroboros import …` or `import ouroboros` in
    #      the same process resolves to this impl, not the shim.
    #   2. If the canonical module itself ever re-imports ``ouroboros``
    #      during its own load (or any helper it triggers does so), Python
    #      already finds the impl in sys.modules and skips re-execution.
    sys.modules[__name__] = impl

    # Phase 1 (shadow mode): surface the Rust binding as a private attribute
    # of the loaded impl so callers can opt in incrementally. On success,
    # `_rust_engine` is a Python module. On failure, it is None.
    try:
        import ouroboros_engine as _oe
    except (ImportError, OSError, RuntimeError, ValueError):
        _oe = None
    impl._rust_engine = _oe

    spec.loader.exec_module(impl)



_bootstrap_canonical_ouroboros()
