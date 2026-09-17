# SPDX-License-Identifier: MIT
"""The hub self-check must stay wired to its alarm.

This is the check on the checks. The audit itself was correct for weeks and simply
never ran — so a guard that only tested the audit would have missed the actual
failure. What needs protecting is the *wiring*:

    camelot-selfcheck.timer -> camelot-selfcheck.service -> (fail) -> alert service

`OnFailure=` is the load-bearing line. If it is dropped, the audit still fails
correctly and still writes status.json, and absolutely nothing tells anyone — which
is the exact condition this whole exercise was built to end.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
UNITS = REPO_ROOT / "infra" / "systemd"
SERVICE = UNITS / "camelot-selfcheck.service"
TIMER = UNITS / "camelot-selfcheck.timer"
ALERT = UNITS / "camelot-selfcheck-alert.service"
BRIDGE = REPO_ROOT / "control_plane" / "dispatch" / "vps_mobile_mesh_bridge.py"
WATCHDOG_SERVICE = UNITS / "camelot-selfcheck-watchdog.service"
WATCHDOG_TIMER = UNITS / "camelot-selfcheck-watchdog.timer"
RUNNER = REPO_ROOT / "scripts" / "ops" / "hub-selfcheck.sh"
DEPLOY = REPO_ROOT / "scripts" / "ops" / "deploy-hub-selfcheck.sh"
AUDIT = REPO_ROOT / "scripts" / "vps_hub_bootstrap.sh"


def _sections(path: Path) -> dict[str, dict[str, str]]:
    """Key=Value pairs per systemd section, comments stripped."""
    assert path.exists(), f"missing {path}"
    sections: dict[str, dict[str, str]] = {}
    section: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("[") and s.endswith("]"):
            section = s.strip("[]")
            continue
        if section is None or "=" not in s:
            continue
        k, _, v = s.partition("=")
        sections.setdefault(section, {})[k.strip()] = v.strip()
    return sections


# --------------------------------------------------------------------------- #
# the chain
# --------------------------------------------------------------------------- #


def test_a_failing_audit_triggers_the_alert_unit() -> None:
    unit = _sections(SERVICE).get("Unit", {})
    assert unit.get("OnFailure") == "camelot-selfcheck-alert.service", (
        "without OnFailure the audit fails silently — the exact defect this "
        "monitoring was built to remove"
    )


def test_the_timer_drives_the_selfcheck_service() -> None:
    timer = _sections(TIMER).get("Timer", {})
    assert timer.get("Unit") == "camelot-selfcheck.service"
    assert timer.get("OnUnitActiveSec"), "timer has no cadence"
    assert _sections(TIMER).get("Install", {}).get("WantedBy") == "timers.target"


def test_the_audit_unit_is_not_retried_into_silence() -> None:
    """A failing post-condition must surface as a failed unit for a human."""
    service = _sections(SERVICE).get("Service", {})
    assert service.get("Type") == "oneshot"
    assert "Restart" not in service, (
        "Restart= on the audit would retry a failing contract until someone "
        "notices the logs, instead of leaving a failed unit in `systemctl --failed`"
    )


def test_the_alert_unit_cannot_mask_the_original_failure() -> None:
    alert = _sections(ALERT).get("Service", {})
    assert alert.get("Type") == "oneshot"
    assert "OnFailure" not in _sections(ALERT).get("Unit", {}), (
        "an OnFailure on the alert unit creates a failure chain instead of one signal"
    )
    assert alert.get("SuccessExitStatus") == "0"


# --------------------------------------------------------------------------- #
# the runner
# --------------------------------------------------------------------------- #


def test_runner_implements_both_subcommands() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "cmd_run()" in text and "cmd_alert()" in text
    assert "run)" in text and "alert)" in text


def test_alert_never_propagates_the_failure() -> None:
    """The failure signal belongs to the self-check unit, not the notifier."""
    body = RUNNER.read_text(encoding="utf-8").split("cmd_alert()", 1)[1]
    assert "return 0   # never propagate" in body


def test_alerts_are_deduplicated() -> None:
    """A 15-minute timer must not send the same alert 96 times a day."""
    text = RUNNER.read_text(encoding="utf-8")
    assert "last-alert.signature" in text
    assert "suppressed" in text, "no suppression path; repeated alerts will be ignored"


def test_alert_reports_which_channels_it_used() -> None:
    """Never imply a notification went somewhere it did not."""
    text = RUNNER.read_text(encoding="utf-8")
    assert "channels" in text
    assert "webhook:unconfigured" in text


def test_a_missing_status_file_is_itself_an_alert_condition() -> None:
    body = RUNNER.read_text(encoding="utf-8").split("cmd_alert()", 1)[1]
    assert "no status file" in body


def test_run_parses_the_audit_result_block_not_its_own_copy_of_the_contract() -> None:
    """Re-stating the post-conditions here would be a second source of truth."""
    text = RUNNER.read_text(encoding="utf-8")
    assert "vps_hub_bootstrap.sh" in text
    assert "--self-check" in text


def test_staleness_of_the_deployed_audit_is_recorded() -> None:
    """The deployed copy sits outside git; its hash must be visible."""
    assert "audit_sha256" in RUNNER.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# the deploy path
# --------------------------------------------------------------------------- #


def test_deploy_script_exists_and_targets_the_units() -> None:
    text = DEPLOY.read_text(encoding="utf-8")
    for u in ("camelot-selfcheck.service", "camelot-selfcheck.timer",
              "camelot-selfcheck-alert.service"):
        assert u in text, f"deploy script does not install {u}"


def test_deploy_script_does_not_lint_unit_files_as_shell() -> None:
    """`bash -n` on a unit file fails on innocuous text like `(parenthetical)`.

    A check that cries wolf on valid input is worse than no check: it teaches the
    reader to ignore the output. Units are validated with `systemd-analyze verify`.
    """
    text = DEPLOY.read_text(encoding="utf-8")
    assert "systemd-analyze verify" in text, "units are not validated with the right tool"
    for line in text.splitlines():
        if "bash -n" in line and ".service" not in line and ".timer" not in line:
            continue
        assert not ("bash -n" in line and (".service" in line or ".timer" in line)), (
            f"deploy script runs bash -n on a unit file: {line.strip()}"
        )


# --------------------------------------------------------------------------- #
# the audit the runner calls
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("mode", ["--self-check", "--apply"])
def test_the_audit_exposes_a_read_only_mode(mode: str) -> None:
    assert mode in AUDIT.read_text(encoding="utf-8")


# A shell comment starts at `#` in word-initial position, so this strips both a
# full-line comment and a trailing one without touching a `#` inside a quoted string
# that is part of a word.
_COMMENT = re.compile(r"(?:^|\s)#.*$")


def _code_lines(text: str) -> list[str]:
    """Lines with comments removed before any danger-token scan.

    A scanner that reads prose flags documentation as a defect — which happened four
    times while building this wiring, each time on an explanatory comment. Only
    executable text can mutate anything, so only executable text is scanned, and
    trailing comments are stripped as well as full-line ones because a directive's
    trailing comment is still prose.
    """
    stripped = [_COMMENT.sub("", ln) for ln in text.splitlines()]
    return [ln for ln in stripped if ln.strip()]


def test_the_audit_is_read_only_in_self_check_mode() -> None:
    """No mutation may sit outside an apply guard, or the monitor itself becomes a risk."""
    text = AUDIT.read_text(encoding="utf-8")
    for mutator in ("apt-get install", "systemctl enable --now", "useradd", "createdb"):
        for line in _code_lines(text):
            if mutator in line:
                # Every mutator must be indented inside a conditional block.
                assert line.startswith((" ", "\t")), (
                    f"possible unguarded mutation at top level: {line.strip()}"
                )


# --------------------------------------------------------------------------- #
# the audit checks engines, not just units
# --------------------------------------------------------------------------- #


def test_the_audit_checks_engine_liveness_not_only_unit_liveness() -> None:
    """A unit that is `active` can still be producing nothing.

    `require_unit camelot-hermes-prime.timer` proves the schedule is on. A timer whose
    cycles stopped passing satisfies it while the hub serves a false status — the same
    defect as the original `ALWAYS_ON_HUB` beside a disabled unit, one level down.
    """
    text = AUDIT.read_text(encoding="utf-8")
    assert "engine producing fresh cycles" in text
    assert "/api/hermes" in text, "engine liveness is not asserted against the hub"


def _served_hermes_keys() -> set[str]:
    """The keys the bridge's `/api/hermes` response actually carries."""
    assert BRIDGE.exists(), f"missing {BRIDGE}"
    block = BRIDGE.read_text(encoding="utf-8").split("'/api/hermes']", 1)[1][:900]
    return set(re.findall(r'"([a-z_]+)":', block))


