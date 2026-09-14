# SPDX-License-Identifier: MIT

"""Guard: OSID cookie-precedence workaround in ``vfs/notebooklm_client.py``.

Background (CAMELOT_OS incident, 2026-09): ``OSID`` / ``__Secure-OSID`` are
host-only service cookies that exist on BOTH ``notebook.google.com`` and
``notebooklm.google.com``. SDK versions whose auth path projects cookies into
a flat ``name -> value`` map (the 0.3.x line, and any release predating PR
#2058, first shipped in 0.8.1) resolve that collision by file order in
``storage_state.json``. The wrong service's OSID then reaches the
``notebooklm.google.com`` RPC host, Google answers ``401``, the internal token
refresh hits a ``302`` sign-in redirect, and the whole thing masquerades as
"authentication expired".

Upstream context: PR #2058 ("stop building requests from a domain-blind cookie
projection") removed the hazard, tracked by issue #2054; PR #2059 / issue
#2057 fixed the sibling PSIDTS-recovery ranking. First fixed release: 0.8.1.

This venv has demonstrably flip-flopped between the regular site-packages
install (0.3.4, vulnerable) and the editable checkout (``tools/notebooklm-py``,
0.8.0 pre-release). While ANY pre-0.8.1 SDK can be active, the wrapper
workaround in ``vfs/notebooklm_client.py`` is load-bearing and must stay.

These tests enforce:
1. The workaround markers remain in the wrapper source while the active SDK
   predates 0.8.1 (auto-skips once the SDK ships PR #2058, signalling that the
   workaround may be retired).
2. A behavioral tripwire on the SDK's own collision resolution, using
   synthetic sentinel values only (never real cookie material), so any change
   in SDK behavior becomes visible and re-arms the workaround requirement.
"""

from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER_PATH = REPO_ROOT / "vfs" / "notebooklm_client.py"

# First release line that ships PR #2058's domain-preserving fix.
POST_2058_MIN = (0, 8, 1)


def _sdk_version_tuple() -> tuple[int, int, int] | None:
    """Return the active notebooklm-py (major, minor, patch), or None if unknown.

    Unknown versions are treated as PRE-fix by the callers (conservative:
    the workaround requirement stays enforced).
    """
    try:
        raw = version("notebooklm-py")
    except PackageNotFoundError:
        return None
    except Exception:  # pragma: no cover - defensive
        return None
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", raw)
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _sdk_is_post_2058() -> bool:
    version_tuple = _sdk_version_tuple()
    return version_tuple is not None and version_tuple >= POST_2058_MIN


def _workaround_markers() -> dict[str, bool]:
    """Check the wrapper source still carries the OSID precedence workaround.

    Markers mirror the actual patch: the forcing loop that overrides colliding
    OSID/__Secure-OSID values with the ``notebooklm.google.com`` entries, and
    the ``(AuthError, ValueError)`` catch that surfaces auth expiry at WARNING
    level with the re-login hint.
    """
    source = WRAPPER_PATH.read_text(encoding="utf-8")
    return {
        "notebooklm.google.com domain check in forcing loop": (
            'c.get("domain") == "notebooklm.google.com"' in source
        ),
        "OSID/__Secure-OSID name pair override": '("OSID", "__Secure-OSID")' in source,
        "auth expiry surfaced via (AuthError, ValueError)": "(AuthError, ValueError)" in source,
        "re-login hint in warning": "notebooklm login" in source,
    }


def test_osid_precedence_workaround_present_while_sdk_predates_2058() -> None:
    if _sdk_is_post_2058():
        pytest.skip(
            "notebooklm-py >= 0.8.1 ships PR #2058; the wrapper OSID "
            "precedence workaround may now be retired."
        )
    missing = [name for name, ok in _workaround_markers().items() if not ok]
    assert not missing, (
        "The active notebooklm-py SDK predates PR #2058, so the wrapper OSID "
        f"precedence workaround in {WRAPPER_PATH} is load-bearing, but these "
        f"markers are missing: {missing}"
    )


def test_sdk_flat_extraction_osid_collision_is_visible() -> None:
    """Behavioral tripwire on the SDK's flat cookie projection.

    Builds a synthetic storage state where ``OSID`` exists on both personal
    app hosts, with distinct sentinel values (synthetic only — no real cookie
    material, per the privacy rule). Records which value wins the flat
    projection:

    * ``notebooklm.google.com`` sentinel wins -> SDK ranks deterministically
      in our favor (self-mitigated; observed on the local 0.8.0 checkout).
    * ``notebook.google.com`` sentinel wins -> file-order hazard (the
      #2054/#2019 failure shape). The wrapper workaround then becomes
      mandatory regardless of version gate, so assert it directly.
    """
    pytest.importorskip("notebooklm")
    from notebooklm.auth import extract_cookies_from_storage

    nb_sentinel = "camelot-guard-osid-from-notebook-google"
    nlm_sentinel = "camelot-guard-osid-from-notebooklm-google"
    synthetic_state = {
        "cookies": [
            {"name": "OSID", "value": nb_sentinel, "domain": "notebook.google.com"},
            {"name": "OSID", "value": nlm_sentinel, "domain": "notebooklm.google.com"},
            {"name": "SID", "value": "camelot-guard-sid", "domain": ".google.com"},
            {
                "name": "__Secure-1PSIDTS",
                "value": "camelot-guard-psidts",
                "domain": ".google.com",
            },
        ]
    }

    flat = extract_cookies_from_storage(synthetic_state)
    winner = flat.get("OSID")
    assert winner in (nb_sentinel, nlm_sentinel), (
        f"Unexpected OSID resolution from flat projection: {winner!r}"
    )

    if winner == nb_sentinel:
        missing = [name for name, ok in _workaround_markers().items() if not ok]
        assert not missing, (
            "SDK flat extraction resolved the colliding OSID by file order "
            f"({winner!r}) - the #2054 hazard shape. The wrapper workaround "
            f"is load-bearing but missing from {WRAPPER_PATH}: {missing}"
        )
