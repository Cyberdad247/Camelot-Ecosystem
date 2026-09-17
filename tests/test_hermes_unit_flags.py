# SPDX-License-Identifier: MIT

"""The Hermes systemd unit must use flags `hermes serve` actually accepts.

`infra/systemd/hermes-agent.service` was authored from the upstream docs, and its
`--host`/`--port` flags shipped with an explicit "NOT verified against upstream"
caveat. Carrying the doubt openly was the right call, but a comment is not a
check — a wrong flag means the service silently fails to start, and the failure
surfaces as an unrelated-looking "unit failed" in `systemctl status`.

The flag set is checked against `tests/fixtures/hermes_serve_help.json`, which
records a real `hermes serve --help` capture from the hub — version, upstream
commit and date included. That matters: a test asserting against its own
hardcoded list of flags would prove only that the file agrees with itself. The
fixture also has to contain each flag it claims, so the accepted set cannot drift
away from the captured text.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
UNIT = REPO_ROOT / "infra" / "systemd" / "hermes-agent.service"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "hermes_serve_help.json"

HUB = "root@162.35.107.134"


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _unit_sections() -> dict[str, dict[str, str]]:
    """Key=Value pairs per systemd section, comments stripped."""
    sections: dict[str, dict[str, str]] = {}
    section: str | None = None
    for line in UNIT.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped.strip("[]")
            continue
        if section is None or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        sections.setdefault(section, {})[key.strip()] = value.strip()
    return sections


def _service_directives() -> dict[str, str]:
    """The [Service] section, where ExecStart and the sandbox live."""
    return _unit_sections().get("Service", {})


def _unit_directives() -> dict[str, str]:
    """The [Unit] section, where ConditionPathExists lives."""
    return _unit_sections().get("Unit", {})


def _exec_start() -> str:
    return _service_directives()["ExecStart"]


def _flags(exec_line: str, takes_value: set[str]) -> list[tuple[str, str | None]]:
    """(flag, value) pairs parsed out of a command line.

    Handles both `--flag value` and `--flag=value`. A value is only consumed for
    flags the fixture says take one, so a bare flag is never mistaken for its
    neighbour's argument.
    """
    tokens = exec_line.split()
    flags: list[tuple[str, str | None]] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("--"):
            if "=" in token:
                name, _, value = token.partition("=")
                flags.append((name, value))
            elif token in takes_value:
                flags.append((token, tokens[i + 1] if i + 1 < len(tokens) else None))
                i += 1
            else:
                flags.append((token, None))
        i += 1
    return flags


def _unit_flags() -> list[tuple[str, str | None]]:
    fixture = _fixture()
    return _flags(_exec_start(), set(fixture["flags_taking_a_value"]))


def test_the_unit_and_its_fixture_are_present() -> None:
    assert UNIT.is_file(), f"missing {UNIT}"
    assert FIXTURE.is_file(), f"missing {FIXTURE}"


def test_the_fixture_records_real_provenance() -> None:
    """A bare list of flags would just be a second hand-written guess."""
    prov = _fixture()["provenance"]
    for field in ("captured_at", "captured_from", "hermes_version", "upstream_commit", "command"):
        assert prov.get(field), f"fixture provenance is missing {field!r}"
    assert "serve" in prov["command"]


def test_the_fixture_took_its_flags_from_the_captured_help_text() -> None:
    """Every flag the fixture accepts must appear in the help text it recorded.

    Without this the accepted set could be edited independently of the capture,
    which is the same "authority with no evidence" problem the fixture exists to
    prevent.
    """
    fixture = _fixture()
    help_text = fixture["help_text"]
    missing = [f for f in fixture["accepted_flags"] if f not in help_text]
    assert not missing, f"fixture lists flags absent from its own captured help: {missing}"


def test_exec_start_runs_the_native_launcher_and_the_serve_subcommand() -> None:
    tokens = _exec_start().split()
    assert tokens[0].endswith("/hermes"), tokens[0]
    assert tokens[1] == "serve", f"expected the serve subcommand, got {tokens[1]!r}"
    # Rule 7: no container runtime in this path.
    assert "docker" not in _exec_start()


def test_condition_path_exists_matches_the_exec_start_binary() -> None:
    """If these disagree, systemd either skips the unit or fails to exec it."""
    directives = _unit_directives()
    binary = _exec_start().split()[0]
    assert directives.get("ConditionPathExists") == binary, (
        f"ConditionPathExists={directives.get('ConditionPathExists')!r} "
        f"but ExecStart runs {binary!r}"
    )


def test_every_exec_flag_is_one_hermes_serve_accepts() -> None:
    accepted = set(_fixture()["accepted_flags"])
    unsupported = [f for f, _ in _unit_flags() if f not in accepted]
    assert not unsupported, (
        f"ExecStart uses flags hermes serve does not accept: {unsupported}. "
        f"Accepts: {sorted(accepted)}"
    )


def test_unit_uses_skip_build() -> None:
    """Not an optimisation — without it the unit cannot start.

    `hermes serve` runs a web UI build step by default. Under this unit's sandbox
    that fails twice: ProtectSystem=strict makes /usr/local read-only so the build
    output cannot be written, and IPAddressDeny=any blocks the npm registry.
    """
    assert ("--skip-build", None) in _unit_flags()


def test_unit_avoids_flags_that_are_meaningless_or_terminal_in_a_service() -> None:
    forbidden = set(_fixture()["flags_that_must_not_be_used_by_a_systemd_unit"])
    used = {f for f, _ in _unit_flags()}
    assert not (used & forbidden), f"unit uses unsuitable flags: {sorted(used & forbidden)}"


def test_host_bind_is_loopback() -> None:
    """The gateway is loopback-only; the mesh bridge fronts it.

    `hermes serve --help` is explicit that a non-loopback bind always requires an
    auth provider, and the unit's own IPAddressDeny=any would block anything but
    loopback and the tailnet anyway.
    """
    host = dict(_unit_flags()).get("--host")
    assert host in {"127.0.0.1", "localhost", "::1"}, f"non-loopback bind: {host!r}"


def test_port_is_an_explicit_valid_port() -> None:
    port = dict(_unit_flags()).get("--port")
    assert port is not None, "unit does not pin --port; it would take upstream's default"
    assert port.isdigit() and 1 <= int(port) <= 65535, f"invalid port: {port!r}"


def test_hermes_home_is_pinned() -> None:
    """Load-bearing under ProtectHome=yes: the default ~/.hermes is unreachable.

    Without it the agent starts and then fails to persist, which presents as
    "running but forgetting everything" rather than as a startup error.
    """
    env = _service_directives().get("Environment", "")
    assert "HERMES_HOME=" in env, f"HERMES_HOME not set: {env!r}"
    assert "ProtectHome=yes" in UNIT.read_text(encoding="utf-8")


def test_the_flag_validator_can_actually_fail() -> None:
    """Negative control.

    A validator that accepted everything would pass every test above while
    protecting nothing. This proves the parser surfaces a flag that is not in the
    accepted set, and that such a flag is genuinely absent from the fixture.
    """
    fixture = _fixture()
    invented = "--definitely-not-a-real-flag"
    parsed = _flags(
        f"/usr/local/bin/hermes serve {invented} --host 127.0.0.1 --port 9119",
        set(fixture["flags_taking_a_value"]),
    )
    parsed_names = [f for f, _ in parsed]
    assert invented in parsed_names, "parser failed to surface an unknown flag"
    assert invented not in set(fixture["accepted_flags"])
    # ...and a value-taking flag is paired with its value, not dropped.
    assert ("--host", "127.0.0.1") in parsed
    assert ("--port", "9119") in parsed
    # The real unit must not be carrying anything the parser would reject.
    assert {f for f, _ in _unit_flags()} <= set(fixture["accepted_flags"])


@pytest.mark.skipif(
    os.environ.get("CAMELOT_HUB_SSH") != "1" or shutil.which("ssh") is None,
    reason="opt-in: set CAMELOT_HUB_SSH=1 to re-verify against the live hub",
)
def test_live_help_still_matches_the_fixture() -> None:  # pragma: no cover - opt-in
    """Re-capture from the hub and confirm the fixture has not gone stale.

    Skipped by default: CI should not depend on SSH to a production hub. Run this
    when upgrading Hermes, and update the fixture with the result.
    """
    out = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=12", HUB, "hermes serve --help"],
        capture_output=True,
        text=True,
        timeout=90,
    )
    if out.returncode != 0:
        pytest.skip(f"could not reach the hub: {out.stderr.strip()[:200]}")
    live, recorded = out.stdout, _fixture()["help_text"]
    missing = [f for f in _fixture()["accepted_flags"] if f not in live]
    assert not missing, f"flags in the fixture no longer offered by the live hub: {missing}"
    unsupported = [f for f, _ in _unit_flags() if f not in live]
    assert not unsupported, f"ExecStart flags the live hub rejects: {unsupported}"
    assert live == recorded, "live help text differs from the fixture; refresh it"