def test_the_engine_check_consumes_the_served_verdict() -> None:
    """The freshness window lives in the bridge; a second copy is a second source of
    truth, and a drifting copy is what let the original claim rot."""
    # `in` on a list is whole-element equality, not a substring search — the earlier
    # form of this assertion could never fail. `any(... in line ...)` is the check that
    # actually scans the directives.
    assert not any(
        "hermes_prime_phial.json" in line
        for line in _code_lines(AUDIT.read_text(encoding="utf-8"))
    ), (
        "the audit reads the state file directly and would have to reimplement the "
        "freshness rule instead of consuming the served verdict"
    )


def test_the_engine_liveness_label_only_prints_served_fields() -> None:
    """Cross-check the audit's label against the endpoint's response.

    Naming a field the endpoint does not carry renders `cycles=None` in the audit
    output, which reads as missing data rather than as an absent field. Checking
    membership against the bridge's own keys is what makes this guard non-vacuous: a
    guard that merely looked for one forbidden name would pass a different wrong name.
    """
    served = _served_hermes_keys()
    assert served, "could not read the /api/hermes response keys"

    block = AUDIT.read_text(encoding="utf-8").split("/api/hermes", 1)[1][:1200]
    printed = set(re.findall(r'd\.get\("([a-z_]+)"\)', block))
    assert printed, "the label asserts no fields, so the check cannot fail meaningfully"

    unknown = printed - served
    assert not unknown, (
        f"the audit prints fields /api/hermes does not expose: {sorted(unknown)} "
        f"(served: {sorted(served)})"
    )
    assert "status" in printed, "the label must assert the served status itself"


