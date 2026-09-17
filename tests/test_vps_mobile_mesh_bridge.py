# SPDX-License-Identifier: MIT
"""Mesh bridge authorization must be enforceable AND deployable.

The guard previously returned False whenever MESH_BRIDGE_TOKEN was unset:

    expected = os.getenv("MESH_BRIDGE_TOKEN", "")
    provided = headers.get("x-camelot-token", "")
    if not expected or not provided:
        return False

Nothing on the hub provisions that variable — it appears in the bridge and in one
test fixture, and in no unit file, deploy script, or workflow. So that version
would have 401'd every consumer the moment it shipped: the PWA mesh panel,
control_plane/cli/knight_hud.py, the Excalibur cockpit, and
scripts/deploy_luxora_nexus_lab.sh's own endpoint checks (which the hub bootstrap
runs as PHASE 6).

The tests below pin both halves of the contract: the security property (a
provisioned token is required and compared in constant time) and the
deployability property (an unprovisioned token does NOT deny service).
"""

from __future__ import annotations

import pytest

from control_plane.dispatch import vps_mobile_mesh_bridge as bridge
from control_plane.dispatch.vps_mobile_mesh_bridge import (
    is_mesh_request_authorized,
    mesh_auth_mode,
)

TOKEN = "fixture-mesh-token"


@pytest.fixture(autouse=True)
def _reset_warn_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """The warning is rate-limited by module state; isolate each test from it."""
    monkeypatch.setattr(bridge, "_last_auth_warning", 0.0)


# --------------------------------------------------------------------------- #
# the security property
# --------------------------------------------------------------------------- #


def test_mesh_bridge_rejects_missing_or_wrong_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MESH_BRIDGE_TOKEN", TOKEN)

    assert is_mesh_request_authorized({}) is False
    assert is_mesh_request_authorized({"x-camelot-token": "wrong"}) is False
    assert is_mesh_request_authorized({"x-camelot-token": TOKEN}) is True


def test_a_provisioned_token_is_compared_in_constant_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """A prefix-length oracle would leak the token a byte at a time."""
    monkeypatch.setenv("MESH_BRIDGE_TOKEN", TOKEN)
    calls: list[tuple[str, str]] = []
    real = bridge.hmac.compare_digest

    def spy(a: str, b: str) -> bool:
        calls.append((a, b))
        return real(a, b)

    monkeypatch.setattr(bridge.hmac, "compare_digest", spy)
    assert is_mesh_request_authorized({"x-camelot-token": "f"}) is False
    assert calls, "token comparison did not go through compare_digest"


def test_whitespace_only_token_counts_as_unprovisioned(monkeypatch: pytest.MonkeyPatch) -> None:
    """`MESH_BRIDGE_TOKEN=' '` in a unit file must not silently disable auth."""
    monkeypatch.setenv("MESH_BRIDGE_TOKEN", "   ")
    assert mesh_auth_mode() == "unconfigured", (
        "a whitespace-only token read as provisioned, so enforcement would engage "
        "against a token no client can match"
    )
    assert is_mesh_request_authorized({"x-camelot-token": "   "}) is True


# --------------------------------------------------------------------------- #
# the deployability property — the landmine this change removes
# --------------------------------------------------------------------------- #


def test_unprovisioned_token_does_not_deny_service(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deploying the bridge without provisioning the token must not take the mesh down."""
    monkeypatch.delenv("MESH_BRIDGE_TOKEN", raising=False)
    assert is_mesh_request_authorized({}) is True, (
        "an unset MESH_BRIDGE_TOKEN denied service; nothing on the hub provisions "
        "it, so this is an outage on deploy rather than a guard"
    )
    assert is_mesh_request_authorized({"x-camelot-token": "anything"}) is True


def test_unconfigured_auth_is_reported_not_hidden(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.delenv("MESH_BRIDGE_TOKEN", raising=False)
    assert mesh_auth_mode() == "unconfigured"
    with caplog.at_level("WARNING"):
        is_mesh_request_authorized({})
    assert any("UNAUTHENTICATED" in r.message for r in caplog.records), (
        "an unguarded bridge must say so"
    )


def test_a_matching_token_reports_enforced_without_warning(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("MESH_BRIDGE_TOKEN", TOKEN)
    assert mesh_auth_mode() == "enforced"
    with caplog.at_level("WARNING"):
        assert is_mesh_request_authorized({"x-camelot-token": TOKEN}) is True
    assert not [r for r in caplog.records if "UNAUTHENTICATED" in r.message]


def test_the_warning_is_rate_limited(monkeypatch: pytest.MonkeyPatch) -> None:
    """A polling consumer must not be able to flood the journal."""
    monkeypatch.setattr(bridge, "_last_auth_warning", 1_000.0)
    window = bridge._AUTH_WARN_INTERVAL_S
    assert window > 0

    # Mid-window: must not re-stamp, so no second warning is emitted.
    monkeypatch.setattr(bridge.time, "monotonic", lambda: 1_000.0 + window - 1)
    bridge._warn_unconfigured_auth()
    assert bridge._last_auth_warning == 1_000.0

    # Window elapsed: stamps, so exactly one warning per window.
    monkeypatch.setattr(bridge.time, "monotonic", lambda: 1_000.0 + window + 1)
    bridge._warn_unconfigured_auth()
    assert bridge._last_auth_warning > 1_000.0


# --------------------------------------------------------------------------- #
# the response advertises the mode
# --------------------------------------------------------------------------- #


def test_mesh_status_reports_the_auth_mode() -> None:
    import inspect

    src = inspect.getsource(bridge.MeshBridgeHandler.do_GET)
    assert "auth_mode" in src, (
        "the status payload should carry auth_mode so an unguarded bridge is visible"
    )
