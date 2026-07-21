"""tests/_fixtures.py — shared test helpers for the portable CLI + V4000 suite.

Cross-test-file feature parity:
  * Forwarding of the old ``_CapturingConsole`` name from the prior
    inline-``type()`` stub refactor so any future test that still uses
    the underscore-prefixed name during a transition window keeps working.

Why a separate module (vs. ``tests/conftest.py``)?
  * These helpers are regular Python classes/functions, not pytest
    fixtures (``@pytest.fixture``). Putting them in conftest would force
    pytest's conftest-collection semantics on them and (more importantly)
    discourage direct ``from tests._fixtures import X`` statements, which
    is exactly the call-site style we want.
  * ``conftest.py`` is reserved for fixtures, hooks, and pytest-bootstrap
    concerns (see ``tests/conftest.py``'s mempalace package alias for the
    canonical pattern in this repo).
"""

from __future__ import annotations

import argparse
from typing import Any


class CapturingConsole:
    """Minimal Rich Console replacement for testing — captures plain text.

    ``self.lines`` accumulates the plain-text rendering of every
    ``.print(...)`` and ``.print_json(...)`` call so tests can assert
    against the captured output (or surface a useful failure diff when
    an ``_preflight_emit_overwrite`` refusal fires in a future regression).
    """

    def __init__(self) -> None:
        self.lines: list[str] = []

    def print(self, *args: Any, **kwargs: Any) -> None:
        text = " ".join(str(a) for a in args)
        self.lines.append(text)

    def print_json(self, payload: str, **_kwargs: Any) -> None:
        self.lines.append(payload)


# Backward-compat re-export. The prior refactor used an inline ``type()``
# stub + the underscore-prefixed name during a transition window; preserve
# the alias so any in-flight migration continues to resolve cleanly.
_CapturingConsole = CapturingConsole


def make_args(**overrides: Any) -> argparse.Namespace:
    """Build a Namespace mimicking argparse output for subcommand handlers.

    Defaults cover every argparse dest that the v1000 IDE/CLI subcommands
    (``cmd_omniroute``, ``cmd_knight``, ``cmd_mcp``, ``cmd_cartridge``)
    read; tests override only the fields under test.
    """
    base: dict[str, Any] = {
        "omniroute_list": False,
        "route": None,
        "select": None,
        "knight_list": False,
        "invoke": None,
        "prompt": None,
        "mcp_describe": None,
        "ping": None,
        "mcp_list": False,
        "mcp_chain": False,
        "emit": None,
        "target": None,
        "cartridge_force": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


# Backward-compat re-export. Same rationale as ``_CapturingConsole`` above.
_make_args = make_args