# --------------------------------------------------------------------------- #
# the watchdog: a monitor that stops must itself be an alert
# --------------------------------------------------------------------------- #


def _duration_seconds(value: str) -> float:
    """Parse a systemd time span (`15min`, `1h`, `90s`) into seconds."""
    m = re.fullmatch(r"\s*(\d+)\s*(ms|s|sec|min|h|hr|d)?\s*", value)
    assert m, f"unparseable systemd duration: {value!r}"
    scale = {"ms": 0.001, "s": 1, "sec": 1, "min": 60, "h": 3600, "hr": 3600, "d": 86400}
    return int(m.group(1)) * scale[(m.group(2) or "s").lower()]


@pytest.mark.parametrize("timer", [TIMER, WATCHDOG_TIMER])
def test_timers_do_not_depend_on_the_units_they_schedule(timer: Path) -> None:
    """`Requires=` is a dependency, not a trigger, and a monitor must not depend on the
    thing it watches.

    `[Timer] Unit=` is the directive that names a timer's target. Adding `Requires=`
    as well does not add a trigger; it (a) starts the target the moment the timer
    starts, bypassing the schedule, and (b) couples the timer's liveness to a unit
    whose documented contract is *expected to fail* while the hub is not ready.
    """
    unit = _sections(timer).get("Unit", {})
    assert "Requires" not in unit, (
        f"{timer.name} declares Requires={unit.get('Requires')}; a timer schedules, "
        "`Unit=` is the trigger, and a dependency here is not a trigger at all"
    )


def test_the_requires_guard_is_not_vacuous(tmp_path: Path) -> None:
    """Negative control: the guard must actually fire on a declared dependency.

    Without this, the assertion above is indistinguishable from never reading the file.
    """
    bad = tmp_path / "bad.timer"
    bad.write_text(
        "[Unit]\nRequires=camelot-selfcheck.service\n\n"
        "[Timer]\nUnit=camelot-selfcheck.service\n",
        encoding="utf-8",
    )
    assert _sections(bad).get("Unit", {}).get("Requires") == "camelot-selfcheck.service", (
        "the guard cannot detect a declared dependency"
    )


def test_the_watchdog_fails_and_reuses_the_same_alert_path() -> None:
    """A stopped monitor is a different condition from a failing post-condition, but it
    must not be a different delivery mechanism."""
    unit = _sections(WATCHDOG_SERVICE)
    assert unit.get("Unit", {}).get("OnFailure") == "camelot-selfcheck-alert.service"
    assert unit.get("Service", {}).get("Type") == "oneshot"
    assert unit.get("Service", {}).get("ExecStart") == (
        "/usr/local/lib/camelot/hub-selfcheck.sh watchdog"
    )


