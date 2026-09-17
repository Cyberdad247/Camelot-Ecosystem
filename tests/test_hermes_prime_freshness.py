# SPDX-License-Identifier: MIT
"""HERMES_PRIME must be reported dead when it stops producing cycles.

`GET /api/hermes` on the hub serves a status for HERMES_PRIME. That status was
previously the literal string ``"ALWAYS_ON_HUB"``. While it served that string:

* ``camelot-hermes-prime.service`` was ``disabled``,
* it had **zero journal entries** — it had never been started,
* and its ``ExecStart`` (``--loop 60``) was an invocation the engine rejects
  outright (``exit=2``).

So the endpoint advertised a live always-on agent that had never once run, and
no test could catch it, because a constant can be asserted for all time.

The status is now derived from the only thing that constitutes evidence: the
PhialEngine state file, and how long ago it last recorded a cycle. This module
tests that rule, and — opt-in — the live hub.

The freshness window is ``HERMES_PRIME_CADENCE_S * HERMES_PRIME_GRACE_MULTIPLIER``
(3 x 60s), so a single slow or skipped run does not flap the dashboard while a
genuinely stopped timer still fails loudly.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from control_plane.dispatch import vps_mobile_mesh_bridge as bridge
from control_plane.dispatch.vps_mobile_mesh_bridge import (
    HERMES_PRIME_CADENCE_S,
    HERMES_PRIME_GRACE_MULTIPLIER,
    hermes_prime_status,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_SRC = REPO_ROOT / "control_plane" / "dispatch" / "vps_mobile_mesh_bridge.py"

HUB = "root@162.35.107.134"
WINDOW_S = HERMES_PRIME_CADENCE_S * HERMES_PRIME_GRACE_MULTIPLIER

# A fixed instant, so the boundary tests are arithmetic rather than racing the clock.
NOW = datetime(2026, 9, 17, 1, 0, 0, tzinfo=timezone.utc)


def _state(*ages_s: float) -> dict:
    """PhialEngine-shaped state whose memory entries are `ages_s` old, oldest first."""
    memory = [
        {
            "cycle_id": f"hp-test{i}",
            "seed": "hub-autonomous",
            "ts": (NOW - timedelta(seconds=age)).isoformat(),
        }
        for i, age in enumerate(ages_s)
    ]
    return {"schema": "camelot-os.phial/hermes_prime/v1", "weights": {}, "memory": memory}


# --------------------------------------------------------------------------- #
# the rule
# --------------------------------------------------------------------------- #


def test_a_recent_cycle_reports_always_on() -> None:
    result = hermes_prime_status(_state(5), now=NOW)
    assert result["status"] == "ALWAYS_ON_HUB"
    assert result["last_cycle_age_s"] == pytest.approx(5)
    assert result["cycles"] == 1


def test_a_stale_cycle_does_not_claim_always_on() -> None:
    """The negative control: this is the case that used to report healthy."""
    result = hermes_prime_status(_state(WINDOW_S + 1), now=NOW)
    assert result["status"] != "ALWAYS_ON_HUB"
    assert result["status"] == "STALE"
    assert result["last_cycle_age_s"] > result["fresh_within_s"]


def test_the_freshness_boundary_is_inclusive_then_degrades() -> None:
    at_boundary = hermes_prime_status(_state(WINDOW_S), now=NOW)
    past_boundary = hermes_prime_status(_state(WINDOW_S + 0.001), now=NOW)
    assert at_boundary["status"] == "ALWAYS_ON_HUB"
    assert past_boundary["status"] == "STALE"


def test_missing_state_is_not_reported_as_alive() -> None:
    for empty in ({}, {"memory": []}, {"memory": None}):
        result = hermes_prime_status(empty, now=NOW)
        assert result["status"] == "NO_STATE"
        assert result["last_cycle_age_s"] is None
        assert result["cycles"] == 0


def test_unparseable_timestamps_do_not_count_as_alive() -> None:
    state = {"memory": [{"cycle_id": "x", "ts": "not-a-timestamp"}]}
    result = hermes_prime_status(state, now=NOW)
    assert result["status"] == "UNPARSEABLE"
    assert result["last_cycle_age_s"] is None


def test_malformed_state_does_not_raise() -> None:
    # NB: `None` is deliberately absent. It is not malformed input — it is the
    # documented "read the state file off disk" path, covered below. Including
    # it here made this test read the repo's real state file and report STALE.
    for bogus in ("string", 42, [], {"memory": "nope"}, {"memory": [1, 2, 3]}):
        result = hermes_prime_status(bogus, now=NOW)  # type: ignore[arg-type]
        assert result["status"] in {"NO_STATE", "UNPARSEABLE"}


def test_omitted_state_reads_the_state_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """No argument means "read from disk" — the path the endpoint actually uses."""
    seen: list[bool] = []

    def fake_read() -> dict:
        seen.append(True)
        return _state(5)

    monkeypatch.setattr(bridge, "read_phial_state", fake_read)
    result = hermes_prime_status(now=NOW)
    assert seen, "the state file was never consulted"
    assert result["status"] == "ALWAYS_ON_HUB"


def test_the_newest_cycle_is_the_one_measured() -> None:
    """An old entry must not mask a newer one, or a dead timer would read healthy."""
    # oldest-first: a fresh cycle, then a very stale one on top of it.
    result = hermes_prime_status(_state(10, WINDOW_S * 5), now=NOW)
    assert result["status"] == "STALE", "measured an older entry instead of the newest"
    assert result["cycles"] == 2


def test_a_non_final_entry_with_a_bad_timestamp_is_skipped() -> None:
    """Corrupt trailing entries degrade rather than poisoning the reading."""
    state = _state(5)
    state["memory"].append({"cycle_id": "corrupt", "ts": None})
    result = hermes_prime_status(state, now=NOW)
    assert result["status"] == "ALWAYS_ON_HUB"
    assert result["last_cycle_age_s"] == pytest.approx(5)


@pytest.mark.parametrize(
    "raw",
    [
        "2026-09-17T01:00:00Z",
        "2026-09-17T01:00:00+00:00",
        "2026-09-17T01:00:00",  # naive: assumed UTC, not local time
    ],
)
def test_timestamp_shapes_the_engine_has_emitted_over_time(raw: str) -> None:
    state = {"memory": [{"cycle_id": "x", "ts": raw}]}
    result = hermes_prime_status(state, now=NOW)
    assert result["status"] == "ALWAYS_ON_HUB"
    assert result["last_cycle_age_s"] == pytest.approx(0, abs=0.001)


# --------------------------------------------------------------------------- #
# the endpoint must consult the rule
# --------------------------------------------------------------------------- #


def _knights_block() -> str:
    text = BRIDGE_SRC.read_text(encoding="utf-8")
    start = text.index("/bifrost/knights")
    return text[start : start + 1200]


def test_the_hermes_prime_entry_is_derived_not_hardcoded() -> None:
    block = _knights_block()
    entry_start = block.index('"HERMES_PRIME"')
    entry = block[entry_start : block.index("},", entry_start)]
    assert "hermes[" in entry, f"HERMES_PRIME status is not derived:\n{entry}"
    assert "ALWAYS_ON_HUB" not in entry, (
        "HERMES_PRIME status is hardcoded again; that is how the hub advertised "
        "an agent whose unit had never been enabled"
    )


def test_hermes_prime_is_not_assigned_a_constant_status_anywhere() -> None:
    text = BRIDGE_SRC.read_text(encoding="utf-8")
    # Comment lines are exempt: a comment cannot assign a status, and the header
    # must be free to name the string whose removal it documents.
    offenders = [
        line.strip()
        for line in text.splitlines()
        if not line.strip().startswith("#")
        and "HERMES_PRIME" in line
        and "ALWAYS_ON_HUB" in line
    ]
    assert not offenders, f"hardcoded HERMES_PRIME status: {offenders}"


# --------------------------------------------------------------------------- #
# live hub (opt-in)
# --------------------------------------------------------------------------- #

_opt_in = pytest.mark.skipif(
    os.environ.get("CAMELOT_HUB_SSH") != "1" or shutil.which("ssh") is None,
    reason="opt-in: set CAMELOT_HUB_SSH=1 to check the live hub",
)


def _ssh(remote: str, timeout: int = 90) -> subprocess.CompletedProcess:
    # encoding is explicit: `text=True` alone decodes with the platform default (cp1252 on
    # Windows) while the hub emits UTF-8. Without this, any non-ASCII byte in the remote
    # output decodes to mojibake and a passing check looks like a failure.
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=12", HUB, remote],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


@_opt_in
def test_live_timer_is_active_and_enabled() -> None:  # pragma: no cover - opt-in
    out = _ssh(
        "systemctl is-active camelot-hermes-prime.timer; "
        "systemctl is-enabled camelot-hermes-prime.timer"
    )
    if out.returncode != 0:
        pytest.skip(f"could not reach the hub: {out.stderr.strip()[:200]}")
    active, _, enabled = out.stdout.strip().partition("\n")
    assert active.strip() == "active", "the Hermes Prime timer is not running"
    assert enabled.strip() == "enabled", "the timer would not survive a reboot"


@_opt_in
def test_live_endpoint_reports_fresh_cycles() -> None:  # pragma: no cover - opt-in
    """The end-to-end assertion: this fails once the timer stops producing."""
    out = _ssh("curl -s --max-time 8 http://127.0.0.1:8095/api/hermes")
    if out.returncode != 0 or not out.stdout.strip():
        pytest.skip(f"could not reach the hub endpoint: {out.stderr.strip()[:200]}")
    payload = json.loads(out.stdout)
    assert "status" in payload, "the hub is still serving a bridge without derived status"
    assert payload["status"] == "ALWAYS_ON_HUB", (
        f"HERMES_PRIME is not producing fresh cycles: {payload['status']} "
        f"(age={payload.get('last_cycle_age_s')}s)"
    )
    age = payload["last_cycle_age_s"]
    assert age is not None and age <= WINDOW_S, f"stale by {age}s (window {WINDOW_S}s)"
    assert payload.get("phial_engine"), "endpoint reports fresh but served no state"


@_opt_in
def test_live_knights_endpoint_carries_the_derived_status() -> None:  # pragma: no cover
    out = _ssh("curl -s --max-time 8 http://127.0.0.1:8095/api/bifrost/knights")
    if out.returncode != 0 or not out.stdout.strip():
        pytest.skip(f"could not reach the hub endpoint: {out.stderr.strip()[:200]}")
    knights = json.loads(out.stdout)["bifrost_knights"]
    hermes = next(k for k in knights if k["id"] == "HERMES_PRIME")
    assert hermes["status"] == "ALWAYS_ON_HUB"
    assert isinstance(hermes.get("cycles"), int), "the entry carries no evidence"
    assert hermes.get("last_cycle_age_s") is not None