def test_the_watchdog_timer_is_independent_of_the_audit_timer() -> None:
    """Matched cadences fail together — same host, same boot, same clock — and a
    watchdog that dies with the thing it watches is not a watchdog."""
    audit = _sections(TIMER).get("Timer", {})
    watch = _sections(WATCHDOG_TIMER).get("Timer", {})
    assert watch.get("Unit") == "camelot-selfcheck-watchdog.service"
    assert _sections(WATCHDOG_TIMER).get("Install", {}).get("WantedBy") == "timers.target"

    audit_s = _duration_seconds(audit["OnUnitActiveSec"])
    watch_s = _duration_seconds(watch["OnUnitActiveSec"])
    assert watch_s != audit_s, "matched cadences fail together"
    assert watch_s > audit_s, (
        f"watchdog cadence ({watch_s}s) must be slower than the audit ({audit_s}s)"
    )
    assert watch_s / audit_s >= 2, (
        "the watchdog should observe several audit cycles per verdict, not 1.5"
    )
    assert watch.get("OnBootSec"), (
        "no first-run delay: a fresh boot could be judged as a stopped monitor"
    )


def test_the_staleness_threshold_exceeds_the_audit_cadence() -> None:
    """The limit must be looser than the cadence, or the watchdog panics on a slow run."""
    audit_s = _duration_seconds(_sections(TIMER)["Timer"]["OnUnitActiveSec"])
    m = re.search(r"CAMELOT_SELFCHECK_MAX_AGE_MIN:-?(\d+)", RUNNER.read_text(encoding="utf-8"))
    assert m, "the runner has no staleness limit for the watchdog to enforce"
    assert int(m.group(1)) * 60 > audit_s, (
        "the watchdog would flag the audit as stale before it is even late"
    )


def test_runner_implements_the_watchdog_subcommand() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "cmd_watchdog()" in text and "watchdog)" in text
    assert "WATCHDOG" in text and "watchdog.json" in text, (
        "the watchdog verdict is not persisted, so nothing can distinguish a stale "
        "monitor from failing post-conditions"
    )


def test_a_stale_monitor_is_reported_as_stale_not_as_failing_postconditions() -> None:
    """Sending the reader to status.json when the real fault is a dead timer is a
    misdiagnosis, and misdiagnosis is what this whole layer exists to prevent."""
    text = RUNNER.read_text(encoding="utf-8")
    assert "_monitor_stale_reason" in text
    assert "MONITOR STALE" in text


def test_the_alert_subject_names_the_actual_condition() -> None:
    """A subject saying "self-check failed" when the audit stopped running sends triage
    to status.json, where the real fault is not."""
    text = RUNNER.read_text(encoding="utf-8")
    assert "MONITOR STALE on" in text, "no distinct subject for a stopped monitor"
    assert "hub self-check failed on" in text, "no subject for failing post-conditions"


def test_there_is_exactly_one_delivery_path() -> None:
    """Two sendmail call sites are two delivery paths to keep in sync, and the one that
    drifts is the one that silently stops notifying."""
    assert RUNNER.read_text(encoding="utf-8").count("| sendmail ") == 1


def test_recovery_is_announced_by_the_only_unconditional_path() -> None:
    """systemd's OnFailure never fires on success, so a recovery announced from the
    alert path could never be delivered in production."""
    body = RUNNER.read_text(encoding="utf-8").split("cmd_watchdog()", 1)[1]
    assert "RECOVERED" in body


def test_deploy_installs_and_enables_the_watchdog() -> None:
    text = DEPLOY.read_text(encoding="utf-8")
    for u in ("camelot-selfcheck-watchdog.service", "camelot-selfcheck-watchdog.timer"):
        assert u in text, f"deploy script does not install {u}"
    assert "systemctl enable --now camelot-selfcheck.timer camelot-selfcheck-watchdog.timer" in text, (
        "a dead-man's switch that is not enabled is not a switch"
    )


def test_the_read_only_guard_still_catches_an_unguarded_mutator() -> None:
    """Negative control: skipping comments must not disarm the guard.

    Without this the fix above is indistinguishable from deleting the check, and
    a genuinely unguarded mutation would slip through silently.
    """
    fake = "#!/usr/bin/env bash\nset -euo pipefail\napt-get install -y qdrant\n"
    unguarded = [
        ln
        for ln in _code_lines(fake)
        if "apt-get install" in ln and not ln.startswith((" ", "\t"))
    ]
    assert unguarded, "comment-stripping disarmed the read-only guard"

    assert _code_lines("  # apt-get install -y qdrant\n") == [], (
        "commented example must not be treated as a directive"
    )
